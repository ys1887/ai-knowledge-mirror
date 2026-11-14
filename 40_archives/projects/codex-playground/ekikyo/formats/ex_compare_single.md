# EX_COMPARE output skeleton (single-source)

- Order: `## 質問文` -> `**核心・結論**` -> `**吉凶順位（1位 = 最吉）**` -> candidate detail sections -> `**まとめ**`.
- `## 質問文` is a script-filled code block section. Emit the heading only; the script inserts the full user input under it.
- Each candidate detail must be led by the active profile only.
- For compare mode, candidate detail evidence is the changing line only: `爻辞`, optional `小象伝`, and the line reading.
- Candidate detail sections must preserve the user-provided candidate labels.
- The ranking section must be a numbered list only; do not mix commentary into that list.
- Candidate detail headings must use `### <順位>位 <候補名>（<卦名>・<変爻>）`.
- Each candidate detail section must contain one quote block, one short interpretation paragraph, and one citation line.
- In candidate detail quote blocks, keep original text and readings together; do not expand into full main-hexagram quotation for compare mode.
- In candidate detail prose, keep the explanation focused on the judgment logic itself; do not expand into extra practical advice beyond what is needed for ranking.
- In each candidate detail, treat the changing line as the primary evidence for ranking.
- Finish with a Markdown table under `**まとめ**`, then one sentence that explicitly names the recommended first-place candidate.
- The final recommendation sentence must be exactly `今回のおすすめは、<候補名>です。`.
