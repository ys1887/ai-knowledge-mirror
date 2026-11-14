# llm-wiki Pattern Notes

## Purpose
- Capture the parts of the Karpathy-style `llm-wiki` idea that are useful for `ekikyo-wiki`.
- Separate durable operating principles from the original article clip and from the original pattern reference note.

## What Applies Here
- Keep `raw/` for source material and `wiki/` for maintained knowledge pages.
- Read `index.md` first during query work.
- Use `log.md` as an append-only record of ingest, query, and lint activity.
- Process sources one at a time by default, then update relevant wiki pages and cross-references.
- Prefer provenance and contradiction tracking over unsupported synthesis.
- Run periodic lint checks for stale claims, orphan pages, and missing links.

## What The Repo Already Does Differently
- External sources may remain at their original paths instead of being copied into `raw/`.
- The repo separates source location tracking into `schema/source-registry.md`.
- The operational contract already lives in `AGENTS.md`, so this note is a support document rather than the primary rule source.

## What To Avoid Copying Literally
- The claim that every source should touch 10-15 wiki pages.
- The assumption that all source material should be copied into one local `raw/` tree.
- The idea that a single monolithic schema file should replace the repo's existing role split.

## Provenance
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/LLM_Wiki.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/karpathy's second brain how to build it.md`
- Original article clip source:
  - `https://x.com/godofprompt/status/2041265656893489419`
