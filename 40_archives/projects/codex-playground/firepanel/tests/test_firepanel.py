from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
import json
import tempfile
from threading import Barrier
from time import sleep
from types import SimpleNamespace
import unittest
from pathlib import Path
from unittest.mock import patch

from dateutil import tz
import config_store
import server
import todoist_feed
from icalendar import Calendar


class FirePanelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        data = Path(self.temp.name)
        self.patches = [
            patch.object(config_store, "SETTINGS_FILE", data / "settings.json"),
            patch.object(config_store, "AUTH_FILE", data / "auth.json"),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        config_store.set_password("test-password-123")
        self.target = data / "example.exe"
        self.target.write_bytes(b"test")
        self.settings = config_store.default_settings()
        self.settings["buttons"][0] = {"label": "テスト", "path": str(self.target)}
        config_store.save_settings(self.settings)
        self.client = server.create_app().test_client()

    def login(self):
        response = self.client.post("/login", data={"password": "test-password-123"})
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            return session["csrf"]

    def test_login_and_status(self):
        self.assertEqual(self.client.get("/api/status").status_code, 401)
        self.assertEqual(self.client.post("/login", data={"password": "wrong"}).status_code, 401)
        self.login()
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        self.assertIn("cpu", response.json)
        self.assertIn("memory", response.json)

    def test_long_password_can_log_in(self):
        password = "long-passphrase-" * 20
        config_store.set_password(password)
        client = server.create_app().test_client()
        self.assertEqual(client.post("/login", data={"password": password}).status_code, 302)

    def test_concurrent_failed_logins_count_every_attempt(self):
        ready = Barrier(6)

        def attempt(_):
            client = self.client.application.test_client()
            ready.wait()
            return client.post("/login", data={"password": "wrong"})

        def slow_rejection(*_):
            sleep(0.02)
            return False

        with patch.object(server, "verify_password", side_effect=slow_rejection) as verify:
            with ThreadPoolExecutor(max_workers=6) as pool:
                responses = list(pool.map(attempt, range(6)))

        self.assertEqual(verify.call_count, 5)
        self.assertTrue(all(response.status_code == 401 for response in responses))
        self.assertEqual(sum("5分後".encode("utf-8") in response.data for response in responses), 1)

    def test_launch_needs_login_and_csrf_and_uses_saved_path(self):
        with patch.object(server.os, "startfile") as start:
            self.assertEqual(self.client.post("/api/launch/0").status_code, 401)
            csrf = self.login()
            self.assertEqual(self.client.post("/api/launch/0").status_code, 403)
            self.assertEqual(self.client.post("/api/launch/6", headers={"X-FirePanel-CSRF": csrf}).status_code, 404)
            self.assertEqual(self.client.post("/api/launch/1", headers={"X-FirePanel-CSRF": csrf}).status_code, 409)
            self.assertEqual(self.client.post("/api/launch/0", headers={"X-FirePanel-CSRF": csrf}).status_code, 200)
            start.assert_called_once_with(str(self.target))

    def test_missing_registered_file_disables_button(self):
        self.target.unlink()
        self.login()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-slot="0" disabled', response.data)

    def test_settings_reject_arbitrary_commands(self):
        self.settings["buttons"][0]["path"] = "cmd.exe /c something"
        with self.assertRaises(ValueError):
            config_store.save_settings(self.settings)

    def test_button_labels_are_escaped(self):
        self.settings["buttons"][0]["label"] = "<b>テスト</b>"
        config_store.save_settings(self.settings)
        self.login()
        html = self.client.get("/").data
        self.assertNotIn("<b>テスト</b>".encode("utf-8"), html)

    def test_untrusted_host_is_rejected(self):
        self.assertEqual(self.client.get("/login", headers={"Host": "other.example"}).status_code, 400)

    def test_eight_saved_buttons_are_preserved_but_only_six_are_displayed(self):
        old_settings = {**self.settings, "buttons": self.settings["buttons"] + [
            {"label": "旧7", "path": str(Path(self.temp.name) / "missing.exe")},
            {"label": "旧8", "path": ""}
        ]}
        config_store.SETTINGS_FILE.write_text(json.dumps(old_settings), encoding="utf-8")
        updated = config_store.load_settings()
        self.assertEqual(len(updated["buttons"]), 8)
        self.assertEqual(updated["buttons"][0], old_settings["buttons"][0])
        config_store.save_settings(updated)
        self.assertEqual(len(json.loads(config_store.SETTINGS_FILE.read_text(encoding="utf-8"))["buttons"]), 8)
        self.login()
        self.assertEqual(self.client.get("/").data.decode("utf-8").count('data-slot="'), 6)

    def test_details_include_drives_and_handle_unavailable_drive(self):
        self.login()

        def disk_usage(path):
            if path == "E:\\":
                raise OSError("drive unavailable")
            return SimpleNamespace(used=30_000_000_000, total=256_000_000_000, percent=11.7)

        with patch.object(server.psutil, "disk_usage", side_effect=disk_usage):
            self.assertNotIn("drives", self.client.get("/api/status").json)
            response = self.client.get("/api/status?details=1")
        self.assertEqual(response.json["drives"]["C"]["total"], 256_000_000_000)
        self.assertIsNone(response.json["drives"]["E"])

    def test_dashboard_has_six_app_slots_todoist_and_fullscreen_control(self):
        self.login()
        html = self.client.get("/").data.decode("utf-8")
        self.assertEqual(html.count('data-slot="'), 6)
        self.assertIn('id="fullscreen-button"', html)
        self.assertIn('id="todoist-list"', html)
        self.assertNotIn('id="logout-form"', html)

    def test_todoist_url_is_validated_and_not_exposed_in_dashboard(self):
        self.settings["todoist_feed_url"] = "https://ext.todoist.com/export/ical/example?token=secret"
        config_store.save_settings(self.settings)
        self.login()
        self.assertNotIn(b"token=secret", self.client.get("/").data)
        for bad_url in ("http://ext.todoist.com/feed", "https://todoist.com.evil.test/feed", "https://127.0.0.1/feed"):
            self.settings["todoist_feed_url"] = bad_url
            with self.assertRaises(ValueError):
                config_store.save_settings(self.settings)

    def test_todoist_api_needs_login_and_returns_feed(self):
        self.assertEqual(self.client.get("/api/todoist").status_code, 401)
        self.login()
        self.assertEqual(self.client.get("/api/todoist").json["state"], "unconfigured")

    def test_calendar_feed_parses_all_day_timed_and_recurring_tasks(self):
        calendar = Calendar.from_ical(b"\r\n".join([
            b"BEGIN:VCALENDAR", b"VERSION:2.0", b"PRODID:-//FirePanel test//EN",
            b"BEGIN:VEVENT", b"UID:all-day", b"DTSTAMP:20261025T000000Z",
            b"DTSTART;VALUE=DATE:20261026", b"DTEND;VALUE=DATE:20261027",
            b"SUMMARY:All day", b"END:VEVENT",
            b"BEGIN:VEVENT", b"UID:repeat", b"DTSTAMP:20261025T000000Z",
            b"DTSTART:20261025T093000", b"DTEND:20261025T103000",
            b"RRULE:FREQ=DAILY;COUNT=3", b"SUMMARY:Recurring", b"END:VEVENT",
            b"END:VCALENDAR", b"",
        ]))
        tasks = todoist_feed.tasks_for_day(calendar, date(2026, 10, 26))
        self.assertEqual(tasks, [
            {"when": "09:30", "title": "Recurring"},
            {"when": "終日", "title": "All day"},
        ])

    def test_feed_uses_next_tasks_when_today_is_empty_and_keeps_cache_on_failure(self):
        day = datetime.now().astimezone().date()
        tomorrow = (day + timedelta(days=1)).strftime("%Y%m%d")
        following = (day + timedelta(days=2)).strftime("%Y%m%d")
        calendar = Calendar.from_ical((
            "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//FirePanel test//EN\r\n"
            f"BEGIN:VEVENT\r\nUID:next\r\nDTSTAMP:{tomorrow}T000000Z\r\n"
            f"DTSTART;VALUE=DATE:{tomorrow}\r\nDTEND;VALUE=DATE:{following}\r\n"
            "SUMMARY:Next task\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
        ).encode("utf-8"))
        feed = todoist_feed.TodoistFeed()
        with patch.object(todoist_feed, "fetch_calendar", side_effect=[calendar, OSError("offline")]), patch.object(
            todoist_feed, "monotonic", side_effect=[100.0, 200.0]
        ):
            first = feed.read("https://ext.todoist.com/feed")
            stale = feed.read("https://ext.todoist.com/feed", refresh=True)
        self.assertEqual(first["scope"], "upcoming")
        self.assertEqual(first["tasks"][0]["title"], "Next task")
        self.assertEqual(stale["state"], "stale")
        self.assertEqual(stale["tasks"], first["tasks"])

    def test_task_near_local_midnight_is_selected_for_local_day(self):
        day = date(2026, 10, 26)
        local_zone = todoist_feed.local_timezone()
        local_start = datetime.combine(day, time(0, 30), local_zone)
        utc_start = local_start.astimezone(timezone.utc)
        utc_end = utc_start + timedelta(hours=1)
        calendar = Calendar.from_ical((
            "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//FirePanel test//EN\r\n"
            "BEGIN:VEVENT\r\nUID:midnight\r\nDTSTAMP:20261025T000000Z\r\n"
            f"DTSTART:{utc_start:%Y%m%dT%H%M%SZ}\r\n"
            f"DTEND:{utc_end:%Y%m%dT%H%M%SZ}\r\n"
            "SUMMARY:Local midnight\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
        ).encode("utf-8"))
        self.assertEqual(todoist_feed.tasks_for_day(calendar, day, local_zone), [
            {"when": "00:30", "title": "Local midnight"}
        ])

    def test_upcoming_task_uses_future_daylight_saving_offset(self):
        calendar = Calendar.from_ical(b"\r\n".join([
            b"BEGIN:VCALENDAR", b"VERSION:2.0", b"PRODID:-//FirePanel test//EN",
            b"BEGIN:VEVENT", b"UID:dst", b"DTSTAMP:20261026T000000Z",
            b"DTSTART:20261102T140000Z", b"DTEND:20261102T150000Z",
            b"SUMMARY:After DST", b"END:VEVENT", b"END:VCALENDAR", b"",
        ]))
        self.assertEqual(todoist_feed.upcoming_tasks(calendar, date(2026, 10, 26), tz.gettz("America/New_York")), [
            {"when": "11/2 09:00", "title": "After DST"}
        ])


if __name__ == "__main__":
    unittest.main()
