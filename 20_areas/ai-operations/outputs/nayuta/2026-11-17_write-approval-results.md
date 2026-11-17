# 全10 Bot の write_approval 有効化・検証結果

確認日：2026-11-17。本人の今回限りの承認に基づく変更。

## 結論

設定変更、10件のconfig写しと注記、個別登録簿・共通索引・changelogの更新を実施した。
default・crownの新規CLI試験と、crownの実Desktop Bot Chat試験は成功。defaultのDesktop試験だけは入力フォーカスを安定して確保できず、誤送信を避けて送信前で停止したため未確認。

## 設定値の読み戻し

| プロフィール | skills.write_approval | memory.write_approval | config check | config写し |
|---|---|---|---|---|
| default | true | true | 終了0 | 正本とバイト一致 |
| mana | true | true | 終了0 | 正本とバイト一致 |
| arcana | true | true | 終了0 | 正本とバイト一致 |
| label | true | true | 終了0 | 正本とバイト一致 |
| phantom | true | true | 終了0 | 正本とバイト一致 |
| nayuta | true | true | 終了0 | 正本とバイト一致 |
| eve | true | true | 終了0 | 正本とバイト一致 |
| takina | true | true | 終了0 | 正本とバイト一致 |
| raven | true | true | 終了0 | 正本とバイト一致 |
| crown | true | true | 終了0 | 正本とバイト一致 |

各正本のYAML値とCLIの解決値を確認。変更前との構造比較で、設定値の差分は2キーだけだった。モデル、approvals.mode、道具、SOUL、認証、日次バックアップ処理は変更していない。

変更前はこの2キーがファイルに明記されておらず、既定値falseとして解決されていた。今回はtrueを明示した。

## 動作試験と掃除

| Bot | 入力経路 | 対象 | 保留ID | 結果 |
|---|---|---|---|---|
| default | 新規CLI | 記憶追加 | 9375c302 | 保留・一覧表示・reject後の不在を確認 |
| default | 新規CLI | テストスキル作成 | bed9ad68 | 保留・一覧・差分表示・reject後の不在を確認 |
| crown | 新規CLI | 記憶追加 | ce57576d | 保留・一覧表示・reject後の不在を確認 |
| crown | 新規CLI | テストスキル作成 | a5f25dad | 保留・一覧・差分表示・reject後の不在を確認 |
| crown | 実Desktop Bot Chatの入力欄 | 記憶追加 | 60c1f354 | その場承認でなく保留・一覧表示・reject後の不在を確認 |
| default | 実Desktop Bot Chat | 記憶追加 | — | 送信前で停止、未確認 |

- 新規CLIは両Botとも終了コード0。
- 別プロセスから保留を確認した。アプリ再起動は行っていない。
- 一覧・差分・却下には、導入済みの `/memory`・`/skills` と共通の保留サブコマンドハンドラを新規プロセスから使用した。Desktop画面での却下操作の試験ではない。
- テスト5件だけをID指定で却下した。一括rejectやapproveは使用していない。
- 両BotのMEMORY.md・USER.mdの前後ハッシュ一致、テストスキル不在、テスト保留不在を確認。清掃確認時、両Botのmemory・skills保留件数はそれぞれ0だった。
- 通常のテスト会話・セッション記録は残しており、既存会話の削除や私的履歴の調査は行っていない。

## 版依存・表示上の注意

- 実行版はv0.23.2（local ae2a81ccc00e）。依頼文のv0.23.0とは異なる。
- skills.write_approval=trueはスキル管理ツールの書き込みを保留する。
- memory.write_approval=trueは、無人・バックグラウンドでは保留、対話CLIではその場承認となる場合がある。
- crownのDesktop試験では承認ダイアログは出ず、pendingに入った。画面のツール見出しは「メモリに保存しました」と表示されたが、実際の結果と本体ハッシュでは未保存だった。見出しだけで保存済みと判断しないこと。
- 汎用ファイルツールやターミナルによる直接編集は対象外。従来のSOUL上の承認条件を維持する。
- バックグラウンドレビューの実際の自動起動と、アプリ再起動後の保留残存は今回実地試験していない。背景由来の保留分岐とファイル保存方式は実装を確認した。

## 写し・登録簿・履歴

AI_knowledgeを基準に、以下を更新した。

- `99_backup/<各Bot>/config.yaml`：10件。秘密値を検査後に全文コピーし、C側正本とのバイト一致を確認。defaultのフォルダ名は`hermes`。
- `99_backup/<各Bot>/COPY-NOTE.md`：10件。configの更新日とC側正本の注記を追記。他の写しの確認日と区別。
- `20_areas/ai-operations/agents/<各Bot>/profile.md`：10件。設定状態と試験範囲・未確認事項を反映。
- `20_areas/ai-operations/agents/index.md`：設定と試験結果を反映。
- `changelog.md`：1行を末尾追記。追記前のバイト列がそのまま接頭辞として残り、追記以外の変更がないことを確認。

SOUL.md・profile.yamlの写しは今回変更していない。共有README・rules.md・雛形も変更していない。コピー一致は今回のコピー時点の確認であり、将来の常時一致を保証しない。

## 戻し方

必要な対象について、`hermes -p <プロフィール名> config set skills.write_approval false` と `hermes -p <プロフィール名> config set memory.write_approval false` を実行し、読み戻し・設定チェック・写しと記録の更新を行う。既存保留を自動承認・一括削除しない。

## 変更前の控え・検証ログ

ローカルのナユタ専用領域：
`C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\cache\scratch\write-approval-rollout\`

変更前ファイル、各Botの設定チェック・CLI解決値、CLI試験結果、ID指定reject結果、文書差分、コピー照合結果を保存した。scratchは一時保存領域であり、恒久バックアップとは扱わない。共有レポートには秘密値・私的会話本文を含めていない。
