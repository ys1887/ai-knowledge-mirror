---
name: karpathy-coding-guardrails
description: Apply disciplined coding guardrails for non-trivial software tasks such as feature implementation, bug fixing, refactoring, code review, or ambiguous engineering work where Codex should surface assumptions, prefer simpler designs, keep changes tightly scoped, and verify outcomes before finishing. Use when the task is substantial enough to benefit from explicit tradeoffs, success criteria, or stronger self-checking. Do not use for trivial one-line edits, casual conversation, or tasks where a more specific skill clearly matches first.
metadata:
  short-description: Guardrails for non-trivial coding work
---

# Karpathy Coding Guardrails

Use this skill to reinforce disciplined behavior on non-trivial coding tasks.

This skill does not replace repository `AGENTS.md`, system policy, or more specific skills. It adds a lightweight set of guardrails when the work is large enough or ambiguous enough that Codex could otherwise make silent assumptions, overbuild, or drift beyond the requested scope.

## Use This Skill When

- The task involves multi-step implementation, debugging, refactoring, or review work.
- The request is ambiguous enough that assumptions and alternatives should be surfaced before coding.
- The user wants a bug fixed, behavior changed, or code reviewed with explicit verification.
- The task is large enough that a brief plan and deliberate self-review materially reduce risk.

## Do Not Use This Skill When

- The task is a trivial typo, rename, or obvious one-line edit.
- The request is casual conversation or otherwise not coding work.
- A more specific skill already fits clearly, such as `markitdown`, `defuddle`, `obsidian-cli`, or another domain workflow skill.
- The user only wants a concept explanation and no implementation or review behavior is needed.

## Core Principles

### 1. Think Before Coding

Do not silently pick an interpretation when the task has multiple plausible meanings.

- State important assumptions explicitly before implementing.
- If a key detail is missing and guessing would be risky, stop and ask.
- If multiple approaches are viable, surface the tradeoff that matters.
- If the requested path appears unnecessarily complex, say so and propose the simpler path.
- In Plan Mode, use planning to remove ambiguity before implementation. Outside Plan Mode, still surface uncertainty before writing risky code.

### 2. Simplicity First

Prefer the smallest clear solution that satisfies the request.

- Do not add features, knobs, abstractions, or configuration the user did not ask for.
- Match the existing language, style, and architecture unless there is a concrete reason not to.
- Avoid introducing new dependencies unless they are clearly necessary.
- If a design starts to sprawl, simplify it before continuing.

### 3. Surgical Changes

Keep the diff tightly tied to the request.

- Touch only the files and lines needed for the requested outcome.
- Do not refactor adjacent code just because you noticed it.
- Mention unrelated issues you see, but do not fix or remove them unless asked.
- Remove only the dead code or unused symbols created by your own change.
- When editing Markdown, prefer minimal diffs and do not rewrite or delete existing content without a reason tied to the task.
- Do not remove comments or formatting you do not understand.

### 4. Goal-Driven Execution

Turn the task into explicit checks, then work until those checks are satisfied or a real blocker appears.

- Define concrete success criteria before or during implementation.
- When fixing bugs, prefer a reproducer or test when practical.
- When changing behavior, verify it with the narrowest effective check: tests, build, lint, targeted run, or static inspection.
- Report what was verified and what remains unverified.
- Perform a self-review before finishing, focusing on requirement fit, regression risk, edge cases, and readability.

## Operating Pattern

Use a short sequence for substantial tasks:

1. Restate the target and any important assumptions.
2. Identify the smallest responsible approach.
3. Implement only the necessary changes.
4. Verify with targeted checks.
5. Self-review for scope drift, overengineering, and missed edge cases.

## Trigger Review Examples

These should lean toward this skill:

- "Fix this bug and make sure tests pass."
- "Review this PR and point out risky changes."
- "This implementation feels too complex. Simplify it."
- "Implement this feature, but keep the diff minimal and safe."

These should usually not trigger this skill:

- "What time is it?"
- "Fix this single typo in README."
- "Convert this PDF to Markdown."
- "Read this URL and summarize it."

## Reference

If you need the source inspiration, read [references/claude-source-notes.md](references/claude-source-notes.md). That file is a compressed note about the original Claude-oriented guidelines and should not be treated as normative policy.
