# bin scripts

Windows ネイティブ環境で利用する手動運用スクリプトを管理するリポジトリです。  
WSL 依存のバックアップ・運用スクリプトは Ubuntu 削除準備に伴い整理済みです。

主な役割は次の2系統です。

- Codex skill runtime 運用
- ChatGPT 会話ログの Markdown 変換

## 手動実行スクリプト

### Skill publish / verify 系
- `codex-publish-skill`
  - `E:\Documents\Playground\lib-skills` を正本として、管理対象 skill を Windows runtime の `skills\` へ配布
  - 既定 source: `E:\Documents\Playground\lib-skills`
  - 既定 dest:
  - `C:\Users\nekol\.codex\skills`
  - `--all`、`--dry-run`、`--delete` に対応
  - `.system` は対象外
  - `runtime\windows\SKILL.md` がある skill は、その Windows runtime variant を配布
- `codex-verify-skill-runtime`
  - `lib-skills` と各 runtime copy の管理対象 skill 差分を確認
  - runtime 側の追加 skill は無視

### データ変換系
- `chatgpt-conversations/export_conversations_to_md.py`
  - ChatGPT `conversations.json` を `YYYY/YYYY-MM` 構成の Markdown へ変換
  - 詳細: `chatgpt-conversations/README.md`
  - 実行例: `py E:\Documents\Playground\bin\chatgpt-conversations\export_conversations_to_md.py --help`

## Skill 運用ルール

- 開発正本は `E:\Documents\Playground\lib-skills`。
- runtime 配布先は `C:\Users\nekol\.codex\skills`。
- 通常運用では `.codex` の全体同期を行わず、`skills/` だけを明示 publish / verify する。
- Windows 側 state (`.codex-global-state.json` / `config.toml` / `auth.json` / `sessions/` / `sqlite/` など) は publish / verify 対象にしない。
- runtime copy は配布先としてのみ扱い、正本として編集しない。
- WSL runtime へ配布する場合は、`--dest \\wsl.localhost\Ubuntu\home\ys\.codex\skills` のように明示指定する。

## 注意
- `codex-publish-skill --delete` は対象 skill ディレクトリ内だけを削除同期します。
- `__pycache__` や `.pyc` などの生成キャッシュは publish / verify 対象外です。

## 関連ドキュメント
- `AGENTS.md`: このフォルダ向けの運用・更新ポリシー
- `OPERATIONS.md`: 日次点検、障害時復旧、Windowsタスクの期待設定

実行例:
`py E:\Documents\Playground\bin\codex-publish-skill --dry-run skill-creator-codex`  
`py E:\Documents\Playground\bin\codex-publish-skill skill-creator-codex`  
`py E:\Documents\Playground\bin\codex-verify-skill-runtime skill-creator-codex`
