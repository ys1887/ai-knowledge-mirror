# 専門Bot３件の作成・確認結果

実施日：2026-11-16。実施者：ナユタ。本人が承認した３件の新規作成のみ。アイコンと日本語表示名の設定、既存Botの設定・登録簿修正、共通skill変更、外部サービス接続、既存バックアップ処理の変更は行っていません。

## 作成したBot

| プロフィール・当面の表示名 | 担当 | モデル | プロバイダ | 新規CLI確認 |
|---|---|---|---|---|
| takina | 経理・家計照合と月次集計 | gpt-6.1-sol | openai-codex | 終了コード0 |
| raven | 公開Web調査・原典確認と報告 | gpt-6.1-sol | openai-codex | 終了コード0 |
| crown | 英国英語学習・日英英日翻訳 | gpt-6.1-sol | openai-codex | 終了コード0 |

３件ともAPI方式はcodex_responses。既存Codexログインで動作。Fresh profileとして作成し、他BotのSOUL・記憶・固有連携はクローンしていません。プロファイル外にコマンド別名を作らないよう --no-alias を使用しました。同梱skill44件は保持し、共有yomiyasu v3.0.0のC側実体を参照しています。同梱skillの保持は専門外の業務権限ではありません。

## 正本・登録簿・成果物・写し

各 <name> は takina / raven / crown のいずれかです。

- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\<name>\`
- 登録簿：`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\agents\<name>\profile.md`
- 成果物：`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\<name>\`
- 全文写し：`E:\Documents\Google Drive\AI_knowledge\99_backup\<name>\`

各自己全文写しにSOUL.md・config.yaml・profile.yamlとCOPY-NOTE.mdを配置。秘密情報の値がないことを確認した正本３件ずつ、計９ファイルのコピー時点バイト一致を確認しました。.env・auth.json・認証ファイル・memoriesは共有写しに含めていません。

## 道具と境界

- takina：file・terminal。terminalは計算照合とyomiyasu検査に限定。Web取得・直接金融接続・元記録編集・支払い等は対象外。
- raven/crown：file・web。terminalはyomiyasu検査に限定。ブラウザ・ログイン必須資料・外部発信・音声・サービス接続は初期対象外。
- 共通の運用補助：skills・memory・clarify。connections・delegation・cronjob・computer_use等は無効。CLIとapi-serverの許可リストを明示設定。
- 他Botのプロフィール・登録簿・成果物・バックアップの編集は例外なし。広いAI_knowledge閲覧は付けず、共通rules.mdと自己管理領域・使用skillを運用参照先に設定。
- 設定・認証・権限・道具の変更は自己Bot分も事前承認。通常の自己領域の小規模可逆更新と区別。
- terminalの用途制限はSOUL上の行動ルールであり、Windows ACLやコマンド隔離による強制ではありません。approvals.mode=smartもファイル単位の承認を強制しません。

## 実施した確認

1. CLI設定の読み戻し、３件のCodexログイン状態と実行モデルgpt-6.1-solを確認。
2. 各新規CLIで自己SOUL・共通rules.md・自己登録簿を実際にread_fileし、役割・保存先・禁止事項を正答。全３件で終了コード0。
3. 実際のtool結果にskill_viewがあり、C側shared-skills/yomiyasuのv3.0.0を読めたことを確認。自己申告だけではなく、承認済み試験セッションのtool結果から照合。
4. Desktopの実際の一覧に、小文字のtakina・raven・crownが表示されたことを確認。日本語名・アイコンは未設定。
5. 自己全文写し９ファイルのバイト一致、登録簿・成果物フォルダ・共通索引の３件の行を確認。
6. changelogへ１Bot１行で計３行を追記し、追記直前の全バイトが保存されたことを確認。同時期に追加されたエイダの英語教材の履歴も保持。

## 未確認・後日調整

- Desktop画面の入力欄からの対話と、専門業務の実依頼・成果物保存試験。
- Web検索・本文取得の実依頼での品質。今回はネット検索なしの規則確認のみ。
- yomiyasuの推敲・検査実行。今回はSKILL.md読込だけ。
- 新３プロフィールの記憶が日次バックアップZIPに収録されること。既存ジョブは変更していません。
- takinaの実金融明細を外部モデルへ入力し、詳細結果をDriveへ保存してよい範囲。初期は匿名化資料から相談。
- Obsidianの許可フォルダ、crownの教材フォルダ、専門skill、サービス連携。共有履歴に英語教材の配置記録があっても、この作業でcrownへフォルダ連携は追加していません。
- イヴの旧モデル表記とMuse側スペースBotsの更新は今回の対象外。Muse側への通知・反映は行っていません。

## 控えと戻し方

このフォルダにagents-index.before.md・changelog.before.md・各diff・verification.jsonを保存しました。生の会話本文や金融資料はこの報告に含めていません。

戻す場合は、まず新規３件の利用・実行を止め、今回作成したプロフィールと自己領域だけを対象に、本人の承認後に撤去します。新たな成果物があれば先に退避します。共通索引は差分を逆適用し、その後の他者更新を消さないようにします。changelogは過去行を削除せず訂正を追記します。認証の共有元や既存Bot、共通skill、バックアップ処理には手を付けません。この説明は削除の実行承認ではありません。
