# crown 自己プロフィールの全文写し

コピー日時：2026-11-16T17:07:37.210644+09:00

正本は C:\Users\nekol\AppData\Local\hermes\profiles\crown\ の各ファイルです。このE側の同名ファイルはコピー時点の全文写しです。秘密情報の値を含まないことを確認し、SOUL.md・config.yaml・profile.yamlをバイト単位で一致確認しました。今後の常時一致を保証するものではありません。

.env、auth.json、その他認証ファイル、memories/はここへコピーしていません。記憶は日次ZIPへ委ねる方針ですが、新プロフィールのZIP収録は未確認です。

## config.yaml 更新確認（2026-11-17）

- コピー日時：2026-11-17T13:35:49+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\crown\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人承認で skills.write_approval・memory.write_approval を true に変更。秘密情報の値を検査し、config.yaml のコピー時点バイト一致を確認。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は上の従来記録のままで、今回の確認日へ置き換えません。

## config.yaml 更新確認（2026-11-18）

- コピー日時：2026-11-18T01:30:00+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\crown\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人が OpenCode Go を契約し、全 Bot のモデルを `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）へ切り替えたことに伴う追随。差分は `model` の4キー（default・provider・base_url・api_mode） のみ。
- 秘密情報の値の混入を検査し（APIキー・トークン等の実値なし）、コピー時点のバイト一致（SHA-256 先頭16桁 `9cf9154ffacaeac2`、671バイト）を確認。更新前の写しは `20_areas/ai-operations/outputs/nayuta/2026-11-18T0130_backup-config-prechange/` に保存。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は従来記録のままで、今回の確認日へ置き換えません。
