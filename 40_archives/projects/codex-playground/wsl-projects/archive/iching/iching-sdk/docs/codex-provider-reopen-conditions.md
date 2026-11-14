# Codex Provider Reopen Conditions

## Current Freeze

`iching-sdk` 本体の追加改修は当面止める。

理由:

- preflight probe
- `run.json` 診断強化
- failure 代表症状分類
- repo-local `AGENTS.md`

まで入れた時点で、追加観測の主問題が `codex exec` runtime 側に寄ったため。

## Reopen Triggers

再開してよい条件は次のどちらか。

1. `.codex` もしくは runtime の state / snapshot 書き込み条件が改善したセッションを得た
2. OpenAI / Codex CLI 側で関連修正または公式 guidance が入った

再開しない条件は次のとおり。

- preflight が引き続き `readonly filesystem` または `state db open failure` で落ちる

## First Checks After Reopen

再開時の最初の確認順は固定する。

1. short probe 1 本

```bash
printf 'Reply with exactly OK.\n' | codex exec --sandbox workspace-write -
```

2. `tests/fixtures/extract_cases/test_1.md` 1 本

```bash
python3 ./iching run \
  --input tests/fixtures/extract_cases/test_1.md \
  --profile honda \
  --provider codex
```

3. その 2 本が preflight を通った場合のみ `test_2`
4. `takashima` や重いケースはその後

## Decision Matrix

### Case A: preflight failure

- meaning: runtime 前段の filesystem / state 問題が継続
- action: `iching-sdk` は触らず、OpenAI 側報告を更新して停止

### Case B: preflight success / full run failure

- meaning: 本実行、streaming、connection 層でだけ失敗している
- action: profile 評価には進まず、runtime 本実行依存の問題として継続切り分け

### Case C: full run success

- meaning: minimal provider path が回復した
- action: 初めて `test_2` を次候補にする

## Explicit Non-Goals Until Reopen

再開条件を満たすまで、次は行わない。

- provider 回避ロジックの追加
- `CODEX_HOME` 迂回の複雑化
- profile 再調整
- 重いケースの追加実験
