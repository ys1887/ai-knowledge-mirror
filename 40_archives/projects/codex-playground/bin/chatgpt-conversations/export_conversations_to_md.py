#!/usr/bin/env python3
"""Export ChatGPT conversations.json to year/month Markdown files.

Output layout:
  <output>/<YYYY>/<YYYY-MM>/<thread>.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set

try:
    from zoneinfo import ZoneInfo
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Python 3.9+ (zoneinfo) is required.") from exc


WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    "com1",
    "com2",
    "com3",
    "com4",
    "com5",
    "com6",
    "com7",
    "com8",
    "com9",
    "lpt1",
    "lpt2",
    "lpt3",
    "lpt4",
    "lpt5",
    "lpt6",
    "lpt7",
    "lpt8",
    "lpt9",
}


@dataclass
class ThreadEntry:
    conversation_id: str
    title: str
    created_at: Optional[dt.datetime]
    updated_at: Optional[dt.datetime]
    message_count: int
    relative_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export ChatGPT conversations.json into year/month Markdown files."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to conversations.json",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output root directory",
    )
    parser.add_argument(
        "--tz",
        default="Asia/Tokyo",
        help="Timezone used for date grouping and fallback titles (default: Asia/Tokyo)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing markdown files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only first N threads (0 means all).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; print summary only.",
    )
    parser.add_argument(
        "--from-month",
        default=None,
        help="Filter start month in YYYY-MM (inclusive).",
    )
    parser.add_argument(
        "--to-month",
        default=None,
        help="Filter end month in YYYY-MM (inclusive through end-of-month).",
    )
    parser.add_argument(
        "--dedupe-by-conversation-id",
        dest="dedupe_by_conversation_id",
        action="store_true",
        default=True,
        help="Skip threads whose conversation_id already exists in output markdown.",
    )
    parser.add_argument(
        "--no-dedupe-by-conversation-id",
        dest="dedupe_by_conversation_id",
        action="store_false",
        help="Disable conversation_id-based dedupe.",
    )
    return parser.parse_args()


def iter_json_array(path: Path, chunk_size: int = 1024 * 1024) -> Iterator[dict]:
    decoder = json.JSONDecoder()
    with path.open("r", encoding="utf-8") as f:
        buffer = ""
        idx = 0
        eof = False

        def ensure_data() -> bool:
            nonlocal buffer, eof
            if eof:
                return False
            chunk = f.read(chunk_size)
            if chunk == "":
                eof = True
                return False
            buffer += chunk
            return True

        while True:
            while idx >= len(buffer) and ensure_data():
                pass
            if idx < len(buffer):
                break
            if eof:
                raise ValueError("Empty input; expected JSON array.")

        while True:
            while True:
                if idx >= len(buffer):
                    if not ensure_data():
                        raise ValueError("Unexpected EOF while searching '['.")
                    continue
                if buffer[idx].isspace():
                    idx += 1
                    continue
                break
            if idx >= len(buffer):
                continue
            if buffer[idx] == "[":
                idx += 1
                break
            raise ValueError("Input is not a JSON array.")

        while True:
            while True:
                if idx >= len(buffer):
                    if not ensure_data():
                        break
                    continue
                ch = buffer[idx]
                if ch.isspace() or ch == ",":
                    idx += 1
                    continue
                break

            if idx >= len(buffer):
                if eof:
                    break
                continue

            if buffer[idx] == "]":
                break

            while True:
                try:
                    obj, end = decoder.raw_decode(buffer, idx)
                    idx = end
                    yield obj
                    if idx > (len(buffer) // 2):
                        buffer = buffer[idx:]
                        idx = 0
                    break
                except json.JSONDecodeError:
                    if not ensure_data():
                        raise


def normalize_timestamp(value: object, tz: ZoneInfo) -> Optional[dt.datetime]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            utc_dt = dt.datetime.fromtimestamp(float(value), tz=dt.timezone.utc)
            return utc_dt.astimezone(tz)
        except (ValueError, OSError):
            return None
    if isinstance(value, str):
        iso = value.strip()
        if not iso:
            return None
        if iso.endswith("Z"):
            iso = iso[:-1] + "+00:00"
        try:
            parsed = dt.datetime.fromisoformat(iso)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=tz)
        return parsed.astimezone(tz)
    return None


def parse_month_arg(value: Optional[str], arg_name: str, tz: ZoneInfo) -> Optional[dt.datetime]:
    if value is None:
        return None
    try:
        parsed = dt.datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise SystemExit(f"{arg_name} must be YYYY-MM, got: {value}") from exc
    return parsed.replace(tzinfo=tz, hour=0, minute=0, second=0, microsecond=0)


def end_of_month(month_start: dt.datetime) -> dt.datetime:
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1, day=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1, day=1)
    return next_month - dt.timedelta(microseconds=1)


def find_earliest_message_time(conversation: dict, tz: ZoneInfo) -> Optional[dt.datetime]:
    best: Optional[dt.datetime] = None
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return None
    for node in mapping.values():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        candidate = normalize_timestamp(message.get("create_time"), tz)
        if candidate is None:
            candidate = normalize_timestamp(node.get("create_time"), tz)
        if candidate is None:
            continue
        if best is None or candidate < best:
            best = candidate
    return best


def extract_part_text(part: object) -> str:
    if part is None:
        return ""
    if isinstance(part, str):
        return part
    if isinstance(part, list):
        return "\n".join(filter(None, (extract_part_text(x) for x in part)))
    if isinstance(part, dict):
        if isinstance(part.get("text"), str):
            return part["text"]
        if isinstance(part.get("content"), str):
            return part["content"]
        if isinstance(part.get("parts"), list):
            return "\n".join(filter(None, (extract_part_text(x) for x in part["parts"])))
        return json.dumps(part, ensure_ascii=False)
    return str(part)


def extract_message_content(content: object) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(filter(None, (extract_message_content(x) for x in content)))
    if isinstance(content, dict):
        ctype = content.get("content_type")
        if ctype in {"text", "multimodal_text"}:
            parts = content.get("parts")
            if isinstance(parts, list):
                text = "\n".join(filter(None, (extract_part_text(p) for p in parts)))
                if text:
                    return text
            if isinstance(content.get("text"), str):
                return content["text"]
            return ""
        if ctype == "code":
            language = content.get("language") or ""
            code_text = content.get("text")
            if not isinstance(code_text, str):
                parts = content.get("parts")
                if isinstance(parts, list):
                    code_text = "\n".join(filter(None, (extract_part_text(p) for p in parts)))
            if not isinstance(code_text, str):
                code_text = json.dumps(content, ensure_ascii=False, indent=2)
            return f"```{language}\n{code_text}\n```"

        for key in ("text", "result", "output_text", "description"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value
        parts = content.get("parts")
        if isinstance(parts, list):
            text = "\n".join(filter(None, (extract_part_text(p) for p in parts)))
            if text:
                return text
        return json.dumps(content, ensure_ascii=False, indent=2)
    return str(content)


def escape_yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def safe_stem(value: str, fallback: str = "thread", max_len: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.strip().lower()
    ascii_only = re.sub(r"[^a-z0-9._-]+", "-", ascii_only)
    ascii_only = ascii_only.strip("._-")
    if not ascii_only:
        ascii_only = fallback
    if ascii_only in WINDOWS_RESERVED_NAMES:
        ascii_only = f"_{ascii_only}"
    return ascii_only[:max_len].rstrip("._-") or fallback


def build_messages(conversation: dict) -> List[dict]:
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return []
    items: List[dict] = []
    seq = 0
    for node in mapping.values():
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        author = message.get("author") if isinstance(message.get("author"), dict) else {}
        role = author.get("role") or "unknown"
        content = extract_message_content(message.get("content"))
        timestamp = message.get("create_time")
        if timestamp is None:
            timestamp = node.get("create_time")
        items.append(
            {
                "role": str(role),
                "text": content.strip(),
                "create_time": timestamp,
                "seq": seq,
            }
        )
        seq += 1
    items.sort(key=lambda x: (x["create_time"] is None, x["create_time"] or 0, x["seq"]))
    return items


def render_markdown(
    *,
    conversation_id: str,
    display_title: str,
    created_at: Optional[dt.datetime],
    updated_at: Optional[dt.datetime],
    source_file: Path,
    messages: List[dict],
) -> str:
    created_iso = created_at.isoformat() if created_at else "null"
    updated_iso = updated_at.isoformat() if updated_at else "null"
    lines: List[str] = []
    lines.append("---")
    lines.append(f'conversation_id: {escape_yaml_string(conversation_id)}')
    lines.append(f'title: {escape_yaml_string(display_title)}')
    lines.append(f'created_at: {escape_yaml_string(created_iso) if created_at else "null"}')
    lines.append(f'updated_at: {escape_yaml_string(updated_iso) if updated_at else "null"}')
    lines.append(f"message_count: {len(messages)}")
    lines.append(f'source_file: {escape_yaml_string(str(source_file))}')
    lines.append("---")
    lines.append("")
    lines.append(f"# {display_title}")
    lines.append("")
    lines.append(f"- Conversation ID: `{conversation_id}`")
    lines.append(f"- Created: `{created_iso}`")
    lines.append(f"- Updated: `{updated_iso}`")
    lines.append(f"- Messages: `{len(messages)}`")
    lines.append("")

    for i, message in enumerate(messages, start=1):
        role = message["role"]
        timestamp = normalize_timestamp(message["create_time"], created_at.tzinfo) if created_at else None
        stamp = timestamp.isoformat() if timestamp else "unknown-time"
        lines.append(f"## {i}. [{role}] {stamp}")
        lines.append("")
        body = message["text"] or "*[empty]*"
        lines.append(body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_month_index(folder: Path, entries: List[ThreadEntry]) -> None:
    sorted_entries = sorted(
        entries,
        key=lambda x: (
            x.created_at is None,
            x.created_at or dt.datetime.max.replace(tzinfo=dt.timezone.utc),
            x.relative_path.name,
        ),
    )
    month_label = folder.name
    lines = [f"# Index {month_label}", ""]
    for entry in sorted_entries:
        created = entry.created_at.isoformat() if entry.created_at else "unknown-time"
        title = entry.title.replace("\n", " ").strip()
        rel = entry.relative_path.name
        lines.append(f"- `{created}` - [{title}]({rel})")
    lines.append("")
    (folder / "index.md").write_text("\n".join(lines), encoding="utf-8")


def load_existing_conversation_ids(output_root: Path) -> Set[str]:
    ids: Set[str] = set()
    if not output_root.exists():
        return ids

    for md_file in output_root.rglob("*.md"):
        if md_file.name == "index.md":
            continue
        try:
            with md_file.open("r", encoding="utf-8") as f:
                if f.readline().strip() != "---":
                    continue
                for line in f:
                    striped = line.strip()
                    if striped == "---":
                        break
                    if striped.startswith("conversation_id:"):
                        raw = striped.split(":", 1)[1].strip()
                        if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
                            raw = raw[1:-1]
                        raw = raw.strip()
                        if raw:
                            ids.add(raw)
                        break
        except OSError:
            continue
    return ids


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_root = Path(args.output).expanduser().resolve()
    tz = ZoneInfo(args.tz)
    from_month = parse_month_arg(args.from_month, "--from-month", tz)
    to_month_start = parse_month_arg(args.to_month, "--to-month", tz)
    to_month = end_of_month(to_month_start) if to_month_start else None

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")
    if not input_path.is_file():
        raise SystemExit(f"Input is not a file: {input_path}")

    if args.limit < 0:
        raise SystemExit("--limit must be >= 0")
    if from_month and to_month and from_month > to_month:
        raise SystemExit("--from-month must be <= --to-month")

    processed = 0
    written = 0
    skipped_existing_file = 0
    skipped_existing_id = 0
    skipped_out_of_range = 0
    skipped_no_created_at_in_range_mode = 0
    month_entries: Dict[Path, List[ThreadEntry]] = {}
    used_names: Dict[Path, set] = {}
    existing_ids = (
        load_existing_conversation_ids(output_root) if args.dedupe_by_conversation_id else set()
    )
    range_filter_enabled = from_month is not None or to_month is not None

    for conversation in iter_json_array(input_path):
        processed += 1
        if args.limit and processed > args.limit:
            break

        conv_id = str(
            conversation.get("conversation_id")
            or conversation.get("id")
            or f"thread-{processed}"
        )

        created_at = normalize_timestamp(conversation.get("create_time"), tz)
        if created_at is None:
            created_at = find_earliest_message_time(conversation, tz)
        updated_at = normalize_timestamp(conversation.get("update_time"), tz)

        if range_filter_enabled:
            if created_at is None:
                skipped_no_created_at_in_range_mode += 1
                continue
            if from_month and created_at < from_month:
                skipped_out_of_range += 1
                continue
            if to_month and created_at > to_month:
                skipped_out_of_range += 1
                continue

        if args.dedupe_by_conversation_id and conv_id in existing_ids:
            skipped_existing_id += 1
            continue

        raw_title = conversation.get("title")
        has_title = isinstance(raw_title, str) and raw_title.strip() != ""
        if has_title:
            display_title = raw_title.strip()
        else:
            if created_at is None:
                display_title = "unknown-time"
            else:
                display_title = created_at.strftime("%Y-%m-%d_%H-%M-%S")

        if created_at is None:
            year = "unknown-year"
            month = "unknown-month"
        else:
            year = created_at.strftime("%Y")
            month = created_at.strftime("%Y-%m")

        folder = output_root / year / month
        rel_folder = Path(year) / month
        date_prefix = created_at.strftime("%Y-%m-%d") if created_at is not None else "unknown-date"
        stem_base = safe_stem(display_title, fallback=f"thread-{conv_id[:8]}")
        candidate_stem = safe_stem(
            f"{date_prefix}_{stem_base}",
            fallback=f"{date_prefix}_thread-{conv_id[:8]}",
        )

        dir_used = used_names.setdefault(folder, set())
        if candidate_stem in dir_used:
            candidate_stem = safe_stem(
                f"{date_prefix}_{stem_base}_{conv_id[:8]}",
                fallback=f"{date_prefix}_thread-{conv_id[:8]}",
            )

        suffix = 2
        final_stem = candidate_stem
        while final_stem in dir_used:
            final_stem = safe_stem(
                f"{candidate_stem}_{suffix}",
                fallback=f"{date_prefix}_thread-{conv_id[:8]}_{suffix}",
            )
            suffix += 1

        filename = f"{final_stem}.md"
        target_path = folder / filename
        relative_path = rel_folder / filename

        messages = build_messages(conversation)
        markdown = render_markdown(
            conversation_id=conv_id,
            display_title=display_title,
            created_at=created_at,
            updated_at=updated_at,
            source_file=input_path,
            messages=messages,
        )

        if not args.dry_run:
            folder.mkdir(parents=True, exist_ok=True)
            if target_path.exists() and not args.overwrite:
                skipped_existing_file += 1
            else:
                target_path.write_text(markdown, encoding="utf-8")
                written += 1
        else:
            written += 1

        if args.dedupe_by_conversation_id:
            existing_ids.add(conv_id)

        dir_used.add(final_stem)
        month_entries.setdefault(folder, []).append(
            ThreadEntry(
                conversation_id=conv_id,
                title=display_title,
                created_at=created_at,
                updated_at=updated_at,
                message_count=len(messages),
                relative_path=relative_path,
            )
        )

        if processed % 200 == 0:
            print(f"Processed {processed} threads...")

    if not args.dry_run:
        for folder, entries in month_entries.items():
            write_month_index(folder, entries)

    print("Done.")
    print(f"Input: {input_path}")
    print(f"Output: {output_root}")
    print(f"Timezone: {args.tz}")
    print(f"From month: {args.from_month or '-'}")
    print(f"To month: {args.to_month or '-'}")
    print(f"Processed: {processed if not args.limit else min(processed, args.limit)}")
    print(f"Written: {written}")
    print(f"Skipped(existing-file): {skipped_existing_file}")
    print(f"Skipped(existing-id): {skipped_existing_id}")
    print(f"Skipped(out-of-range): {skipped_out_of_range}")
    print(f"Skipped(no-created-at-in-range-mode): {skipped_no_created_at_in_range_mode}")
    print(f"Months indexed: {len(month_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
