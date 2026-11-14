"""Create and publish a verified, full Hermes backup. No automatic deletion."""
from __future__ import annotations

import datetime as dt
import hashlib
import os
from pathlib import Path
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


def main() -> int:
    if not READY.is_dir():
        raise RuntimeError(f"The synced destination is missing: {READY}")
    if not HERMES.is_file():
        raise RuntimeError(f"Hermes launcher is missing: {HERMES}")
    STAGING.mkdir(parents=True, exist_ok=True)
    name = "hermes-backup-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S") + ".zip"
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
    with source.open("rb") as src, partial.open("xb") as dst:
        shutil.copyfileobj(src, dst)
        dst.flush()
        os.fsync(dst.fileno())
    if partial.stat().st_size != source.stat().st_size or digest(partial) != expected:
        raise RuntimeError(f"Published copy failed verification; partial retained: {partial}")
    partial.rename(target)
    log(f"Published {target} ({target.stat().st_size} bytes, sha256={expected}). Cloud sync status not verified.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        log(f"FAILED: {exc}")
        sys.exit(1)
