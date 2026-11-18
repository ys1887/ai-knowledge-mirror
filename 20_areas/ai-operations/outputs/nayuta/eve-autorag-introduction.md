# イヴへのAutoRAG導入結果：MCP登録済み・モデル取得中断で索引未完成

## 最新の結果：プロセス限定PATH修復後、本人指定で中断（2026-11-17）

実施・実物確認・本節更新：ナユタ、2026-11-17。**Windows標準tarによるMinSync導入は成功しました。ただしKURE-Sparse-nanoの取得が低速で、本人が「中断し、KB後比較と停止記録まで行う」を選択。今回のrefreshと子プロセスを停止しました。索引完成・検索運用成功とは扱いません。** 新規イヴCLIのstatus/searchは未実施です。以下の旧停止節は履歴であり、現況は本節を優先します。

### 今回の実施範囲と不変確認

- refresh子プロセスの環境辞書だけを変更し、管理npm → 管理Node → `C:/Windows/System32` → 元PATHの残部、の順で起動。Windows標準 `tar.exe` を選ぶ修復です。GNU tarがWindowsドライブ表記をリモートと誤解釈すること、Windows標準tarではZIP展開が通ることを事前の小規模試験で確認済みです。
- PC共通のユーザー/マシンPATHはレジストリ値の前後一致。親プロセスPATHも不変。イヴを含む全10 Botのconfig・イヴSOUL・profile.yaml・AutoRAG configの計13ファイルはSHA-256前後一致。MCP登録・固定版2.13.12・既存設定は変更していません。
- `protoc`導入、追加修復、AutoRAGコード変更、再登録、定期実行、Marketplace一式・setupスキルの導入は行っていません。今回の設定変更がないため、既存のイヴconfig全文写しと注記は更新不要。正本と写しは今回もバイト一致を確認しました。

### 実測結果（いずれも中断時点）

| 項目 | 結果 |
|---|---|
| refresh本体 | 19:46:24.935開始 → 20:18:33.616中断（日本時間）。1,928.681秒＝32分8.681秒。本人指定による停止後の終了コード1であり、自然な失敗終了や成功構築時間ではない |
| MinSync | workspace/.autorag/bin/minsync.exeを取得。`--version`は終了0、`minsync 0.7.3`。225,686,528バイト |
| workspace配下.autorag全体 | 12,041ファイル・390,185,799バイト（372.11 MiB）。補助実行ファイル・解析済み文書・進捗等を含む未完成領域であり、完成した検索索引の容量ではない |
| 内訳の主要部分 | parsed領域164,311,025バイト、minsync領域180,690バイト。MinSync工程で中断し、完成したベクトル索引は未確認 |
| モデル全体 | Windows既定C:/Users/nekol/AppData/Local/minsync/models、16ファイル・1,242,780,021バイト。Qwen領域1,203,010,888バイト、KURE領域39,769,133バイト |
| 未完了の取得物 | KURE-Sparse-nanoのmodel重みの.partが39,037,678バイト。削除・移動・手動導入はせず残置。Qwen側には.partを検出せず |
| KB全体の前後比較 | 除外部分も含む17,868ファイル・363,618,330バイト。追加/変更/削除0、ディレクトリ追加削除0、リンク差分なし、読取エラー0、新規.jikji_agent_map.md 0 |
| 停止確認 | refresh本体と子を終了。対象のrefresh用node/MinSync残存プロセスは検出なし。比較ラッパーもKB後比較後に終了1 |
| 未確認 | 索引の完成・完成時容量・成功refresh時間、新規イヴCLIのstatus/出典付きsearch、本人の横断実質問。いずれも成功扱いにしない |

全通常ファイルの相対パス・サイズ・SHA-256、ディレクトリ、リンクを比較しました。最終状態の比較であり、一時的な書込みを完全に否定する監視ではありません。報告書・イヴ台帳・共通台帳・changelogの4件の意図した記録更新は、このKB比較の後に分離して行います。

