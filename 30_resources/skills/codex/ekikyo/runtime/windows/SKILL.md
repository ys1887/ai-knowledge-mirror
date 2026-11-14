---
name: ekikyo
description: "ekikyo の EXTRACT回答生成 skill。embedded evidence を使って E:\\Documents\\Playground\\ekikyo\\work\\ に回答 md を組み立てる Windows-native skill。"
---

# ekikyo

## Purpose
Use `E:\Documents\Playground\ekikyo` as the Takashima-source EXTRACT workspace in Windows-native Codex sessions.
This skill is the main operational entrypoint. It orchestrates prompt build, LLM prose drafting, answer assembly, raw appendix insertion, and final save to `E:\Documents\Playground\ekikyo\work\YYYY-MM-DD_NN.md`.

## Maintenance Note
- This Windows runtime uses `E:\Documents\Playground\ekikyo`.
- Do not call WSL or assume a WSL execution repo exists for this workflow.
- Keep repository scripts, formats, assets, and runtime assumptions in sync through Git.
- The legacy WSL skill variant, if ever needed again, lives in `E:\Documents\Playground\lib-skills\codex\ekikyo\SKILL.md`.

## Source Of Truth
- Canonical quotes:
  - `E:\Documents\Playground\ekikyo\assets\honka.md`
  - `E:\Documents\Playground\ekikyo\assets\koji.md`
- Canonical Takashima interpretation: `E:\Documents\Playground\ekikyo\assets\takashima\`
- EXTRACT contract authority:
  - `E:\Documents\Playground\ekikyo\spec\extract_contract.md`
- EXTRACT runtime format authority:
  - `E:\Documents\Playground\ekikyo\formats\shared.md`
  - `E:\Documents\Playground\ekikyo\formats\ex_simple_single.md`
  - `E:\Documents\Playground\ekikyo\formats\ex_simple2_single.md`
  - `E:\Documents\Playground\ekikyo\formats\ex_5_single.md`
  - `E:\Documents\Playground\ekikyo\formats\ex_compare_single.md`
- Human-facing structure references:
  - `E:\Documents\Playground\ekikyo\examples\`
  - `E:\Documents\Playground\ekikyo\fixtures\`
  - They are for structure verification only, not the runtime source of truth.
- Workspace instructions:
  - `E:\Documents\Playground\ekikyo\AGENTS.md`

## Contract
- Only `EXTRACT` is supported.
- Ignore any `GENERAL` guidance that remains in mirrored prompt sources.
- The deliverable is the final answer md file in `E:\Documents\Playground\ekikyo\work\YYYY-MM-DD_NN.md`.
- The final md must contain answer content only.
- The repository provides source, prompt-build, and postprocess scripts. This skill is responsible for orchestration across those steps.
- In `EX_SIMPLE`, `EX_SIMPLE2`, and `EX_5`, the classical quote blocks are not LLM output. The script inserts the canonical source block under each relevant heading.
- The LLM writes prose only in `**核心・結論**`, each `### 解釈`, and `## 総合解釈`.
- Do not add artificial subsection headings such as `卦辞`, `彖伝`, `大象伝`, `爻辞`, or `小象伝` inside the final answer.
- Treat `## 総合解釈` as the thickest judgment section and follow the active runtime formats as the source of truth for its structure.
- In `EX_SIMPLE`, `EX_SIMPLE2`, and `EX_5`, `## 総合解釈` should actively reuse and re-integrate Takashima source logic from the relevant hexagram sections instead of collapsing into a short summary.
- In `## 総合解釈`, do not reopen with a repeated one-line conclusion; start by re-integrating the relevant hexagram meaning per the active templates.
- In `EX_SIMPLE`, `EX_SIMPLE2`, and `EX_5`, when using Takashima source wording, weave short quotes or close paraphrases into prose instead of adding separate blockquotes.
- Keep Takashima-source references separate from the script-fixed classical quote blocks.
- Canonical answers in `E:\Documents\Playground\ekikyo\examples\` are structure references only.
- `examples\` and `fixtures\` may be read only for structure or format verification.
- Do not use `examples\` or `fixtures\` as the content basis of the prose draft, as a rewrite source, or as a wording/style donor for the final answer body.
- The `work\` output directory is not part of the evidence set. Use `python scripts\next_work_filename.py --work-dir "E:\Documents\Playground\ekikyo\work"` to determine the next output path instead of reading prior answer bodies.
- Do not run `dir`, `ls`, `sort`, or similar directory-listing logic to infer the next `work\YYYY-MM-DD_NN.md`; the helper script is the required path-resolution step.
- Do not open or read previous generated answer bodies unless the user explicitly asks.
- Answer prose must be derived from the built prompt evidence and canonical repository sources, not from prior generated answers.
- Add concrete timing or start-condition guidance only when the question needs it.
- Do not reprint the final answer body in chat; return only a short completion note or the output path.

## Input Preservation
- Preserve the pasted EXTRACT input markers exactly.
- `[MODE:EXTRACT]` must remain the first non-empty line.
- `[TEMPLATE:EX_SIMPLE]`, `[TEMPLATE:EX_SIMPLE2]`, `[TEMPLATE:EX_5]`, or `[TEMPLATE:EX_COMPARE]` must remain the second line immediately after `MODE`.
- Never combine `MODE` and `TEMPLATE` onto one line.
- Do not rewrite, normalize, or reformat the marker lines before passing the input into the repository scripts.
- If the user already pasted valid EXTRACT input, save and use that text as-is.
- In `EX_COMPARE`, repository parsing accepts candidate headings such as `### 候補名`, `#### 候補A：候補名`, `候補A：候補名`, and `候補名：`; preserve the original question block in the final answer.

