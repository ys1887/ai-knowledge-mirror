"""Read and validate the local FirePanel settings and login secret."""

import hashlib
import hmac
import ipaddress
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlsplit


DATA_DIR = Path(__file__).resolve().parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"
AUTH_FILE = DATA_DIR / "auth.json"
BUTTON_COUNT = 6
PREVIOUS_BUTTON_COUNT = 8
ALLOWED_SUFFIXES = {".exe", ".lnk"}


def default_settings():
    return {
        "host": "127.0.0.1",
        "port": 8765,
        "todoist_feed_url": "",
        "buttons": [
            {"label": f"アプリ {number}", "path": ""}
            for number in range(1, BUTTON_COUNT + 1)
        ],
    }


def validate_todoist_feed_url(feed_url):
    if not isinstance(feed_url, str) or len(feed_url) > 2048:
        raise ValueError("TodoistカレンダーURLが正しくありません。")
    feed_url = feed_url.strip()
    if feed_url:
        try:
            parsed = urlsplit(feed_url)
            port = parsed.port
            hostname = parsed.hostname
        except ValueError as exc:
            raise ValueError("TodoistカレンダーURLが正しくありません。") from exc
        if (
            parsed.scheme != "https"
            or not hostname
            or not (hostname == "todoist.com" or hostname.endswith(".todoist.com"))
            or port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise ValueError("TodoistのHTTPSカレンダーURLを指定してください。")
    return feed_url


def validate_settings(settings):
    if not isinstance(settings, dict):
        raise ValueError("設定の形式が正しくありません。")
    try:
        address = ipaddress.IPv4Address(settings["host"])
    except (KeyError, ipaddress.AddressValueError, TypeError) as exc:
        raise ValueError("待受IPにはIPv4アドレスを指定してください。") from exc
    if address.is_unspecified or address.is_multicast or not (
        address.is_private or address.is_loopback
    ):
        raise ValueError("待受IPにはPCのローカルIPを指定してください。")
    port = settings.get("port")
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("ポート番号は1024～65535で指定してください。")
    buttons = settings.get("buttons")
    if not isinstance(buttons, list) or len(buttons) not in (BUTTON_COUNT, PREVIOUS_BUTTON_COUNT):
        raise ValueError("ボタンは6個必要です。")
    for number, button in enumerate(buttons, 1):
        if not isinstance(button, dict):
            raise ValueError(f"ボタン{number}の設定が不正です。")
        label, path = button.get("label"), button.get("path")
        if not isinstance(label, str) or not 1 <= len(label.strip()) <= 24:
            raise ValueError(f"ボタン{number}の名前は1～24文字で入力してください。")
        if not isinstance(path, str):
            raise ValueError(f"ボタン{number}の起動先が不正です。")
        if path and (not Path(path).is_absolute() or Path(path).suffix.lower() not in ALLOWED_SUFFIXES):
            raise ValueError(f"ボタン{number}の起動先は絶対パスの.exeか.lnkを指定してください。")
    return {**settings, "todoist_feed_url": validate_todoist_feed_url(settings.get("todoist_feed_url", ""))}


def is_launchable(path):
    target = Path(path)
    return target.is_absolute() and target.is_file() and target.suffix.lower() in ALLOWED_SUFFIXES


def load_settings():
    if not SETTINGS_FILE.exists():
        return default_settings()
    try:
        return validate_settings(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("設定ファイルを読み込めません。") from exc


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def save_settings(settings):
    settings = validate_settings(settings)
    for number, button in enumerate(settings["buttons"][:BUTTON_COUNT], 1):
        if button["path"] and not is_launchable(button["path"]):
            raise ValueError(f"ボタン{number}の起動先が見つかりません。")
    _write_json(SETTINGS_FILE, settings)


def load_auth():
    if not AUTH_FILE.exists():
        return None
    try:
        auth = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        if not all(isinstance(auth.get(key), str) for key in ("salt", "password_hash", "secret_key")):
            raise ValueError("認証ファイルの形式が正しくありません。")
        if any(
            len(bytes.fromhex(auth[key])) != length
            for key, length in (("salt", 16), ("password_hash", 32), ("secret_key", 32))
        ):
            raise ValueError("認証ファイルの内容が正しくありません。")
        return auth
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("認証ファイルを読み込めません。") from exc


def set_password(password):
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("合言葉は8文字以上にしてください。")
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000)
    _write_json(AUTH_FILE, {
        "salt": salt.hex(),
        "password_hash": password_hash.hex(),
        "secret_key": secrets.token_hex(32),
    })


def verify_password(password, auth):
    try:
        salt = bytes.fromhex(auth["salt"])
        expected = bytes.fromhex(auth["password_hash"])
    except (KeyError, TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000)
    return hmac.compare_digest(actual, expected)
