# 易経占いプロジェクト（`ekikyo`）

`ekikyo` は、Takashima 系 canonical source を基準に EXTRACT 用の実行テキストと postprocess 用 script を提供する最小ベースです。  
repo 本体は `input parse -> source select -> prompt text with embedded evidence to stdout` と answer postprocess を担当し、LLM 実行や最終 save-path orchestration は skill など外側の運用レイヤーが担当します。

## v1 の範囲

- 実装対象は `EXTRACT` のみ
- `MODE` 無記載はエラー
- `EXTRACT` で `TEMPLATE` 無記載はエラー
- provider / `run` / `validate` / 常設 artifact 保存 / `run.json` は repo 本体に持ち込まない

## CLI

```bash
python3 scripts/build_extract_prompt.py --input <path|->
```

- 入力はファイルパスまたは `-` で標準入力
- 出力は実行用 prompt text のみ
- `--output-dir` を付けると、検査用の evidence bundle を別ファイルに出力できる
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、prompt text に解釈生成用の evidence が埋め込まれる
- final answer では、classical block は script が source から機械差し込みし、`## 高島易断` も後追い追記する

利用可能な postprocess script:

```bash
python3 scripts/next_work_filename.py [--work-dir <path>] [--date YYYY-MM-DD]
python3 scripts/build_answer_skeleton.py --input <input md>
python3 scripts/assemble_extract_answer.py --input <input md> --output <answer md>
python3 scripts/append_takashima_raw.py --input <input md> --output <answer md>
python3 scripts/extract_chienomori_quotes.py [--source-dir <path>] [--honka-output <path>] [--koji-output <path>] [--combined-output <path>]
```

- `next_work_filename.py` は `work/YYYY-MM-DD_NN.md` の次番号を機械的に決める
- `next_work_filename.py` は通常の占い結果を `work/YYYY-MM-DD_NN.md` で保存するときだけ使う
- `work/` へ提出するレポートは通し番号を使わず、`report_<レポート名>.md` で保存する
- `build_answer_skeleton.py` は template ごとの見出し骨格だけを出力する
- `assemble_extract_answer.py` は drafted answer に canonical quote block を差し込み、必須 section / heading の不足を fail-fast で検出する
- `append_takashima_raw.py` は final answer 末尾に `## 高島易断` を機械追記し、save 対象ファイルの不在を fail-fast で検出する
- `extract_chienomori_quotes.py` は知恵の森ソースから `卦辞 / 彖伝 / 大象伝 / 爻辞 / 小象伝` の原文＋読み下しだけを転記して、本卦版・爻版・結合版の 3 つの work file を生成する
- これらの script 自体は LLM を起動しない

## source policy

- 正本は `assets/honka.md` / `assets/koji.md` / `assets/takashima/`
- EXTRACT の実行契約は `spec/extract_contract.md`

## ディレクトリ構成

```text
ekikyo/
├─ .github/
├─ AGENTS.md
├─ README.md
├─ assets/
│  ├─ honka.md
│  ├─ koji.md
│  ├─ 高島易断占例.md
│  └─ takashima/
├─ fixtures/
├─ formats/
├─ scripts/
├─ skills/
├─ spec/
├─ tests/
└─ work/
```

## canonical / originals

- `assets/honka.md`
  - 本卦側の原文・読み下し・ひらがな引用の正本
- `assets/koji.md`
  - 変爻側の原文・読み下し・ひらがな引用の正本
- `assets/高島易断占例.md`
  - 占例抜粋の正本
- `assets/takashima/`
  - 高島解釈の正本

`source_file` は citation path 用、file path は内部参照用です。  
最終回答には citation path のみを使い、section path は出しません。

## format

- runtime 正本
  - `formats/shared.md`
  - `formats/ex_simple_single.md`
  - `formats/ex_5_single.md`
  - `formats/ex_compare_single.md`

これらの runtime format を script が結合して実行テキストを作ります。  
`EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、quotes block と高島本文の該当箇所も prompt 内の evidence として同梱されます。最終 answer では、classical block は LLM に再現させず script が source から機械差し込みします。

## fixtures / canonical answer

- `fixtures/` に canonical case の入力と canonical answer を置きます。
- canonical answer は文面一致の正解ではなく、骨格参照です。

## skill 運用との関係

- 主運用の入口は `/ekikyo` skill です。
- skill は外側の orchestration として、入力貼り付け後に prompt build、LLM prose draft、answer assembly、raw append、`work/` への最終保存を順に実行します。
- repo 本体はそのために必要な source、format、build script、postprocess script を提供します。
- inspection 用の evidence 出力は任意ですが、常設 artifact 保存は repo の標準運用に含めません。

## テスト

```bash
python3 -m unittest tests.test_build_extract_prompt
```

- stdlib `unittest` のみ使用
- parser / selection / prompt-build / fixture smoke を確認
