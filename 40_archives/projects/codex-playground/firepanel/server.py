"""Serve the FirePanel dashboard on a chosen local IPv4 address."""

from datetime import timedelta
import os
from threading import Lock
from time import monotonic
import secrets

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import psutil
from waitress import serve

from config_store import BUTTON_COUNT, is_launchable, load_auth, load_settings, verify_password
from todoist_feed import TodoistFeed


def drive_usage(letter):
    try:
        usage = psutil.disk_usage(f"{letter}:\\")
    except OSError:
        return None
    return {"used": usage.used, "total": usage.total, "percent": usage.percent}


def create_app():
    auth = load_auth()
    if auth is None:
        raise RuntimeError("先に python settings.py で合言葉を設定してください。")
    app = Flask(__name__)
    app.secret_key = auth["secret_key"]
    app.config.update(
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        SESSION_COOKIE_NAME="firepanel_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        TRUSTED_HOSTS=[load_settings()["host"], "localhost"],
        MAX_CONTENT_LENGTH=4096,
    )
    failed_logins = {}
    login_lock = Lock()
    todoist_feed = TodoistFeed()
    psutil.cpu_percent(interval=None)

    def signed_in():
        return session.get("signed_in") is True

    def csrf_valid():
        supplied = request.headers.get("X-FirePanel-CSRF", "")
        expected = session.get("csrf", "")
        return bool(expected) and secrets.compare_digest(supplied, expected)

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.get("/")
    def dashboard():
        if not signed_in():
            return redirect(url_for("login"))
        buttons = [
            {"label": item["label"], "enabled": is_launchable(item["path"])}
            for item in load_settings()["buttons"][:BUTTON_COUNT]
        ]
        return render_template("dashboard.html", buttons=buttons, csrf=session["csrf"])

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if signed_in():
            return redirect(url_for("dashboard"))
        error = None
        if request.method == "POST":
            address = request.remote_addr or "unknown"
            with login_lock:
                now = monotonic()
                count, first = failed_logins.get(address, (0, now))
                if now - first >= 300:
                    count, first = 0, now
                blocked = count >= 5
                accepted = False
                if not blocked:
                    accepted = verify_password(request.form.get("password", ""), auth)
                    if accepted:
                        failed_logins.pop(address, None)
                    else:
                        failed_logins[address] = (count + 1, first)
            if blocked:
                error = "試行回数が多いため、5分後にお試しください。"
            elif accepted:
                session.clear()
                session["signed_in"] = True
                session["csrf"] = secrets.token_hex(24)
                session.permanent = True
                return redirect(url_for("dashboard"))
            else:
                error = "合言葉が違います。"
        return render_template("login.html", error=error), (401 if error else 200)

    @app.get("/api/status")
    def status():
        if not signed_in():
            return jsonify(error="認証が必要です。"), 401
        result = dict(
            cpu=round(psutil.cpu_percent(interval=None)),
            memory=round(psutil.virtual_memory().percent),
        )
        if request.args.get("details") == "1":
            result["drives"] = {letter: drive_usage(letter) for letter in ("C", "E")}
        return jsonify(result)

    @app.get("/api/todoist")
    def todoist():
        if not signed_in():
            return jsonify(error="認証が必要です。"), 401
        feed_url = load_settings()["todoist_feed_url"]
        return jsonify(todoist_feed.read(feed_url, refresh=request.args.get("refresh") == "1"))

    @app.post("/api/launch/<int:slot>")
    def launch(slot):
        if not signed_in():
            return jsonify(error="認証が必要です。"), 401
        if not csrf_valid():
            return jsonify(error="操作を確認できません。画面を再読み込みしてください。"), 403
        buttons = load_settings()["buttons"][:BUTTON_COUNT]
        if slot < 0 or slot >= len(buttons):
            return jsonify(error="ボタンがありません。"), 404
        target = buttons[slot]["path"]
        if not is_launchable(target):
            return jsonify(error="アプリが登録されていません。"), 409
        try:
            os.startfile(target)
        except OSError:
            app.logger.exception("Could not launch configured application in slot %s", slot + 1)
            return jsonify(error="アプリを起動できませんでした。"), 500
        return jsonify(message=f"{buttons[slot]['label']} を起動しました。")

    @app.post("/logout")
    def logout():
        if not signed_in() or not csrf_valid():
            return redirect(url_for("login"))
        session.clear()
        return redirect(url_for("login"))

    return app


def main():
    settings = load_settings()
    app = create_app()
    address = f"http://{settings['host']}:{settings['port']}"
    print(f"FirePanel: {address}")
    print("終了: Ctrl+C")
    serve(app, host=settings["host"], port=settings["port"], ipv6=False, max_request_body_size=4096)


if __name__ == "__main__":
    main()
