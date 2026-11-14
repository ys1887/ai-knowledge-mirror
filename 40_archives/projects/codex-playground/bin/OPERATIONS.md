# Operations Runbook

このファイルは `E:\Documents\Playground\bin` の運用チェックと復旧手順をまとめたものです。

## Scope
- 同期方針:
  - skill の開発正本は `E:\Documents\Playground\lib-skills`
  - runtime 配布先は `C:\Users\nekol\.codex\skills`
  - Windows ネイティブ環境から runtime へは `skills\` のみ明示 publish する
  - `.codex` の state (`auth.json` / `config.toml` / `sessions/` / `sqlite/` など) は同期しない

## Daily Check
1. 必要な runtime skill の整合確認:
   - `py E:\Documents\Playground\bin\codex-verify-skill-runtime skill-creator-codex ekikyo`
2. 期待結果:
   - 対象 skill が `OK runtime skill` になる
   - `--all` は未配布 skill も検出するため、必要時だけ使う

## Skill Runtime Workflow
1. skill を `E:\Documents\Playground\lib-skills` で編集
2. 必要なら validator を実行
3. dry-run publish:
   - `py E:\Documents\Playground\bin\codex-publish-skill --dry-run <skill>`
4. 実 publish:
   - `py E:\Documents\Playground\bin\codex-publish-skill <skill>`
5. verify:
   - `py E:\Documents\Playground\bin\codex-verify-skill-runtime <skill>`
6. 必要なら Codex クライアントを再起動して反映確認

## Logs
- 現在このフォルダ内に定期実行タスク用ログはありません。
- ChatGPT 会話エクスポートは独立ツールです。

## Recovery
1. Skill runtime の整合確認:
   - `py E:\Documents\Playground\bin\codex-verify-skill-runtime <skill>`
2. 差分がある場合は dry-run で内容確認:
   - `py E:\Documents\Playground\bin\codex-publish-skill --dry-run <skill>`
3. 問題なければ publish:
   - `py E:\Documents\Playground\bin\codex-publish-skill <skill>`
4. 再 verify:
   - `py E:\Documents\Playground\bin\codex-verify-skill-runtime <skill>`

## Notes
- ChatGPT 会話エクスポートは独立ツールであり、skill runtime の publish / verify とは別運用。
- WSL runtime へ配布する場合は、`--dest \\wsl.localhost\Ubuntu\home\ys\.codex\skills` を明示指定する。
