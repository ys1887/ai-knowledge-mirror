Motto: "Small, clear, safe steps — grounded in real docs when available."

Scope
- This file is the repository-level instruction file for Copilot.
- Repository/workspace `AGENTS.md` and other local instructions override this file when present.

Principles
- Keep changes minimal, safe, and reversible.
- Prefer clarity over cleverness; simplicity over complexity.
- Avoid new dependencies unless necessary; remove when possible.

Reading Order
- Read repository instructions first when available: `AGENTS.md`, this file, `README.md`, tests, and existing scripts.
- Prefer primary sources: official docs, in-repo docs, existing code, tests, and documented entrypoints.
- If uncertain about requirements or external behavior, pause and verify before coding.
- Do not guess file names, asset layouts, or undocumented workflows.

Workflow
- Follow: Plan -> Read -> Verify -> Implement -> Self-Review -> Test -> Reflect.
- Share a short plan before major edits, keep diffs reviewable, and confirm assumptions against the code and docs you are changing.
- Prefer existing scripts and documented entrypoints over reconstructing workflows from scratch.
- Distinguish helper/intermediate artifacts from final deliverables and keep their responsibilities separate.

Self-Review
- After implementation and before declaring the task complete, review for requirement fit, regression risk, error handling, edge cases, and test gaps.
- If issues are found, fix them when feasible; otherwise report the issue, impact, and a concrete follow-up fix.
- Even when no issues are found, explicitly report remaining risks, assumptions, and unverified items.

Skills
- Treat installed skills as reusable workflows rather than ad hoc prompts.
- When a request clearly matches a skill, read that skill's `SKILL.md` and follow it before inventing a custom flow.
- Prefer the skill's documented scripts, templates, and references over recreating them inline.
- If both repository instructions and a skill apply, follow repository instructions first and use the skill within those constraints.

Safety
- Never log secrets or PII.
- Validate external inputs and escalate auth or permission changes.
- Fail fast on invalid inputs and handle transient failures with bounded retries.
