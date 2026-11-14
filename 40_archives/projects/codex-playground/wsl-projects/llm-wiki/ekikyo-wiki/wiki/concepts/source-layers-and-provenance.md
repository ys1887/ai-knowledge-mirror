# Source Layers And Provenance

**ページ目的:** 4ソースを混ぜて使うときに、何をどの層として扱うべきかを整理する。

## この wiki で区別する層

| 層 | 典型例 | 使いどころ | 主な注意 |
| --- | --- | --- | --- |
| 引用層 | `quotes_honka.md`, `quotes_koji.md` | 原文 block や読み下しの確認 | 推測補完しない |
| 解釈層 | `takashima_interp_**.md`, `assets/takashima/` | 高島系の論旨把握 | 逐語引用と混同しない |
| 研究・整理層 | Obsidian の `150_易経_資料`, `140_高島易断`, project の index / prompt | 用語整理、構造把握、補助導線 | ノート単位で原出典の確認余地がある |
| 履歴・運用層 | Obsidian の `110_易占`, prompt 改善メモ | 個人史、運用史、問いの蓄積 | 単発の占断をそのまま一般知識にしない |
| 版確認層 | PDF library | 書名・巻構成・底本確認 | OCR 不可や暗号化で粒度に限界がある |

## 実務上の原則

- 原文を固定したいときは引用層を優先する。
- 高島系の判断の流れを読みたいときは解釈層を優先する。
- ノートや clip から得た知見は、原出典がどこにあるかを意識して再配置する。
- 個人の占い履歴は重要な source layer だが、単発結果をそのまま durable claim に昇格させない。

## 「要確認」に落とすべき場面

- ノートの `source:` 欄が空欄のまま、出典が文面から特定できないとき。
- 現代語訳ノートがどの版や底本に依拠したか未確認のとき。
- PDF がスキャン中心で、機械抽出だけでは本文確認が十分でないとき。
- `ekikyo_project` と `ekikyo` repo に似た構造があっても、片方をもう片方の完全な写しと断定できないとき。

## 初回 foundation で採った方針

- まずは source note を厚めにし、後続の query が raw 再読に直行しないようにする。
- 個別卦や詳細比較より先に、「どのソースをどの強さで信用するか」を wiki 側に固定する。

## Provenance

- `/home/ys/projects/llm-wiki/ekikyo-wiki/AGENTS.md`
- `/home/ys/projects/ekikyo/formats/shared.md`
- `/mnt/e/Documents/Playground/ekikyo_project/project_source/prompts/ekikyo_custom_prompt.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/110_易占/高島に寄せる？.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/110_易占/テンプレート改善：本卦と変爻.md`
- `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/140_高島易断/周易占筮法秘伝_現代語訳.md`
- `/mnt/e/Documents/PDF/易経/高島易断/高島易断_01.pdf`
