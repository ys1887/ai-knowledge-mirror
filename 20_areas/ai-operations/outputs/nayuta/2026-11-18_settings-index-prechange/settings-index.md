# AI設定の一覧

各AIの現行設定は、agents の各AIのフォルダ内の固定ファイル `settings.md` にまとめます。このファイルは、その入口と比較表です。

| 参加者 | 設定ファイル | 実行場所 | モデル・プロバイダ | 最終確認日 | 状態 |
|---|---|---|---|---|---|
| エイダ | `ada/settings.md`（このフォルダ内） | Muse の VM（Ubuntu）／チャット | Muse Wonder／Muse Power | 2026-11-09 | 記入済み |
| マナ／Hermes Agent | `mana/settings.md`（このフォルダ内） | Windows PC の Hermes Agent（Desktop／Bot Chat、CLI） | `deepseek-v4.1-flash`（opencode-go、API方式 `chat_completions`）※2026-11-18に実設定と照合して修正（暫定の一律設定） | 2026-11-18（モデルのみ。他は2026-11-09） | 記入済み（`mana/settings.md` 本文のモデル欄は未追随） |
| Codex | `codex/settings.md`（このフォルダ内） | 未記入 | 未記入 | 未記入 | 受け皿のみ |
| Claude | `claude/settings.md`（このフォルダ内） | 未記入 | 未記入 | 未記入 | 受け皿のみ |
| Gemini | `gemini/settings.md`（このフォルダ内） | 未記入 | 未記入 | 未記入 | 受け皿のみ |

## 更新ルール

- 各AIは、自分の `settings.md` だけを更新します。直接書けないAIの分は、受け皿（未記入のファイル）を置くところまでを代行できます。内容の記入を代行する場合は、本人の許可を得て、経路と出典を明記して行います。
- `settings.md` は現行設定の要約と正本の所在を書く場所です。実際の設定そのものではありません。内容が実際の設定と食い違う場合は、正本を優先します。
- パスワード、復旧キー、APIキー、トークン、認証ファイルの内容は書かないでください。設定ファイルの写しや抜粋を置く場合も、秘密情報を除いたものだけにします。
- 設定を変更したら、同じ作業の中で `settings.md` の最終確認日と変更履歴も更新します。

## マナ行のモデル修正と残作業（2026-11-18）

- 実物最終確認日：2026-11-18。台帳最終更新日：2026-11-18。本人承認で、上の比較表のマナ行だけを実設定に合わせて修正した。根拠は `C:\Users\nekol\AppData\Local\hermes\config.yaml` と各 `profiles\<slug>\config.yaml` の `model` ブロックの実読み（全10プロフィールが `deepseek-v4.1-flash`／`opencode-go`／`https://opencode.ai/zen/go/v1`／`chat_completions` で一致）。モデル以外の項目は再監査していない。
- 残作業：`mana/settings.md` の「使用モデル」とプロフィール別表のモデル列は2026-11-09時点（`openai/gpt-6-sol`／`nous`）のまま。更新ルール上、自分の `settings.md` は各AIが更新する分担のため、マナ本人の追随待ち。
- この修正は設定そのものを変えるものではない。モデル切替の決定と実行は本人、登録簿（各 `profile.md`・`agents/index.md`・`changelog.md`）への反映はエイダが実施済みで、ナユタは本節と表のマナ行だけを担当した。

## 共通索引基盤：AutoRAG（2026-11-17、試行の記録。同日アンインストール済み）

