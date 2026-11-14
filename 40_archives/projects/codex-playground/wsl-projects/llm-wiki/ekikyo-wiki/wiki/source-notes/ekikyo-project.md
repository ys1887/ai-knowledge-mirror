# ekikyo_project

**ページ目的:** `ekikyo_project` がどのような EXTRACT ワークスペースで、何を source-of-truth としていたかを整理する。

## ソースの性格

`ekikyo_project` は、`sources / prompts / scripts` をまとめて運用する統合ワークスペースであり、`project_source/index.md` が探索起点になっている。初回 foundation で durable と見なせる核は、次の三層分離である。

| 層 | 代表ファイル | 役割 |
| --- | --- | --- |
| 引用層 | `quotes_honka.md`, `quotes_koji.md` | 本卦・変爻の引用 block を供給する |
| 解釈層 | `takashima_interp_**.md` | 高島系の解釈論旨を供給する |
| 補助層 | `jokaden.md`, `bungenden.md`, `keijiden.md` | 序卦伝・文言伝・繋辞伝を限定的に補助利用する |

## 強み

- どのソースをどう優先して読むかが prompt 文書に明示されている。
- `EX_SIMPLE / EX_5 / EX_COMPARE` の出力構造が分かる。
- 表記ゆれや引用ルールまで含めて、運用上の知恵がまとまっている。

## 限界

- operational document が中心であり、資料そのものの authority とは別に扱う必要がある。
- generated output や作業物を primary evidence と見なすべきではない。
- 現在の canonical base が `ekikyo` repo 側に寄っている可能性が高く、最新正本とのズレは要確認。

## 初回 foundation での使いどころ

- source layering の初期整理。
- 古典層と解釈層を混同しないための運用原則の抽出。
- テンプレート差分が、将来どの kinds of wiki page を作るかの参考になることの確認。

## 要確認

- `ekikyo_project` と `ekikyo` repo の exact migration lineage。
- `project_source/sources/` 内の各 markdown source と PDF/Obsidian 側の対応関係。

## Provenance

- `/mnt/e/Documents/Playground/ekikyo_project/README.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/index.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/prompts/ekikyo_custom_prompt.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/outputs/ex_simple_output_template.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/outputs/ex_5_output_template.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/outputs/ex_compare_output_template.md`
