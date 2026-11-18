# Hermes プロファイル別 config.yaml の全文写し

コピー日：2026-11-18。

正本は C 側の Hermes プロファイル（`C:/Users/nekol/AppData/Local/hermes/profiles/<name>/config.yaml`）であり、このフォルダ配下の各 `config.yaml` は復旧・再構成用の全文写しです。**C 側が正本で、こちらは写し**です。原本変更時はこの写しを更新します。`memories/`、`.env`、`auth.json`、`sessions/`、`skills/` は置きません（秘密情報と個人データを含むため）。

## 今回のコピー（2026-11-18T14:00:20+09:00）

| プロファイル | 変更内容（C側） | SHA-256 先頭16桁 | バイト | バイト一致 |
|---|---|---|---|---|
| nayuta | `delegation.max_concurrent_children=3`、`child_timeout_seconds=900`、`prefix_stagger_seconds=2`（前日までのモデル設定・`delegation.model=deepseek-v4.1-flash` を含む） | `1ae6964ae5f74b54` | 632 | 確認済み（`cmp` 一致） |
| mana | `delegation.provider=opencode-go`、`max_concurrent_children=5`、`child_timeout_seconds=900`、`prefix_stagger_seconds=2`、メイン `gpt-6-luna`／サブ `deepseek-v4.1-flash` | `4462934fec3480e7` | 129095 | 確認済み |
| arcana | メインを `gemini-4-argon`／`opencode-go`／`chat_completions` に手動変更（暫定）。`delegation.model` は未設定 | `a0808ce9e09cfc95` | 579 | 確認済み |

## 秘密情報の検査

3ファイルとも `api_key`／`token`／`secret` 等に実値なし（該当はコメント行と環境変数名のみ）。.env 由来の値は本書には含めていません。

## 注意

- この写しは「その時点の全文」です。以後の変更は自動追随しません。原本を変えたときに更新してください。
- ナユタ・マナのモデル／委譲設定の経緯は、親フォルダの `COPY-NOTE.md` にも記録があります。

## 全Bot分の写しを追加（2026-11-18T14:23:18+09:00）

本人の依頼により、残りのプロファイルも写しを追加・更新しました（9プロファイル全て、`cmp` でバイト一致を確認）。

| プロファイル | メイン | サブ（delegation.model） | 並列/タイムアウト | SHA-256 先頭16桁 | バイト |
|---|---|---|---|---|---|
| arcana | `gemini-4-argon` | `deepseek-v4.1-flash` | 2 / 900 | `75dabae4850604e7` | 735 |
| crown | `glm-5.3-flash` | `deepseek-v4.1-flash` | 2 / 900 | `fc65a6a94819873b` | 821 |
| eve | `deepseek-v4.1-flash` | `deepseek-v4.1-flash` | 2 / 900 | `431c65ad81726037` | 456 |
| label | `deepseek-v4.1-flash` | `deepseek-v4.1-flash` | 2 / 900 | `055fe9dccb78be74` | 129078 |
| mana | `gpt-6-luna` | `deepseek-v4.1-flash` | 5 / 900 | `4462934fec3480e7` | 129095 |
| nayuta | `deepseek-v4.1-flash` | `deepseek-v4.1-flash` | 3 / 900 | `1ae6964ae5f74b54` | 632 |
| phantom | `gemini-4-argon` | `deepseek-v4.1-flash` | 2 / 900 | `84e43a959bac1a9e` | 129070 |
| raven | `deepseek-v4-pro` | `deepseek-v4.1-flash` | 5 / 900 | `a1a7e85768040dba` | 852 |
| takina | `deepseek-v4.1-flash` | `deepseek-v4.1-flash` | 2 / 900 | `af46466268c51235` | 806 |

- 全プロファイル共通で `delegation.provider=opencode-go`、`reasoning_effort=medium`、`subagent_auto_approve=false`、`independent_completions=false`。
- `prefix_stagger_seconds=2` は mana・nayuta・raven のみ。
- 新モデル（`glm-5.3-flash`／`deepseek-v4-pro`／`gemini-4-argon`）は、いずれも単発の応答で疎通を確認済み。
- 追加・更新分の `api_key`／`token`／`secret` にも実値なし（コメント行のみ）。
- 前節の arcana で「`delegation.model` 未設定」と記録した箇所は、この時点で `deepseek-v4.1-flash` を設定済みです（上の表が最新）。