### 再開・戻し方・PC復旧時の注意

- 中断時のrefresh-progress.jsonはstate=running、phase=minsync、pid=24204のまま残っています。そのPIDの処理は停止済みです。進捗ファイルを手修正せず残したため、表示だけで現在も処理中と判断しないでください。
- 取得遅延の原因は未特定です。追加のネットワーク修復、モデル差替え、別保存先への誘導、生成物削除は行いません。再開は別途相談・承認後に、同じ固定設定とKB全体の新しい前後比較を伴って行います。モデル取得・索引構築が完了するまでは検索運用を開始しません。
- 実行コマンドは履歴節と同じ `npx -y -p @autorag/librarian@2.13.12 autorag lite refresh --config C:/Users/nekol/.autorag/config.json --method parsed,minsync`。再試行時もrefresh環境内だけで管理npm/NodeとWindows標準tarを選び、PC共通PATHや登録済みMCPを変更しない方針です。
- 今回のPATH修復はプロセス終了で消滅するため永続PATHの復元操作は不要。Bot側の取消しは別途承認でイヴのautorag登録だけを外します。.autorag・モデル・隔離npmキャッシュ・部分ファイルの削除は別途判断します。
- PC復旧時はイヴの正本/安全な全文写しと、下の履歴にあるAutoRAG設定全文・固定版・除外条件を使って復旧します。homeはC:/Users/nekol/.autorag、workspaceはそのworkspace、モデルはWindows既定のLocal/minsync/modelsです。索引・モデルはHermes日次バックアップの対象外で、再取得・再構築が必要です。今回の部分成果を完成済みバックアップと扱わず、初回同様のKB比較と新規イヴCLI試験を伴わせます。

今回の変更前控え・証拠：`C:/Users/nekol/AppData/Local/hermes/profiles/nayuta/backups/eve-autorag-native-tar-20261117-1941`。before-state.json、registry-path-before.json、refresh-wrapper.before.py、refresh-start.json、refresh-result.json、refresh-stdout.log、refresh-stderr.log、minsync-version.json、user-requested-stop.json、protected-after.json、stop-verification.json、interrupted-progress-fields.json、kb-before-refresh.json、kb-after-refresh.json、kb-refresh-comparison.json、stop-records-beforeを保存。既定保存先・固定設定・登録コマンドの全文は以下の履歴から引き継ぎます。秘密情報の値・会話本文は共有記録に載せません。

---

## 18:53時点の結果（履歴：初回refresh失敗）

**当時はイヴのMCP登録と2ツール検出に成功し、初回refreshはMinSync導入時に失敗。** 以下はその時点の保存先・未取得表記を含む履歴であり、現在の取得状況は冒頭の最新節を参照してください。

### 実測とKB比較

| 項目 | 今回の実測・結果 |
|---|---|
| 再取得を伴う起動 | 初期化79.232秒。その後の計測コードのSDK項目名不一致で一覧計測前に終了。計測側だけを修正 |
| 完成キャッシュでの単体起動 | 初期化14.487秒、ツール一覧14.492秒。autorag-lite 2.13.12、プロトコル2025-11-25 |
| ツール | autorag.status / autorag.searchの2件のみ、read-only hintあり、説明文検査指摘0 |
| イヴ登録 | --connect-timeout 180を追加して成功、2/2有効、終了0。config読み戻し確認 |
| 初回refresh | 18:47:23.914開始、18:53:53.189終了（日本時間）。389.275秒＝6分29.275秒、終了1。失敗までの時間であり成功構築時間ではない |
| 索引予定領域 | workspace配下の.autoragは3ファイル・309バイト。失敗進捗309バイトと空Cargo管理ファイル2件だけで、利用可能な索引ではない |
| AutoRAG home全体 | 4ファイル・1,175バイト（設定866バイトを含む） |
| モデル | Windows既定予定先は未作成・未取得 |
| refresh前後KB | 17,868ファイル・363,604,483バイト。追加/変更/削除0、ディレクトリ追加削除0、読取エラー0、リンク0、新規.jikji_agent_map.md 0 |
| 設定差分 | イヴのmcp_servers.autorag追加だけ。既存項目値不変。他9 Botのconfigハッシュ不変 |
| 新規イヴCLIのstatus/search | refresh失敗で停止したため未実施。本人の横断質問も未提供・未試行 |
| 全文写し | 秘密値確認後に99_backup/eve/config.yamlを追随、正本バイト一致。COPY-NOTE追記。SOUL/profile写しは無変更 |

