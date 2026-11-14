# AI_knowledge の PARA 再編（実施記録）

- 日付：2026-11-13
- 実施者：エイダ（本人の承認した対応表どおり）
- 根拠：対応表 `mapping-table-2026-11-13`（作業側に保管）。設計は最終提案（2026-11-13）どおり

## 実施内容

1. 新規フォルダ11件を作成した（10_projects、20_areas とその配下3件、30_resources と skills、40_archives とその配下3件）。
2. 分割を済ませた。統治ファイル（guide、rules、changelog、work-log）はルートへ、settings-index は agents へ。yomiyasu と skills の索引は 30_resources/skills へ。Context は、月次索引3件を 20_areas/life へ、backlog 索引を 40_archives/context へ分けた。
3. フォルダ単位の移動と改名を10件行った。10_common → 30_resources/knowledge、20_agents → ai-operations/agents、40_log → ai-operations/logs、Hermes 成果物 → ai-operations/outputs、scripts → ai-operations/scripts、skills の残り → 40_archives/projects/lib-skills、Playground → 40_archives/projects/codex-playground、80_sources → 30_resources/sources、90_templates → 30_resources/templates、メール移行の状態記録 → 40_archives/projects。
4. 空になった 00_home、30_context、50_projects と、吸収した索引・案内3件（00_home の一覧、Context の README、旧プロジェクト一覧）をゴミ箱へ移した（完全削除はしていない）。
5. 新規ページ13件を作成した（Projects の索引と2ページ、Areas の索引とページ、Archives の索引とページ、knowledge の索引）。
6. 文書を追随させた。ルート README を書き換え（題名の「（下書き）」を外し、優先情報源の宣言を追加）、guide、登録簿の索引、settings 索引、skills 索引、資料索引、エイダの settings と記録索引、changelog と work-log へ記録した。
7. 仕組みを追随させた。コンテキスト巡回（0:00 と 12:00）の書き込み先を life の月次索引へ変え、全体確認のフォルダ ID 一覧を新しい構成へ差し替えた。朝のチェーン（9:30）の登録簿パスも新しい場所へ直した。

## 途中の出来事

- フォルダの移動と改名を同時に行う呼び出しで、Drive API の一時的な失敗が3件（logs、scripts、templates）あった。いずれも実物を確認すると未実施だったため、移動と改名を分けてやり直し、解消した。
- 移動の承認カード待ちで作業が止まった場面があり、本人の承認で再開した。

## 検証（2026-11-13 実施分）

- ルート直下は、統治ファイル5件と 10_projects、20_areas、30_resources、40_archives、99_backup だけになったことを Drive の一覧で確認した。
- 新構成のツリー（3階層まで）を取得し、最終提案と一致することを確認した。
- PC ミラー（E:\Documents\Google Drive\AI_knowledge）でも新しい構成がそのまま見え、旧フォルダの残りや Playground／codex の名前のずれは解消したことを確認した。
- Archives 内の Git リポジトリが PC 側で開けることを確認した（lib-skills は記録どおりの HEAD、codex-playground 内の ekikyo も読み取り可）。
- スクリプト正本が 20_areas/ai-operations/scripts に見えることを PC ミラーで確認した。
- コンテキスト巡回の状態ファイルのスナップショットを移行後のツリーで差し替えた（168件。保管一式と outputs はフォルダ単位の記録）。次回（0:00）の巡回は新しい書き込み先で動く。
- スペース「AI_knowledge」の目録と運用メモを新しい構成へ更新した。スペース「Hermes Bots」は登録簿の再取り込みを開始した（完了の確認は次回の朝のチェーンの結果と合わせる）。
- 索引だけから答えられるかの確認：Bot の成果物の出力先、スクリプトの正本と実行用コピーの置き場、yomiyasu 原本の置き場、12月のメール移行の確認2件は、いずれも新しい索引とページからたどれる。

## 残件

- Hermes 側への引き渡し文は、再編後の構成で作り直す（2026-11-12 の未送付分と、rules.md の参照文言の件を含む）。本人へ渡すところまでで、送付は本人の操作。
- ルートフォルダ名を `AI` へ変える件は保留のまま（条件は引き渡しの送付と Hermes 側の追随の完了）。
- Hermes Bots の登録簿にエイダの行が紛れている件と、スペース「Hermes Bots」の反映が止まっている件は、登録簿側の担当と合わせて別途確認する。
