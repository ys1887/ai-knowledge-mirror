---
name: skill-creator-codex
description: Build or update Codex-focused skills with strong trigger design, metadata, validation, runtime deployment awareness, and workspace-specific operating rules. Use when creating a new Codex skill, porting an existing skill to Codex, improving SKILL.md frontmatter or trigger behavior, or preparing a skill for runtime deployment from this repo.
metadata:
  short-description: Create or update Codex skills
---

# Skill Creator Codex

Create or update skills meant to be used by Codex, especially when the work needs strong trigger design, metadata hygiene, validation, runtime deployment awareness, or workspace-specific operating rules.

This skill is optimized for the workflow in `E:\Documents\Playground\lib-skills` where this repo is the edit source-of-truth and runtime deployment is published from this repo into `C:\Users\nekol\.codex\skills`. Publish to `/home/ys/.codex/skills` only when WSL runtime support is still needed or explicitly requested.

## Use This Skill For

- Creating a new Codex skill from scratch.
- Updating an existing skill to improve trigger behavior, frontmatter, validation, or helper resources.
- Porting a Claude-oriented or generic skill into a Codex-oriented skill.
- Designing a skill that must respect local `AGENTS.md`, runtime deployment rules, self-review expectations, and git workflow expectations.

## Do Not Use This Skill For

- Listing installable skills or installing a skill from GitHub only. Use `skill-installer` for that.
- General repo implementation tasks that are not about skill creation or skill maintenance.
- Generic Claude-only advice that is not intended to produce or improve a Codex skill artifact.

## Core Principles

### Start From Real Use Cases

Before writing or editing files, identify 2-3 concrete prompts that should trigger the skill and 2-3 prompts that should not. Use those examples to shape the frontmatter description, structure, and validation plan.

### Keep The Trigger Tight

Frontmatter is the highest leverage part of the skill. The description must say both what the skill does and when to use it, using phrases users would realistically say. Avoid descriptions that are so broad that they steal unrelated requests from other skills.

### Prefer Progressive Disclosure

Keep `SKILL.md` focused on the workflow, decision points, and important guardrails. Put detailed guidance into `references/`, deterministic helpers into `scripts/`, and output assets into `assets/`.

### Optimize For Codex Reality

Design the skill for the environment it will actually run in:

- Codex may be in Plan Mode or Default mode.
- The workspace may carry `AGENTS.md` and `codex-rules.yaml` constraints.
- WSL and Windows `.codex` homes are intentionally separated in this environment.
- Locally authored custom skills must be created or updated in this repo first, even when the user asks from outside this repo.
- Runtime copies under `C:\Users\nekol\.codex\skills` and, when still needed, `/home/ys/.codex/skills` are deployment targets, not authoring locations.

## Operating Sequence

Follow this order unless there is a clear reason not to.

### 1. Explore Current State

- Read the relevant `AGENTS.md`, local rules files, existing skill files, and direct call sites before proposing edits.
- If the user references an existing skill, inspect its current `SKILL.md`, `agents/openai.yaml`, bundled resources, and trigger shape first.
- When relevant, read [references/claude-guide-notes.md](references/claude-guide-notes.md) for the distilled guidance from the Claude skills guide.

### 2. Lock Intent

Clarify:

- What the skill should enable.
- Which user prompts should trigger it.
- Which prompts should not trigger it.
- Whether the skill is new, a port, or an update.
- Whether it needs scripts, references, assets, or only tighter instructions.

In Plan Mode, keep asking until the implementation is decision-complete. In Default mode, make reasonable assumptions only when the risk is low and the intent is already clear enough to build safely.

### 3. Choose Branch Strategy

Before git-affecting work, state whether the change belongs on `main` or on a working branch.

- `main` is acceptable for small, low-risk text-only adjustments.
- Prefer a working branch for new skills, helper script changes, file moves, or multi-file updates.
- For this repo, a safe default branch name is `codex/<skill-name>` or `codex/<task-name>`.

### 4. Design The Skill Package

Decide the minimum useful package:

- `SKILL.md` for trigger logic, workflow, and guardrails
- `agents/openai.yaml` for UI metadata
- `scripts/` when deterministic helpers save time or prevent repeated code rewriting
- `references/` for detailed guides, checklists, schemas, and policy notes
- `assets/` only for files used in final outputs or UI presentation