KB比較は除外部分を含む全通常ファイルの相対パス・サイズ・SHA-256とディレクトリを対象に、記録更新前に完了。最終状態の比較であり、一時的な書込みを完全に否定する監視ではありません。報告書・台帳・写し・changelogの意図した更新は比較後に分けて行います。

### 今回の停止理由

```text
error: MinSync is required but installing the `minsync` binary failed:
tar: Cannot connect to C: resolve failed
. Install it manually with `cargo install minsync`.
```

refresh-progress.jsonもstate=failed、phase=parsed、Refresh failed: MinSyncRequiredError。実プロセスではCargo/rustcのビルド動作を確認し、その後のフォールバックのアーカイブ展開で上記エラーになりました。先行するCargo経路の失敗理由自体は未確定です。

refresh環境で選ばれるtarは `C:\Users\nekol\AppData\Local\hermes\tools\git-2.56.1+1-win32-x64\usr\bin\tar.exe`（GNU tar 1.35）。`C:\Windows\System32\tar.exe` も存在しますが、選択変更・代替tarによる再試験はしていません。C:表記との解釈不整合は疑いであり、修正確認済みとは扱いません。PATH変更、補助ツール手動導入、AutoRAGコード変更、refresh再実行は行わず停止しました。

### 現在の保存先と生成物

- 設定正本：`C:\Users\nekol\.autorag\config.json`。workspace：`C:\Users\nekol\.autorag\workspace`（明示設定）。
- 索引予定領域：`C:\Users\nekol\.autorag\workspace\.autorag`。現在あるのはrefresh-progress.json 309バイト、minsync-cargo/.crates.toml 0バイト、minsync-cargo/.crates2.json 0バイト。
- モデル予定先：`C:\Users\nekol\AppData\Local\minsync\models`。本人がWindows既定を受諾、上書き環境変数は設けず、現時点で未作成。
- 完成したnpm実行キャッシュ：`C:\Users\nekol\AppData\Local\npm-cache\_npx\8e5b5d15c05af942`。46,601ファイル・923,103,512バイト。索引容量ではない。
- 旧キャッシュの隔離先1：`C:\Users\nekol\AppData\Local\npm-cache\_npx-quarantine\8e5b5d15c05af942-20261117`（15,690ファイル・322,484,073バイト）。
- 隔離先2：同quarantine配下の `8e5b5d15c05af942-20261117-retry2`（3,258ファイル・30,430,120バイト）。どちらも削除ではなく移動で、全ファイルの前後SHA-256一致。現在も残置。
- AutoRAG設定・workspace・モデルはHermes homeやGoogle Driveに置かない。npmキャッシュ、Rust取得/ビルド用データ、Hermesの接続ログ/検査キャッシュは別に生じる。全PCの書込み全量監査はしていない。日次バックアップ処理は変更なし。

### 承認された警告の例外と検査

本人が `npm warn deprecated` だけを記録付き継続の例外にしました。再取得で出た2件は `lodash.isequal@4.5.0`（node:utilのisDeepStrictEqual推奨）と `node-domexception@1.0.0`（プラットフォーム標準DOMException推奨）。警告抑制・ignore_scripts解除はしていません。セキュリティ/監査、設定検査、ツール異常、KB差分等の停止条件は維持。

