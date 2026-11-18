# プロフィール全文写し

コピー日：2026-11-13。正本は C 側の Hermes プロフィール（`C:/Users/nekol/AppData/Local/hermes/profiles/mana/`）であり、このフォルダの `SOUL.md`、`config.yaml`、`profile.yaml` は復旧・再構成用の全文写しです。原本変更時は秘密情報の値を再確認して自己写しを更新します。`memories/`、`.env`、`auth.json` は置きません。

config.yaml の写し更新日：2026-11-13。ユーザー指定のC側正本から再コピーし、バイト一致を確認しました。SOUL.md と profile.yaml のコピー日は従来どおりです。
2026-11-14：本人承認による現行閲覧範囲の修正後、C側正本のSOUL.mdを再コピーしました。config.yamlとprofile.yamlの正本は今回変更していません。

## config.yaml 更新確認（2026-11-17）

- コピー日時：2026-11-17T13:35:49+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\mana\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人承認で skills.write_approval・memory.write_approval を true に変更。秘密情報の値を検査し、config.yaml のコピー時点バイト一致を確認。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は上の従来記録のままで、今回の確認日へ置き換えません。

## config.yaml 更新確認（2026-11-18）

- コピー日時：2026-11-18T01:30:00+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\mana\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人が OpenCode Go を契約し、全 Bot のモデルを `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）へ切り替えたことに伴う追随。差分は `model` の4キー（default・provider・base_url・api_mode） のみ。
- 秘密情報の値の混入を検査し（APIキー・トークン等の実値なし）、コピー時点のバイト一致（SHA-256 先頭16桁 `9b909e68e2d12c9b`、128933バイト）を確認。更新前の写しは `20_areas/ai-operations/outputs/nayuta/2026-11-18T0130_backup-config-prechange/` に保存。
## SOUL.md / config.yaml 写し更新（2026-11-18）

- コピー日時：2026-11-18T16:41:45+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\mana\`。`SOUL.md` と `config.yaml` はC側正本の全文写し。
- `config.yaml`：モデル（`gpt-6-luna`／`codex_responses`）、委譲設定、`approvals.deny` と `pre_tool_call` フックを現行正本に合わせて反映。ファイル道具で読み戻し、正本・写しの行数（2434）とサイズ（130870 bytes）が一致すること、変更箇所の値を確認。バイト単位のハッシュ照合はしていない。
- `SOUL.md`：99_backupへのターミナルからの直接操作を恒常禁止とし、写し更新はファイル操作道具で行う改訂を反映。ファイル道具で読み戻し、正本・写しの行数（51）とサイズ（10911 bytes）が一致すること、改訂箇所を確認。バイト単位のハッシュ照合はしていない。
- `config.yaml` の認証情報系の有効設定値を点検し、実値は見つからなかった（検出されたトークン関連の設定名は数値の上限値）。認証ファイルは含めていない。
- `profile.yaml` は今回の対象外で、未変更。
