# PC共通Node.js 22→24系：事前確認

確認日：2026-11-17。まだ更新していない。管理者昇格、msiexecの実行、Node/npm/Corepack/他パッケージの変更、autorag導入は行っていない。公式MSIのダウンロード、チェックサム・署名確認、MSIデータベースの読み取りのみ実施。

## 判定

更新候補は **v24.22.3 LTS（Krypton）x64**。公式index.jsonで24系の最新LTSを確認し、取得したMSIのSHA-256が公式値と一致、Windows Authenticode署名もValidだった。実施が後日になる場合は最新24系とファイル検証をやり直す。

ただし標準MSIはNodeRuntimeだけでなくnpm/Corepackも機能に含む。現在のProgram Files側npmは10.9.2で、更新先同梱npmは11.19.1。この同梱変更を「Node以外のパッケージ更新はしない」の例外として承認するか、先に判断が必要。勝手にnpm更新を含めない。

## 1. 現在の導入形態

- PC共通：`C:\Program Files\nodejs\node.exe`、v22.17.0。
- HKLMのWindows Installer登録：Node.js 22.17.0、Publisher=Node.js Foundation、WindowsInstaller=1。
- ProductCode：`{974591B0-CB6E-49FA-8E9B-4A0463A3E1C0}`。
- 取得した公式22.17.0 MSIのProductCodeとも一致。
- レジストリ上のInstallDateは20250626、InstallSourceはE:\Documents\Downloads\。そのフォルダ自体は閲覧していない。
- **MSIで入っていることは確認済み。** 手動実行したのかwinget経由なのかまでは未確定。ZIP展開のみの導入ではない。
- NodeRuntime、corepack、npm、DocumentationShortcuts、EnvironmentPath関連機能は現状インストール済み（Installer APIのstate=3）。

現在のMSIのUpgradeCodeと新24.22.3 MSIのUpgradeCodeは同じ。通常は新MSIによる旧版置換の系統。管理者権限が必要なマシン全体インストール（ALLUSERS=1）であり、昇格前に本人の操作または明示承認を挟む。

## 2. 複数のNode/npmとPATH

このterminalでの解決：
- node：Program Filesの22.17.0が先。
- npm/npx：Hermes管理のnpm12.0.2が先。
- 他にHermes管理Node26.12.1、npm12.2.2、Node26同梱npm、ユーザーRoaming側npm11.2.0が存在。
- machine PATHにはProgram Files\nodejs、user PATHにはHermes\binとRoaming\npmが登録されている。Hermes toolsの追加PATHはこの実行環境側のものと区別する。

そのため、単にnpm -vを見るとProgram Filesの同梱npmではない版が表示される。このterminalではnpm12.0.2がNode22.17.0を非対応と警告し、対応範囲は ^22.22.2 || ^24.15.0 || >=26.0.0。

更新後は新しく開いた通常シェル、Hermes内terminal、各CLIの絶対パスで区別して確認する必要がある。既存プロセスのPATH・実行中ランタイムがMSI更新だけで全て切り替わるとは限らない。

### 前回autorag確認への補足・訂正

導入済み `tools/mcp_tool_config.py` では、MCPのbareなnode/npm/npxはHermesのPM管理版へ解決し、子PATHも管理版優先にする。絶対パス指定は別扱い。Hermes管理のNode26.12.1は実在し、--versionも確認済み。

したがって **PC共通Node22が、Hermes内MCPのbare npx経路でも必ず使われるとした前提は訂正する。** PC全体を24へ更新する判断と、Hermes MCPのNode24以上要件は別問題。autoragのWindows動作・依存関係・実接続は未試験のままであり、この発見だけで導入可とはしない。

## 3. 依存先の棚卸しと影響の当たり

### Hermes MCP

default、mana、arcana、label、phantom、nayuta、eve、takina、raven、crownのconfigを非秘密設定だけ確認。10件ともmcp_serversの登録は0件。通常のprofile-local plugins配下にもportable mcp.jsonは見つからなかった。

現在のHermesに接続確認すべきNode MCPはこの調査範囲ではない。外部MCPや別クライアントの設定全体を監査した結果ではない。下記のMCP用npmパッケージは存在するが、インストールされているだけで稼働中・Hermes接続中とは判断しない。

### npmグローバルパッケージ

npmの実体・prefixで一覧が異なるため、通常の `npm ls -g --depth=0 --json` とProgram Files版npmの絶対パス、Roaming prefixを指定した一覧、各package.jsonを照合した。

