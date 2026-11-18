# プロフィール全文写し

SOUL.md のコピー日：2026-11-16。config.yaml・profile.yaml のコピー日：2026-11-13。正本は C 側の Hermes プロフィール（`C:/Users/nekol/AppData/Local/hermes/profiles/arcana/`）であり、このフォルダの `SOUL.md`、`config.yaml`、`profile.yaml` は復旧・再構成用の全文写しです。原本変更時は秘密情報の値を再確認して自己写しを更新します。`memories/`、`.env`、`auth.json` は置きません。

config.yaml の写し更新日：2026-11-13。ユーザー指定のC側正本から再コピーし、当時のバイト一致を確認しました。今回更新したのは SOUL.md の写しだけで、config.yaml と profile.yaml の写しは変更していません。
2026-11-14：本人承認による現行閲覧範囲の修正後、C側正本のSOUL.mdを再コピーしました。config.yamlとprofile.yamlの正本は今回変更していません。
2026-11-14：本人承認による条件付きの易経KB参照規則の追加後、C側正本のSOUL.mdを再コピーし、バイト一致を確認しました。正本は引き続きC側です。config.yamlとprofile.yamlの正本・写しはこの作業では変更していません。
2026-11-16：本人承認による全種類の占断の年フォルダ保存への統一後、C側正本のSOUL.mdを再コピーし、バイト一致を確認しました。正本は引き続きC側です。config.yamlとprofile.yamlの正本・写しはこの作業では変更していません。

## config.yaml 更新確認（2026-11-17）

- コピー日時：2026-11-17T13:35:49+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\arcana\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人承認で skills.write_approval・memory.write_approval を true に変更。秘密情報の値を検査し、config.yaml のコピー時点バイト一致を確認。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は上の従来記録のままで、今回の確認日へ置き換えません。

## config.yaml 更新確認（2026-11-18）

- コピー日時：2026-11-18T01:30:00+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\arcana\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人が OpenCode Go を契約し、全 Bot のモデルを `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）へ切り替えたことに伴う追随。差分は `model` の4キー（default・provider・base_url・api_mode） のみ。
- 秘密情報の値の混入を検査し（APIキー・トークン等の実値なし）、コピー時点のバイト一致（SHA-256 先頭16桁 `29a44c80be5ca8f9`、584バイト）を確認。更新前の写しは `20_areas/ai-operations/outputs/nayuta/2026-11-18T0130_backup-config-prechange/` に保存。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は従来記録のままで、今回の確認日へ置き換えません。
