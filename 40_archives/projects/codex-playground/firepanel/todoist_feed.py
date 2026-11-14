"""Read a Todoist iCalendar feed and select today's or upcoming tasks."""

from datetime import date, datetime, time, timedelta
from http.client import HTTPException
import os
from threading import Lock
from time import monotonic
from urllib import request

from icalendar import Calendar
import recurring_ical_events
from dateutil import tz

from config_store import validate_todoist_feed_url


MAX_FEED_BYTES = 2_000_000
REFRESH_SECONDS = 300
MANUAL_REFRESH_SECONDS = 30


def local_timezone():
    return tz.tzwinlocal() if os.name == "nt" else tz.tzlocal()


class TodoistFeed:
    def __init__(self):
        self._lock = Lock()
        self._url = None
        self._calendar = None
        self._last_attempt = 0.0
        self._last_success = None
        self._error = False

    def read(self, url, refresh=False):
        if not url:
            return {"state": "unconfigured", "tasks": [], "updated_at": None}
        timezone = local_timezone()
        today = datetime.now(timezone).date()
        with self._lock:
            if url != self._url:
                self._url = url
                self._calendar = None
                self._last_attempt = 0.0
                self._last_success = None
                self._error = False
            now = monotonic()
            age = now - self._last_attempt
            interval = MANUAL_REFRESH_SECONDS if refresh else REFRESH_SECONDS
            if self._last_attempt == 0.0 or age >= interval:
                self._last_attempt = now
                try:
                    self._calendar = fetch_calendar(url)
                    self._last_success = datetime.now().astimezone().isoformat(timespec="minutes")
                    self._error = False
                except (OSError, ValueError, HTTPException):
                    self._error = True
            calendar = self._calendar
            updated_at = self._last_success
            failed = self._error
        if calendar is None:
            return {"state": "error", "tasks": [], "updated_at": updated_at}
        try:
            tasks = tasks_for_day(calendar, today, timezone)
            scope = "today"
            if not tasks:
                tasks = upcoming_tasks(calendar, today, timezone)
                scope = "upcoming" if tasks else "today"
        except (ValueError, TypeError, KeyError):
            return {"state": "error", "tasks": [], "updated_at": updated_at}
        return {
            "state": "stale" if failed else "ok",
            "scope": scope,
            "tasks": tasks,
            "updated_at": updated_at,
        }


class TodoistRedirects(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_todoist_feed_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_calendar(url):
    validate_todoist_feed_url(url)
    opener = request.build_opener(TodoistRedirects())
    with opener.open(request.Request(url, headers={"User-Agent": "FirePanel/1"}), timeout=6) as response:
        content = response.read(MAX_FEED_BYTES + 1)
    if len(content) > MAX_FEED_BYTES:
        raise ValueError("Todoist feed is too large")
    calendar = Calendar.from_ical(content)
    if calendar.name != "VCALENDAR":
        raise ValueError("Invalid iCalendar feed")
    return calendar


def tasks_for_day(calendar, day, timezone=None):
    if not isinstance(day, date):
        raise TypeError("day must be a date")
    timezone = timezone or local_timezone()
    tasks = []
    start_of_day = datetime.combine(day, time.min, timezone)
    for event in recurring_ical_events.of(calendar).between(start_of_day, start_of_day + timedelta(days=1)):
        if event.name != "VEVENT" or str(event.get("STATUS", "")).upper() == "CANCELLED":
            continue
        start = event.decoded("DTSTART")
        if isinstance(start, datetime):
            local = start.astimezone(timezone) if start.tzinfo else start
            if local.date() != day:
                continue
            when = local.strftime("%H:%M")
        else:
            if start != day:
                continue
            when = "終日"
        title = str(event.get("SUMMARY", "")).strip()
        if title:
            tasks.append({"when": when, "title": title[:120]})
    tasks.sort(key=lambda task: (task["when"] == "終日", task["when"], task["title"]))
    return tasks


def upcoming_tasks(calendar, day, timezone=None):
    timezone = timezone or local_timezone()
    found = []
    tomorrow = datetime.combine(day + timedelta(days=1), time.min, timezone)
    end = datetime.combine(day + timedelta(days=31), time.min, timezone)
    for event in recurring_ical_events.of(calendar).between(tomorrow, end):
        if event.name != "VEVENT" or str(event.get("STATUS", "")).upper() == "CANCELLED":
            continue
        start = event.decoded("DTSTART")
        local = start.astimezone(timezone) if isinstance(start, datetime) and start.tzinfo else start
        event_day = local.date() if isinstance(local, datetime) else local
        if event_day <= day:
            continue
        title = str(event.get("SUMMARY", "")).strip()
        if not title:
            continue
        when = f"{event_day.month}/{event_day.day}"
        if isinstance(local, datetime):
            when += f" {local:%H:%M}"
        found.append((local, {"when": when, "title": title[:120]}))
    found.sort(key=lambda entry: (entry[0].date() if isinstance(entry[0], datetime) else entry[0], entry[1]["when"], entry[1]["title"]))
    return [task for _, task in found[:5]]
