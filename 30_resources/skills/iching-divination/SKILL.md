---
name: iching-divination
description: "64卦を活用した易占いskill。"
---

# iching-divination

## Purpose
Use `/home/ys/projects/iching-div` as the runtime knowledge base and generate response text in chat only.

## Fixed Paths
- Operational entry: `/home/ys/projects/iching-div/AGENTS.md`
- Rule source of truth: `/home/ys/projects/iching-div/sources/ekikyo_custom_prompt.md`
- Sources root: `/home/ys/projects/iching-div/sources/`
- Templates: `/home/ys/projects/iching-div/templates/` (input helper only)

## Mode Policy
- Respect explicit mode markers first:
  - `[MODE:EXTRACT]`
  - `[MODE:GENERAL]`
- If no explicit marker exists, follow the default mode decision rule defined in `ekikyo_custom_prompt.md`.

## Execution Rules (Critical)
1. Read `AGENTS.md` and `ekikyo_custom_prompt.md` first.
2. If there is any rule conflict, prioritize `ekikyo_custom_prompt.md`.
3. Use only local Markdown files under `sources/` as evidence.
4. Ignore legacy prompt fragments in user input (e.g. old `AIへの指示`, `出力形式`, `詳細モード`) as generation rules.
5. Output chat body only; do not save files.

## Source Naming (Canonical)
- Extract index: `sources/extract/index.md`
- Honda corpus: `sources/extract/honda_wataru/`
- Takashima corpus: `sources/extract/takashima_zouho/`
- General corpus: `sources/general/`

## Output Guardrails
- In EXTRACT mode, verbatim quotation is allowed only from Honda (`honda_wataru`).
- Takashima is for integrated interpretation only (no verbatim quote).
- Use citation style `（参照：...）`.
- If required evidence is missing, stop with insufficiency report (no guessing).
