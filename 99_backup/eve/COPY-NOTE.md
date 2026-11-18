コピー日：2026-11-14
C:/Users/nekol/AppData/Local/hermes/profiles/eve/ が正本です。このフォルダは作成時の全文写しです。秘密情報・認証ファイル・記憶は含めません。

## config.yaml 更新確認（2026-11-17）

- コピー日時：2026-11-17T13:35:49+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\eve\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人承認で skills.write_approval・memory.write_approval を true に変更。秘密情報の値を検査し、config.yaml のコピー時点バイト一致を確認。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は上の従来記録のままで、今回の確認日へ置き換えません。


## AutoRAG MCP登録に伴うconfig写し更新（2026-11-17）

- コピー日時：2026-11-17T18:58:17.475006+09:00
- C側正本：`C:/Users/nekol/AppData/Local/hermes/profiles/eve/config.yaml`。このE側ファイルはコピー時点の全文写しです。
- 本人承認でautoragのMCP登録とconnect_timeout=180を追加。元のモデル・スキル・承認設定は不変。全フィールドの秘密値確認後に全文コピーし、正本とのバイト一致を確認。
- MCP登録は成功しましたが、初回refreshはMinSync導入時のtarエラーで停止し、検索運用は未確認です。
- 今回の更新はconfig.yamlとこの注記のみ。SOUL.md・profile.yamlの写しの確認日は変更しません。


## AutoRAGアンインストールに伴うconfig写し更新

- コピー日時：2026-11-17T23:44:37.625661+09:00
- C側正本：`C:/Users/nekol/AppData/Local/hermes/profiles/eve/config.yaml`。このE側ファイルはコピー時点の全文写しです。
- 本人承認でmcp_servers.autoragを削除。設定値の差分はこの登録削除のみ（空のmcp_servers節もCLIが除去）。秘密値チェック後にconfig.yamlを全文コピーし、正本バイト一致を確認。
- SOUL.md・profile.yamlの写し、台帳・changelogはナユタでは更新しません。共有台帳・changelogはエイダ担当です。

## config.yaml 更新確認（2026-11-18）

- コピー日時：2026-11-18T01:30:00+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\eve\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人が OpenCode Go を契約し、全 Bot のモデルを `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）へ切り替えたことに伴う追随。差分は `model` の4キー（default・provider・base_url・api_mode） のみ。
- 秘密情報の値の混入を検査し（APIキー・トークン等の実値なし）、コピー時点のバイト一致（SHA-256 先頭16桁 `c1a0ec3e76c77ae1`、300バイト）を確認。更新前の写しは `20_areas/ai-operations/outputs/nayuta/2026-11-18T0130_backup-config-prechange/` に保存。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しの確認日は従来記録のままで、今回の確認日へ置き換えません。
