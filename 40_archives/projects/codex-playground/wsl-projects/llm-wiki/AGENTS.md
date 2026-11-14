# llm-wiki operational entry

## Purpose
- Parent repo for multiple persistent wiki workspaces.
- Each subdirectory can hold one wiki such as `ekikyo-wiki/`.
- Shared rules live here; domain-specific rules live in each sub-wiki's own `AGENTS.md`.

## Scope
- This file applies to the entire `llm-wiki/` tree.
- Read the root `AGENTS.md` first, then the target sub-wiki `AGENTS.md`, before editing any wiki subtree.

## Core Rules
- Keep changes small, safe, and reversible.
- Prefer primary sources and existing repo docs over guesswork.
- Treat raw/source material as read-only unless explicitly asked to mutate it.
- Preserve the raw/wiki/schema separation used by each sub-wiki.
- Keep repo state easy to inspect and recover.
- Prefer private GitHub repos unless explicitly instructed otherwise.

## Layout Conventions
- `*/raw/` holds source material.
- `*/wiki/` holds maintained markdown knowledge pages.
- `*/schema/` holds operational rules and supporting notes.
- `*/index.md` is the content catalog.
- `*/log.md` is the append-only activity log.

## Sub-Wiki Contract
- If a sub-wiki has its own `AGENTS.md`, that file governs that subtree.
- Update both root and sub-wiki contracts when the overall repo shape changes.
