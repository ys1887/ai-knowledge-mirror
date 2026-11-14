# AGENTS.md

## Scope
- This file defines repo-local working rules for `iching-sdk`.
- User-facing CLI contract lives in `README.md`; do not duplicate it here.

## Repo Priorities
- The only supported entrypoint is `./iching`.
- Treat `README.md` as the current contract for CLI behavior, `iching.toml`, exit codes, and artifacts.
- Before changing behavior, read `README.md` and `tests/test_cli.py` first.

## Provider Debugging
- `codex` provider is runtime-sensitive; prefer small diagnostic steps over broad retries.
- For provider checks, start with a short `codex exec` probe and then `tests/fixtures/extract_cases/test_1.md`.
- Treat `run.json` as the primary diagnostic artifact for provider failures.

## Change Discipline
- If CLI contract changes, update `README.md` and `tests/test_cli.py` in the same change.
- Prefer small, safe, reversible diffs over structural rewrites.
- Do not restate global AGENTS rules or copy long CLI details from `README.md`.
