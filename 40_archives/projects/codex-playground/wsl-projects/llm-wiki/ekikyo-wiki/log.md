# Log

This file is the chronological, append-only log for `ekikyo-wiki`.
Use it to record ingest work, important queries, and lint passes.

## Format
- Prefer headings in the following form:
  - `## [YYYY-MM-DD] ingest | <source or topic>`
  - `## [YYYY-MM-DD] query | <question or page>`
  - `## [YYYY-MM-DD] lint | <scope>`
- Append new entries to the end of the file.
- Record only work that changes or materially informs the long-term state of the wiki.

## Entry Template
### Summary
- What was processed, answered, or checked.

### Files
- Which wiki pages or reference files were created, updated, or reviewed.

### Sources
- Which raw or external sources were used.

### Notes
- Follow-up items, uncertainties, or stale risks.

## Initial State
- Repository skeleton created.
- `AGENTS.md`, `LLM_Wiki.md`, and `index.md` initialized.
- No source ingest has been logged yet.

## [2026-04-07] ingest | llm-wiki bootstrap
### Summary
- Established `llm-wiki` as the parent repo, kept `ekikyo-wiki/` beneath it, and aligned local contract paths to the new layout.
### Files
- `/home/ys/projects/llm-wiki/AGENTS.md`
- `/home/ys/projects/llm-wiki/.gitignore`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/AGENTS.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/log.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/raw/.gitkeep`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/.gitkeep`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/.gitkeep`
### Sources
- Existing local wiki skeleton and reference note files.
### Notes
- Git repository initialization, private GitHub repo creation, and initial push were performed as part of the bootstrap.

## [2026-04-07] ingest | source registry bootstrap
### Summary
- Registered the current source locations for `ekikyo-wiki` in a dedicated schema file and exposed the registry from the wiki index.
### Files
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/source-registry.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/index.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/log.md`
### Sources
- `C:\Users\nekol\Proton Drive\Obsidian\100_易経`
- `E:\Documents\PDF\易経`
- `E:\Documents\Playground\ekikyo_project`
- `\\wsl.localhost\Ubuntu\home\ys\projects\ekikyo`
### Notes
- Treat the four entries as the initial authoritative source registry until a move or rename is reported.

## [2026-04-07] ingest | initial foundation
### Summary
- Read the four registered source locations and created the first compact foundation set for `ekikyo-wiki`.
- Prioritized overview, source-layer concepts, and one source note per registered source instead of mass hexagram generation.
- Preserved cross-source differences and marked unresolved lineage / provenance gaps as `要確認`.
### Files
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/overview/foundation-overview.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/concepts/classical-reading-units.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/concepts/source-layers-and-provenance.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/source-notes/obsidian-100-iching.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/source-notes/pdf-library-iching.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/source-notes/ekikyo-project.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/source-notes/ekikyo-repo.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/wiki/comparisons/source-roles-and-coverage.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/index.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/log.md`
### Sources
- `C:\Users\nekol\Proton Drive\Obsidian\100_易経`
- `E:\Documents\PDF\易経`
- `E:\Documents\Playground\ekikyo_project`
- `\\wsl.localhost\Ubuntu\home\ys\projects\ekikyo`
### Notes
- Hexagram-level durable pages are deferred to later ingest passes.
- Note-level provenance inside Obsidian clip / translation materials is uneven and remains a follow-up task.
- The migration lineage between `ekikyo_project` and `ekikyo` is suggestive but not yet fully mapped file-by-file.

## [2026-04-07] ingest | Obsidian diff batch
### Summary
- Ingested the newly added Obsidian diff batch under `180_易経_Clip編集` and `190_易サイトclip` as a limited test, and reflected the durable portions in the wiki.
- Kept the update localized to existing overview, concept, source-note, and comparison pages instead of expanding into broad hexagram coverage.
### Files
- `wiki/overview/foundation-overview.md`
- `wiki/concepts/classical-reading-units.md`
- `wiki/concepts/source-layers-and-provenance.md`
- `wiki/source-notes/obsidian-100-iching.md`
- `wiki/source-notes/pdf-library-iching.md`
- `wiki/source-notes/ekikyo-project.md`
- `wiki/source-notes/ekikyo-repo.md`
- `wiki/comparisons/source-roles-and-coverage.md`
- `index.md`
- `log.md`
### Sources
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/180_易経_Clip編集`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/190_易サイトclip`
### Notes
- This was a limited diff-ingest test, not a full re-ingest of all registered sources.
- Existing foundation pages were updated where the new batch clarified source roles and provenance.

## [2026-04-07] ingest | llm-wiki reference note consolidation
### Summary
- Moved the `llm-wiki` reference note and the Karpathy article clip into `schema/`, then added a repo-specific summary note for the practical operating ideas.
- Updated the index to point to the schema-stored reference note and the new summary note.
### Files
- `/home/ys/projects/llm-wiki/ekikyo-wiki/index.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/log.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/LLM_Wiki.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/karpathy's second brain how to build it.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/llm-wiki-pattern.md`
### Sources
- `LLM_Wiki.md`
- `karpathy's second brain how to build it.md`
### Notes
- Kept the raw article clip separate from the new summary so the schema layer holds the reusable operating guidance rather than the original article text.