| 保存先 | パッケージ | 版 | Node24への見立て |
|---|---|---|---|
| Program Files\nodejs | corepack | 0.33.0 | engines上は24を含む。Node MSIの機能対象なので同梱変更に注意 |
| Program Files\nodejs | npm | 10.9.2 | engines上は24を含むが、新MSI標準構成なら11.19.1へ変わる |
| Roaming\npm | @gongrzhe/server-gmail-autoauth-mcp | 1.1.8 | engines >=14。宣言上の阻害なし。ただし旧MCPの実接続・認証互換は未確認 |
| Roaming\npm | @isaacphi/mcp-gdrive | 0.2.0 | engines宣言なし。24対応は未保証、接続試験未実施 |
| Roaming\npm | @modelcontextprotocol/server-brave-search | 0.6.2 | engines宣言なし。24対応は未保証、接続試験未実施 |
| Roaming\npm | @openai/codex | 0.168.0 | engines >=16。現在--version成功。更新後に再確認する代表候補 |
| Roaming\npm | npm | 11.2.0 | engines ^20.17.0 または >=22.9.0。24を含む。今回はこのパッケージを更新しない |
| Roaming\npm | opencode-ai | 1.19.5 | 現在--version成功。更新後に再確認する代表候補。版そのものは変えない |
| Roaming\npm | uv | 1.4.0 | npm版のパッケージ。実際のuv実行経路はC:\Users\nekol\.local\bin\uv.exeで、別のもの。いずれも変更対象外 |

Roaming側7パッケージと、Program Files側2パッケージを区別。グローバルnpm12が表示したProgram Files側一覧だけではRoaming側を見落とす。

### 開発道具・プロジェクト

限定したメタデータ探索でpackage.jsonを14件発見：Hermesリポジトリ内13件と、Documents\Codex配下の1プロジェクト。個人のソース本文は読まず、名前・版・engines・scriptsの項目名・依存名だけを確認した。

| 対象 | 影響の当たり |
|---|---|
| Hermesリポジトリroot | **engines.node >=26、pnpm ^12。Node24はソース開発用要件を満たさない。** 現存するHermes管理Node26/pnpm12を維持し、24へ統一しない |
| Hermes Desktopソース | Node>=26。Electron、node-pty等あり。Node24で再build/installしない。現在の完成済みHermes.exeとソースbuild環境は分ける |
| Hermes website | Node>=26.0。24で開発・buildするのは要件外 |
| Hermes UI/TUI/web/shared等 | monorepo側のNode26/pnpmの運用を維持。npm installはソース側で拒否する設定があり、実行しない |
| 同梱photon sidecar | 宣言はNode>=18.17。ただし存在だけで利用中とはしない。外部サービス試験はしていない |
| 同梱whatsapp bridge | Node要件の宣言なし。存在だけで利用中とはしない |
| Documents\Codex\2026-05-26\wsl-codex-wsl-vscode-codex-windows | enginesなし。メタデータだけでは24互換を保証できない。build/testは未実施 |
| VS Code | User版1.139.1を登録情報で確認。アプリ内蔵Electron/Node自体はPC共通NodeのMSI更新対象外。タスク・拡張が外部nodeを呼ぶ場合の影響は別途あり得る |
| Hermes完成済みDesktop | 実行中のHermes.exeを確認。管理下Node26を消さない。MSI更新に合わせた強制終了・再インストールは行わない |

現在の代表コマンドの基準値：codex-cli 0.168.0、opencode 1.19.5、corepack 0.33.0、管理Node26.12.1、管理pnpm12.15.0。

Git Bashからbare corepack --versionは、C:\c\Program Files\...を参照して失敗した。node.exeとcorepack.jsの絶対パスで実行すると0.33.0を返したため、**更新前から存在するランチャー/パスの問題**として記録する。今回修正しない。

### 棚卸しの範囲と限界

探索rootはHermesリポジトリ、C:\Users\nekol\projects、Documents、Desktop。深さ4までで、依存・生成物・会話・記憶・キャッシュ等のフォルダとリンク/ジャンクションは除外した。Obsidianは探索・存在確認をしていない。

C:\Users\nekol\scripts内の対象拡張子ではNode関連参照は見つからなかった。実行中のnode.exe等の専用プロセス、およびnode/npm等を直接実行するタスクスケジューラのActionは確認時に見つからなかったが、間接起動・別名実行まで不存在を証明するものではない。

未指定のE側プロジェクト、別ユーザー、WSL内、他アプリの秘密を含むMCP設定、VS Codeの全拡張、常駐サービス全体は未監査。PC内の全Node利用を完全に網羅したとは言わない。追加対象があれば具体的な場所の許可後に確認する。

## 4. 更新先・チェックサム・署名

