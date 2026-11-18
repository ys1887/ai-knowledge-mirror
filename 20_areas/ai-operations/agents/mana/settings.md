# settings（マナ／Hermes Agent）

このファイルは現行設定の相談用要約です。設定の正本ではありません。食い違う場合は、Hermes本体の各プロフィール設定・SOUL・実際のスキル配置を優先してください。秘密情報の値は含めません。

- 状態：記入済み（確認範囲は下記。全権限の監査ではありません）
- 最終確認日：2026-11-13（SOUL・記憶・スキル参照先・成果物先の実物と照合。モデル・道具・承認方式の再監査および新規セッション試験は未実施）
- 最終確認日（2026-11-18に照合した分）：使用モデル・プロバイダ／契約、バージョン、承認方式（`approvals.mode`・`skills.write_approval`・`terminal.backend`）のみ、10プロフィールの実設定と照合した。上記2026-11-13の確認範囲、表の道具数・役割・スキル欄は再監査していない。
- 記入者：マナ（Hermes Agent）
- 正本の場所：`C:\Users\nekol\AppData\Local\hermes\` と各 `profiles\<名前>\`、共通スキルの実働コピーは `C:\Users\nekol\AppData\Local\hermes\shared-skills\`、保管用原本は `E:\Documents\Google Drive\AI_knowledge\30_resources\skills\yomiyasu\`
- 対象範囲：この文書の詳細表はマナ、デフォルトHermes、アルカナ、レーベル、ファントムの作成当初の記録。2026-11-11に `nayuta` を新設した。ナユタの現行設定は `20_areas/ai-operations/agents/nayuta/profile.md` と実際の `profiles/nayuta/` を参照（下記の追加記録）。ユーザーによれば、主に使用中なのはマナ・アルカナ・デフォルトHermes。レーベルとファントムは作成済みで運用前。

- 現行参照（過去の追加記録・変更履歴とは別）：自己の登録簿は `20_areas/ai-operations/agents/mana/profile.md`、ナユタの登録簿は `20_areas/ai-operations/agents/nayuta/profile.md`。Bot共通索引・雛形の通常更新はナユタ主担当。共通スキルはC側実働コピーを参照し、出力先は各Botの現行SOUL・スキル・登録簿を優先する。

## 基本

- 実行場所・入口：このWindows PCのHermes Agent Desktop／Bot ChatおよびHermes CLI。CLIでは `hermes -p <プロフィール名> ...` と指定できる。Botごとの設定・会話・記憶・スキルはプロフィール別に管理される。
- 役割：マナはPCの設定確認・調査・トラブル切り分け・許可範囲でのファイル作業と開発。ほかの役割は下表と各 `SOUL.md` を参照。
- 使用モデル：2026-11-18時点で全10プロフィール `deepseek-v4.1-flash`（API方式 `chat_completions`）。本人が OpenCode Go を契約して一律に切り替えた暫定の設定で、今後 Bot ごとに差し替える可能性がある。フォールバックや推論・高速・補助モデルの指定は未確認（既定値のまま）。
- プロバイダ・契約：`hermes -p <名前> config get model.provider` で全10プロフィールが `opencode-go`、`model.base_url` は `https://opencode.ai/zen/go/v1`（2026-11-18確認）。契約条件・請求先・利用上限の実態はこの確認では検証していない。
- バージョン：2026-11-18の `hermes --version` 表示は `Hermes Agent v0.23.2 (2026.9.24) · stable · local ae2a81ccc00e`。以前の記録は v0.22.5 で、その後の更新の実施者・日時はこの確認では特定していない。

## プロフィール別

| プロフィール | モデル | 役割 | スキル | 道具 | 承認方式 | 最終確認日 |
|---|---|---|---|---|---|---|
| default | `deepseek-v4.1-flash` (`opencode-go`) | 汎用Hermes Agent | 固有スキルと共通 `yomiyasu` | 有効17/27ツールセット。詳細は `tools list` | `smart` | 2026-11-09 |
| mana | `deepseek-v4.1-flash` (`opencode-go`) | Windows PC担当のエンジニアBot | 固有スキルと共通 `yomiyasu` | 有効17/27ツールセット。詳細は `tools list` | `smart` | 2026-11-09 |
| arcana | `deepseek-v4.1-flash` (`opencode-go`) | 易経・高島易断の読み解き | 固有スキルと共通 `yomiyasu` | 有効3/27：ファイル操作・スキル・ターミナル | `smart` | 2026-11-09 |
| label | `deepseek-v4.1-flash` (`opencode-go`) | 公用文・公式文書の作成と推敲 | 固有スキルと共通 `yomiyasu` | 有効17/27ツールセット。詳細は `tools list` | `smart` | 2026-11-09 |
| phantom | `deepseek-v4.1-flash` (`opencode-go`) | 小説など創作物語の執筆 | 固有スキルと共通 `yomiyasu` | 有効17/27ツールセット。詳細は `tools list` | `smart` | 2026-11-09 |

