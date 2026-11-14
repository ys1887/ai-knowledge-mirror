# Foundation Overview

**ページ目的:** `ekikyo-wiki` の初回 foundation を俯瞰し、最初に読むべき入口を示す。

## この foundation の範囲

- 初回は `overview / concepts / source-notes / minimal comparison` を優先し、個別卦ページの大量生成は見送る。
- query 時の既定動作を raw 再読ではなく wiki first に寄せるため、まず source role と provenance の地図を作る。
- 解釈の主軸は高島系だが、ソース層は単一ではない。個人ノート、PDF、EXTRACT 用 workspace、現行 canonical repo を併置して扱う。

## 4ソースの現在位置

| ソース | 現在の役割 | 初回 foundation で残したこと |
| --- | --- | --- |
| Obsidian `100_易経` | 個人履歴・研究メモ・markdown 化資料の混成母艦 | durable 層と transient 層の切り分け |
| PDF library `易経` | 版確認・所蔵確認の母艦 | 高島系 PDF 群と一般向け易経本の併存 |
| `ekikyo_project` | EXTRACT 運用史の母艦 | 引用層・解釈層・補助層の分離 |
| `ekikyo` repo | 現行 canonical EXTRACT 基盤 | source-of-truth と責務分離 |

## 読み進め方

1. まず [Source Roles And Coverage](../comparisons/source-roles-and-coverage.md) で、4ソースの役割差を掴む。
2. 次に必要な source note を読み、どのソースを何のために使うかを判断する。
3. 用語や読み筋は [Classical Reading Units](../concepts/classical-reading-units.md) と [Source Layers And Provenance](../concepts/source-layers-and-provenance.md) で確認する。
4. それでも wiki が不足する場合だけ、該当ソースの原資料へ降りる。

## 現時点の保留

- 個別卦ページはまだ未着手。
- Obsidian 内の clip / 現代語訳ノートは、ノートごとの原出典確認が未了のものがある。
- `ekikyo_project` から `ekikyo` repo への移行線は見えるが、全ファイルの一対一対応は未整理であり詳細比較は要確認。

## Provenance

- `/home/ys/projects/llm-wiki/ekikyo-wiki/AGENTS.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/LLM_Wiki.md`
- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/source-registry.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/index.md`
- `/home/ys/projects/ekikyo/AGENTS.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/150_易経_資料/六十四卦一覧.md`
- `/mnt/e/Documents/PDF/易経/i-ching_book.pdf`
