# iching-sdk

`iching-divination` のローカル素材を、`./iching` CLI から扱える SDK として整備する作業用リポジトリです。

現時点での主用途は、手元の Codex 環境で `iching` CLI を実行することです。二次用途として、同じ CLI を Claude Code など別ランタイムから呼べる状態を保ちます。

## MVP Scope

- 安定化対象は HTTP API ではなく `iching` CLI の入出力契約です。
- built-in provider は現時点では `codex` のみです。
- `sources/`, `rules/`, `prompts/`, `templates/` は外部ファイルとして保守し、コードへの埋め込みは最小限に留めます。
- packaging 用の配布導線はまだ整備せず、正式入口は repo 直下の `./iching` スクリプトです。

## 公開契約

`main` 取り込み前提で、現時点で互換維持対象とみなすのは次です。

- `./iching answer`
- `./iching run`
- `./iching validate --context <resolve.json|run.json>`
- `iching.toml` の `default_provider` と `[providers.codex]`

補足:

- CLI の引数、終了コード、artifact 名はこの README の記述を current contract とします。
- 旧 top-level `provider`, `codex_model`, `codex_sandbox`, `codex_approval_policy` は当面互換維持しますが、新規設定では推奨しません。
- built-in provider の追加、HTTP API、常駐サーバー化、GUI 統合は current contract に含めません。

## 現在のコマンド

- `./iching index --mode extract|general [--profile <name>]`
- `./iching resolve --input <path|-> [--mode extract|general] [--profile <name>]`
- `./iching select --input <path|-> [--mode extract|general] [--profile <name>] [--sources-root <dir>]`
- `./iching build-prompt --input <path|-> [--mode extract|general] [--profile <name>] [--sources-root <dir>]`
- `./iching answer --prompt <path|-> [--provider codex] [--codex-model <name>] [--codex-sandbox <mode>] [--codex-approval-policy <policy>] [--answer-preset codex-exec] [--answer-cmd <cmd> [args...]]`
- `./iching run --input <path|-> [--mode extract|general] [--profile <name>] [--out-dir <dir>] [--provider codex] [--codex-model <name>] [--codex-sandbox <mode>] [--codex-approval-policy <policy>] [--answer-preset codex-exec] [--answer-cmd <cmd> [args...]]`
- `./iching validate --mode extract|general --input <path|-> [--profile <name>] [--context <resolve.json|run.json>] [--sources-root <dir>] [--out-dir <dir>]`

## 最短運用

日常運用は `run`、prompt を途中で確認したいときだけ modular workflow を使います。

### 推奨最小 `iching.toml`

repo root に `iching.toml` を置くと、provider 既定値に加えて EXTRACT profile の既定値も共有できます。

```toml
default_profile = "legacy"

[providers.codex]
path = "/home/ys/.nvm/versions/node/v22.21.1/bin/codex"
model = "gpt-5"
sandbox = "workspace-write"
```

- 優先順位は `CLI > iching.toml > built-in default` です。
- `default_profile` は `index`, `resolve`, `select`, `build-prompt`, `run`, `validate` の EXTRACT 挙動に影響します。
- 新旧両方が同時にある場合は provider table 形式が旧 top-level 形式より優先されます。
- 将来の複数 provider 対応を見据えた形ですが、現時点で実際に使える built-in provider は `codex` のみです。
- 初期既定値は `legacy` です。split profile を使うときは `--profile honda` または `--profile takashima` を明示します。

### One-shot Workflow

```bash
./iching run --input question.md
```

- `run` は `resolve -> build-prompt -> answer -> validate` を順番に実行します。
- 入力本文には必ず `MODE` を明示します。`MODE` がない入力はエラーです。
- `EXTRACT` では `TEMPLATE` も必須です。暗黙フォールバックはしません。
- stdout には最終回答本文を出します。
- `--out-dir` 未指定時は `out/run/<timestamp>/` に `resolve.json`, `select.json`, `prompt.txt`, `answer.md`, `report.json`, `evidence.json`, `run.json` を保存します。
- `validate` が失敗した場合も回答本文と artifact は残りますが、終了コードは非 0 になります。
- `--provider codex` は SDK 内蔵の Codex provider を使い、`codex exec` を解決します。
- 優先順位は `--answer-cmd` > `--provider` > `--answer-preset` です。
- `approval_policy` は current Codex CLI 互換のため、現時点では標準 `codex exec` command に反映しません。

#### One-shot Success Example

```bash
cat > question.md <<'EOF'
[MODE:GENERAL]

易の考え方について短く説明してください。
根拠があれば validator 互換の参照行も付けてください。
EOF

./iching run --input question.md --out-dir /tmp/iching-example
echo $?
sed -n '1,120p' /tmp/iching-example/report.json
```

