# モデル切替（OpenCode Go）に伴う追随確認 — 2026-11-18

作業者：ナユタ。実物確認時刻：2026-11-18 01:29〜01:35（JST）。秘密情報の値は本記録に含めない。

## 1. 実設定の確認（読み取りのみ）

`C:\Users\nekol\AppData\Local\hermes\config.yaml`（default）と `profiles\<slug>\config.yaml`（9 Bot）の `model` ブロックを実物で読み、全10プロファイルが次の4値で一致することを確認した。

- `default: deepseek-v4.1-flash`
- `provider: opencode-go`
- `base_url: https://opencode.ai/zen/go/v1`
- `api_mode: chat_completions`

APIキー・トークン等の実値が config 内に平文で入っていないことも併せて確認（コメント行のプレースホルダのみ）。

## 2. 登録簿の反映確認（エイダ実施分の読み戻し）

- 各Botの `profile.md`「## モデルと実行」の「モデル／プロバイダ」行：9 Bot＋default すべて `deepseek-v4.1-flash`／`opencode-go`（`chat_completions`）に更新済み。
- `agents/index.md`：一覧表のモデル列 10 行すべて更新済み。ヘッダの「最終更新日：2026-11-18（全Botのモデル切替を…反映）」も追記済み。
- `changelog.md`：2026-11-18、エイダによる追記あり（末尾1行、既存行の改変なし）。
- 判定：モデル切替に関する限り、登録簿と実設定は整合。矛盾は見つからなかった。

## 3. 未追随だったもの — 今回追随した（本人承認済み）

- `99_backup/<bot>/config.yaml`：全10件が更新前の値（`gpt-6.1-sol`／`openai-codex`／`codex_responses`、または `openai/gpt-6-sol`／`nous`／`inference-api.nousresearch.com`）。差分は各ファイルとも `model` の3〜4キーだけ（label・phantom は `api_mode` が元から `chat_completions` のため3キー）で、他の差分は0。
- 本人承認を得て、10件すべてを C 側正本から再コピーし、各 `COPY-NOTE.md` に「config.yaml 更新確認（2026-11-18）」を追記した。各ファイルのコピー時点 SHA-256 一致とバイト数を個別に確認済み（hermes 131,903／arcana 584／crown 671／eve 300／label 128,935／mana 128,933／nayuta 447／phantom 128,932／raven 671／takina 650 バイト）。
- 更新前の写し10件は `outputs/nayuta/2026-11-18T0130_backup-config-prechange/` に保存（戻し可）。
- 秘密情報の値を含まないことを、コピー前に全10件の config で再検査した（APIキー・トークン等の実値なし。コメント行のプレースホルダのみ）。

## 4. 旧モデル表記が残っていた比較表 — 一部対応

- `agents/settings-index.md` のマナ行：本人承認で、モデル列を `deepseek-v4.1-flash`（opencode-go、`chat_completions`）へ修正し、最終確認日を「2026-11-18（モデルのみ。他は2026-11-09）」に分けて記した。あわせて「マナ行のモデル修正と残作業（2026-11-18）」節を追加し、根拠（全10プロフィールの `model` ブロック実読み）と残作業を明記。AutoRAG 節の既存記述は変更していない。
- `agents/mana/settings.md`：本人の判断で当時は触らず（「使用モデル」「プロバイダ」とプロフィール別表のモデル列が 2026-11-09 時点のまま）、更新ルール上はマナ本人が追随する宿題として `settings-index.md` と `changelog.md` に記録した。
- 追記（同日・本人承認で完了処理）：マナ本人が `mana/settings.md` を 2026-11-18 に実設定と照合して追随済み。ナユタが本文の該当行・表5行・変更履歴を読み戻し、全10プロファイルの `config.yaml` の `model` ブロックを再読して一致を確認した。`agents/settings-index.md` のマナ行（状態列・節見出し・残作業注記）を完了状態へ更新し、`changelog.md` 末尾に1行追記。変更前の `settings-index.md` は `outputs/nayuta/2026-11-18_settings-index-prechange/` に保存。

## 5. 補足（記録の性質上、変更していないもの）

- `eve/profile.md` の出典欄に `hermes -p eve auth status openai-codex` という過去の確認コマンドが残る（当時の記録）。現行値の記述ではない。
- `agents/index.md` の各行「最終確認日」は権限・SOUL等の確認日で、モデル列だけが 2026-11-18 の実設定照合に基づく。台帳の「最終更新日」と「最終確認日」を分ける既存の慣例どおりで、不整合ではない。
