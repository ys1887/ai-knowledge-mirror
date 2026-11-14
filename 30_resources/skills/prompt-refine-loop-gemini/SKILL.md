---
name: prompt-refine-loop-gemini
description: プロンプトを自動で改善して完成度を高めるskill。
---

# Prompt Refine Loop Gemini

## Purpose
Use this skill when you want to refine a draft prompt with a mostly hands-off loop after the first input. It runs a repeatable revise/review cycle with Gemini Developer API and saves full iteration logs.

## Use Cases
- Improve ChatGPT custom instructions or system prompts over multiple rounds.
- Run "max N rounds with early stop" prompt polishing in one command.
- Keep audit-ready logs of each iteration and convergence scoring.

## Preconditions
- `GEMINI_API_KEY` is set in the current shell.
- Python 3 is available.
- You can provide input as pasted text or a `.md`/`.txt` file.

## Workflow
1. Accept initial prompt input.
- Short text: pass with `--input-text`.
- Long text: put in a file and pass with `--input`.

2. Run automated loop via script.
- `python3 scripts/refine_loop.py --input <path> --max-iter 5`
- Optional model override: `--model <model-id>`

3. Review outputs.
- `final_prompt.md`: final refined prompt
- `iterations.jsonl`: full per-iteration logs
- `summary.md`: stop reason and score trajectory

## Recommended Commands
- File input (recommended):
`python3 scripts/refine_loop.py --input /path/to/prompt.md --max-iter 5`

- Direct text input:
`python3 scripts/refine_loop.py --input-text "<your prompt text>" --max-iter 5`

- Custom threshold/model/output:
`python3 scripts/refine_loop.py --input /path/to/prompt.md --max-iter 7 --threshold 0.12 --model gemini-2.5-pro --out-dir /mnt/e/Documents/Workspace/prompt-loop`

## Defaults
- Provider: Gemini Developer API (`generativelanguage.googleapis.com`)
- Default model: `gemini-2.5-pro` (high quality)
- `max-iter`: 5
- `threshold`: 0.15
- Output root: `/mnt/e/Documents/Workspace/prompt-loop`

## Output Structure
A run directory is created as:
- `run-YYYYMMDD_HHMMSS/`

Inside each run:
- `final_prompt.md`
- `iterations.jsonl`
- `summary.md`

## Safety and Failure Handling
- Fails fast when `GEMINI_API_KEY` is missing.
- Retries transient API/network errors with capped exponential backoff.
- Never prints API key values.
- Preserves completed outputs for completed iterations.

## Resources
- `scripts/refine_loop.py`: deterministic loop runner.
- `references/prompt-roles.md`: prompt-role templates and tuning notes.
- `assets/templates/initial-prompt.md`: starter template for first draft.
