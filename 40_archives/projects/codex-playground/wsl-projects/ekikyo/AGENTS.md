# `ekikyo` operational entry (takashima-source transition)

## Purpose
- This repository is a prompt-building base for EXTRACT prompt assembly.
- The repository scripts resolve input structure, the active Takashima-oriented source layout, execution prompt text, answer assembly, and raw appendix insertion.
- This repository does not embed an LLM execution runtime or app-style orchestration layer. Skill-level orchestration may call these scripts from outside the repository boundary.

## Source Of Truth
- Operational entry: `/home/ys/projects/ekikyo/AGENTS.md`
- Local rule source: `/home/ys/projects/ekikyo/spec/extract_contract.md`
- Canonical quote source:
  - `/home/ys/projects/ekikyo/assets/honka.md`
  - `/home/ys/projects/ekikyo/assets/koji.md`
- Canonical interpretation source:
  - `/home/ys/projects/ekikyo/assets/takashima/`
- Format fragments: `/home/ys/projects/ekikyo/formats/`
- Example fixtures: `/home/ys/projects/ekikyo/fixtures/`

## Runtime Contract
1. Read the input.
2. Parse `MODE`, `TEMPLATE`, hexagram numbers, changing lines, and compare candidates.
3. Use canonical Takashima-oriented sources as the source-of-truth for quotes and interpretation.
4. Build execution prompt text and write it to `stdout`.
5. Assemble canonical quote blocks into the drafted answer when applicable.
6. Append the Takashima raw appendix when applicable.

## Fixed v1 Boundaries
- Only `EXTRACT` is implemented.
- Missing `MODE` is an error.
- `EXTRACT` without `TEMPLATE` is an error.
- Error policy is fail-fast.
- Do not use:
  - `codex exec`
  - provider abstraction
  - `run`
  - `validate`
  - heavy artifact saving as a default repository feature
  - `run.json`
  - app-style external dependency runtime layers inside this repository

## CLI
- Command:
  - `python3 scripts/build_extract_prompt.py --input <path|->`
- Additional repository scripts:
  - `python3 scripts/next_work_filename.py [--work-dir <path>] [--date YYYY-MM-DD]`
  - `python3 scripts/build_answer_skeleton.py --input <input md>`
  - `python3 scripts/assemble_extract_answer.py --input <input md> --output <answer md>`
  - `python3 scripts/append_takashima_raw.py --input <input md> --output <answer md>`
- The repository is being organized around the fixed `takashima` path layout.
- Output is prompt text only, never JSON.
- Final answer writing and save-path orchestration belong to the calling skill or other external operator, not to the repository itself.

## Work Output Naming
- `work/` 配下の通常の占い結果は、既存どおり `YYYY-MM-DD_NN.md` の通し番号運用を使ってよい。
- `python3 scripts/next_work_filename.py` は通常の占い結果ファイル名を決めるための補助 script として扱う。
- `work/` 配下へ提出するレポートは、通し番号を使わず `report_<レポート名>.md` を使う。
- `<レポート名>` には提出時に識別可能な題名をそのまま使い、占い結果ファイルと混同しないことを優先する。
- レポート提出物の保存時は、`next_work_filename.py` を使わず、レポート名ベースで保存先を決める。

## Source Layout Policy
- Canonical quotes are the source-of-truth for original text, readings, and hiragana lines.
- Canonical Takashima interpretation files are the source-of-truth for interpretation.

## Prompt Assembly Rules
- Include both citation paths and internal file paths in execution text.
- Use citation paths only for final-answer reference instructions.
- Never expose internal file paths in final-answer instructions.
- Treat canonical answers as structural references, not literal target text.
- Do not use canonical answers as a prose source, rewrite base, or wording donor for the final answer body.