If the skill has multiple modes or variants, keep the routing logic in `SKILL.md` and move variant-specific detail into direct child references.

### 5. Scaffold Or Update

For new skills, initialize the folder and create a clean starter layout. The helper scripts in `scripts/` are the preferred base when they fit:

- `scripts/init_skill.py`
- `scripts/generate_openai_yaml.py`
- `scripts/quick_validate.py`

When updating an existing skill, preserve working helpers unless there is a concrete reason to replace them.

### 6. Validate

Check all of the following:

- `SKILL.md` frontmatter is valid and specific.
- The skill name is hyphen-case and stable.
- `agents/openai.yaml` matches the skill's actual purpose.
- Trigger examples and non-trigger examples still make sense after the edit.
- Scripts and references mentioned in `SKILL.md` actually exist.
- The workflow does not claim behavior that belongs to another skill.

Use `scripts/quick_validate.py` for the minimum validation pass. Then run a manual trigger review using [references/trigger-checklist.md](references/trigger-checklist.md).

### 7. Deploy Or Hand Off

If the goal includes runtime installation, keep the boundary clear:

- Edit custom skills in this repo first.
- Use `skill-installer` when the task is to fetch skills from curated lists or GitHub repos.
- For this workspace, the default publish target is the Windows runtime copy: `C:\Users\nekol\.codex\skills`.
- After creating or updating a local custom skill, publish and verify the Windows runtime copy unless the user explicitly asks for a narrower deployment. Publish and verify `/home/ys/.codex/skills` only when WSL runtime support is still needed or explicitly requested.
- Do not treat either runtime copy as the source-of-truth, even if the current Codex session is loading from it.

See [references/codex-runtime-rules.md](references/codex-runtime-rules.md) before making deployment claims.

## Metadata Guidance

### `SKILL.md` Frontmatter

Use frontmatter to define a precise trigger.

- `name`: lowercase, digits, hyphens only
- `description`: one clear paragraph covering what the skill does and when to use it
- `metadata.short-description`: optional, short UI-oriented summary when helpful

Good descriptions include:

- the task
- the environment or target system when relevant
- likely trigger phrases
- boundaries that avoid over-triggering

Bad descriptions are vague, generic, or missing realistic usage cues.

### `agents/openai.yaml`

Treat this as UI metadata, not extra instructions.

- Read [references/openai_yaml.md](references/openai_yaml.md) before generating or editing values.
- Keep `display_name`, `short_description`, and `default_prompt` aligned with the current `SKILL.md`.
- Only add optional interface fields such as icons or brand color when they are intentionally supplied.

## When To Use `skill-installer`

Use `skill-installer` as a companion, not as the main authoring method for local custom skills.

Use it when:

- the user wants to list available upstream skills
- the user wants to install a curated or GitHub-hosted skill
- you want to inspect or bring in an external example skill before porting it

Do not use it as a substitute for editing the source-of-truth skill in this repo.

## Deployment Default

For self-authored local skills in this environment:

- Start in `E:\Documents\Playground\lib-skills`, even if the user is currently chatting from another project.
- Validate in the source repo first.
- Then publish to `C:\Users\nekol\.codex\skills`.
- If WSL runtime support is still needed or explicitly requested, also publish to `/home/ys/.codex/skills`; otherwise call out that WSL runtime deployment was intentionally skipped.

## Output Pattern

Unless the user clearly wants a narrower scope, structure the work as:

1. Explore
2. Lock intent
3. Lock implementation details
4. Scaffold or update files
5. Validate triggers and metadata
6. Confirm runtime/deployment path
7. Self-review before declaring completion

## Self-Review Requirements

Before finishing, explicitly review:

- requirement fit
- trigger conflict risk
- metadata drift
- missing helper files or stale references
- validation gaps
- deployment-path confusion between source-of-truth and runtime

If anything remains unverified, say so directly.

## Reference Map

- [references/claude-guide-notes.md](references/claude-guide-notes.md): distilled lessons from the attached Claude skills guide
- [references/codex-runtime-rules.md](references/codex-runtime-rules.md): source-of-truth, runtime, deployment, and git/reporting rules
- [references/trigger-checklist.md](references/trigger-checklist.md): under-trigger and over-trigger review checklist
- [references/openai_yaml.md](references/openai_yaml.md): `agents/openai.yaml` field rules
