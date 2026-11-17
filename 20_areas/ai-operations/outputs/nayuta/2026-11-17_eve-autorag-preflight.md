# イヴへのAutoRAG Lite導入：事前確認

確認日：2026-11-17。調査のみ。Node/npmの更新、パッケージ・モデル・補助CLIのインストール、MCP起動、索引作成、eveの設定・SOUL・登録簿・写し・changelogの変更は行っていない。公開資料はナユタの自己scratchに取得し、コードは実行していない。

## 結論

現時点では導入保留。

1. PATH上のNode.jsがv22.17.0で、AutoRAGのNode >=24.0.0要件を満たさない。
2. Marketplace版プラグインはmacOSのみ検証済み。Windowsは未検証とされる。
3. MCP接続だけでなく、索引の構築先、モデル・補助CLIの取得、更新担当を別途決める必要がある。
4. 読み取り専用MCPは設定できるが、初回索引構築に使うJikjiには索引対象rootへのガイドファイル作成の記載があり、検索対象ツリーへの無書込みは未保証。初回構築も含めた隔離テストが必要。

## 1. Node.js

実測：
- `node --version`：v22.17.0
- `npm --version`：12.0.2
- PATH上のnode：C:\Program Files\nodejs\node.exe
- npmの警告：対応Nodeは ^22.22.2 || ^24.15.0 || >=26.0.0。現在の22.17.0とは不整合。

更新する場合の選択肢（未実施）：
- 影響を限定する案：承認したeve専用の場所に公式Windows ZIP版Nodeを置き、当該MCP子プロセスだけ絶対パス・限定PATHで使う。全体のNodeを置換せずに済むが、Nodeとnpm/npxの組合せ、MCPの起動方法の確認が必要。
- PC全体を更新する案：公式MSIで対応版へ更新する。通常は管理者権限が必要になり、他BotのMCP、npmパッケージ、開発ツールにも影響し得る。既存の22.17.0に戻す控えと互換性試験が必要。
- 版管理ツールによる併存案：fnm等を導入して切り替える。ツール導入とシェル/PATH設定変更が追加され、Desktopから起動するMCPに目的のNodeが渡るか検証が必要。

24系を選び現在のnpm12を使うなら24.15.0以上が必要。取得時点の公式ダウンロードページでは26.13.1 LTSも提供されていたが、今回はいずれも取得・展開していない。

## 2. Hermesの追加方法と設定先

実行版：Hermes v0.23.2、local ae2a81ccc00e。

`hermes -p eve config path`：
`C:\Users\nekol\AppData\Local\hermes\profiles\eve\config.yaml`

現状、eveの `mcp_servers` は未設定。

profileを明示した `hermes -p eve mcp add <name> --command <executable> --env KEY=VALUE ... --args ...` が正式な追加方法。`--args`は最後に置く。このコマンドは接続してツールを検出し、選択後に `mcp_servers.<name>` を保存するため、事前確認中には実行していない。新規セッションまたは `/reload-mcp` で反映する。

後日、Nodeの経路とAutoRAG専用configの場所を承認した場合の接続イメージ（未実行）：

```text
hermes -p eve mcp add autorag --command npx --env "AUTORAG_CONFIG=C:/Users/nekol/AppData/Local/hermes/profiles/eve/autorag/config.json" "AUTORAG_MCP_READ_ONLY=1" "AUTORAG_MCP_TOOLS=autorag.status,autorag.search" "AUTORAG_AUTH_MODE=environment" --args -y -p @autorag/librarian@2.13.12 autorag-mcp
```

これは現在のNode22で実行してよいコマンドではない。eve専用Node案では、command・子プロセスPATH等をその絶対パスに合わせて確定する必要がある。npmのキャッシュや既定モデルキャッシュは自動的にprofile隔離されるとは限らない。

Hermes側にも `mcp_servers.autorag.tools.include` / `exclude` があり、公開ツールを絞れる。不要なMCP samplingを無効にする案も導入時に含める。

Marketplace一式の `hermes -p eve plugins install autorag` と、MCPだけの登録は別の操作。今回はMCPだけが目的なので、4つの付属スキル・Desktop Finder・自動化機能までまとめて導入する必要はない。

## 3. 提供物・供給元・規約・スキャン

