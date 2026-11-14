# Claude Guide Notes

Distilled from the local PDF `The Complete Guide to Building Skills for Claude` available on 2026-03-10. This is a compact design aid, not a copy of the original document.

## High-Value Takeaways

- Start with 2-3 concrete use cases before writing the skill.
- Skills work best when they encode repeatable workflows, not generic advice.
- Progressive disclosure matters: keep metadata small, `SKILL.md` focused, and detailed material in linked files.
- The frontmatter description is the main trigger surface and needs realistic trigger phrases.
- A strong skill usually includes validation gates, not just happy-path steps.
- Iteration matters: test both expected triggers and non-triggers.

## Observed Skill Categories

- Document and asset creation: consistent output quality, templates, quality checks.
- Workflow automation: step-by-step methods, validation gates, iterative refinement.
- MCP enhancement: tool sequencing, domain context, and error handling on top of tool access.

`skill-creator` is explicitly a workflow-automation pattern: define use cases, generate frontmatter, write instructions, validate, and iterate.

## Practical Benchmarks

Use these as review prompts rather than hard metrics:

- Does the skill trigger for most relevant prompts?
- Does it avoid unrelated prompts?
- Does the workflow complete with fewer clarifying turns?
- Are validation and correction loops built in where mistakes are costly?
- Can a new user succeed on the first try with minimal redirection?

## Patterns Worth Reusing In Codex

- Separate "what should trigger" from "what should not trigger".
- Keep the main workflow sequential when the task is fragile.
- Move long reference material out of `SKILL.md`.
- Use scripts when deterministic checks are safer than pure prose.
- Validate metadata and packaging before claiming the skill is ready.
