# `ekikyo-wiki` operational entry

## Purpose
- This repository is an I Ching-focused persistent wiki operated in the `llm-wiki` pattern.
- The primary interpretation family is Takashima Ekidan, but the wiki may also incorporate other books, websites, notes, and the user's own divination history.
- The goal is not to re-read all raw sources on every query. The goal is to accumulate durable, cross-referenced markdown knowledge over time.
- Obsidian is the primary reading and browsing interface. Codex maintains the wiki layer.

## Source Of Truth
- Parent repository contract:
  - `/home/ys/projects/llm-wiki/AGENTS.md`
- Reference pattern:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/LLM_Wiki.md`
- Repository contract:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/AGENTS.md`
- Content index:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/index.md`
- Chronological log:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/log.md`
- Raw source root:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/raw/`
- Wiki page root:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/`
- Supporting rules:
  - `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/`

## Repository Layout
- `raw/`
  - Immutable or effectively immutable raw sources stored locally in this repository.
  - Keep copies here only when local storage is practical and useful.
- External sources
  - Obsidian notes, PDF files, `ekikyo` repository files, and websites may remain outside this repository.
  - External sources are allowed as linked sources and do not need to be duplicated into `raw/`.
- `wiki/`
  - LLM-maintained markdown knowledge pages.
  - This layer contains summaries, topic pages, hexagram pages, comparison notes, synthesis pages, and other reusable knowledge artifacts.
- `schema/`
  - Supporting operational rules such as retrieval, provenance, source registration, and maintenance notes.
- `index.md`
  - Content-oriented entrypoint into the wiki.
- `log.md`
  - Append-only chronological record of ingest, query, and lint activity.

## Operating Modes
- `ingest`
  - Process one source, or a small controlled batch of sources, into persistent wiki knowledge.
- `query`
  - Answer from the wiki first, then read source material only where the wiki is insufficient.
- `lint`
  - Health-check the wiki for contradictions, stale claims, orphan pages, weak provenance, and missing cross-links.

## Ingest Flow
1. Identify the source to ingest.
2. Confirm whether the source is local under `raw/` or external.
3. Read the source directly, or use a prior large-source summary when that is the agreed workflow.
4. Extract durable knowledge rather than copying transient chat output.
5. Create or update relevant pages under `wiki/`.
6. Update `index.md` so the new or changed pages are discoverable.
7. Append an ingest entry to `log.md`.
8. Record provenance on affected wiki pages.

## Query Flow
1. Read `index.md` first.
2. Read the most relevant pages under `wiki/`.
3. If the wiki is sufficient, answer from the wiki with citations or source references as appropriate.
4. If the wiki is insufficient, consult the source registry or external source references and read only the necessary raw sections.
5. If the query produces durable knowledge, file the result back into `wiki/` instead of leaving it only in chat.

## Logging and Indexing
- `index.md` is a catalog of wiki content, not a diary.
- `log.md` is chronological and append-only.
- Prefer parseable log headings such as:
  - `## [YYYY-MM-DD] ingest | <source or topic>`
  - `## [YYYY-MM-DD] query | <question or page>`
  - `## [YYYY-MM-DD] lint | <scope>`
- On ingest, update both the relevant wiki pages and `index.md`, then append to `log.md`.
- On important query or lint passes, append a log entry when the result changes the long-term state of the wiki.

## Provenance and Staleness
- Every durable claim in `wiki/` should be traceable to one or more sources.
- Do not promote unsupported recollection or unverified chat output into the wiki as fact.
- Distinguish source update time from verification time whenever that information is available.
- Mark or note stale material when a newer source may supersede it.
- Prefer explicit source references over vague attribution.

## History Handling
- The user's divination history is a valid source layer.
- Existing Obsidian history may remain outside this repository and be referenced as external source material.
- History without outcome notes is still usable as raw context, but it is weaker as evidence for durable knowledge.
- For future divination records, later outcome notes are encouraged because they improve the value of the history layer.
- Raw history should not be treated as finished knowledge by default. Repeated patterns, interpretive lessons, and cross-case observations belong in `wiki/`.

## Workflow Expectations
- Prefer small, clear, reversible changes.
- Ingest sources one at a time by default.
- Stay close to the original `llm-wiki` pattern: raw layer, wiki layer, schema layer, plus index and log.
- Use Copilot or another tool for expensive large-source summarization when that saves token cost, but keep Codex responsible for repository structure, durable filing, and cross-reference maintenance.
- Keep the wiki in markdown and keep operations understandable without specialized infrastructure.

## Fixed Boundaries
- Do not rewrite or mutate raw sources unless explicitly asked.
- Do not assume all sources must be copied into this repository.
- Do not fall back to full-corpus reading as the default query strategy.
- Do not create large-scale directory reshuffles without explicit direction.
- Do not treat the current source registry format as fixed yet; the registry contract can evolve.
- Do not confuse transient question-answering with durable wiki maintenance. Only durable outputs belong in `wiki/`.
