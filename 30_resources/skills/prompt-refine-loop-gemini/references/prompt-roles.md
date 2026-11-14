# Prompt Roles Reference

Use these role intents when tuning loop behavior.

## Role A: ChatGPT-style optimizer
Goal: produce a cleaner, stricter prompt draft while preserving user intent.

Checklist:
- Clarify objective and target audience
- Make constraints explicit and testable
- Add output format requirements
- Remove contradiction or duplicate constraints
- Avoid unnecessary verbosity

## Role B: Gemini reviewer
Goal: critique the draft with practical, concrete improvements.

Checklist:
- Identify ambiguity, missing constraints, and edge cases
- Flag likely failure modes
- Suggest explicit checks and acceptance criteria
- Prioritize high-impact fixes over cosmetic wording

## Role C: Reviser
Goal: apply reviewer feedback to produce the next draft.

Checklist:
- Keep intent unchanged
- Integrate high-impact actions first
- Preserve useful constraints from prior draft
- Return only prompt content (no commentary)

## Scoring guidance
Convergence score is interpreted as "remaining improvement needed":
- `0.00-0.14`: near convergence, safe to stop
- `0.15-0.39`: moderate room for improvement
- `0.40-1.00`: major gaps remain

Tune stop behavior with `--threshold` and `--max-iter`.
