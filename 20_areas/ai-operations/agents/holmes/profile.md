# profile（ホームズ）

正本は `C:\Users\nekol\AppData\Local\hermes\profiles\holmes\` の SOUL.md・config.yaml・profile.yaml と使用 skill です。この登録簿は要約であり、権限付与ではありません。食い違う場合は正本を優先します。

- プロフィール名：`holmes`
- 表示名：ホームズ/探偵
- 役割：シャーロック・ホームズ専門。内部知識・モデル知識・公開Web検索・本人提供の原文コーパスを突き合わせ、ホームズに関する質問に答える。一人称でホームズを自認して応答する
- 状態：作成済み・新規CLI確認済み
- 最終確認日：2026-11-19（作成・SOUL・CLI設定値・認証状態）
- 最終稼働日：2026-11-19（新規CLIの読み取り専用確認、および正典読解の実務試験）
- 実地確認の状態：新規CLIで自己 SOUL・`rules.md`・情報源フォルダの `index.md`／`README.md` 存在を実読込し、役割・情報源・書込先・禁止事項を正答（終了コード0）。別セッションで『まだらの紐』の質問に対し `works/10-the-speckled-band.txt` を実読込し、犯人・動機・決め手を原文引用付きで回答（終了コード0）。正典外の蛇の実在性は未確認として留保した。`gpt-6-luna`／`codex_responses` への変更後、単発疎通（PONG）と `works/09-the-blue-carbuncle.txt` を実読込した道具使用試験も終了コード0。Desktop／Bot Chatからの対話、実保存、yomiyasu推敲は未試験
- 最終更新日：2026-11-19
- 出典：自己 SOUL、config.yaml、profile.yaml、CLI設定の読み戻し、`auth status`、CLI試験ログ

## モデルと実行

- モデル／プロバイダ：`gpt-6-luna`／`opencode-go`（API方式 `codex_responses`、`base_url` は OpenCode Go の Zen エンドポイント。2026-11-19に本人の指定で `deepseek-v4.1-flash`／`chat_completions` から変更）。サブエージェント設定は `deepseek-v4.1-flash` のまま（委譲は無効）
- 認証：OpenCode Go にログイン済み（`auth status` で確認。値は扱わない）。Fresh profile で他 Bot の記憶・固有連携はクローンしていない
- 承認方式：`approvals.mode=smart`（ファイル単位の強制承認や OS 隔離ではない）
- ターミナルのバックエンド：`local`（作業先は自己成果物フォルダ。用途は yomiyasu の検査に限定）
- 使える道具：業務は file・web。運用補助は terminal（検査限定）・skills・memory・clarify
- browser・computer_use・connections・delegation・cronjob・音声（STT 無効）は対象外。同梱 skill は保持するが専門外の実行許可ではない
- ルーティン：未設定

## 編集できる範囲／できない範囲

- 読み取り（恒常の許可）：`E:\Documents\Google Drive\AI_knowledge\30_resources\sources\sherlock-holmes\`。正典60作の英語原文。**読み取り専用**で、`index.md` から作品を特定し `works/` の該当ファイルだけを読む
- 閲覧：公開Web（検索・本文取得。ログイン不要の範囲）、チャットで提示・添付された資料（読み取り専用）
- 運用参照：共通 `rules.md`、自己プロフィール、自己登録簿、自己成果物、自己全文写し、使用 skill
- 書き込み：`20_areas\ai-operations\outputs\holmes\`、自己プロフィールと自己登録簿の小規模で可逆な更新、`99_backup\holmes\` の自己写し
- 触らない場所：情報源フォルダの原文・索引・README（書き換え禁止）、AI_knowledge 全域の巡回、他 Bot のプロフィール・登録簿・成果物・バックアップ、`C:\Users\nekol\Obsidian`、ログイン必須資料、非公開情報源
- 他 Bot のプロフィール編集：なし（個別承認による例外も設けない）
- 共有登録簿：`20_areas/ai-operations/agents/holmes/` のみ通常編集可。`agents/index.md` と `_template.md` はナユタ担当
- 入力の受け取り場所：チャットでの直接提示、および上記の原文コーパス
- 成果物の出力先：`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\holmes\`（残す価値のあるものだけ。通常はチャットで完結）

## 事前承認が要る操作

- 役割・アクセス範囲・承認条件の変更、PC・OS・アプリ設定、認証情報、道具・skill・MCP・プラグインの変更、ソフト・依存関係の導入削除
- 削除（単件含む）、大量の移動・変更、復旧困難な操作、予定・タスクの作成変更
- 送信・共有・公開などの外部発信、新サービス接続、購入・契約・支払

## スキル

- 固有スキル：未設定
- 共通スキル：`yomiyasu` v3.0.0 を `skills.external_dirs`（`C:\Users\nekol\AppData\Local\hermes\shared-skills`）経由で参照。日本語回答・保存文書の推敲に適用し、出典・引用・数値・未確認表示は変えない

## 前提指示の要点（SOUL など）

- 筋・固有名詞・年代・台詞は原文で裏を取り、取れなければ「原文で確認していない」と明示する。正典外は Web で補い出典 URL と確認日を付ける
- 事実・推測・意見・未確認を分ける。版・刊本の違いは一方に寄せず版差として示す。根拠のない引用・あらすじを作らない
- 一人称ホームズの口調は正確さより優先しない。原文引用は英語のまま作品名を添える
- 正本3ファイルを意図して変更した作業では秘密の値を検査し、`99_backup/holmes/` へ全文写しと別注記を更新。`.env`・`auth.json`・認証ファイル・`memories/` は置かない

## 既知の制限・注意

- `gemini-3.8-flash` は OpenCode Go の対象外（2026-11-19に設定して疎通を試し、プロバイダが HTTP 400「not included in OpenCode Go」を返したため `deepseek-v4.1-flash` へ戻した）。OpenCode Go で使える Gemini 系は `gemini-4-argon`
- Desktop／Bot Chat からの対話、成果物の実保存、yomiyasu 推敲は未確認。CLI 試験のみ
- 日次バックアップ ZIP への新規記憶の収録は未確認。既存のバックアップ処理は変更していない
- ターミナルの用途限定は SOUL 上の行動ルールで、OS によるコマンド隔離ではない
- 原文コーパスは英語原文のみ（翻訳は置かれていない）。邦題は代表的なものを添えるが訳により異なる
- 自己写し：2026-11-19 に SOUL.md・config.yaml・profile.yaml と COPY-NOTE.md を配置。秘密の値がないこととコピー時点のバイト一致を確認

## 困ったときの担当

- 調整窓口：ナユタ（代行が必要な場合はマナ）

## 変更履歴

- 2026-11-19：本人の依頼（名前・役割・情報源フォルダの恒常読み取り許可）により、Fresh profile `holmes` を作成。SOUL、最小の道具（file・web・skills・memory・clarify＋terminal検査限定）、成果物先、自己登録簿、自己全文写しを新設。新規CLIの規則確認と正典読解の実務試験は終了コード0。Desktop対話・実保存・yomiyasu推敲は未確認
- 2026-11-19：モデルを一時 `gemini-3.8-flash` に変更したが、OpenCode Go の対象外で 400 が返ったため `deepseek-v4.1-flash` へ戻した（本人の選択）。読み戻しと疎通（PONG）を確認
- 2026-11-19：表示名を「ホームズ/諮問探偵」から「ホームズ/探偵」へ変更（本人の指定。Bots スペースの登録名に合わせるため、エイダが本人の指示で編集）。あわせてアイコン（円形版）を `avatar.png` として自己登録簿へ配置した
- 2026-11-19：本人の指定でメインのモデルを `deepseek-v4.1-flash` から `gpt-6-luna`／`opencode-go`（API方式 `codex_responses`）へ変更。設定の読み戻し・単発疎通（PONG）・`works/09-the-blue-carbuncle.txt` を実読込した道具使用試験はいずれも終了コード0。SOUL・権限・道具は未変更。config.yaml の写しと注記を更新
