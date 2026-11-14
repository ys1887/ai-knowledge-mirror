---
name: chatgpt-conversations-md-export
description: ChatGPTの会話データを月別Markdownに書き出すskill。
---

# ChatGPT Conversations MD Export

## Purpose
Use this skill to convert ChatGPT `conversations.json` into Markdown files with stable folder layout and safe incremental updates.

## Use This Skill When
- You received a new ChatGPT export JSON that includes old + new threads.
- You want monthly incremental output (for example `2026-02` to `2026-06`).
- You want to avoid duplicate threads across repeated runs.

## Script
- `py E:\Documents\Playground\bin\chatgpt-conversations\export_conversations_to_md.py`

## Output Rules
- One thread per file.
- Folder layout: `YYYY/YYYY-MM/`.
- Filename prefix: `YYYY-MM-DD_`.
- Monthly `index.md` is generated in each `YYYY-MM` folder.
- Dedupe key: `conversation_id` from markdown frontmatter.

## Required Workflow
1. Run `--dry-run` first.
2. Run the real export.
3. Re-run the same command once and confirm dedupe skips duplicates.

## Recommended Commands

Dry-run:
```powershell
py E:\Documents\Playground\bin\chatgpt-conversations\export_conversations_to_md.py `
  --input E:\Documents\Workspace\conversations\conversations.json `
  --output E:\Documents\Workspace\conversations\by-year-month-md `
  --tz Asia/Tokyo `
  --from-month 2026-02 `
  --to-month 2026-06 `
  --dry-run
```

Real run:
```powershell
py E:\Documents\Playground\bin\chatgpt-conversations\export_conversations_to_md.py `
  --input E:\Documents\Workspace\conversations\conversations.json `
  --output E:\Documents\Workspace\conversations\by-year-month-md `
  --tz Asia/Tokyo `
  --from-month 2026-02 `
  --to-month 2026-06
```

Re-run dedupe check:
```powershell
py E:\Documents\Playground\bin\chatgpt-conversations\export_conversations_to_md.py `
  --input E:\Documents\Workspace\conversations\conversations.json `
  --output E:\Documents\Workspace\conversations\by-year-month-md `
  --tz Asia/Tokyo `
  --from-month 2026-02 `
  --to-month 2026-06
```

## Notes
- `--from-month` / `--to-month` use `YYYY-MM`.
- `--to-month` is inclusive through end-of-month.
- Disable dedupe only when explicitly needed:
  - `--no-dedupe-by-conversation-id`