## Prompt Builder
- Run from `E:\Documents\Playground\ekikyo`.
- This Windows runtime copy must not call WSL or the Ubuntu repo path.
- `python scripts\build_extract_prompt.py --input <path|->` builds the execution prompt text.
- `python scripts\build_answer_skeleton.py --input <input md>` builds the template-specific draft skeleton.
- `python scripts\next_work_filename.py --work-dir "E:\Documents\Playground\ekikyo\work"` resolves the next `E:\Documents\Playground\ekikyo\work\YYYY-MM-DD_NN.md` path.
- In `EX_SIMPLE`, `EX_SIMPLE2`, and `EX_5`, the prompt text includes embedded source evidence from the relevant quotes blocks and Takashima interpretation sections.
- In `EX_COMPARE`, the prompt remains lightweight and does not inline the same evidence blocks.
- If `--output-dir` is used, the generated `*.evidence.md` file is a helper artifact for inspection only, not the deliverable.

## Windows Encoding Notes
- Japanese Markdown files in this workflow are UTF-8.
- When reading generated Japanese files in PowerShell, use `Get-Content -Encoding UTF8`.
- Do not treat mojibake in raw PowerShell stdout as file corruption; reread the file with explicit UTF-8 before judging the content.
- Prefer writing long Japanese script output to a UTF-8 file, then inspect that file with `Get-Content -Encoding UTF8`.
- If Python stdout must be inspected directly, set this PowerShell UTF-8 prelude first in the same session:
  - `$env:PYTHONUTF8 = "1"`
  - `$env:PYTHONIOENCODING = "utf-8"`
  - `[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()`
  - `$OutputEncoding = [System.Text.UTF8Encoding]::new()`

## Orchestration Flow
1. Accept the pasted EXTRACT input after `/ekikyo`.
2. Preserve the pasted marker lines exactly and write the input text without reformatting `MODE` or `TEMPLATE`.
3. Resolve the next output path with `python scripts\next_work_filename.py --work-dir "E:\Documents\Playground\ekikyo\work"`. Do not infer the number by listing the output directory manually.
4. Build the execution prompt text from the repository scripts.
5. Build the answer skeleton with `python scripts\build_answer_skeleton.py --input <input md>`.
6. Write only the prose draft with the LLM, filling the required prose sections in that skeleton.
7. Run answer assembly so canonical quote blocks are inserted mechanically.
8. Run raw append when the template requires `## 高島解釈原文`.
9. Save the final md file to the resolved `E:\Documents\Playground\ekikyo\work\YYYY-MM-DD_NN.md`.

## Assembly Flow
- After the LLM writes the prose draft, run `python scripts\assemble_extract_answer.py --input <input md> --output <answer md>`.
- This step rewrites the relevant `本卦` / `変爻` / 補助卦 sections so the classical block matches the canonical source exactly, including `> `, blank lines, prose, and `（占）`.
- In `EX_COMPARE`, skip the assembly step.

## Postprocess
- For `EX_SIMPLE`, `EX_SIMPLE2`, and `EX_5`, after the answer body is assembled, run `python scripts\append_takashima_raw.py --input <input md> --output <answer md>` so the final file ends with mechanically copied Takashima source text under `## 高島解釈原文`.
- Do not run the raw-text append step for `EX_COMPARE`.
- Do not introduce always-on artifact saving. Keep temporary evidence output optional and inspection-only.
