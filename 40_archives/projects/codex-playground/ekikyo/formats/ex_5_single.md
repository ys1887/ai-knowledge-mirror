# EX_5 output skeleton (single-source)

- Order: `## 質問文` -> `## 本卦` -> `## 変爻` -> `## 之卦` -> supporting auxiliary hexagrams in input order -> one references section.
- `## 質問文` is a script-filled code block section. Emit the heading only; the script inserts the full user input under it.
- `## 本卦` is a script-filled quote section. Emit the heading only; the script inserts the honka source block under it.
- `## 変爻` is a script-filled quote section. If a changing line exists, emit the heading only; the script inserts the changing-line source block under it.
- If multiple changing lines exist, emit one `## 変爻` section per line in input order.
- If `変爻：なし`, omit both `## 変爻` and `## 之卦`.
- If `之卦` is present, treat it as the landing direction of the change, not as a second main hexagram with equal weight. Emit the `## 之卦` heading only; the script inserts the zhigua source block under it.
- For each supporting auxiliary hexagram such as `互卦`, `錯卦`, and `綜卦`, emit the section heading only; the script inserts the source block under it.
- Do not read or cite auxiliary changing lines.
- The main hexagram and changing line are the primary evidence for the reading.
- If there is exactly one changing line, treat that changing line as the main message for this reading.
- If there are two or more changing lines, treat the main hexagram's `卦辞` as the main message and use the changing lines as supporting evidence.
- `之卦` is supporting evidence for landing direction or after-state; do not let it overtake the main hexagram or changing line.
- Supporting auxiliary hexagrams such as `互卦`, `錯卦`, and `綜卦` are supporting structure only.
- Do not emit `（参照：...）` at the end of any section.
- After the fixed quote sections, emit exactly one `## 参照` section before `## 高島易断`.
- The references section must list only actually used hexagram citations in input order, deduplicated, with bullet lines in the form `- <citation path> | <卦名>`.