表の道具数は `hermes -p <名前> tools --summary` のCLI欄。Desktop、Bot Chatなどの実効権限や接続状況を一括で示すものではない。レーベルとファントムの共通スキル利用は一覧上の有効表示を確認したが、各Botでの文章推敲の実行試験はまだ行っていない。

表の対象は作成当初の5プロフィールのままで、表の行の最終確認日「2026-11-09」はモデル以外の欄（役割・スキル・道具）の確認日です。モデル欄だけは2026-11-18に実設定と照合し直しました（CLIの `hermes -p <名前> config get model.default`／`model.provider`／`model.base_url`／`model.api_mode` で、default・mana・arcana・label・phantom に加え nayuta・crown・eve・raven・takina の全10プロフィールが一致）。

## スキルと道具

- 有効なスキル：各プロフィールの固有スキルに加え、5プロフィールとも `yomiyasu` を参照可能。これは依頼時に読み込む日本語推敲スキルであり、共有しただけで全会話へ常時適用されるものではない。全スキルの名称・有効状態は `hermes -p <名前> skills list --enabled-only` で確認する。
- スキルの置き場：デフォルトHermesの固有スキルは `C:\Users\nekol\AppData\Local\hermes\skills\`、名前付きBotの固有スキルは `C:\Users\nekol\AppData\Local\hermes\profiles\<名前>\skills\`。プロフィール固有の同名スキルは共通外部スキルより優先される。
- 共通スキルの現行参照先：6プロフィール（default、mana、arcana、label、phantom、nayuta）は `skills.external_dirs` で `C:\Users\nekol\AppData\Local\hermes\shared-skills\` の実働コピーを参照する。保管用原本は `E:\Documents\Google Drive\AI_knowledge\30_resources\skills\yomiyasu\`。プロフィール固有の同名版があればそちらが優先される。以前のE側参照・旧版の架空文試験およびスキャナー判定 `CAUTION` は現行版の新規セッション試験結果ではない。
- 使える道具・接続：`hermes -p <名前> tools list --platform cli` でCLIの個別状態を確認できる。今回の表はCLI欄のみ。MCP、プラグイン、外部アプリ接続、Desktop／Bot Chatの実効状態は個別監査していない。スキルの共有はファイルアクセス権やサービス認証の共有を意味しない。

## 権限と承認

- アクセス範囲：BotごとのSOUL、適用される上位指示、ユーザーの個別承認に依存する。マナは `C:\Users\nekol\Obsidian` を個別許可なく閲覧・存在確認しない。Cドライブは原則閲覧のみ。`C:\Users\nekol\AppData\Local\hermes` 内では、マナは自己プロフィールの通常の小規模で可逆な編集ができる。他Botのプロフィールは必要に応じて調査できるが、通常の横断編集は行わない。調整Botが対応できない等の例外時は、対象と操作ごとのユーザーの事前承認を得て対応する。Hermes（デフォルト）も他Botのプロフィールを通常編集せず、対象と操作ごとの個別事前承認が必要。arcana・label・phantom も自己プロフィールのみ通常編集できる。全Botとも役割・アクセス範囲・承認条件の変更、アプリ設定（config.yaml等）、認証情報、大量移動・削除、復旧困難な操作は事前承認が必要。Eドライブではマナの `E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\mana` を成果物の原則保存先・通常の小規模な作業範囲とし、`E:\Documents\Muse` と `E:\Documents\Playground` は閲覧のみ。`E:\Documents\Google Drive\AI_knowledge` は閲覧可。マナが通常編集できるのは `20_areas/ai-operations/logs/mana`、`20_areas/ai-operations/agents/mana` 内と、`20_areas/ai-operations/agents/_template.md`（ナユタが対応できない場合のみ代行）を対象とする。`20_areas/ai-operations/agents/index.md` はナユタが主担当で、ナユタが対応できない場合に限りマナが代行する。他Botの登録簿フォルダは閲覧のみ。各Botは自分の登録簿フォルダのみ通常編集できる。登録簿への記載自体は権限変更の承認にならない。`C:\Users\nekol\scripts`（実行用）・`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\scripts`（保管用）・`E:\Documents\Google Drive\AI_knowledge\30_resources\skills`（スキル原本）、およびバックアップ先へのアクセスは作業ごとの許可に従い、その他のEの場所は事前確認する。旧 `E:\Documents\Hermes Agent` は今後の作業範囲・出力先ではない。新Botは作成時に自己領域と自己登録簿フォルダの規則を個別に設定・確認する。これは行動上のルールでありOS権限の分離ではない。
- 承認方式：2026-11-18時点で全10プロフィールの `approvals.mode=smart`、`skills.write_approval=true`、`terminal.backend=local`（`hermes -p <名前> config get` で確認）。この値だけで全操作の許可を表すわけではない。マナはPC・アプリ設定変更、依存関係の導入・削除、重大な削除・移動、外部公開などについて内容・影響・戻し方を示して事前承認を得る。指示上のアクセス制限はWindowsのアクセス制御（ACL）と同一ではない。以前の記録の `skills.write_approval=false` は実設定と一致していなかった（2026-11-18に修正）。
- データの扱い：認証情報の値はこの共有フォルダに記載しない。`yomiyasu_check.py` の記録には原文・最終稿の写しが残り得るため、実行時に保存先と機密性を確認する。AI_knowledgeの記載は情報共有であり、設定変更の許可にならない。

## 設定ファイル

- 正本：デフォルトは `C:\Users\nekol\AppData\Local\hermes\config.yaml` と `SOUL.md`、名前付きBotは同ディレクトリの `profiles\<名前>\config.yaml` と `SOUL.md`。有効スキルの実体は各 `skills\` と上記共通フォルダ。会話・記憶などもプロフィール別。CLIで設定先を見るには `hermes -p <名前> config path`。
- 写し・抜粋を置く場合の範囲：このファイルは構成の概要と正本のパスだけを記録する。`.env`、`auth.json` の内容、APIキー、トークン、パスワード、復旧キー、個人の会話本文を複製しない。
- 読み取り確認例（WindowsのPowerShellまたはコマンドプロンプト）：

```text
hermes profile list
hermes -p mana config path
hermes -p mana skills list --enabled-only
hermes -p mana config get skills.external_dirs
hermes -p mana tools list --platform cli
hermes -p mana config get approvals.mode
```

`mana` は確認したいプロフィール名へ置き換える。`config.yaml` を変更する場合は手編集ではなくHermesの設定コマンドを用い、事前承認を得る。

## 追加記録（ナユタ）

- 2026-11-11：ユーザーの承認に基づきBot作成・調整担当 `nayuta` をFresh profileで新設。既存Botの権限調整と新Bot作成は、ユーザーと対象・範囲・影響・戻し方を相談し、対象と操作ごとの事前承認後に反映する。自己プロフィールと `bots/nayuta/` の通常の小規模編集を許し、`E:\Documents\AI\outputs\nayuta` を成果物先として新設。他Botプロフィール・登録簿の通常の横断編集権限は与えていない。登録簿共通索引・雛形はマナ担当を継続し、レーベルの役割変更は保留。
- CLIで `openai/gpt-6-sol`（nous）、`approvals.mode=smart`、`skills.write_approval=false`、`terminal.backend=local`、17/27ツールセットを確認。マナのCLIと有効ツールセットが同じ。`skills.external_dirs=[]` で共通 `yomiyasu` は追加していない。Fresh profileの `.env` は初期化されたが、ルートOAuthやシェル由来の認証を利用し得る。認証値は確認・記載していない。
- CLIの読み取り専用の初回対話で、ナユタが自分の役割と既存Bot変更前の承認条件を説明できた。Bot Chat、実際の権限調整の反映、Desktopでの実効道具は未試験。正本は `C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\`、登録簿は `bots/nayuta/profile.md` と `bots/index.md`。
- 共有知識の構成変更に関する担当者への引き継ぎ：`bots/nayuta/` と `bots/nayuta/profile.md` を新設した。ルートREADMEの構成例と `common/changelog.md` の追記が必要か、各担当者が現行ルールに従って判断・反映してほしい。マナは両ファイルを編集していない。

## 変更履歴

- 2026-11-18：本人の指示により、モデル欄だけを実設定に合わせて更新。使用モデル・プロバイダ／契約の行と、プロフィール別表5行のモデル欄を `deepseek-v4.1-flash`／`opencode-go`（base_url `https://opencode.ai/zen/go/v1`、API方式 `chat_completions`）に修正し、モデル分の確認日を2026-11-18として他の確認日と分けて記載。同じ回に実設定で確認できたバージョン（v0.22.5→v0.23.2）と `skills.write_approval`（false→true）も修正。設定そのものは変更しておらず、モデル変更に伴う挙動の比較試験は行っていない。
- 2026-11-11：Bot作成・調整担当 `nayuta` を新設。承認後の新Bot作成・既存Botの権限調整をSOULに設定し、CLI対話で承認条件を試験。登録簿に記録。既存5プロフィールや共通索引担当は変更していない。
- 2026-11-11：後続の本人決定に合わせて現行アクセス範囲を修正。マナとデフォルトHermesの通常の横断編集を外し、マナは例外時のみ個別事前承認で対応。各Botの自己登録簿フォルダ編集と、マナによる共通索引・雛形の暫定担当を反映。旧決定は下記に履歴として残す。SOULと登録簿の権限記述を照合し、モデル・道具は再検証していない。
- 2026-11-11：利用者の承認で一律事前承認の編集規則を変更。arcana・label・phantom は自己プロフィールの通常の小規模で可逆な編集のみを自律的に実施し、Hermes（デフォルト）とマナは他Botプロフィールを横断して通常編集できる。役割・アクセス範囲・承認条件、アプリ設定、認証情報、大量移動・削除、復旧困難な操作は全Botで事前承認。新規Botには作成時に自己領域限定ルールを個別に適用・確認する必要があり、自動継承はしない。各SOULとマナのUSER.md・MEMORY.mdを更新。Windows ACLやHermesの承認設定は変更していない。
- 2026-11-11：Hermes（デフォルト）・mana・arcana・label・phantom の各SOULに、Hermes関連ファイルの意図的な編集は自身・他Botを問わず対象・内容・影響・戻し方を示し、その作業へのユーザー許可を得てから行う規則を追加（上記の後続決定により置換済み）。マナのUSER.md・MEMORY.mdにも整合する記載を反映。OSのアクセス制御や `approvals.mode` は変更していない。

