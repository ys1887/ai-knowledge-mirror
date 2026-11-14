# EX_SIMPLE2 output skeleton (single-source)

- Order: `## 質問文` -> `## 本卦` -> `## 変爻` -> `## 之卦` -> one references section.
- `## 質問文` is a script-filled code block section. Emit the heading only; the script inserts the full user input under it.
- `## 本卦` is a script-filled quote section. Emit the heading only; the script inserts the honka source block under it.
- `## 変爻` is a script-filled quote section. Emit the heading only; the script inserts the selected changing-line source block under it.
- `## 之卦` is a script-filled quote section for the landing direction of the change. Emit the heading only; the script inserts the zhigua honka source block under it.
- Treat `之卦` as the landing direction of the change, not as a second main hexagram with equal weight.
- Do not emit any changing-line section for `之卦`.
- `EX_SIMPLE2` requires `之卦`; reject `変爻：なし` or missing `之卦`.
- Do not emit `（参照：...）` at the end of any section.
- After the fixed quote sections, emit exactly one `## 参照` section before `## 高島易断`.
- The references section must use bullet lines in the form `- <citation path> | <卦名>`.
