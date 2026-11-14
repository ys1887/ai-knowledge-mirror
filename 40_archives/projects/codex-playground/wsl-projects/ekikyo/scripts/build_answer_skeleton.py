from __future__ import annotations

import argparse
import sys
from pathlib import Path

from profiles import ValidationError
from resolving import resolve_input
from workflow import build_answer_skeleton


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"input file not found: {path}")
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an answer skeleton for the active EXTRACT template.")
    parser.add_argument("--input", required=True, help="Input file path.")
    args = parser.parse_args(argv)

    try:
        text = _read_text(Path(args.input))
        resolved = resolve_input(text)
        sys.stdout.write(build_answer_skeleton(resolved))
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
