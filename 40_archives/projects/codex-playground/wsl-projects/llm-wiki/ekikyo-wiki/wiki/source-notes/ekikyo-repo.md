# ekikyo Repo

**ページ目的:** `/home/ys/projects/ekikyo` を、現行の canonical EXTRACT 基盤として要約する。

## ソースの性格

`ekikyo` repo は、Takashima 系 source を基準に EXTRACT 用 prompt text と postprocess script を組み立てる最小基盤である。ここで重要なのは、source と責務の固定である。

- canonical quote source:
  - `assets/quotes/quotes_honka.md`
  - `assets/quotes/quotes_koji.md`
- canonical interpretation source:
  - `assets/takashima/`
- runtime / contract:
  - `spec/extract_contract.md`
  - `formats/*.md`
  - `scripts/*.py`

## 強み

- script と LLM の責務分離が明確で、どこまでが fixed source block かが分かる。
- fail-fast 方針が徹底されており、不足時に推測で埋めない。
- canonical source root が明示されているため、後続の provenance 記述が安定する。

## 限界

- `EXTRACT` 専用 repo であり、wiki 全体の source diversity はここだけでは表現できない。
- 高島系の current canonical base としては強いが、個人史や他流派比較の source ではない。
- repo の contract は運用規範であって、解釈内容そのものの全体像ではない。

## 初回 foundation での使いどころ

- canonical path の固定。
- 高島系運用で「何を引用 block とし、何を解釈 prose とするか」の整理。
- 将来、個別卦ページを作る際の provenance anchor の確保。

## 要確認

- `ekikyo_project` 側の source と `assets/takashima/` の対応表。
- `assets/reference_cases/高島易断_占例.md` を foundation wiki にどう取り込むか。

## Provenance

- `/home/ys/projects/ekikyo/AGENTS.md`
- `/home/ys/projects/ekikyo/README.md`
- `/home/ys/projects/ekikyo/spec/extract_contract.md`
- `/home/ys/projects/ekikyo/formats/shared.md`
- `/home/ys/projects/ekikyo/assets/quotes/quotes_honka.md`
- `/home/ys/projects/ekikyo/assets/quotes/quotes_koji.md`
