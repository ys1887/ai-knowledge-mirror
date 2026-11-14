# Source Roles And Coverage

**ページ目的:** 4つの登録済みソースの役割差を、初回 query の判断材料として比較する。

## 比較表

| ソース | もっとも強い役割 | 何に向くか | 主な弱み |
| --- | --- | --- | --- |
| Obsidian `100_易経` | 混成の研究母艦 | 履歴、研究メモ、整理済み markdown、後の pattern 抽出 | note 単位の provenance が uneven |
| PDF library `易経` | 版確認の母艦 | 書名・巻構成・底本確認、原資料の存在確認 | OCR / copy 制限で本文抽出が不均一 |
| `ekikyo_project` | 運用史の母艦 | source layering、テンプレート構造、表記ルール | current canonical base とは限らない |
| `ekikyo` repo | 現行 canonical EXTRACT の母艦 | canonical path、責務分離、fail-fast contract | 高島系以外の知識は薄い |

## cross-source の見取り図

- Obsidian と PDF library は内容ソース寄りである。
- `ekikyo_project` と `ekikyo` repo は運用・構造ソース寄りである。
- `ekikyo_project` と `ekikyo` repo には重なりがあり、どちらも EXTRACT 専用・高島系中心・引用層と解釈層の分離を重視する。
- ただし、現時点では `ekikyo` repo の方が canonical root の明示と責務分離が強く、より現行正本に近い。

## 初回 foundation における優先順

1. source の役割差を知るためにこのページを読む。
2. canonical path や current contract が必要なら `ekikyo` repo を先に見る。
3. 運用史や旧来 prompt 設計まで見たいなら `ekikyo_project` を見る。
4. 内容 source や個人史に降りるときは Obsidian と PDF library を見る。

## 要確認

- `ekikyo_project` の markdown source と `ekikyo` repo の assets の対応表。
- Obsidian 内 markdown 化資料と PDF library の版対応。

## Provenance

- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/110_易占/高島に寄せる？.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/140_高島易断/周易占筮法秘伝_現代語訳.md`
- `/mnt/e/Documents/PDF/易経/高島易断/高島易断_01.pdf`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/index.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/prompts/ekikyo_custom_prompt.md`
- `/home/ys/projects/ekikyo/AGENTS.md`
- `/home/ys/projects/ekikyo/spec/extract_contract.md`
