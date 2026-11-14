# Hermesの作業フォルダ移行記録

- 記録日：2026-11-09
- 記録者：マナ
- 目的：各AIが現行の構成・保存先を共有できるようにする。設定の正本は各アプリとWindowsタスクにある。

## 移行後の置き場

- AI間の共有情報：`E:\Documents\Google Drive\AI_knowledge\exchange\mana`。ここには構成・手順・結果だけを置き、認証情報の値やZIP、実行コードは置かない。
- 共通スキル `yomiyasu`：`E:\Documents\AI\skills\yomiyasu`。旧 `E:\Documents\Hermes Agent\shared-skills\yomiyasu` から43ファイルをコピーし、SHA-256で一致を確認。デフォルトHermes・mana・arcana・label・phantom の `skills.external_dirs` は `E:/Documents/AI/skills` に変更した。マナでは `skill_view` の実際の参照先も新フォルダと確認した。旧コピーはまだ残している。
- Hermes日次フルバックアップの実行スクリプト：`E:\Documents\AI\scripts\hermes-backup-daily.py`、ログ：同フォルダの `hermes-backup-daily.log`。
- 作業用ZIP：`E:\Documents\Backup`。この場所で `hermes backup --keep 0` のZIPを作り、CRC・必要ファイル・ルートSQLiteのquick_checkを検証する。
- 完成ZIP：解錠済みCryptomatorドライブの `Z:\HermesBackup`。検証済み作業用ZIPを `.partial` 名でコピーし、サイズとSHA-256を照合してから完成名に変更する。Zが見えない場合、スクリプトは実行前に失敗する設計であり、ログや作業用ZIPが残る場合がある。保管庫の解錠やクラウド同期そのものは未検証。
- Windowsタスク `Hermes-Agent-Full-Backup`：毎日12:15（日本時間）、ログオン中のみ、開始できなかったときは次の開始可能時点で実行。実行先を `C:\WINDOWS\py.exe` の引数 `-3.13 "E:\Documents\AI\scripts\hermes-backup-daily.py"`、作業フォルダを `E:\Documents\AI\scripts` に変更した。手動でタスクを起動し、`LastTaskResult=0` と新たな完成ZIPを確認。次の定刻自動実行はまだ未検証。

## 過去ZIPと保留物

旧 `E:\Documents\Hermes Agent\backups` の完成ZIP7件を `Z:\HermesBackup` へコピーし、ファイルごとのサイズとSHA-256一致を確認。旧側は削除していない。新スクリプトの直接実行とタスク経由の試行でも新たな完成ZIPをZへ作成した。ZIPは資格情報を含み得るため、AI_knowledgeには移していない。

`E:\Documents\Hermes Agent` 内の以下は現時点で残置する。旧バックアップZIPと旧スクリプト・ログ、旧共通スキル一式は移行確認用の退避。`mana` 内のyomiyasu取得ステージング、旧版ZIP、架空文テスト記録、`__pycache__` は作業・検査用であり、AI共通知識の正本として移さない。`arcana/2026-11-08_01.md` は個別の易占結果を含むため、共有知識置き場へ一括転載しない。`mana/SOUL.before-operations-update.md` は旧ルールの控えであり現行設定として扱わない。

`mana/obsidian-backup-report-2026-11-08.md` は個別バックアップの作業報告。2026-11-08の手動試行ではrobocopyコード3、最終失敗0、コピー24,320件だったが、この記録は現在の定刻実行結果を保証しない。スクリプト正本は `E:\Documents\Muse\script\obsidian-backup.cmd`。マナは `C:\Users\nekol\Obsidian` を個別許可なく閲覧・存在確認しない。詳細が必要な場合は、削除前にこの旧報告書を個別に保全するか相談する。

## 削除前の注意

`E:\Documents\Hermes Agent` 全体はマナが削除していない。利用者が削除する前に、必要な旧ログ、旧版ZIP、個別報告、易占結果の保全要否を判断すること。また、`Z:\HermesBackup` の中身がPC故障後にも回収できることと、次の定刻タスクが正常に動くことを別途確認する。旧フォルダを削除した後は、旧パスへの単純なロールバックはできない。
