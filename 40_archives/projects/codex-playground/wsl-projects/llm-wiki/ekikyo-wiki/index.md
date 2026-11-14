# Index

This file is the content-oriented entrypoint into `ekikyo-wiki`.
Read this file first when querying the wiki.

## Overview
- Domain:
  - I Ching / Ekikyo knowledge integration wiki
- Primary interpretation family:
  - Takashima Ekidan
- Repository pattern:
  - `llm-wiki` style persistent markdown wiki
- Main layers:
  - `raw/`
  - `wiki/`
  - `schema/`
  - `log.md`

## Core References
- [AGENTS.md](./AGENTS.md)
  - Active operational contract for this repository.
- [LLM Wiki Pattern](./schema/LLM_Wiki.md)
  - Local reference note for the original `llm-wiki` pattern, stored under `schema/`.
- [Karpathy Second Brain Notes](./schema/llm-wiki-pattern.md)
  - Repo-specific summary of the practical ideas extracted from the article clip.
- [Source Registry](./schema/source-registry.md)
  - Current locations of source material used by this wiki.
- [log.md](./log.md)
  - Chronological record of ingest, query, and lint activity.

## Wiki Categories
### Overview
- [Foundation Overview](./wiki/overview/foundation-overview.md)
  - 初回 foundation の範囲、4ソースの現在位置、読み進め方を示す入口ページ。

### Hexagrams
- No pages yet.

### Concepts
- [Classical Reading Units](./wiki/concepts/classical-reading-units.md)
  - 卦辞・彖伝・大象伝・爻辞・小象伝と補助層の役割分担を整理する。
- [Source Layers And Provenance](./wiki/concepts/source-layers-and-provenance.md)
  - 引用層・解釈層・研究層・履歴層・版確認層の使い分けを整理する。

### Source Notes
- [Obsidian 100_易経](./wiki/source-notes/obsidian-100-iching.md)
  - 個人履歴、研究ノート、markdown 化資料が混在する Obsidian ソースの性格を整理する。
- [PDF Library 易経](./wiki/source-notes/pdf-library-iching.md)
  - PDF 群の構成と、版確認ソースとしての強みと限界を整理する。
- [ekikyo_project](./wiki/source-notes/ekikyo-project.md)
  - EXTRACT ワークスペースとしての source layering とテンプレート運用を整理する。
- [ekikyo Repo](./wiki/source-notes/ekikyo-repo.md)
  - 現行 canonical EXTRACT 基盤としての source-of-truth と責務分離を整理する。

### Comparisons
- [Source Roles And Coverage](./wiki/comparisons/source-roles-and-coverage.md)
  - 4ソースの役割差、向く用途、主な弱みを見比べる。

### History-Derived Knowledge
- No pages yet.

## Source Layer
- Local raw sources:
  - `raw/`
- External linked sources:
  - Obsidian notes
  - `ekikyo` repository files
  - PDFs
  - websites

## Maintenance Notes
- Update this file whenever durable pages are added or significantly changed.
- Prefer short one-line summaries for each page entry.
- Use this file as the first stop during query before reading deeper wiki pages.
