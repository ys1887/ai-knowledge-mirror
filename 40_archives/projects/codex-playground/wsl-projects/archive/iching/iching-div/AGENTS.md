# `iching-div` operational entry (split-source v1)

## Purpose
- This repository is a prompt-building base for split-source EXTRACT work.
- The preprocessing script resolves input structure, fixed profile, split sources, and execution text.
- It does not run providers, validators, artifacts, or external runtimes.

## Source Of Truth
- Operational entry: `/home/ys/projects/iching-div/AGENTS.md`
- Local rule source: `/home/ys/projects/iching-div/sources/ekikyo_custom_prompt.md`
- Split assets:
  - Honda: `/home/ys/projects/iching-div/assets/split/honda/`
  - Takashima: `/home/ys/projects/iching-div/assets/split/takashima/`
- Format fragments: `/home/ys/projects/iching-div/formats/extract/`
- Example fixtures: `/home/ys/projects/iching-div/examples/extract/`

## Runtime Contract
1. Read the input.
2. Parse `MODE`, `TEMPLATE`, hexagram numbers, changing lines, and compare candidates.
3. Resolve one fixed profile:
   - `legacy`
   - `honda`
   - `takashima`
4. Select split citation files and internal section files.
5. Build execution prompt text and write it to `stdout`.

## Fixed v1 Boundaries
- Only `EXTRACT` is implemented.
- `[MODE:GENERAL]` is recognized but must fail with an explicit unimplemented error.
- Missing `MODE` is an error.
- `EXTRACT` without `TEMPLATE` is an error.
- Error policy is fail-fast.
- Do not use:
  - `codex exec`
  - provider abstraction
  - `run`
  - `validate`
  - artifact saving
  - `run.json`
  - external dependency runtime layers

## CLI
- Command:
  - `python3 scripts/build_extract_prompt.py --input <path|-> --profile <legacy|honda|takashima>`
- Input mode overrides are not supported in v1.
- Output is prompt text only, never JSON.

## Selection Policy
- `legacy`
  - `EX_SIMPLE`: Honda and Takashima both use `kaji`, `tanden`, `taisho`, required `yao_n`
  - `EX_5`: main hexagram uses both sources with `kaji`, `tanden`, `taisho`, required `yao_n`
  - `EX_5`: auxiliary hexagrams use both sources with `kaji`, `tanden`, `taisho` only
  - `EX_COMPARE`: Honda leads candidate detail; Takashima is support-only with `kaji`, `taisho`, required `yao_n`
- `honda`
  - Honda split source only
  - Final interpretation section is `本田解釈` only
- `takashima`
  - Takashima split source only
  - Final interpretation section is `高島解釈` only

## Prompt Assembly Rules
- Include both citation paths and internal section paths in execution text.
- Use citation paths only for final-answer reference instructions.
- Never expose section paths in final-answer instructions.
- Treat canonical answers as structural references, not literal target text.

## Archive Policy
- Replaced prompt-era files are preserved under `/home/ys/projects/iching-div/archive/pre-split-migration/`.
- Do not delete archived copies during this migration.
