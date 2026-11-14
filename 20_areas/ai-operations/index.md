# ai-operations（Area）

AI の運用そのものに関する責任領域です。終わりのない維持の対象をここに置きます。

- 現在の状態：運用中
- 最終確認日：2026-11-14
- 次の節目：Hermes への引き渡し文の送付（`10_projects/hermes-operations.md` を参照）

## 中身

| 置き場 | 内容 |
|---|---|
| `agents/` | AI と Bot の登録簿（index）と、各 AI の profile と settings。settings-index もここ |
| `logs/` | 参加者ごとの記録。各自は自分のフォルダだけに書きます。個々の記録は書き換えず、古さだけを理由に Archives へは移しません |
| `outputs/` | Hermes Bot ごとの成果物。各 Bot の名前のフォルダが、その Bot の領域です |
| `scripts/` | PC 用スクリプトの正本。実行用コピーは PC の `C:\Users\nekol\scripts` |
| `pc-environment.md` | PC 環境の状態の要約。計測の正本はスペース「Muse の PC 環境」 |
| `context-patrol-runbook.md` | コンテキスト巡回（0:00 / 12:00）の手順書（正本）。ジョブの定義側は要約だけを持ちます |
| `context-patrol-state.md` | コンテキスト巡回の状態の要約（情報源ごとの最終成功時刻と実行概要）。Hermes 側との共有用で、巡回のたびに更新。実行記録は `logs/ada/context-patrol-log.md` |
