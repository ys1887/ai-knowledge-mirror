# EXTRACT mode instructions (Takashima contract)

## 1. Source Contract
- Use only the Takashima source family for EXTRACT answers.
- Shared quote sources:
  - `assets/quotes/quotes_honka.md`
  - `assets/quotes/quotes_koji.md`
- Takashima interpretation sources:
  - `assets/extract_takashima_split`
- Do not mix Honda or legacy interpretation into this contract.
- Do not write handwritten citation lines in the answer.
- `## 高島解釈原文` is appended by the SDK script and must not be written by the LLM.

## 2. Output Contract
- Keep the answer in the Takashima shape used by `ekikyo`.
- `EX_SIMPLE` and `EX_5` both start with `## 核心・結論`.
- The main answer body uses `## 本卦`, `## 変爻`, `## 総合解釈`.
- Inside each hexagram section, write quote-only subsections first and prose-only `### 解釈` last.
- For `EX_5`, include auxiliary hexagram sections only when the input provides them.
- When `変爻：なし`, still keep a `## 変爻` section and explain that there is no changing line.
- Keep the prose focused on Takashima only; do not reintroduce Honda comparisons.

## 3. Writing Rules
- Quote sections are quote-only.
- `### 解釈` and `## 総合解釈` are prose-only.
- Short embedded Takashima phrasing is encouraged, but do not inflate with long quote blocks.
- The final `## 総合解釈` is the main judgment section, not a brief tail note.
- `EX_COMPARE` remains out of scope for this Takashima contract.
