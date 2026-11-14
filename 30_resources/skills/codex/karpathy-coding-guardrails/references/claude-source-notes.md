# Claude Source Notes

This file captures the ideas worth porting from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) without copying the original Claude-oriented packaging.

## Source Shape

- The upstream repo centers on a short `CLAUDE.md` and a Claude skill variant.
- Its value is behavioral guidance, not Claude-specific code or APIs.

## Ported Ideas

- Surface assumptions instead of silently choosing one interpretation.
- Prefer the simplest solution that satisfies the request.
- Keep edits tightly scoped to the requested outcome.
- Define success criteria and verify them before claiming completion.

## Codex-Specific Reframing

- Codex may operate under `AGENTS.md`, Plan Mode, and existing workspace rules, so the guardrails are additive rather than authoritative.
- Trigger design must stay narrow enough that this skill does not steal tasks from more specific workflow skills.
- Self-review and explicit verification are part of the expected finish line in this workspace.

## What Was Not Ported Literally

- Claude plugin packaging and `CLAUDE.md` installation instructions.
- Claude-specific wording about marketplace or plugin installation.
- Any expectation that this skill overrides existing repo policy.
