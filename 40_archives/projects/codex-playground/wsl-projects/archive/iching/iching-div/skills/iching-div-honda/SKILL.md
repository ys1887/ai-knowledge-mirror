---
name: iching-div-honda
description: "iching-div の honda profile 固定入口。"
---

# iching-div-honda

## Purpose
Use `/home/ys/projects/iching-div` as a split-source EXTRACT prompt builder with the fixed `honda` profile.

## Fixed Contract
- Profile is always `honda`.
- Do not ask the user to choose a profile.
- Build prompt text via:
  - `python3 scripts/build_extract_prompt.py --input <path|-> --profile honda`
- Return the final answer in chat after using the built prompt text as the execution basis.

## Scope
- `EXTRACT` only
- `[MODE:GENERAL]` must be treated as an explicit unimplemented error
- Missing `MODE` is an error
- Missing `TEMPLATE` in `EXTRACT` is an error

## Source Policy
- Use Honda split assets only.
- Final-answer reference lines must use citation paths only.
- Never expose section paths in the final answer.

## Profile Rules
- Use Honda split source only.
- Final interpretation section is `本田解釈` only.
- Do not rely on Takashima material for final structure or interpretation.

## Output Rules
- Canonical answers are structural references, not text to copy.