### 対象の識別
- 提供元：Marker-Inc-Korea / Marker Inc. Korea。
- Marketplace：autorag、community tier、プラグイン版1.0.0。
- Marketplace READMEの固定コミット：40ef977a1262fb1090b2be04556739994eb29225。
- MCP実行パッケージ：`@autorag/librarian@2.13.12`。
- `plugin.json`、`mcp.json`、READMEと関連実装を上記コミットから確認。mainは内容が異なるため、固定版と混同しない。
- Marketplaceではplatforms=[macos]。カタログ登録はWindowsでの稼働証明ではない。

### 初回取得物
- npmの固定トップレベルパッケージと依存関係。npmレジストリでも2.13.12・Apache-2.0・Node>=24.0.0を確認。展開サイズは11,580,488バイト（トップレベルのみ）。
- 依存には範囲指定があり、トップレベルの版固定だけでは依存全体は固定されない。xlsxはcdn.sheetjs.comのtgzを参照する。
- MarketplaceプラグインのDesktop側は追加で専用runtimeにnpm installする。READMEの目安は依存込み約1GBであり、MCPのnpx経路と二重に展開される可能性がある。Desktop側は今回の目的外。
- 初回refreshはMinSync・Jikji等を用意する。MinSyncはcargo経路またはNomaDamas/MinSyncのSHA-256検証付きGitHub release asset。Jikjiはcargo経路の記載。RustやWindowsビルド依存が追加で必要になる可能性があり、未検証。
- ローカルモデルはMinSyncがHugging Faceから取得する。READMEの概算はQwen3-Embedding-0.6Bが約1.2GB、KURE-Sparse-nanoが約290MB、合計約1.5GB。インストール全体が1.5GBという意味ではない。
- 確認したモデル提供元：Qwen/Qwen3-Embedding-0.6B、nlpai-lab/KURE-Sparse-nano。両モデルカードはApache-2.0。キャッシュの既定はREADMEでは `~/.cache/minsync/models`。Windowsでの実際の解決先とプロファイル別配置は未確認。
- WindowsではEverythingのポータブルバイナリも同梱され、機能使用時に専用のファイル名索引用プロセス・データを作る構成がある。不要なら無効化を検討する。

### ライセンス・利用規約
AutoRAG本体とHermes向けプラグインはApache-2.0。モデルカードもApache-2.0。確認した範囲では、ローカルMCPからの利用・自動化・第三者製クライアント接続を禁止する条項は見つからなかった。配布時のライセンス/NOTICE保持等の条件はある。これは法的な適合保証や依存全体の監査ではない。

Dazziデスクトップアプリやクラウドの契約は別物。今回は導入・ログイン・サブスクリプション利用をしない。Hister等の任意コネクタのライセンス/サービス規約を今回のローカルファイル検索に混ぜない。

### スキャン
Hermesでのインストール時スキャンは未実施。Marketplace本文に公開されたスキャン判定は確認できなかった。community登録・固定SHA・READMEの自己申告は、安全判定の代わりにはしない。『問題なし』というスキャン結果は報告できない。

### データの行き先
ローカル索引・ローカル埋め込みでも、検索断片をイヴが読むとイヴのモデル提供元へ送られる。AI_knowledge全体が外部へ一括送信されるという意味ではないが、『完全にPC内で完結』でもない。remote embedder/reranker・外部コネクタは明示的に使わない構成が必要。

## 4. 索引・対象指定・追随

AutoRAGの設定解決は明示configまたは `AUTORAG_CONFIG` が優先。searchPathsをAI_knowledgeの絶対パス配列で指定し、workspacePathを別の専用作業領域にする。`AUTORAG_SEARCH_PATHS` はCSVの検索root指定、`AUTORAG_WORKSPACE` はworkspaceの上書き。`excludePaths`も設定できる。

提案段階の配置例（未作成）：
- 設定：eveプロフィール内 `autorag/config.json`
- workspace：eveプロフィール内 `autorag/workspace`
- 検索root：`E:\Documents\Google Drive\AI_knowledge`
- データソース：ローカルファイルのみ。メール・チャット・Obsidian等のコネクタは追加しない。既存アーカイブの自動検出・自動接続は行わない。

主な書込み先：
- `<workspace>/.autorag/parsed/`：解析済みMarkdownのミラー。
- `<workspace>/.autorag/minsync/`：MinSync側の作業領域、.minsyncのmanifest/ベクトルDB等。
- `<workspace>/.autorag/bin/`、Everything用領域等。
- JikjiのOSデータディレクトリ（JIKJI_DATA_DIRで上書き可能）。
- AutoRAG homeのconfig、memory、report関連データ、モデルキャッシュ、npmキャッシュ。

