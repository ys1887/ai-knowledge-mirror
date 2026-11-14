# Codex Skills Library

このリポジトリは、再利用可能な Codex スキルを一元管理するための場所です。

## スキル一覧

- `backup-codex/`: 日次バックアップ相当を任意タイミングで手動実行するスキル（出力先: `E:\Documents\Backup`）。
- `backup-ubuntu/`: 週次フルバックアップ相当を任意タイミングで手動実行するスキル（出力先: `E:\Documents\Backup`）。
- `book-ocr-gemini/`: Geminiで書籍画像/PDFをOCRし、改行整形とページ統合を行ってMarkdown化するスキル。
- `brainstorming/`: アイデアを実装可能な設計案へ整理し、選択肢とトレードオフを明確化するスキル。
- `chatgpt-conversations-md-export/`: ChatGPTエクスポートJSONを年/月Markdownへ変換し、期間指定と重複回避で増分出力するスキル。
- `epub2pdf/`: EPUB を PDF に変換するための手順とスクリプト。
- `iching-divination/`: 易経占いプロジェクトの資料を参照して、占い本文をチャット出力するランチャースキル。
- `iching-sdk/`: `iching-sdk` プロジェクトのCLIと素材を使うSDK版の易占いランチャースキル。
- `md-combine/`: 複数Markdownの結合、見出し1段降格（コードフェンス除外）を定型化するスキル。
- `nano-banana/`: Gemini Imagen で画像生成を行うスキルと関連ドキュメント。
- `pdf2md/`: ローカルツール（pdftotext + OCRフォールバック）でPDFをMarkdown化する全自動スキル。
- `pdf2md-gemini/`: Gemini APIでPDF/画像を原文忠実にMarkdown化する全自動スキル。
- `prompt-refine-loop-gemini/`: Gemini Developer APIを使い、入力プロンプトを反復改善して最終版へ収束させるスキル。
- `safe-git-publish/`: シークレット漏えいとブランチ運用を意識した安全な commit/push フロー。

各スキルフォルダはドキュメントとスクリプトを独立して持つため、単体で改善しやすく、同一リポジトリ内で一貫して管理できます。

## Source of Truth / Runtime Rule

- 開発正本はこのリポジトリ `E:\Documents\Playground\lib-skills`。
- runtime 配布先は Windows 側 `C:\Users\nekol\.codex\skills` を既定とする。
  - WSL 側 `/home/ys/.codex/skills` は、WSL runtime support がまだ必要な場合、または明示依頼がある場合のみ対象にする。
- 正本は常に `E:\Documents\Playground\lib-skills` 側で、runtime 側は配布先としてのみ扱う。
- `.codex` 全体同期は行わず、`skills/` のみを明示 publish する。

## Daily Workflow (Windows Runtime Publish)

1. このリポジトリで skill を編集
2. 変更確認
   - `git status -sb`
   - `git diff --stat`
3. 必要なら validator 実行
4. dry-run publish
   - Windows-native publish helper or explicit copy to `C:\Users\nekol\.codex\skills`
5. 実 publish
   - Windows runtime `C:\Users\nekol\.codex\skills` へ反映
6. verify
   - Codex Desktop で対象 skill が読み込まれることを確認
7. WSL 側 publish / verify は WSL runtime support がまだ必要な場合のみ行う
8. 必要なら Codex Desktop を再起動して反映確認
9. GitHub へ commit / push

## Operating Rule (Important)

- 日常の編集・commit・push はローカル `lib-skills-codex` で行う
- 保存先/基準（GitHub正本）は `origin/main`（`ys1887/lib-skills-codex`）
- ローカルは日常編集を行う作業コピーとして扱う

## Important Notes

- branch への push は作業保存であり、反映完了ではない
- 反映完了の定義は `main` への反映 + `origin/main` への push
- 未commit/未push の変更は GitHub には存在しない（PC故障時に復元不可）
- ローカルでの削除・変更は `commit + push` するまで GitHub に反映されない
- 大きな削除前は必要に応じてバックアップブランチを作成する
  - 例: `git branch backup-YYYYMMDD`
- `git pull` は `--ff-only` を推奨
  - 例: `git pull --ff-only`
- 完了確認の目安:
  - `git branch --show-current`
  - `git rev-list --left-right --count origin/main...main`
- シークレット（`.env`、トークン、認証情報）は Git に含めない

## セキュリティメモ

- このリポジトリには `.env.example` のみ含めます。
- 実キーやローカル実行ファイルは `.gitignore` で除外します。