| 用途 | 版 | 取得元 | 検証 |
|---|---|---|---|
| 更新用 | 24.22.3 LTS x64 | https://nodejs.org/dist/v24.22.3/node-v24.22.3-x64.msi | 公式SHA-256一致、Authenticode Valid／OpenJS Foundation |
| 復旧用 | 22.17.0 x64 | https://nodejs.org/dist/v22.17.0/node-v22.17.0-x64.msi | 公式SHA-256一致、Authenticode Valid／OpenJS Foundation |

SHA-256：

```text
node-v24.22.3-x64.msi
4a1ab5bdec5434bae58efae6c3e5077a011f6f1e76d2b47b7b10af043f7db545

node-v22.17.0-x64.msi
896ff4a1aff30468e93e77a8884bb1aec466df7febf08daaa1d22dd5e4b14756
```

照合元は各版のnodejs.org/dist/<version>/SHASUMS256.txt。PGP署名によるSHASUMSファイルの独立検証は未実施だが、HTTPSで取得した公式チェックサムとWindows署名を確認した。

ダウンロード先はナユタ専用scratchのnode24-preflight/installers。まだMSIは実行していない。scratchは一時保存であり、後日実施ならファイルの再存在確認・ハッシュ照合と、必要に応じた再取得を行う。

## 5. 予定する変更範囲と戻し方（未承認・未実施）

変更候補：Program Files\nodejs、NodeのWindows Installer登録、MSI機能に含まれるPATH登録・ショートカット等。標準構成では同梱npm/Corepackも対象になる。Roamingグローバルパッケージ、Hermes管理Node/npm/pnpm、Bot設定、他ランタイムは変更しない。ネイティブモジュール再buildやパッケージ更新で直し込まない。追加のPython/Visual Studio Build Tools等を入れる『Tools for Native Modules』も実行しない。

承認後に行うなら、実施直前にNode/npmの実体、MSI機能、machine/user PATH、グローバル一覧を控え、更新用/復旧用MSIを再検証する。本人が承認した時間帯にUAC操作を挟み、新MSIを実行する。Hermesや他アプリの終了・再起動が必要なら別途本人に確認する。

問題発生時は、管理者操作で24のNode MSI製品をアンインストールし、確保した22.17.0 MSIを再インストールする。旧版MSIをそのまま重ねれば必ずdowngradeできるとは扱わない。保存した機能・PATH状態と比較して戻し、node/npmの絶対パスと通常シェルでの解決、代表CLIを再確認する。Roaming・Hermes管理ツールを削除しない。アンインストール/再インストールは今回実行しておらず、復旧成功を保証したものではない。

22.17.0は古いパッチ版なので、これは不具合時の一時復旧用であり、最新22系への安全更新を同時に行う許可ではない。新24系でnative addon ABIが合わない場合も、この依頼では勝手に再buildせず戻す方針。

更新後の確認候補：
1. 新しい通常シェルでnode -v、npm -v、where node/npm/npx。Program Filesのnodeが24系であること。
2. Program Files版npm、Hermes管理npm、Roaming版npmを区別し、それぞれの版・一覧を照合。
3. codex --version、opencode --version、corepackの絶対パス起動。
4. 10 BotのMCP登録状態が変わっていないこと。現時点で接続対象は0件なので、新規MCPは追加しない。
5. Hermes管理Node26/pnpm12の版を保持していること。ソースbuildやnpm installはしない。
6. 小さなローカルNode smoke testと、本人の実利用で問題があれば停止・復旧。未許可の外部サービス接続はしない。

## 承認前の残る判断

- 標準Node MSIに同梱されるnpm10.9.2→11.19.1とCorepack機能の置換を、今回の例外として含めるか。Node実行ファイルだけを厳密に変更する場合、標準MSIをそのまま使う案とは分けて再設計が必要。
- 未指定E側やWSL等にNode利用プロジェクトがあれば、追加確認する正確な場所。今回の限定棚卸しで進めるか。
- 実施時刻とUACの本人操作。現時点の依頼は事前確認段階なので、まだ更新許可として扱わない。

## 証拠と参照

ローカル証拠：
`C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\cache\scratch\node24-preflight\`

mcp-profiles.json、plugin-mcp.json、global-manifests.json、projects.json、commands.json、msi-features.json、installer-verification.json、取得MSIと公式SHASUMSを保存。署名はGet-AuthenticodeSignatureで両ファイルValidを確認した。

公式情報：
- https://nodejs.org/dist/index.json
- https://nodejs.org/en/blog/release/v24.22.3
- https://nodejs.org/dist/v24.22.3/SHASUMS256.txt
- https://nodejs.org/dist/v22.17.0/SHASUMS256.txt

Hermes実装：tools/mcp_tool_config.py、package.json、apps/desktop/package.json、website/package.json。