- exit code `0` なら回答生成と validate の両方が成功です。
- `report.json` の `evidence_status` が `sufficient` なら参照形式も通っています。
- 失敗時は `answer.md` と `report.json` を見れば、本文内容と validator の指摘を切り分けられます。

### Modular Workflow

```bash
./iching build-prompt --input question.md > prompt.txt
./iching answer --prompt prompt.txt > answer.md
./iching validate --mode general --input answer.md
```

- `answer` は artifact を持たず、stdout に回答本文だけを返します。
- `answer` の終了コードは成功 `0`、prompt 読み込み失敗または provider / preset / `answer-cmd` 解決失敗で `2` です。
- `--provider codex` は SDK が `codex exec` を組み立てて実行する標準入口です。
- `--codex-model`, `--codex-sandbox`, `--codex-approval-policy` は `--provider codex` 指定時だけ使えます。
- prompt には `## Selected Sources` セクションが入り、どの source files を見る前提かが分かるようになります。
- `answer.md` に validator 互換の参照行 `（参照：filename.md|section）` が含まれていれば、そのまま `validate` を通せます。
- EXTRACT の比較占いを後から厳密に再検証したい場合は、`resolve.json` か `run.json` を `--context` に渡します。
- 既存互換のため `--answer-preset codex-exec` も引き続き使えます。

#### Modular Success Example

```bash
cat > question.md <<'EOF'
[MODE:GENERAL]

易の考え方について短く説明してください。
根拠があれば validator 互換の参照行も付けてください。
EOF

./iching build-prompt --input question.md > prompt.txt
./iching answer --prompt prompt.txt > answer.md
./iching validate --mode general --input answer.md --out-dir /tmp/iching-validate-example
echo $?
sed -n '1,120p' /tmp/iching-validate-example/report.json
```

- exit code `0` なら validate まで成功です。
- `report.json` の `evidence_status` が `sufficient` なら参照形式も通っています。
- `./iching validate --mode extract --input answer.md --context out/run/.../run.json` の形にすると、EXTRACT 比較占いでも `run` と同じ文脈で再検証できます。

## provider failure の見方

provider failure の切り分けは、まず stderr の短い要約を見て、その後で必要なら `run.json` を確認するのが最短です。

- `run` の `--provider codex` は full prompt 実行前に短い preflight probe を行う場合があります。
- preflight で止まった場合、`error_summary` は `preflight failed: ...` で始まります。

- `codex executable not found`
  - `codex` CLI 未導入です。
- `codex authentication required`
  - 既知の認証不足パターンです。
- `codex CLI compatibility issue ...`
  - SDK の呼び方と local `codex exec` の受理引数がずれています。
- `codex sandbox or filesystem issue ...`
  - sandbox / state DB / snapshot / 書き込み権限系です。
- `codex connection issue ...`
  - websocket / HTTPS / stream 切断系です。
- `codex provider failed with exit code ...`
  - その他の provider 実行失敗です。

`run.json` では次の順に見ると切り分けが早くなります。

1. `final_status`
2. `error_source`
3. `error_type`
4. `preflight_ran` と `preflight_exit_code`
5. 必要なら `error_summary`, `preflight_stderr`, `error_stderr`, `runtime_diagnostics`

補足:

- provider failure 時も `run.json` は保存されます。
- `error_type` は `provider_missing`, `provider_auth`, `provider_cli_compat`, `provider_sandbox_or_fs`, `provider_connection`, `provider_execution_failed` のいずれか、または provider 非依存エラー時の `null` です。
- `error_source` は `provider`, `answer_command`, `runtime`, `config` のどこで失敗したかを表します。
- `error_summary` には代表症状が含まれ、たとえば `readonly filesystem`, `state db open failure`, `shell snapshot failure`, `stream disconnected`, `cli argument error` のように見分けやすくなります。
- `run.json` には `answer_command`, `provider`, `provider_options`, `resolved_codex_path`, `resolved_codex_version`, `preflight_*`, `runtime_diagnostics`, `hints`, selection 要約, validation 要約も残ります。

## Input Contract

