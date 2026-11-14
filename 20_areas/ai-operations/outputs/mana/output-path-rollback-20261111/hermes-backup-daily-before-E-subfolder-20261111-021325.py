"""Publish a verified backup to E and Z; retire yesterday's matching pair."""
from __future__ import annotations

import datetime as dt
import hashlib
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(r"E:\Documents\AI\scripts")
STAGING = Path(r"E:\Documents\Backup")
READY = Path(r"Z:\HermesBackup")
HERMES = Path.home() / "AppData" / "Local" / "hermes" / "hermes-agent" / ".hermes" / "bin" / "hermes.exe"
REQUIRED = {"state.db", "profiles/mana/state.db", "profiles/arcana/state.db",
            "profiles/mana/SOUL.md", "profiles/arcana/SOUL.md"}
BACKUP_NAME = re.compile(r"hermes-backup-(\d{8})-\d{6}\.zip\Z")


def log(message: str) -> None:
    stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    line = f"{stamp} {message}"
    print(line, flush=True)
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
        with (ROOT / "hermes-backup-daily.log").open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        print("Could not write log; inspect task history.", file=sys.stderr)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate(path: Path) -> None:
    if path.stat().st_size == 0:
        raise RuntimeError("Empty backup ZIP")
    with zipfile.ZipFile(path) as z:
        missing = REQUIRED - set(z.namelist())
        if missing:
            raise RuntimeError(f"Missing expected entries: {sorted(missing)}")
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC error at {bad}")
        # The root SQLite copy must be complete and self-consistent.
        with tempfile.TemporaryDirectory(dir=STAGING) as scratch:
            dbfile = Path(scratch) / "state.db"
            with z.open("state.db") as src, dbfile.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            db = sqlite3.connect(f"file:{dbfile.as_posix()}?mode=ro", uri=True)
            try:
                if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise RuntimeError("Root SQLite quick_check failed")
            finally:
                db.close()


def retire_yesterday(today: dt.date, new_name: str) -> None:
    """Only remove one complete, identical E/Z pair from the prior date."""
    yesterday = (today - dt.timedelta(days=1)).strftime("%Y%m%d")
    e_names = {p.name for p in STAGING.iterdir() if p.is_file()
               and (m := BACKUP_NAME.fullmatch(p.name)) and m.group(1) == yesterday}
    z_names = {p.name for p in READY.iterdir() if p.is_file()
               and (m := BACKUP_NAME.fullmatch(p.name)) and m.group(1) == yesterday}
    if not e_names and not z_names:
        log(f"No backup from yesterday ({yesterday}); no deletion.")
        return
    if len(e_names) != 1 or e_names != z_names:
        log(f"Yesterday's E/Z backups are not one matching-name pair; no deletion "
            f"(E={len(e_names)}, Z={len(z_names)}).")
        return
    old_name = e_names.pop()
    if old_name == new_name:
        raise RuntimeError("Refusing to retire the new backup")
    e_old, z_old = STAGING / old_name, READY / old_name
    if e_old.stat().st_size != z_old.stat().st_size or digest(e_old) != digest(z_old):
        log(f"Yesterday's E/Z backups differ: {old_name}; no deletion.")
        return
    # Recheck the new pair immediately before removing the old one.
    e_new, z_new = STAGING / new_name, READY / new_name
    if (not e_new.is_file() or not z_new.is_file()
            or e_new.stat().st_size != z_new.stat().st_size
            or digest(e_new) != digest(z_new)):
        raise RuntimeError("New E/Z pair is not identical; yesterday retained")
    # No general retention sweep: leave any older archives for manual handling.
    e_old.unlink()
    z_old.unlink()
    log(f"Removed yesterday's verified E/Z pair: {old_name}")


def main() -> int:
    if not HERMES.is_file():
        raise RuntimeError(f"Hermes launcher is missing: {HERMES}")
    STAGING.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now()
    name = "hermes-backup-" + started.strftime("%Y%m%d-%H%M%S") + ".zip"
    source = STAGING / name
    target = READY / name
    partial = READY / (name + ".partial")
    if source.exists() or target.exists() or partial.exists():
        raise RuntimeError("Refusing to overwrite an existing backup")
    log(f"Starting backup: {source}")
    result = subprocess.run([str(HERMES), "backup", "-o", str(source), "--keep", "0"],
                            env={**os.environ, "HERMES_HOME": str(Path.home() / "AppData" / "Local" / "hermes")})
    if result.returncode != 0:
        raise RuntimeError(f"hermes backup exited {result.returncode}; source retained for inspection")
    validate(source)
    expected = digest(source)
    if not READY.is_dir():
        raise RuntimeError(f"The destination is missing: {READY}; verified E backup retained: {source}")
    with source.open("rb") as src, partial.open("xb") as dst:
        shutil.copyfileobj(src, dst)
        dst.flush()
        os.fsync(dst.fileno())
    if partial.stat().st_size != source.stat().st_size or digest(partial) != expected:
        raise RuntimeError(f"Published copy failed verification; partial retained: {partial}")
    partial.rename(target)
    log(f"Published {target} ({target.stat().st_size} bytes, sha256={expected}). Cloud sync status not verified.")
    try:
        retire_yesterday(started.date(), name)
    except OSError as exc:
        log(f"Could not complete yesterday's cleanup: {exc}; inspect both volumes.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"FAILED: {exc}")
        sys.exit(1)
