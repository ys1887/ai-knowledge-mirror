# EX_SIMPLE output skeleton (single-source)

- Order: `## 質問文` -> `## 本卦` -> `## 変爻` -> one references section.
- `## 質問文` is a script-filled code block section. Emit the heading only; the script inserts the full user input under it.
- `## 本卦` is a script-filled quote section. Emit the heading only; the script inserts the honka source block under it.
- `## 変爻` is a script-filled quote section. Emit the heading only; the script inserts the selected changing-line source block under it.
- `EX_SIMPLE` requires one changing line. Reject `変爻：なし` or missing `変爻`.
- Do not reformat or reproduce the fixed quote blocks yourself.
- Do not emit `（参照：...）` at the end of any section.
- After the fixed quote sections, emit exactly one `## 参照` section before `## 高島易断`.
- The references section must use bullet lines in the form `- <citation path> | <卦名>`.