- 設定バリデータ警告なしで登録成功。保存後 `hermes -p eve config check` 終了0。
- Hermes OSV検査：eve/cache/osv_check.jsonに `npm|@autorag/librarian|2.13.12`、result=nullの記録を確認・証拠保存。トップレベルパッケージのMAL指摘なしであり、依存全体の脆弱性監査や安全保証ではない。
- 返った2ツールの説明文検査は指摘0。Marketplaceプラグイン一式の導入スキャンはこの経路では実施しない。
- 管理Nodeは `C:\Users\nekol\AppData\Local\hermes\tools\node-26.12.1-win32-x64\node.exe`。起動解決だけでなくrefreshの実node子プロセスでも確認。npm/npxはnpm-12.2.2-win32-x64配下。
- 起動シェルのalias解釈エラー表示はありましたが、CLIは登録成功しました。シェル設定の修正は対象外として行っていません。

### 成功した登録と固定設定

```bash
hermes -p eve mcp add autorag --connect-timeout 180 --command npx --env 'AUTORAG_CONFIG=C:/Users/nekol/.autorag/config.json' 'AUTORAG_MCP_READ_ONLY=true' 'AUTORAG_MCP_TOOLS=autorag.status,autorag.search' 'AUTORAG_AUTH_MODE=environment' 'PI_CODING_AGENT_DIR=C:/Users/nekol/.autorag/model-runtime' 'npm_config_allow_remote=all' 'npm_config_ignore_scripts=true' --args -y -p @autorag/librarian@2.13.12 autorag-mcp
```

イヴconfigにはcommand/args/上記7環境変数、connect_timeout=180.0、enabled=trueを保存。既存model/skills/memory等は不変。新規セッションまたは/reload-mcpが反映経路です。認証値の参照・コピー・変更はしていません。

AutoRAG configの全文・除外パターンは下の履歴内の「作成した設定の全文」と同じままです。現在もjikji=false、everything=false、fsearch=false、datasources={}、AI_knowledgeのみ、outputsを含め、指定の99_backup/codex-sessions/メール・カレンダー形式/生成物/過去work/スキルreceived・workを除外。26件の除外関数事前試験は失敗0ですが、完成索引での反映は未確認。トップレベル2.13.12固定だけで依存全体は固定されません。

Marketplace一式、付属setupスキル、Desktop検索ペイン、外部サービス接続、定期実行は導入していません。マナには登録していません。npm_config_allow_remote=allはSheetJS tarball取得用ですがSheetJS限定の許可ではなく、子プロセスだけに適用。ignore_scripts=trueを維持します。

### refreshの手順と証拠

実行したのは、上記と同じ管理版npx・環境設定による次のコマンドです。

```text
npx -y -p @autorag/librarian@2.13.12 autorag lite refresh --config C:/Users/nekol/.autorag/config.json --method parsed,minsync
```

設定読み戻し→KB全体の前状態取得→parsed/minsyncのみのCLI実行と時間測定→失敗後のKB全体後比較→記録更新の順。以後は不具合の原因・変更対象・戻し方を本人に提示し、修復承認後に新しい前後比較付きで再実行します。新規イヴCLIでstatusと出典付きsearchが返るまでは運用可能と記録しません。本人の横断実質問がなければ検索応答確認までに留めます。

現回の変更前控え・証拠：`C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\backups\eve-autorag-resume-20261117-1837`。主要ファイルはrecords-before、cache-quarantine.json、quarantined-cache-hashes.json、cold-standalone-result.json、standalone-result.json、standalone-stderr.log、osv-verdict.json、eve-config.registered.yaml、refresh-start.json、refresh-stdout.log、refresh-stderr.log、refresh-result.json、refresh-tool-resolution.json、kb-before-refresh.json、kb-after-refresh.json、kb-refresh-comparison.json、final-inventory-before-records.json、backup-copy-verification.json。前回の報告書全文も控え済みです。共有先へ秘密値や会話本文は置きません。

