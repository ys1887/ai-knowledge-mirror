---
name: llm-wiki-ingest
description: Ingest source registry entries into a wiki root from the current working directory by reading its local AGENTS.md, source registry, wiki pages, index, and log. Use when the user asks to ingest wiki sources, update a wiki from multiple source locations, or run a source-driven wiki maintenance pass in the current wiki root.
metadata:
  short-description: Ingest source registries into a wiki root
---

# LLM Wiki Ingest

## Purpose
- Ingest one wiki's registered source locations into durable markdown knowledge pages.
- Treat the current working directory as the starting point, then resolve the wiki root by walking upward until the directory contains the wiki contract and the standard wiki files.

## Use This Skill When
- The user asks to ingest a wiki from its source registry.
- The user asks to update `wiki/`, `index.md`, and `log.md` from multiple source locations.
- The user says to read a wiki's sources from the current project or current directory.
- The request is about wiki maintenance, not answering a one-off question.

## Do Not Use This Skill When
- The user wants a one-off factual answer without persisting it in the wiki.
- The user wants code changes, app feature work, or repository refactoring.
- The user is doing an `ekikyo` EXTRACT run or any other non-wiki workflow.
- The request does not involve a wiki root, source registry, or durable markdown outputs.

## Workflow
1. Start from the current working directory.
2. Walk upward until you find a wiki root containing:
   - `AGENTS.md`
   - `index.md`
   - `log.md`
   - `schema/source-registry.md`
   - `wiki/`
3. If no such root exists, stop and report that the current directory is not a supported wiki root.
4. Read the wiki's `AGENTS.md` first, then the source registry, then `index.md`, then the most relevant existing wiki pages.
5. Read every source listed in the registry that is in scope for the requested ingest pass.
6. Extract durable knowledge only. Do not rewrite raw sources.
7. Create or update the relevant markdown pages under `wiki/`.
8. Update `index.md` so the new or changed pages are discoverable.
9. Append an ingest entry to `log.md`.
10. Record provenance on the wiki pages you changed.

## Guardrails
- Keep the output bounded to the wiki root discovered from the current working directory.
- Preserve source provenance and do not collapse multiple sources into unsupported claims.
- If the current directory is not a wiki root, fail safely instead of guessing a target.
- If the requested ingest is too large for a single pass, summarize the source coverage and stop before inventing incomplete pages.
