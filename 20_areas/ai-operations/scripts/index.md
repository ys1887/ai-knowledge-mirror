# scripts 一覧

- 置き場所：`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\scripts`（AI_knowledge 内。スクリプトの正本・保管の置き場。2026-11-12 に旧 `E:\Documents\AI\scripts` から正本を移し、2026-11-13 の PARA 移行で現在の場所へ移った）
- 実行：実行用コピーは `C:\Users\nekol\scripts` に置き、そちらで動かします。正本を更新したら、実行用コピーも合わせて更新してください（自動では同期されません）
- ルール：スクリプトを追加・移動・削除した側が、その作業の中でこの一覧も更新します。ログや `__pycache__` のような実行時の産物は、正本の置き場に入れません
- 最終更新：2026-11-14

| 名前 | 何をする | どう動く | ログ・状態 | 状態 |
|---|---|---|---|---|
| obsidian-backup | Obsidian の正本（`C:\Users\nekol\Obsidian`）を Cryptomator 保管庫（`Z:\Obsidian`）へ毎日ミラーコピーする（2段構成：`E:\Documents\Backup\Obsidian` へは常時、保管庫へは Z: があるとき） | Windows タスク「Obsidian Backup」で毎日 12:00 | ログは実行用コピーと同じフォルダの `obsidian-backup.log` | 正本はこのフォルダ（`20_areas\ai-operations\scripts\obsidian-backup\`）。実行用コピーは `C:\Users\nekol\scripts\obsidian-backup\` に配置済みで、タスクの向き先も 2026-11-12 に本人が C 側へ変更済みです。移設後の定刻実行は 2026-11-12 の回で成功を確認済みで、その後もミラーへの取り込みが続いていることを 2026-11-14 に確認しました。`E:\Documents\AI\scripts\obsidian-backup\` の実体は、2026-11-14 に `E:\Documents\AI` フォルダごと削除済みです |
| hermes-backup-daily.py | Hermes Agent の完全バックアップを作成し、検証して `Z:\HermesBackup` へ zip で出す（自動削除はしません） | Windows タスクで毎日 12:15 ごろ（`C:\WINDOWS\py.exe` がスクリプトを実行。引数は `C:\Users\nekol\scripts` の実行用コピーを向いている） | ログはスクリプト内の固定値 ROOT 配下の `hermes-backup-daily.log`。正本の ROOT は `C:\Users\nekol\scripts` に変更済みです。フォルダが無ければスクリプトが作り直します | 正本はこのフォルダ（ROOT を C 側へ書き換えた改訂版）。C 側への再コピーと、タスクの引数の向き先変更は、2026-11-12 に本人が実施済みです。新しい場所での定刻実行の成功は 2026-11-13 に確認済みで、2026-11-14 も当日の ZIP の生成を確認しました |

- simplelogin-mailbox-add は正本化の対象外として `E:\Documents\AI\scripts` に残置していましたが、12月の SimpleLogin 後片付けで使う場面がないと判断し、2026-11-14 に `E:\Documents\AI` フォルダごと削除しました