容量はモデルの固定部分に加え、文書の解析済みテキスト、分割チャンク数、dense/sparse索引、DB管理情報などで増える。複数のミラー/索引があり、原本サイズに対する単一の倍率は提示できない。今回、AI_knowledgeの容量計測や索引作成はしていないので、実容量・所要時間は未確認。

初回には `autorag lite refresh` が必要。以後はmtime・サイズ・内容hash等を使った増分更新。MCPサーバーを起動しただけで本文索引が常に最新になるわけではない。readonly接続からrefreshは呼べないため、更新は別途承認したCLI手動実行、またはwatch/スケジュールに分ける必要がある。watch/定期ジョブは今回作成しない。

AI_knowledge全域をrootにしても、秘密情報・他Botの私的会話・メール/チャットアーカイブの除外条件は残る。ルート内に該当物があれば、初回構築前に除外パスを確定する。索引自体にも本文のミラーや断片が入るので、秘密性・保存先を原本と同等に扱う。

## 5. readonlyと公開ツール

指定：`AUTORAG_MCP_READ_ONLY=1`（またはtrue）。
固定版 `src/mcp/server.ts` ではreadonly時に `autorag.refresh`、`autorag.report`、`autorag.convert` の登録を省く。`AUTORAG_MCP_TOOLS` は元のMCP名の完全一致CSVで、例は `autorag.status,autorag.search`。READMEのアンダースコア表示と、実装のドット区切り名を混同しない。

最初はstatusとsearchだけに絞る案。出典はsearch結果から取得し、reportによる別の成果物保存はさせない。イヴの通常成果物先 `outputs/eve` は変えない。readOnlyHintという注釈だけに頼らず、未公開ツールの実際のtools/listと検索時の書込みを検証する。

### 原本ツリーへの書込みについての注意
固定コミットREADMEは、Jikjiが各索引rootへ `.jikji_agent_map.md` を置くと明記している。一方で『原本文書を変更しない』とも説明する。固定版クライアントは `--no-agent-rules` を既定で渡し、AGENTS.md/CLAUDE.md/.cursorrulesの書換えを避けるが、それだけでガイドの新規作成まで止まるとは確認できなかった。

readonly環境変数はMCP公開ツールと設定解決の一部を制限するもので、初回CLI構築の全副作用やWindows ACLによる保護を保証しない。Jikji無効化などの回避案を確定し、捨ててよい小さな入力コピーで作成/変更ファイルを比較してからAI_knowledgeへ適用する必要がある。今回は未実行。

## 次に承認が必要な事項

現時点で導入承認は求めず、前提の選択肢を示す段階。
- Nodeをeve専用で併存させるか、PC全体で更新するか。
- Marketplace一式でなくMCPだけにするか（今回の依頼に沿うのは後者）。
- AutoRAG config/workspace、npm/model/Jikjiキャッシュ、補助実行ファイルの正確な保存先。
- 原本ツリーへの書込み回避策と、Windowsでの隔離試験。
- AI_knowledge内のメール・チャット・私的データ等の除外パス。
- readonly接続ではできない索引更新を、誰がいつ実施するか。初回は手動、定期化は別承認が安全。

## 主な出典

- https://hermes-agent.nousresearch.com/marketplace/autorag
- https://github.com/Marker-Inc-Korea/AutoRAG/tree/40ef977a1262fb1090b2be04556739994eb29225/plugins/hermes
- https://github.com/Marker-Inc-Korea/AutoRAG/blob/40ef977a1262fb1090b2be04556739994eb29225/src/mcp/server.ts
- https://github.com/Marker-Inc-Korea/AutoRAG/blob/40ef977a1262fb1090b2be04556739994eb29225/src/jikji/client.ts
- https://registry.npmjs.org/@autorag%2flibrarian/2.13.12
- https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- https://huggingface.co/nlpai-lab/KURE-Sparse-nano
- https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference
- https://nodejs.org/en/download

導入済みHermesの `hermes_cli/mcp_config.py` と実際のCLI helpも確認。公開ソースの取得一覧は自己scratch `autorag-preflight/manifest.json` に記録。
