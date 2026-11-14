from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from profiles import ValidationError
from workflow import next_work_output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve the next work output filename.")
    parser.add_argument(
        "--work-dir",
        default=str(Path(__file__).resolve().parent.parent / "work"),
        help="Work directory to scan. Defaults to the repository work directory.",
    )
    parser.add_argument(
        "--date",
        dest="day",
        help="Override date in YYYY-MM-DD format. Defaults to the current local date.",
    )
    args = parser.parse_args(argv)

    try:
        work_dir = Path(args.work_dir)
        current_day = date.fromisoformat(args.day) if args.day else None
        sys.stdout.write(str(next_work_output_path(work_dir, today=current_day)))
        sys.stdout.write("\n")
    except (ValidationError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