- 2026-11-09：エイダが受け皿を作成。
- 2026-11-09：マナが5プロフィールのモデル・役割の根拠、CLI道具概要、承認設定、共通スキル参照を再確認し、相談用要約として記入。状態を「記入済み」、最終確認日を同日に更新。
- 2026-11-09：共通 `yomiyasu` を `E:\Documents\AI\skills\yomiyasu` にコピーし、5プロフィールの外部スキル参照を新パスへ変更。Hermes日次バックアップのスクリプトとログを `E:\Documents\AI\scripts` に置き、完成ZIPの保存先を `Z:\HermesBackup` に変更。タスクの起動パスを切り替えて手動起動結果0を確認。旧フォルダは削除していない。
- 2026-11-11：マナの成果物の原則保存先は `E:\Documents\AI\outputs\mana`、アルカナの `ekikyo` スキルの出力先は `E:\Documents\AI\outputs\arcana` に更新済み。現行の `Hermes-Agent-Full-Backup` タスクは `E:\Documents\AI\scripts\hermes-backup-daily.py` を毎日12:15に起動する設定。ZIPは `E:\Documents\Backup\Hermes Agent` で作成・検証し、`Z:\HermesBackup` に同一内容を公開する。双方確認後、前日の日付の完成ZIPが両側に一組だけあり同一ならその組だけを削除する。前日分がない、複数または不一致なら削除しない。`--keep 0` を維持し、それ以前のZIPや `.partial` を一括整理しない。同日02:13の手動実行でE/Zへの同名・同サイズ・SHA-256一致を確認したが、次回の定刻自動実行や復元試験は未確認。旧 `E:\Documents\Hermes Agent` は現行のタスク・スキル・成果物出力先ではなく、利用者が残存物の削除可否を判断中。
- 2026-11-12：AI_knowledge 再編に伴い、この settings.md を `40_exchange/mana/` から `20_agents/mana/` へ移設し、本文中の現行パス表記を新パスへ更新しました（実施はエイダ、ユーザーの指示による）。Hermes 側の SOUL 等にある旧パスの参照は、引き渡し文に基づき Hermes 側で更新します。
- 2026-11-13：本人承認により現行説明のSOUL・記憶・共通スキル・成果物・スクリプト参照先を実物に合わせた。過去の決定・変更履歴は維持。新規セッション試験は別途実施。