- すべての入力で `MODE` を必須とします。
- 許可される `MODE` は `[MODE:EXTRACT]`, `[MODE:GENERAL]` です。
- `MODE` marker は最初の非空行にのみ置けます。本文の途中に置いてはいけません。
- `EXTRACT` では `TEMPLATE` も必須です。
- 許可される `TEMPLATE` は `[TEMPLATE:EX_SIMPLE]`, `[TEMPLATE:EX_5]`, `[TEMPLATE:EX_COMPARE]` です。
- `TEMPLATE` marker は `[MODE:EXTRACT]` の直後の header block に 1 つだけ置きます。
- 比較占いの構造化された正規ルートは `EXTRACT + [TEMPLATE:EX_COMPARE]` です。
- `GENERAL` は当面テンプレートを持たず、`[MODE:GENERAL]` だけを書いて使います。
- `MODE` や `TEMPLATE` が不足している場合、CLI は不足項目と許可値を含む案内付きエラーを返します。
- `EX_COMPARE` では、結果入力ブロックに候補が 2 件以上必要です。
- 現時点では、CLI が template 本文全体を厳密に構文解析しているわけではありません。必須 marker、compare 候補数、最低出力契約の確認を優先し、細部の厚みは canonical answer と acceptance で扱います。
- EXTRACT 入力から卦番号を取れた場合、SDK は該当卦の source files だけを選びます。卦番号をまだ取れない不完全入力では、後方互換のため EXTRACT source 全体を候補に戻します。

### EXTRACT template ごとの最低入力

- `EX_SIMPLE`
  - `### 1. 占いに至った背景・状況`
  - `### 2. 易経への質問`
  - `### 3. 占い結果入力`
  - `本卦`, `変爻`
- `EX_5`
  - `EX_SIMPLE` の項目一式
  - 必要に応じて `之卦`, `互卦`, `錯卦`, `綜卦`
  - 補助卦は空欄や `なし` を許容します
- `EX_COMPARE`
  - `### 1. 占いに至った背景・状況`
  - `### 2. 易経への質問`
  - `### 3. 占い結果入力`
  - 候補 2 件以上
  - 各候補に `本卦`, `変爻`

## MVP 完了チェックリスト

- `index / resolve / select / build-prompt / answer / run / validate` が CLI として揃っている。
- `validate --context <resolve.json|run.json>` で後追い検証できる。
- `run.json` に selection 要約、validation 要約、provider failure diagnostics が保存される。
- built-in provider として `codex` MVP が使える。
- opt-in smoke test の起動方法と skip 条件が明示されている。
- current contract が `iching` CLI の入出力に限定され、out-of-scope が固定されている。

## 受け入れ基準

`main` に取り込む前の受け入れ観点は次です。

- README の最短手順が実際の CLI 契約と矛盾しない。
- `answer` / `run` / `validate --context` / `iching.toml` provider table 形式の説明が current implementation と一致する。
- 旧 top-level config は互換扱いとして残しつつ、推奨設定は provider table 形式に寄せる。
- packaging, API, 新 provider 追加を今回の完成条件に混ぜない。

## レイヤー構成

- 下層: `index`, `validate` のような基盤機能
- 中層: `resolve`, `select`, `build-prompt` のような実行補助
- 上層: `run` / `answer` のような高レベル実行

この構成により、まず skill 運用で手順を観察し、安定した手順だけを SDK 側へ移す方針を取ります。

## EXTRACT

- raw テンプレート入力を前提にします。
- `TEMPLATE:EX_SIMPLE`, `TEMPLATE:EX_5`, `TEMPLATE:EX_COMPARE` の 3 系統を扱います。
- 根拠本文・引用形式・`（参照：...）` 形式を厳密に守ります。
- 回答後は必ず `validate` を通し、不足や参照形式を確認します。
- 比較占いは `EXTRACT` の正規ルートとして扱い、候補別根拠・順位・まとめ表まで出します。

### 最低出力契約

- `EX_SIMPLE`
  - 最低保証は `核心・結論`, `本卦`, `変爻` です。
- `EX_5`
  - 最低保証は `核心・結論`, `本卦`, `変爻` です。
  - 補助卦入力がある場合は、`補助卦` に相当する節も最低保証に含めます。
  - 現在の canonical answer では `補助卦` 総合見出しではなく `之卦` / `互卦` / `錯卦` / `綜卦` の個別節で表現しており、validator もその互換を許容します。
- `EX_COMPARE`
  - 最低保証は `核心・結論`, `吉凶順位`, 候補別詳細 2 件以上, `まとめ` 表です。
- `本卦` と `変爻` は、見出し名だけではなく、易の根拠を伴う解釈節として成立していることを期待します。
- `彖伝`, `大象伝`, `小象伝`, `文言伝` などは推奨要素です。現段階では最低保証の必須節には含めません。
- canonical answer は理想回答例として維持します。SDK 契約の runtime 判定は、required sections と validator 互換 citation を主軸にします。

#### EXTRACT Success Example

```bash
cat > extract-question.md <<'EOF'
[MODE:EXTRACT]
[TEMPLATE:EX_SIMPLE]

### 1. 占いに至った背景・状況
今の学び方の方向性が合っているかを見たいです。

### 2. 易経への質問
このまま学びを進めてよいか、易の観点から読みたいです。
参照行は validator 互換の形式 `（参照：<実ファイル名>.md|<卦名> - <項目名>）` を厳守し、`honda_wataru/01_乾為天.md` のようにサブディレクトリ付き実ファイル名をそのまま書いてください。

### 3. 占い結果入力
本卦：1乾為天
変爻：5爻
EOF

./iching run --input extract-question.md --provider codex --out-dir /tmp/iching-extract-example
echo $?
sed -n '1,120p' /tmp/iching-extract-example/report.json
```

