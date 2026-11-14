# Provider Matrix Harness

`Codexアプリ固有` と `codex provider / 接続経路全体` を切り分けるための固定比較手順。

## Fixed Cases

共通テーマ:

- `今後の占い運用はCodexCLI中心に寄せるべきか、それともCodexアプリ中心を維持するべきか`

固定条件:

- workspace は `/home/ys/projects/iching-sdk`
- 新規セッションで実行する
- `Windows` 側パスは混ぜない
- まずは各条件 2 回、必要なら 3 回まで増やす

CLI で自動化する条件:

- `CodexCLI / 本田指定あり / 最終回答のみ`
- `CodexCLI / 本田指定なし / 最終回答のみ`

Codexアプリで手動記録する条件:

- `Codexアプリ / 本田指定あり / 最終回答のみ`
- `Codexアプリ / 本田指定なし / 最終回答のみ`

## Usage

プロンプトと記録シートだけ生成する:

```bash
python3 scripts/run_codex_provider_matrix.py --prepare-app-only
```

CLI 2 条件を 2 回ずつ実行し、同時にアプリ用記録シートも生成する:

```bash
python3 scripts/run_codex_provider_matrix.py --repetitions 2
```

出力先:

- `docs/comparisons/provider-matrix-2026-03-13/prompts/`
- `docs/comparisons/provider-matrix-2026-03-13/app-manual.md`
- `docs/comparisons/provider-matrix-2026-03-13/cli-results.json`
- `docs/comparisons/provider-matrix-2026-03-13/cli-results.md`

## Recorded Fields

CLI 側は次を自動集計する。

- 最終回答が保存されたか
- `provider` failure 相当ログが出たか
- `./iching run` 系へ入ったか
- ログ中に現れた主要ファイル
- 実行時間

Codexアプリ側は `app-manual.md` に次を手入力する。

- 最終回答まで出たか
- `provider` failure ログが出たか
- `./iching run` 系へ入ったか
- 読みに行った主要ファイル
- 補足メモ

## Interpretation

- CLI とアプリの両方で失敗が多い:
  - provider / 接続経路寄り
- アプリだけ失敗が多い:
  - アプリ経路寄り
- `./iching run` 系だけ失敗が多い:
  - ワークフロー選択寄り
- 本田指定ありだけ安定:
  - `iching-divination` / Honda 読解経路が当面の回避策
