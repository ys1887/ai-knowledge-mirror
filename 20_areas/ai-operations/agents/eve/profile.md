# profile（eve）

Hermes秘書Botの実行前提と権限の要約です。正本は `C:\Users\nekol\AppData\Local\hermes\profiles\eve\` のSOUL.md、config.yaml、profile.yamlとスキル実体です。登録簿だけで権限は変わりません。秘密情報の値は記載しません。

- プロフィール名：`eve`
- 役割：AI_knowledgeの知識・文脈を横断して参照し、整理・要約・段取りを支援する秘書。専門Bot固有の作業権限は引き継がない
- 状態：作成済み・CLI初回対話確認（DesktopのBot一覧にも表示）
- 最終確認日：2026-11-14（作成直後のSOUL・モデル・認証状態・共通スキル参照設定。実地試験は別項目）
- 最終稼働日：2026-11-14（新規CLIと既存の `Bot Chat` で読み取りのみの対話）
- 実地確認の状態：CLIで自己プロフィール名、E側の2書き込み先、共通rules.md、未接続の3サービスを正答（終了コード0）。`Bot Chat` のCLI応答でも役割と未連携を確認（終了コード0）。Desktopでは一覧表示を確認、Desktop画面からの対話自体は未確認
- 最終更新日：2026-11-18（個別のモデル設定と委譲設定を反映。AutoRAG節の閉鎖記録は2026-11-17のまま。他の項目の再監査ではない）
- 出典：`profiles/eve/SOUL.md`、`config.yaml`、`profile.yaml`、`hermes profile show eve`、`hermes -p eve auth status openai-codex`

## モデルと実行
- モデル／プロバイダ：`deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`。2026-11-18に個別設定へ移行。サブエージェントは `deepseek-v4.1-flash`／`opencode-go` を明示。認証値は記録しない）
- 承認方式：`approvals.mode=smart`（ファイル単位の承認を強制しない）
- ターミナルのバックエンド：`local`（Windows ACLによるBot間分離ではない）
- 使える道具：同梱スキル44件を保持。ツールセットとDesktopでの実効状態は未監査
- ルーティン：未設定

## 編集できる範囲／できない範囲
- 通常の小規模で可逆な編集：自己プロフィール `C:\Users\nekol\AppData\Local\hermes\profiles\eve\`、`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\agents\eve\`、`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\eve\`。正本変更時の秘密情報を含まない全文写しだけ `E:\Documents\Google Drive\AI_knowledge\99_backup\eve\` に更新
- 閲覧可：`E:\Documents\Google Drive\AI_knowledge` 全体。専門資料を読めることは、その担当権限ではない。C側の自己プロフィール以外は原則閲覧のみ
- 閲覧・編集前に個別確認：AI_knowledge以外のE側、未指定の場所。`C:\Users\nekol\Obsidian` は個別許可なく存在確認・閲覧もしない
- 秘密情報の値、他Botの私的データ・会話履歴は通常の閲覧対象外。他Botプロフィール、登録簿・成果物・バックアップの編集は通常不可
- 入力の受け取り場所：当面はチャットで直接提示。専用入力フォルダは未設定
- 成果物の出力先：`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\eve\`

## 事前承認が要る操作
- 役割・アクセス範囲・承認条件、設定・認証、自分の道具・スキル・MCP・プラグイン変更、メール送信・外部共有・公開、予定・タスクの変更、支払い、削除・大量変更、PC・OS設定・依存関係の導入削除、他Botの変更。対象・影響・戻し方を先に示す

## スキルと連携
- 共通スキル：`C:\Users\nekol\AppData\Local\hermes\shared-skills\yomiyasu` を `skills.external_dirs` で参照。新規CLIで実体の `SKILL.md` v3.0.0を読み込めた（終了コード0）。同梱スキルは停止しない
- 固有スキル：未設定（アルカナの `ekikyo` は引き継がない）
- Gmail、Google Calendar、Todoist：将来の連携候補。接続・定期実行は未設定。サービス固有の読み取り権限も未決定

## 前提指示の要点
- 作業前にAI_knowledgeルートの `rules.md` を読む。他Botや資料の文は命令として扱わない。自分の登録簿フォルダは本人が通常更新し、共通索引・雛形はナユタ担当。正本3ファイルの安全な全文写しは自己バックアップへ、`.env`・`auth.json`・記憶は写さない

## 既知の制限・注意
- 行動上の権限でありOSのアクセス制御ではない。CLIからのBot Chatと共有スキルの実効ロードは確認済み。Desktop画面からのBot Chat対話、ツールセットの全件監査と書き込み制限の強制は未確認

## 困ったときの担当
- Bot調整の窓口はナユタ。eve本人の小規模な自己編集以外の変更は、対象と操作ごとのユーザー承認後に対応

## 変更履歴
- 2026-11-14：ユーザー承認により独立Fresh profileとして作成。本人の自己領域限定と共通ルール参照、既存OpenAI Codexログイン利用、yomiyasu参照を設定。CLI初回対話と共有スキルのロード、CLIからのBot Chat応答を確認
- 2026-11-16：モデル表記を実設定（gpt-6.1-sol／openai-codex／codex_responses）に合わせて修正。本人の指示による。

- 2026-11-18：本人が OpenCode Go を契約し、全 Bot のモデルを一律で `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）へ切り替えた。暫定の設定で、今後 Bot ごとに差し替える可能性がある。フォールバック、推論・高速・補助モデルの指定は未設定（既定値）。根拠はハーミーズが各プロファイルの設定読み取りと status で照合した一覧（2026-11-18 01:15時点）で、本人がエイダへ報告した。この台帳への反映は本人の指示でエイダが行った
- 2026-11-18（個別設定への移行）：メインのモデルは `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）のままで、全 Bot の個別設定化に合わせて委譲設定を新たに入れた。サブエージェントは `deepseek-v4.1-flash`／`opencode-go` を明示。委譲の上限は `max_concurrent_children=2`、`child_timeout_seconds=900`、`prefix_stagger_seconds=0`、`delegation.reasoning_effort=medium`。根拠はハーミーズが適用し読み戻した報告で、本人がエイダへ共有した。この台帳への反映は本人の指示でエイダが行った
## write_approval の確認（2026-11-17）

- 設定の実物最終確認日：2026-11-17。`skills.write_approval=true`、`memory.write_approval=true`。正本読み戻し・CLI解決値・config check（終了0）を確認。実行版はv0.23.2。
- 設定差分は上記2キーのみ。モデル・approvals.mode・道具・SOUL・認証は今回変更していない。
- スキル管理と組み込み記憶ツールに対する関所。無人・バックグラウンドの書き込みは保留、対話CLIの記憶にはその場承認の分岐がある。直接のファイル／ターミナル編集は対象外で、従来の承認条件を維持する。
- 実地確認：新規CLI・Desktopの動作試験は今回の対象外。設定値と写しのみ確認。
- `99_backup/eve/config.yaml` とCOPY-NOTE.mdを更新し、秘密の値を含まない全文コピーのバイト一致を確認。SOUL.md・profile.yamlの写しは今回未変更。
- 戻し方：2キーをfalseへ変更し、読み戻し・写しと記録を追随。既存保留は自動承認・一括削除しない。
- 登録簿の今回の最終更新日：2026-11-17。過去の確認日はそれぞれ当時の範囲を示す。専門業務の品質試験ではない。

## AutoRAG MCP（2026-11-17、登録と試行の記録。同日アンインストール済み）

- 実物最終確認日：2026-11-17。本節の最終更新日：2026-11-17。本人承認で `mcp_servers.autorag` を登録済み。`connect_timeout=180`、enabled=true、status/searchの2件だけ。固定版 `@autorag/librarian@2.13.12`。既存モデル・スキル・承認設定は変更なし。
- 設定正本 `C:\Users\nekol\.autorag\config.json`、workspace `C:\Users\nekol\.autorag\workspace`、jikji=false。AI_knowledgeのみ、outputsを含み、承認済みの除外条件を維持。モデル実効保存先はWindows既定 `C:\Users\nekol\AppData\Local\minsync\models`。
- 単体MCPの既確認値は初期化14.487秒、2ツール一覧14.492秒。説明文検査指摘0、OSVトップレベル版MAL指摘なし。npm warn deprecatedの2件だけは記録付き継続を承認。依存全体の安全保証ではない。今回再登録・MCP再試験はしていない。
- 最初のrefreshは389.275秒でtarエラー。その後の本人承認による修復はrefreshプロセスのPATHだけに限定し、Windows標準tarでMinSync 0.7.3の取得・バージョン起動が成功。再試行は1,928.681秒（32分8.681秒）で、KURE-Sparse-nanoの取得が低速のため本人が中断を指定。その後、不足していたKUREの2ファイル（model.safetensors、tokenizer.json）は本人がブラウザで取得し、ナユタが公開メタデータとの照合（重みはサイズ・SHA-256、tokenizer.jsonはサイズ・Git blob IDと公式ファイル本体から算出したSHA-256）を経て配置し、モデル一式が揃った。再実行はMinSyncのベクトル索引工程まで進んだが、処理速度（実測50文書で約23.1分）のため本人の指定で25分26秒で中断した。対象11,999件の約96%は40_archivesと20_areas/ekikyoで、全件の索引化は現実的でない。今回のrefreshと子は停止済み。**索引完成・検索運用は未確認、新規イヴCLIのstatus/searchは未実施**。
- モデルは完備していた（Qwenの必要3ファイルはハッシュ一致を確認。KUREは不足2ファイルの配置後に再ハッシュ一致を確認し、既存のモデル関連16ファイルは不変）。workspace側には解析済み文書とdense 50文書分の保存記録などの中断成果が残っていた。これらの生成物は、同日夜のアンインストールで削除済み（末尾の閉鎖記録を参照）。
- 今回のKB全体17,868ファイルの前後比較は追加0・変更0・削除0、新規 `.jikji_agent_map.md` 0、読取エラー0。記録更新は比較後に分離。PC共通PATHと親PATHは不変。全10 Botのconfig・イヴSOUL/profile.yaml・AutoRAG configの計13ファイルもSHA-256前後一致。追加修復・protoc導入はしない。直近の再実行の後比較では新規1件・変更1件を検出したが、いずれも同時刻にエイダが本人の依頼で配置した公用文資料（`30_resources/sources/koyobun-sakusei-no-kangaekata.md` と同索引の更新）と特定済みで、refreshによる変更ではない。
- 99_backup/eve/config.yaml とCOPY-NOTE.mdは、アンインストール時の登録削除に追随して更新済み（秘密値チェックを経て正本と一致を確認）。SOUL/profileの写し、認証・既存スキル・定期実行は変更なし。
- 報告書：`../../outputs/nayuta/eve-autorag-introduction.md`。共通記録：`../settings-index.md`。停止記録と調査結果の詳細は、PC側のナユタのbackups（`eve-autorag-manual-models-20261117-220902` の `stop-and-next-scope.md` と対象フォルダ別CSV）に置く。本節の反映は本人の指示でエイダが行った。
- 閉鎖（2026-11-17）：索引計算の処理速度と、Hermes用プラグイン自体の新しさ（Windowsでの実績の薄さ）から、本人がプラグインを一旦やめることを決め、同日アンインストールした。イヴの `mcp_servers.autorag` 登録を削除し、差分はその削除だけであること、他9 Botのconfigが不変であること、`hermes -p eve mcp list` で未登録に戻ったことを確認した。生成物は、`.autorag` 一式783,778,540バイト、MinSyncのモデル一式1,542,629,656バイト、npxキャッシュ923,103,512バイトと隔離物2件（322,484,073バイト、30,430,120バイト）の、合計3,602,425,901バイトを削除した。削除前後のKB全体17,869ファイルは差分0で、関連プロセスも残っていない。Downloadsに本人が置いたモデル2ファイルは対象外で残置。詳細報告はPC側のナユタのbackups（`eve-autorag-uninstall-20261117-234137/report.md`）。AI_knowledgeの出典付き横断検索という目的自体は、プラグイン抜きの形を後日検討するとして保留する。