- exit code `0` なら回答生成と validate の両方が成功です。
- `report.json` の `evidence_status` が `sufficient` なら EXTRACT の参照形式も通っています。
- EXTRACT では、参照行に実ファイル名の省略形ではなく `honda_wataru/01_乾為天.md` のようなフル相対パスが必要です。

## GENERAL

- 一般質問を主に扱います。
- 入力冒頭に `[MODE:GENERAL]` を必ず書きます。
- 本文は自由入力で、比較や順位という語が出てもそのまま一般質問として扱います。
- 構造化された比較占いをしたい場合は、`EXTRACT` の `TEMPLATE:EX_COMPARE` を使います。
- GENERAL でも validator 互換の参照行 `（参照：filename.md|section）` を守ります。
- GENERAL でも回答後は必ず `validate` を通します。

## Helper Commands

- `./iching index --mode extract|general`
  - 登録されている source 一覧や mode ごとの対象確認に使います。
  - 標準フローの必須ステップではありません。

- `./iching select --input <path|-> [--mode extract|general]`
  - `resolve` の結果をもとに、今見るべき source files を group 単位で返します。
  - GENERAL では `general_core` を返します。
  - EXTRACT legacy では `extract_honda`, `extract_takashima` を返します。
  - EXTRACT `--profile honda` では `extract_honda` だけを返し、split section files を追加メタデータとして返します。
  - EXTRACT `--profile takashima` では `extract_takashima` だけを返し、split section files を追加メタデータとして返します。

## 現時点で扱わないもの

- HTTP API / Web API の提供
- 常駐サーバーやデーモン化
- `codex` 以外の built-in provider 実装
- GUI や別アプリ向けの統合層
- OpenAI API などへの provider 直結実装
- packaging 用の配布導線の整備

これらは、手元 CLI 運用で不足が明確に出たら別フェーズで扱います。

## Opt-in Smoke Test

- 実 `codex` CLI の最小疎通確認は opt-in です。通常の `python3 -m unittest -q tests.test_cli` では smoke test は skip されます。
- 実行する場合は `ICHING_RUN_CODEX_SMOKE=1 python3 -m unittest -q tests.test_cli` を使います。
- smoke test は成功疎通だけを対象にし、`codex` 未導入、認証不足、ローカル権限由来の起動失敗では skip されます。

## EXTRACT Acceptance

- EXTRACT の代表ケースは [docs/extract-acceptance.md](docs/extract-acceptance.md) と `tests/fixtures/extract_cases/manifest.json` で管理します。
- 代表ケースには、実際に易経プロジェクトで使って目視確認した `test_1.md`, `test_2.md`, `test_3.md`, `test_4.md` を採用しています。
- `test_*_answer_canonical.md` は、iching-sdk の完成形回答を基準にした canonical answer です。最低保証そのものではなく、推奨される厚みと構成の目安として扱います。
- 受け入れ確認は、fixture と同じ質問文をこのスレッドに直接貼って `iching-sdk` skill の出力を見る運用を前提にします。
- CLI 側では `build-prompt`, `run`, `validate` を使って required sections と参照形式の回帰を補助確認します。
- `manifest.json` は最低保証、canonical answer は理想回答例、`docs/extract-acceptance.md` は目視確認観点という役割分担で揃えます。
- 安定化フェーズ全体の判断基準は [docs/stabilization-policy.md](docs/stabilization-policy.md) にまとめます。

## Maintenance Notes

- `MODE` 名や `TEMPLATE` 名を変更するときは、まず SDK 内の許可値定義と prompt fragment 対応を更新します。
- EXTRACT テンプレートを追加・変更するときは、少なくとも `prompting`, `resolving`, validator, fixture, canonical answer, `tests/fixtures/extract_cases/manifest.json`, README, `docs/extract-acceptance.md` を一緒に見直します。
- `prompting` は marker 契約と prompt fragment の対応、`resolving` は入力契約と context 生成、validator は最低出力契約、fixture / canonical answer / manifest は受け入れ基準、README と docs は公開契約の説明を担当します。
- `EX_COMPARE` は比較占いの正規ルートです。比較占いの保守は `GENERAL` ではなく `EX_COMPARE` を起点に考えます。
- `override_mode` は今回は仕様変更しません。外部ラッパー追加、CLI 契約見直し、mode 不一致事故の観測時に整理候補として扱います。
- source selection の責務は `EXTRACT = 本田 + 高島`, `GENERAL = general sources` を基準に保ちます。