### 現在の戻し方・PC復旧

- Bot側を戻す場合は本人承認のうえで `hermes -p eve mcp remove autorag` により当該登録だけを外し、新規セッション等で反映。古いconfig全体を戻して他の設定まで巻き戻さない。写し・COPY-NOTE・台帳を追随する。
- `.autorag`、モデル、npmキャッシュ、隔離物、Rust取得/ビルド用データは別途判断。今回は手動削除なし。隔離物を戻す場合も現在の同名キャッシュを上書きしない。changelogの過去行は戻さず、訂正は後続追記。
- PC復旧時は日次Hermesバックアップまたは安全なイヴ全文写しからプロフィール正本を承認のうえで復旧し、この報告のAutoRAG configを既定homeへ再作成。現在は登録済みでも索引未完成である点を引き継ぐ。
- AutoRAG homeとモデルはHermes日次バックアップ対象外の配置。索引・モデル・npm取得物は再取得/再構築を前提とし、Google Driveへ実体を写していない。Windows既定モデル先を別OSの~/.cacheと取り違えない。
- 未解決のMinSync導入について、Cargo経路の失敗理由とtar解決を調査し、変更対象・影響・戻し方を示して別途承認後に修復する。PC共通PATHやHermes本体を勝手に変更しない。
- 将来のマナ利用は同じ設定・索引への登録を別途承認して追加。共通台帳への記載自体は権限や登録を変更しない。

---

## 前回停止時点の記録（履歴。以下の未登録・未実行表記は当時の状態）

- 実施日・実物確認日：2026-11-17（日本時間）。実施者：ナユタ。本人が承認した設定案・コマンド・対象・検証手順に基づく今回限りの作業。
- **導入は未完了。イヴのMCP登録は保存していない。refresh・索引作成・新規イヴCLIのstatus/search試験は未実施。**
- 報告書・台帳・changelogの更新は、KB後比較を終えた後に行う。これらの意図した記録更新は、無書込み比較期間とは分ける。

## 結果の一覧

| 項目 | 実物確認結果 |
|---|---|
| AutoRAG config | `C:\Users\nekol\.autorag\config.json` を作成・JSON読み戻し一致 |
| workspace | `C:\Users\nekol\.autorag\workspace` を作成。停止時点では空 |
| MCP登録 | `hermes -p eve mcp add autorag ...` を実行したが、接続が既定30秒でタイムアウト。保存確認に `n` と回答し、未保存 |
| 全10 Botのconfig | 作業前後SHA-256一致。イヴも変更なし |
| 初回refresh所要時間 | **未計測（未実行）**。接続待ち30秒をrefresh時間と混同しない |
| 索引の実測容量 | **未作成**。`workspace\.autorag` 自体が存在しない。完成索引の容量実測はできていない |
| モデル | `C:\Users\nekol\AppData\Local\minsync` は停止時点で存在しない |
| KB後比較 | 17,867ファイル、363,586,428バイト。追加0・変更0・削除0、ディレクトリ追加削除0、読取エラー0、リンク0 |
| Jikji map | `.jikji_agent_map.md` の新規作成0 |
| 検索試験 | tools/list、status、searchの成功は未確認。本人の横断実質問も未試行 |
| バックアップ写し | イヴconfig原本と `99_backup/eve/config.yaml` はバイト一致。原本未変更なので写し・COPY-NOTEは更新していない |

## 停止の直接の理由

CLIの実出力：

```text
Connecting to 'autorag'...
Failed to connect: Connecting to MCP server 'autorag' timed out after 30s
(bounded by connect_timeout; an OAuth login also by oauth.timeout); CancelledError
Save config anyway (you can test later)? [y/N]: n
```

