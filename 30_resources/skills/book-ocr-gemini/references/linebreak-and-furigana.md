# Linebreak + Furigana Heuristics

## Goal
- Keep author-intended line breaks (headings, paragraph breaks, annotation starts)
- Join OCR wrap-only line breaks
- Normalize inline furigana from `漢字かな` into `漢字（かな）` when confidence is high

## Linebreak (heuristic mode)
- Preserve:
  - blank lines
  - short standalone heading-like lines
  - lines ending with `。！？`
  - lines followed by annotation markers such as `〇`
- Join:
  - long non-final lines followed by text that naturally continues the sentence

## Furigana (paren mode)
- Convert conservative matches like:
  - `孔穎達くようたつ` -> `孔穎達（くようたつ）`
- Avoid converting common okurigana cases:
  - `助ける`, `産み出す`
- Existing `（...）` text is left as-is.

## Known Limits
- OCR output itself may fluctuate between runs (`flash` vs `pro`)
- Ruby/reading placement inside dense classical commentary is not always recoverable perfectly
