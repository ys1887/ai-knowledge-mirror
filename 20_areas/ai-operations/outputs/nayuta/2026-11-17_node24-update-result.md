# PC共通Node.js 24系への更新結果

実施日：2026-11-17。本人承認済みのProgram Files側Node・同梱npm・Corepackのみ更新。RoamingとHermes管理分は更新対象外。

## 実行結果

- 公式 `node-v24.22.3-x64.msi` を再ハッシュ照合し、Windows署名Validを確認後、UACを介して実行。
- MSI終了コード：**0**。
- MSI結果の再起動要求：**なし**。PC再起動は行っていない。
- Windows Installer登録は24.22.3に変わり、旧22.17.0のNode製品登録は残っていないことを確認。
- 更新後のProgram Files側は以下のとおり。

| 項目 | 変更前 | 変更後 |
|---|---|---|
| Node.js | 22.17.0 | **24.22.3** |
| 同梱npm（npm-cli.jsの直接呼出し） | 10.9.2 | **11.19.1** |
| Corepack | 0.33.0 | **0.36.0** |

Node実行先は `C:\Program Files\nodejs\node.exe`。

## PATH・npm表示の注意

MSIはmachine PATHのNode項目、user PATHのRoaming npm項目を末尾へ再配置した。項目の追加・削除はなく、それ以外の項目同士の順序は維持されていることを比較確認した。手動でPATHを書き換えてはいない。

レジストリのmachine/user PATHを使って新しく起動した検査用PowerShellでは、nodeの解決先がProgram Files、npm.cmdの解決先もProgram Filesであることを確認した。ただし **npm -vの表示は11.2.0** だった。

これは `C:\Program Files\nodejs\npm.cmd` が既存prefix内のnpmを優先する実装で、Roaming側の既存npm11.2.0を選んだため。同梱npm自体はnode.exeから `node_modules/npm/bin/npm-cli.js --version` を直接呼び、11.19.1と確認した。

Hermes内terminalでは別管理のnpm12.0.2が優先されるため、`node -v` は24.22.3、`npm -v` は12.0.2。更新前のNode/npm非対応警告はこの組合せの版表示確認では出なかった。

Roaming・Hermes管理分を変えない条件に従い、npmの優先経路を追加で調整してはいない。

## 動作確認

| 確認 | 結果 |
|---|---|
| 新しい検査用シェルのnode/npm解決と版 | 終了0。Node24.22.3、npm表示11.2.0、上記経路を確認 |
| Codex CLI起動 | `codex-cli 0.168.0`、終了0 |
| OpenCode CLI起動 | `1.19.5`、終了0 |
| CorepackのWindowsランチャー起動 | `0.36.0`、終了0 |
| ローカルNode smoke test | 終了0。UTF-8ファイル読み書き、SHA-256、TLSコンテキスト作成、URL処理を確認。ネット接続なし |
| グローバルnpm一覧 | 終了0。Roaming側7パッケージの版を維持 |
| Hermes CLI | v0.23.2、終了0 |
| Hermes管理Node/pnpm | 26.12.1／12.15.0のまま |
| 10 Botのconfig.yaml | 前後SHA-256一致 |

全10プロフィールのMCP登録は事前確認時点で0件、configも未変更のため、新規MCP接続や外部サービス認証の試験はしていない。autoragは追加していない。

Hermesソース開発環境はNode26以上を要求するため、管理版26を残している。Node24でHermesソースのnpm install/buildやnative addon再buildは行っていない。個別プロジェクトの本格的なbuildや、実アカウント接続までの互換性保証ではない。

事前確認で見つかったGit Bashのbare corepackランチャー問題は更新前からのもの。今回の確認はWindowsランチャーと絶対パスの実体で行い、既存のシェル設定を修正していない。

## 対象外を変更していないことの確認

- Roaming\npm配下：**8,024ファイル**をハッシュ照合。追加・削除・内容変更なし。
- Hermes tools配下：**1,416件の実行ファイル・ランチャー・package.json**をハッシュ照合。追加・削除・内容変更なし。
- 全10 Botのconfig.yaml：前後一致。
- Roamingの他パッケージ、Hermes管理Node/npm/pnpm、Python等の他ランタイムを更新する操作はしていない。
- autorag、索引、Jikji、Bot設定・認証・SOUL・99_backup写し、日次バックアップ処理は未変更。

検証範囲で更新に起因する不具合は見つからなかったため、ロールバックは行っていない。

## 復旧資料

一時scratchから、以下のナユタ専用の保存先へ更新用・旧版MSIと変更前状態を保存した。

`C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\backups\node24-20261117-1414\`

主な記録：
- `node-v24.22.3-x64.msi`：実行した更新用MSI。
- `node-v22.17.0-x64.msi`：復旧用旧版MSI。
- `before.json` / `after.json`：版、PATH、保護対象ファイル・configのハッシュ。
- `upgrade-msi.log` / `upgrade-result.json`：実行ログ・終了0。
- `verification.json` / `post-tests.json` / `smoke-result.json`：検証結果。

更新用SHA-256：
`4a1ab5bdec5434bae58efae6c3e5077a011f6f1e76d2b47b7b10af043f7db545`

旧版SHA-256：
`896ff4a1aff30468e93e77a8884bb1aec466df7febf08daaa1d22dd5e4b14756`

どちらもnodejs.org公式SHASUMSと一致し、AuthenticodeはValid／OpenJS Foundation。

復旧が必要になった場合は、本人の承認・UAC操作を挟んで24系のMSI製品をアンインストールし、保存した22.17.0 MSIを再インストールする。PATH・版・代表CLIを再確認し、Roaming/Hermes管理分を削除しない。今回は復旧操作自体は未実施。

## 関連資料

事前確認：`2026-11-17_node24-preflight.md`（同じoutputs/nayuta内）。

前回autorag事前確認への補足：Hermes MCPのbare node/npm/npxはPM管理版を選ぶ実装であり、PC共通Node22の不足だけをHermes MCPの起動不可理由とはしない。このNode更新はその区別を踏まえて本人が承認したPC全体の変更である。autoragのWindows動作・原本書込み回避等は別途判断のまま。
