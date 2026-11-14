# 易経占いプロジェクト（`iching-div`）

`iching-div` は、split source を前提に EXTRACT 用の実行テキストを組み立てるための最小ベースです。  
SDK 的な実行基盤は持ち込まず、`input parse -> profile resolve -> source select -> prompt text to stdout` に限定します。

## v1 の範囲

- 実装対象は `EXTRACT` のみ
- `[MODE:GENERAL]` は認識するが未実装エラー
- `MODE` 無記載はエラー
- `EXTRACT` で `TEMPLATE` 無記載はエラー
- provider / `run` / `validate` / artifact 保存 / `run.json` はなし

## CLI

```bash
python3 scripts/build_extract_prompt.py --input <path|-> --profile <legacy|honda|takashima>
```

- 入力はファイルパスまたは `-` で標準入力
- 出力は実行用 prompt text のみ
- mode override は不可

## profile

- `legacy`
  - 実験用の二重解釈プロファイル
  - 共通引用 source と Honda/Takashima の両 interpretation source を読む
  - compare では Honda 主導、Takashima は補強専用
- `honda`
  - 共通引用 source + Honda interpretation source
  - 最終解釈は `本田解釈` のみ
- `takashima`
  - 共通引用 source + Takashima interpretation source
  - 最終解釈は `高島解釈` のみ

## ディレクトリ構成

```text
iching-div/
├─ AGENTS.md
├─ README.md
├─ archive/
│  └─ pre-split-migration/
├─ assets/
│  ├─ canonical/
│  │  ├─ quotes/
│  │  └─ interp/
│  │     ├─ honda/
│  │     └─ takashima/
│  ├─ originals/
│  │  └─ takashima_interp/
│  └─ split/
│     ├─ honda/
│     └─ takashima/
├─ examples/
│  └─ extract/
├─ formats/
│  └─ extract/
├─ scripts/
│  ├─ build_extract_prompt.py
│  ├─ resolving.py
│  ├─ profiles.py
│  ├─ indexing.py
│  └─ selecting.py
├─ sources/
│  ├─ ekikyo_custom_prompt.md
│  ├─ extract/
│  └─ general/
└─ tests/
```

## canonical / originals / split

- `assets/canonical/quotes/`
  - 全 profile 共通の原文・読み下し引用正本
- `assets/canonical/interp/takashima/`
  - 高島解釈の正本
- `assets/canonical/interp/honda/`
  - 本田解釈の正本（当面は暫定配置を含む）
- `assets/originals/takashima_interp/`
  - 取り込み元の原本一式
  - reference 用 custom prompt / input template もここに保存
- `assets/split/`
  - builder が実際に参照する split asset 一式

## split asset の扱い

- `assets/split/honda/`
  - Honda split source 一式
  - `index.json`
  - 各卦 `manifest.json`
  - section md
  - `exceptions.json`
- `assets/split/takashima/`
  - Takashima split source 一式

`source_file` は citation path 用、section md は内部参照用です。  
最終回答には citation path のみを使い、section path は出しません。

## format fragment

- `formats/extract/shared.md`
- `formats/extract/ex_simple_single.md`
- `formats/extract/ex_simple_legacy.md`
- `formats/extract/ex_5_single.md`
- `formats/extract/ex_5_legacy.md`
- `formats/extract/ex_compare_single.md`
- `formats/extract/ex_compare_legacy.md`
- `formats/extract/profile_legacy.md`
- `formats/extract/profile_honda.md`
- `formats/extract/profile_takashima.md`

これらを script が結合して実行テキストを作ります。

## examples / canonical answer

- `examples/extract/` に fixture 入力と canonical answer を置きます。
- canonical answer は文面一致の正解ではなく、骨格参照です。

## holding / corpus

- 現役でない source corpus は `work/holding/` に退避します。
- v1 の prompt builder は split asset を選択して execution text を作る役割に限定します。

## テスト

```bash
python3 -m unittest tests.test_build_extract_prompt
```

- stdlib `unittest` のみ使用
- parser / selection / prompt-build / fixture smoke を確認
