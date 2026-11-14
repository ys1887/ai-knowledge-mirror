# LLM Wiki

## Reference
- Original gist:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Title:
  - `llm-wiki`
- Purpose:
  - A pattern for building personal knowledge bases using LLMs.

## Core Idea
- Standard RAG re-discovers knowledge from raw documents on every query.
- The `llm-wiki` pattern instead builds a persistent markdown wiki between the user and the raw sources.
- The LLM reads a source, extracts durable knowledge, updates the wiki, maintains cross-references, and keeps synthesis current over time.
- The wiki is the accumulated artifact. Query-time retrieval should rely on the wiki first, not on re-reading the full corpus.

## Architecture
- Raw sources
  - Immutable source material that the LLM reads but does not rewrite.
- Wiki
  - LLM-maintained markdown pages that store summaries, concepts, entities, comparisons, and synthesis.
- Schema
  - An operational contract such as `AGENTS.md` that defines structure, workflow, and conventions.

## Operations
- Ingest
  - Read a source, extract the important knowledge, update relevant wiki pages, update the index, and append to the log.
- Query
  - Read the index first, then the relevant wiki pages, and only then consult raw sources if the wiki is insufficient.
- Lint
  - Periodically check for contradictions, stale claims, orphan pages, missing links, and missing topic pages.

## Indexing And Logging
- `index.md`
  - Content-oriented catalog of wiki pages.
  - Read this first during query.
- `log.md`
  - Chronological append-only record of ingests, queries, and lint passes.
  - Prefer parseable headings with date and operation type.

## Local Adoption In `ekikyo-wiki`
- This repository applies the `llm-wiki` pattern to I Ching material.
- The main interpretation family is Takashima Ekidan.
- Other books, websites, personal notes, and divination history are also valid sources.
- Sources may stay distributed.
  - Small or stable files may be copied into `raw/`.
  - Large or already-managed materials may remain in Obsidian, `ekikyo`, PDFs, or websites and be referenced externally.
- Obsidian is the primary reading interface.
- Codex maintains the markdown wiki structure in this repository.

## Local Differences From The Original Pattern
- The original gist is abstract and domain-agnostic. This repository is domain-specific to I Ching study and divination history.
- This repository explicitly allows a mixed source model: local raw files plus external linked sources.
- This repository treats divination history as a source layer that can later be promoted into durable knowledge.
- Large-source summarization may be delegated to Copilot or another tool, while Codex remains responsible for durable filing, indexing, logging, and cross-reference maintenance.

## Deferred Or Optional
- Search tooling beyond `index.md`
- Formal source registry schema
- Dataview or other Obsidian-specific automation
- Image-heavy workflows
- Dedicated CLI or MCP search tools

## Notes
- This file is a local reference note, not a full copy of the original gist.
- `AGENTS.md` is the active operational contract for this repository.
