---
name: iching-div-legacy
description: "iching-div の legacy profile 固定入口。"
---

# iching-div-legacy

## Purpose
Use `/home/ys/projects/iching-div` as a split-source EXTRACT prompt builder with the fixed `legacy` profile.

## Fixed Contract
- Profile is always `legacy`.
- Do not ask the user to choose a profile.
- Build prompt text via:
  - `python3 scripts/build_extract_prompt.py --input <path|-> --profile legacy`
- Return the final answer in chat after using the built prompt text as the execution basis.

## Scope
- `EXTRACT` only
- `[MODE:GENERAL]` must be treated as an explicit unimplemented error
- Missing `MODE` is an error
- Missing `TEMPLATE` in `EXTRACT` is an error

## Source Policy
- Use local split assets and local `sources/` only.
- Final-answer reference lines must use citation paths only.
- Never expose section paths in the final answer.

## Profile Rules
- Use both Honda and Takashima split sources.
- `EX_SIMPLE`: both use `kaji`, `tanden`, `taisho`, required `yao_n`
- `EX_5`: main hexagram uses both sources with `kaji`, `tanden`, `taisho`, required `yao_n`
- `EX_5`: auxiliary hexagrams use both sources with `kaji`, `tanden`, `taisho` only
- `EX_COMPARE`: Honda leads candidate detail; Takashima is support-only for comparison

## Output Rules
- `legacy` can end with both `本田解釈` and `高島解釈`.
- Canonical answers are structural references, not text to copy.
