---
name: iching-div-takashima
description: "iching-div の takashima profile 固定入口。"
---

# iching-div-takashima

## Purpose
Use `/home/ys/projects/iching-div` as a split-source EXTRACT prompt builder with the fixed `takashima` profile.

## Fixed Contract
- Profile is always `takashima`.
- Do not ask the user to choose a profile.
- Build prompt text via:
  - `python3 scripts/build_extract_prompt.py --input <path|-> --profile takashima`
- Return the final answer in chat after using the built prompt text as the execution basis.

## Scope
- `EXTRACT` only
- `[MODE:GENERAL]` must be treated as an explicit unimplemented error
- Missing `MODE` is an error
- Missing `TEMPLATE` in `EXTRACT` is an error

## Source Policy
- Use Takashima split assets only.
- Final-answer reference lines must use citation paths only.
- Never expose section paths in the final answer.

## Profile Rules
- Use Takashima split source only.
- Final interpretation section is `高島解釈` only.
- Do not rely on Honda material for final structure or interpretation.

## Output Rules
- Canonical answers are structural references, not text to copy.
