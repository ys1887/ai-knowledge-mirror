# イヴへの AutoRAG MCP 導入結果：初回接続タイムアウトで停止

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
