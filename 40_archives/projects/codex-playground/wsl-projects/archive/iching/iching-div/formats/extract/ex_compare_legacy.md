# EX_COMPARE output skeleton (legacy)

- Order: `**核心・結論**` -> `**吉凶順位（1位 = 最吉）**` -> candidate detail sections -> `**まとめ**`.
- Each candidate detail must be Honda-led.
- For compare mode, use `kaji`, `taisho`, and required `yao_n`.
- Takashima sections are comparison support only and must not become independent final-answer sections.
- Candidate detail sections must preserve the user-provided candidate labels.
- The ranking section must be a numbered list only; do not mix commentary into that list.
- Candidate detail headings must use `### <順位>位 <候補名>（<卦名>・<変爻>）`.
- Each candidate detail section must contain one quote block, one short interpretation paragraph, and one citation line.
- In candidate detail quote blocks, keep original text and readings together; if the selected changing-line source includes `小象伝`, include it in the same unified quote block rather than splitting it into another item.
- In candidate detail prose, keep the explanation focused on the judgment logic itself; do not expand into extra practical advice beyond what is needed for ranking.
- In each candidate detail, treat `爻辞` or `卦辞` as the primary evidence for ranking, and use `彖伝` or `大象伝` only as supporting reinforcement when needed.
- Do not create `**高島解釈**` or any Takashima-labeled standalone section in compare mode.
- Use Takashima only to sharpen comparison judgments behind the scenes, not as a separately narrated answer block.
- Finish with a Markdown table under `**まとめ**`, then one sentence that explicitly names the recommended first-place candidate.
- The final recommendation sentence must be exactly `今回のおすすめは、<候補名>です。`.
