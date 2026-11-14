# ekikyo-sdk

`./iching` CLI を使って、Takashima 専用の易占い `EXTRACT` ワークフローを回すための SDK です。

## Supported Surface

- `./iching resolve --input <path|-> [--mode extract]`
- `./iching select --input <path|-> [--mode extract] [--sources-root <dir>]`
- `./iching build-prompt --input <path|-> [--mode extract] [--sources-root <dir>]`
- `./iching answer --prompt <path|-> [--provider codex] [--codex-model <name>] [--codex-sandbox <mode>] [--codex-approval-policy <policy>] [--answer-preset codex-exec] [--answer-cmd <cmd> [args...]]`
- `./iching run --input <path|-> [--mode extract] [--out-dir <dir>] [--provider codex] [--codex-model <name>] [--codex-sandbox <mode>] [--codex-approval-policy <policy>] [--answer-preset codex-exec] [--answer-cmd <cmd> [args...]]`
- `./iching validate --mode extract --input <path|-> [--context <resolve.json|run.json>] [--sources-root <dir>] [--out-dir <dir>]`

## Contract

- `MODE` は `[MODE:EXTRACT]` のみを使います。
- `EXTRACT` では `[TEMPLATE:EX_SIMPLE]`, `[TEMPLATE:EX_5]`, `[TEMPLATE:EX_COMPARE]` を受け付けます。
- `EX_SIMPLE` と `EX_5` は Takashima 契約の見出し構造を使い、`run` の最終出力末尾に `## 高島解釈原文` を付けます。
- `EX_COMPARE` は比較占いの正規ルートです。
- 公開導線は Takashima-only です。

## Typical Usage

```bash
./iching run --input question.md
```

`run` は `resolve -> build-prompt -> answer -> validate` を順に実行し、`out/run/<timestamp>/` に次の artifact を保存します。

- `resolve.json`
- `select.json`
- `prompt.txt`
- `answer.md`
- `report.json`
- `evidence.json`
- `run.json`

## Input Shape

### EX_SIMPLE

- `### 1. 占いに至った背景・状況`
- `### 2. 易経への質問`
- `### 3. 占い結果入力`
- `本卦`
- `変爻`

### EX_5

- `EX_SIMPLE` の項目一式
- 必要に応じて `之卦`, `互卦`, `錯卦`, `綜卦`
- 補助卦は空欄や `なし` を許容します

### EX_COMPARE

- `### 1. 占いに至った背景・状況`
- `### 2. 易経への質問`
- `### 3. 占い結果入力`
- 候補 2 件以上
- 各候補に `本卦`, `変爻`

## Validation

- `EX_SIMPLE` と `EX_5` は、引用がなくても Takashima raw contract の見出しが揃っていれば `validate` を通せます。
- `EX_COMPARE` は比較候補ごとの citation 付き出力を前提にします。
- `tests/fixtures/extract_cases/manifest.json` と `docs/extract-acceptance.md` は、比較と acceptance の参照用です。