- 実物最終確認日：2026-11-17。台帳最終更新日：2026-11-17。イヴへMCPを登録して試行したが、同日にアンインストール済みで、現在は全BotともMCP未登録。登録時の形は、connect_timeout=180、readonlyのstatus/searchだけ、固定版 `@autorag/librarian@2.13.12`。以下は試行と閉鎖の記録として残す。
- 設定正本：`C:\Users\nekol\.autorag\config.json`。workspace：`C:\Users\nekol\.autorag\workspace`。その `.autorag\` 配下は、中断時点の測定で12,041ファイル・390,185,799バイト（補助実行ファイル・解析済み文書等を含む未完成領域）。モデル実効先はWindows既定 `C:\Users\nekol\AppData\Local\minsync\models`。Qwen・KUREとも必要ファイルが揃い、手動配置した2ファイルは照合一致を確認した。これらの生成物は同日夜のアンインストールで削除済み（末尾の閉鎖記録を参照）。
- 固定版：`@autorag/librarian@2.13.12`。jikji=false、everything=false、fsearch=false、datasources={}。AI_knowledgeのみ、outputsを含め、99_backup・codex-sessions・メール/カレンダー形式・生成物・過去work・スキルreceived/workを除外。正確なパターン・環境変数は報告書を参照。
- MCP環境変数：AUTORAG_MCP_READ_ONLY=true、AUTORAG_MCP_TOOLS=autorag.status,autorag.search。認証探索分離・npm子プロセス設定も維持。既確認の温キャッシュ一覧14.492秒、説明文検査指摘0、OSVトップレベル版MAL指摘なし。npm非推奨2件だけ記録付き継続を承認。今回再登録はせず、依存全体の安全保証とは扱わない。
- 初回refreshは389.275秒でtarエラー。その後、本人承認でrefresh内のPATHだけを管理npm→管理Node→System32→元PATH残部にして再実行。MinSync 0.7.3導入は成功したが、KURE取得が低速のため本人指定で1,928.681秒（32分8.681秒）で中断。モデル完備後に再実行したところ、ベクトル索引工程まで進んだが、実測50文書・約23.1分という処理速度のため本人指定で25分26秒で中断した。対象11,999件はMinSyncへ渡した文書ファイル数で、約96%が40_archivesと20_areas/ekikyoにあり、全件の索引化は現実的でない。refreshと子は停止済み。進捗JSONはrunning/minsyncのまま残置しており、表示だけで実行中と判断しない。新規イヴCLIのstatus/searchは未実施。
- 今回のKB全体17,868ファイルの前後差分0、新規Jikji map0、読取エラー0。PC共通PATH・親PATH・全10 Bot config・イヴSOUL/profile.yaml・AutoRAG configは不変。config全文写しは正本一致を再確認し、変更がないため写し・注記は再更新不要。記録はKB比較後に更新。直近の再実行の後比較で検出した新規1件・変更1件は、同時刻にエイダが本人の依頼で配置した公用文資料と特定済みで、refreshによる変更ではない。この回の記録反映は、ナユタが停止条件により保留したため、本人の指示でエイダが代行した。追加修復・protoc導入・定期実行・Marketplace一式・setup・Desktopペイン・サービス接続は行わない。
- 閉鎖（2026-11-17）：索引計算の処理速度と、Hermes用プラグイン自体の新しさ（Windowsでの実績の薄さ）から、本人がプラグインを一旦やめることを決め、同日アンインストールした。イヴの登録を削除し（差分はその削除のみ。他9 Botのconfigは不変）、`.autorag` 一式783,778,540バイト、MinSyncのモデル一式1,542,629,656バイト、npxキャッシュ923,103,512バイトと隔離物2件の、合計3,602,425,901バイトを削除した。削除前後のKB全体17,869ファイルは差分0。config全文写しとCOPY-NOTEは登録削除に追随して更新済み。Downloadsに本人が置いたモデル2ファイルは対象外で残置。導入の経緯は報告 `../outputs/nayuta/eve-autorag-introduction.md`、閉鎖の詳細はPC側ナユタのbackups（`eve-autorag-uninstall-20261117-234137/report.md`）を参照。AI_knowledgeの出典付き横断検索という目的自体は、プラグイン抜きの形を後日検討するとして保留する。この記録自体で権限・設定は変わらない。
