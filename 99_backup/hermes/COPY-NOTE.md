# Hermes（default）のプロフィール全文写し

コピー日：2026-11-13。正本は C 側の Hermes プロフィール（`C:/Users/nekol/AppData/Local/hermes/`）であり、このフォルダの `SOUL.md`、`config.yaml`、`profile.yaml` は復旧・再構成用の全文写しです。原本変更時は秘密情報の値を再確認して自己写しを更新します。`memories/`、`.env`、`auth.json` は置きません。

## config.yaml 更新確認（2026-11-17）

- コピー日時：2026-11-17T13:35:49+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人承認で skills.write_approval・memory.write_approval を true に変更。秘密情報の値を検査し、config.yaml のコピー時点バイト一致を確認。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は上の従来記録のままで、今回の確認日へ置き換えません。

## config.yaml 更新確認（2026-11-18）

- コピー日時：2026-11-18T01:30:00+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人が OpenCode Go を契約し、全 Bot のモデルを `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）へ切り替えたことに伴う追随。差分は `model` の4キー（default・provider・base_url・api_mode） のみ。
- 秘密情報の値の混入を検査し（APIキー・トークン等の実値なし）、コピー時点のバイト一致（SHA-256 先頭16桁 `7288d4373f1bceb2`、131903バイト）を確認。更新前の写しは `20_areas/ai-operations/outputs/nayuta/2026-11-18T0130_backup-config-prechange/` に保存。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は従来記録のままで、今回の確認日へ置き換えません。

## config.yaml 更新確認（2026-11-18 その2）

- コピー日時：2026-11-18T13:56:38+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人の依頼により、ハーミーズ（default）へサブエージェント運用の推奨設定を適用。差分は `delegation` の5キーのみ：`model=deepseek-v4.1-flash`、`provider=opencode-go`、`reasoning_effort=medium`、`max_concurrent_children=2`、`child_timeout_seconds=900`。`prefix_stagger_seconds` は 0 のまま。
- 秘密情報の値の混入を検査し（`api_key`／`token` 等の実値なし。該当行はコメントと空値のみ）、コピー時点のバイト一致（SHA-256 先頭16桁 `b70edbd7da877dd0`、132046バイト）を確認。
- 同日、プロファイル側の設定も変更したが、本フォルダは default プロフィールの写しのみを扱うため、以下は**写しを更新していない**（記録のみ）：
  - `C:\Users\nekol\AppData\Local\hermes\profiles\nayuta\config.yaml` — `delegation.max_concurrent_children=3`、`child_timeout_seconds=900`、`prefix_stagger_seconds=2`（SHA-256 先頭16桁 `1ae6964ae5f74b54`、632バイト）
  - `C:\Users\nekol\AppData\Local\hermes\profiles\mana\config.yaml` — `delegation.provider=opencode-go`、`max_concurrent_children=5`、`child_timeout_seconds=900`、`prefix_stagger_seconds=2`（SHA-256 先頭16桁 `4462934fec3480e7`、129095バイト）
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は従来記録のままで、今回の確認日へ置き換えません。

## プロファイル別写しの追加（2026-11-18T14:00:20+09:00）

- 本人の依頼により `profiles/nayuta/config.yaml`、`profiles/mana/config.yaml`、`profiles/arcana/config.yaml` の全文写しを、このフォルダ配下の `profiles/<name>/config.yaml` として追加。3ファイルとも `cmp` でバイト一致を確認し、秘密情報の実値なしを検査済み。
- 詳細（ハッシュ・バイト数・変更内容）は `profiles/COPY-NOTE.md` に記録。C側が正本で、E側は写しという扱いは本フォルダと同じです。
