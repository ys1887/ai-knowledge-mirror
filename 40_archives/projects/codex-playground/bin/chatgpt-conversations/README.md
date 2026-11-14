# conversations.json Export to Markdown

## Purpose
Convert ChatGPT export `conversations.json` into:

- one thread per Markdown file
- grouped by year and month: `YYYY/YYYY-MM`

## Command

```bash
python3 /home/ys/bin/chatgpt-conversations/export_conversations_to_md.py \
  --input /mnt/e/Documents/Workspace/conversations/conversations.json \
  --output /mnt/e/Documents/Workspace/conversations/by-year-month-md \
  --tz Asia/Tokyo
```

## Behavior Summary

- Output layout: `<output>/<YYYY>/<YYYY-MM>/<thread>.md`
- Thread filename prefix: `YYYY-MM-DD_` (based on `create_time` in `--tz`)
- One `index.md` is generated per `<YYYY-MM>` folder.
- Optional month range filters:
  - `--from-month YYYY-MM` (inclusive)
  - `--to-month YYYY-MM` (inclusive through month-end)
- Optional dedupe by existing `conversation_id` in output markdown:
  - default: enabled
  - disable via `--no-dedupe-by-conversation-id`
- Thread title fallback (only when title is missing):
  - `YYYY-MM-DD_HH-mm-ss`
  - if collision in the same second, append `_id8`

## Useful Options

- `--dry-run`: parse and count only, no writes
- `--limit N`: process first N threads only
- `--overwrite`: overwrite existing thread markdown files
- `--from-month YYYY-MM --to-month YYYY-MM`: incremental range export
- `--no-dedupe-by-conversation-id`: allow re-export even if same conversation already exists

## Incremental Example

```bash
python3 /home/ys/bin/chatgpt-conversations/export_conversations_to_md.py \
  --input /mnt/e/Documents/Workspace/conversations/conversations.json \
  --output /mnt/e/Documents/Workspace/conversations/by-year-month-md \
  --tz Asia/Tokyo \
  --from-month 2026-02 \
  --to-month 2026-06
```
