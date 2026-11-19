# holmes 自己プロフィールの全文写し

コピー日時：2026-11-19T01:17+09:00

正本は `C:\Users\nekol\AppData\Local\hermes\profiles\holmes\` の各ファイルです。このE側の同名ファイルはコピー時点の全文写しです。秘密情報の値を含まないことを確認し、SOUL.md・config.yaml・profile.yaml をバイト単位で一致確認しました（SHA-256 先頭16桁：SOUL.md `8b00ee98f5c19f9d`、config.yaml `8d99bdfca0440a34`、profile.yaml `488f12b9763bded4`）。今後の常時一致を保証するものではありません。

`.env`、`auth.json`、その他認証ファイル、`memories/` はここへコピーしていません。認証は OpenCode Go のログインを共有しており、値は扱っていません。記憶は日次ZIPへ委ねる方針ですが、新規プロフィールのZIP収録は未確認です。

## 初回配置（2026-11-19）

- 本人の依頼（名前・役割・情報源フォルダの恒常読み取り許可）で Fresh profile `holmes` を作成した直後の写し。
- モデルは `deepseek-v4.1-flash`／`opencode-go`（API方式 `chat_completions`）。設定は `hermes config set` 経由で反映し、読み戻しで確認済み。
- 作成中に `gemini-3.8-flash` を試したが OpenCode Go の対象外（HTTP 400）だったため、本人の選択で `deepseek-v4.1-flash` に戻した。戻した後の状態を写している。

## config.yaml 更新確認（2026-11-19、モデル変更）

- コピー日時：2026-11-19T01:30+09:00
- 正本：`C:\Users\nekol\AppData\Local\hermes\profiles\holmes\config.yaml`。C側が正本で、このE側ファイルは今回の全文写しです。
- 本人の指定でメインのモデルを `deepseek-v4.1-flash`（`chat_completions`）から `gpt-6-luna`／`opencode-go`（`codex_responses`）へ変更したことに伴う追随。差分は `model` の2キー（default・api_mode）のみ。
- 秘密情報の値の混入を検査し（秘密らしいキーなし）、コピー時点のバイト一致（SHA-256 `506294def2a1b77afb1dfb6fe37fb94316fa721f7bd0dbf6ad25cdc5b61974eb`、859バイト）を確認。
- この追記の更新対象は config.yaml のみです。SOUL.md・profile.yaml の写しは初回配置時点のままで、今回の確認日へ置き換えません。