CLI自体の終了コードは0だったが、接続失敗・未保存なので成功とは判定しない。タイムアウト延長・再試行・スクリプト無効化解除等は行っていない。

MCP stderrにはnpm依存パッケージの非推奨警告が残った：`lodash.isequal@4.5.0`、`node-domexception@1.0.0`。これらはHermesの危険構成検査警告とは別。導入済みパッケージ群の完全性・起動可能性は確認できていない。接続前には起動シェルの `alias` 解釈エラー表示もあったが、この作業ではシェル設定を変更していない。根本原因をコールドキャッシュだけと断定しない。

停止後、対象キャッシュ名・autorag/librarianに一致するnode/cmd/cargo/minsync/jikjiプロセスを照合し、一致する残存プロセスはなかった。

## 配置・生成物

- AutoRAG home：`C:\Users\nekol\.autorag`。既定位置。設定とworkspaceを手動作成。
- config：`C:\Users\nekol\.autorag\config.json`、866バイト。停止時のhome内通常ファイルはこの1件のみ。
- workspace：`C:\Users\nekol\.autorag\workspace`。索引予定先はその `.autorag\`。現時点で索引なし。
- モデル予定先：`C:\Users\nekol\AppData\Local\minsync\models`。Windows実装の既定を本人が受諾。`HF_HOME`・`FASTEMBED_CACHE_DIR`等で寄せていない。
- npmキャッシュ内で確認できたパッケージ：`C:\Users\nekol\AppData\Local\npm-cache\_npx\8e5b5d15c05af942\node_modules\@autorag\librarian\package.json`、name=`@autorag/librarian`、version=`2.13.12`。
- 同npxキャッシュサブツリーの停止後実測：15,690ファイル、322,484,073バイト。ただし事前の同キャッシュ個別一覧は採っておらず、すべてを今回の新規生成量と断定しない。これは索引容量でもインストール完了証明でもない。
- MCP stderr：`C:\Users\nekol\AppData\Local\hermes\profiles\eve\logs\mcp-stderr.log`。Hermes側には接続ログ等は残るが、autorag本体の設定・索引・モデルはHermes home内へ配置していない。
- npmの共有取得キャッシュやHermesの通常接続記録以外の詳細な全PC書込み追跡は行っていない。
- 日次バックアップ処理は変更していない。

## 版とNode経路

- npmパッケージ指定：`@autorag/librarian@2.13.12`。トップレベル固定で、依存全体の固定ではない。
- 事前確認で配布tgzをメモリ内検証し、npmレジストリ記載SHA-512と一致した。これは依存全体の安全監査ではない。
- Hermes管理Node：`C:\Users\nekol\AppData\Local\hermes\tools\node-26.12.1-win32-x64\node.exe`、直接プローブv26.12.1・終了0。
- PMで選択中のnpm：`C:\Users\nekol\AppData\Local\hermes\tools\npm-12.2.2-win32-x64\npm.cmd`。
- bare npxはHermesのPM管理版を選ぶ実装。autoragサーバー自体の起動に成功していないので、そのサーバープロセス上でのNode実測は未確認。

## 作成した設定の全文

```json
{
  "workspacePath": "C:/Users/nekol/.autorag/workspace",
  "searchPaths": ["E:/Documents/Google Drive/AI_knowledge"],
  "jikji": false,
  "everything": false,
  "fsearch": false,
  "datasources": {},
  "excludePaths": [
    "E:/Documents/Google Drive/AI_knowledge/99_backup",
    "E:/Documents/Google Drive/AI_knowledge/30_resources/sources/codex-sessions",
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.venv/**",
    "**/*.msg",
    "**/*.eml",
    "**/*.emlx",
    "**/*.mbox",
    "**/*.mbs",
    "**/*.pst",
    "**/*.ost",
    "**/*.ics",
    "**/*.ical",
    "**/*.icalendar",
    "**/*.ifb",
    "**/*.vcs",
    "**/*.vcal",
    "**/*.jcal",
    "E:/Documents/Google Drive/AI_knowledge/40_archives/projects/**/work/**",
    "E:/Documents/Google Drive/AI_knowledge/30_resources/skills/**/{received,work}/**"
  ]
}
```

`20_areas/ai-operations/outputs` は含めるが、その中の共通除外対象も除外する。スキルのreceived/workは列挙時点で実在0。将来追加された同名フォルダも対象のパターンを設定。過去プロジェクトのwork実在3件：

- `40_archives/projects/codex-playground/ekikyo/work/`
- `40_archives/projects/codex-playground/wsl-projects/archive/iching/iching-div/work/`
- `40_archives/projects/codex-playground/wsl-projects/ekikyo/work/`

固定版の除外判定関数を既存Nodeで検査した事前試験は26件・失敗0・終了0。ただし本番refreshの索引への除外反映試験は未実施。

## 試行した登録コマンドと環境変数

```bash
hermes -p eve mcp add autorag --command npx --env 'AUTORAG_CONFIG=C:/Users/nekol/.autorag/config.json' 'AUTORAG_MCP_READ_ONLY=true' 'AUTORAG_MCP_TOOLS=autorag.status,autorag.search' 'AUTORAG_AUTH_MODE=environment' 'PI_CODING_AGENT_DIR=C:/Users/nekol/.autorag/model-runtime' 'npm_config_allow_remote=all' 'npm_config_ignore_scripts=true' --args -y -p @autorag/librarian@2.13.12 autorag-mcp
```

- READ_ONLY=trueでrefresh/report/convertを公開しない。allowlistは元のMCP名 `autorag.status,autorag.search` の完全一致。
- Hermesでの予定名は `mcp__autorag__autorag_status` と `mcp__autorag__autorag_search`。実登録・実行未確認。
- AUTH_MODE=environmentとPI_CODING_AGENT_DIRで保存済み認証等の探索を避ける。認証値は扱っていない。
- npm_config_allow_remote=allは固定依存のSheetJS tarball取得用。SheetJSだけに限定する値ではない。
- npm_config_ignore_scripts=trueでnpmライフサイクルスクリプトを抑止。解除していない。
- すべて当該子プロセス用。PC共通のnpm設定は変更していない。
- 保存予定先はイヴ `config.yaml` の `mcp_servers.autorag` だったが未保存。他Bot設定・SOUL・権限・認証は変更なし。

## スキャンと注意

- Hermesの危険構成検査はある。事前の登録骨格に対する実装検査は警告0。
- 今回の登録試行でHermesの危険構成検査警告は表示されず、接続段階まで進んだ。
- Marketplaceプラグイン導入スキャンは今回の経路では実施していない。MCPツール説明の検査は未接続のため成功判定なし。
- npm非推奨警告とHermesセキュリティ検査は区別する。
- 検索断片をイヴが使う場合にはイヴのモデル提供元へ渡る。現時点では検索試験自体を行っていない。

## KB前後比較の範囲と証拠

除外指定に関係なくKB全体を通常ファイルの相対パス・サイズ・SHA-256で比較。ディレクトリ一覧・リンク・読取エラーも検査。前後とも17,867ファイル、363,586,428バイト。ファイル追加・削除・内容変更、ディレクトリ追加削除、新規Jikji mapはいずれも0。全10 Botのconfigハッシュも不変。

前状態はconfig作成・登録試行前、後状態は停止後かつこの報告書・台帳・changelog更新前。最終状態の比較であり、一時的な書込みまで完全に否定する監視ではない。

ローカル証拠・変更前控え：

```text
C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\backups\eve-autorag-20261117\
```

主なファイル：`before-state.json`、`eve-config.before.yaml`、`records-before/`、`kb-before-all.json`、`prepared.json`、`kb-after-stop.json`、`kb-stop-comparison.json`、`post-stop-state.json`、`stop-result.json`、`mcp-stderr.txt`。KBの本文そのものは比較記録に保存せず、パス・ハッシュ等を保存。これらはナユタ領域内のローカル控えで、共有先に秘密情報や会話本文を置いていない。

## 未実行のrefresh手順（再開の承認後）

以下は手順記録であり、今回の実行結果ではない。

1. タイムアウト原因と接続待ち時間の見直し案を本人に提示し、再開承認を得る。設定の新規衝突やキャッシュ状態を再確認。
2. 同じ固定版・Hermes管理Node/npm・認証分離・npm子プロセス設定で登録。2ツールだけを検出し、警告・失敗なら停止。
3. KB全体の新しい前状態を採取。
4. 同じ管理版npxと環境設定で次を実行し、経過時間と終了結果を採る：

```text
npx -y -p @autorag/librarian@2.13.12 autorag lite refresh --config C:/Users/nekol/.autorag/config.json --method parsed,minsync
```

5. KB全体の後比較、索引・モデル・補助ツールの実パスと容量を検査。差分・想定外書込み・警告で停止。
6. 新規イヴCLI（または/reload-mcp後）でstatusと出典付き検索を実行。本人の横断質問がなければ検索が返ることの確認まで。
7. 検証完了後にイヴ台帳・共通基盤の台帳・秘密値検査済みconfig写し・changelogを更新。

MinSyncはcargoが使える場合0.7.3を--lockedで取得・ビルドする経路、フォールバックにGitHub release取得がある。Qwen3-Embedding-0.6B、KURE-Sparse-nanoのREADME概算は約1.5GBだが、今回の実測ではない。Jikji・Everything・fsearch・データソースはこの設定で使わない。定期実行は作らない。

## 戻し方

- **現在：イヴのMCP登録はないので、Bot側で外すものはない。** config原本・既存写しとも変更前のまま。共有記録は「未完了・停止」を維持する。
- `.autorag`、npmキャッシュ、将来のMinSyncモデル等の削除は別途判断。今回は削除しない。
- 将来登録後に戻す場合は、イヴのautorag登録だけを正規CLIから外し、新規セッション等で反映、config写し・記録を追随する。他Botの登録や共有モデルを巻き込まない。
- 記録の変更前控えは上記records-beforeに保存。changelogは過去行を戻さず、訂正が必要なら後続追記。

## PC復旧・再構築

1. この報告書と既存の日次Hermesバックアップからイヴの正本設定・規則を復旧。今回はMCP登録が未保存なので、復旧しただけでautoragが使える状態にはならない。
2. 承認後、固定版のNode>=24を用意し、上記configを既定AutoRAG homeへ再作成。モデルのWindows既定位置を再確認し、別OSのパスを流用しない。
3. npmキャッシュ・索引・モデルは再取得・再構築可能な生成物。固定トップレベル版だけで依存全体は再現固定されないことを確認する。今回これらをGoogle DriveやHermes homeへ移して保管していない。
4. 除外・jikji=false等を読み戻し、KBハッシュ前後比較付きでrefreshを実施。新規CLIで2ツールを再検証してから運用に戻す。
5. 将来マナが使う場合は同じ設定・索引へのMCP登録だけを別途承認して追加。今回の記録はマナの権限・登録を変更しない。

## 今回の対象別処理

- 作成：AutoRAG config、workspace、ナユタの変更前控え・検証記録、本報告書。
- 記録更新：イヴprofile、settings-indexの共通基盤節、changelogへの末尾1行。
- 変更なし：イヴconfig、全他Botのconfig、SOUL・認証・既存skill、日次バックアップ設定。
- 写し追随なし：イヴconfig原本に変更がなく、既存99_backup写しとのバイト一致を確認したため。COPY-NOTEも無変更。
- 未完了：MCP登録、refresh・索引容量/時間実測、status/search、新規イヴCLI確認。再開は本人との相談後。
