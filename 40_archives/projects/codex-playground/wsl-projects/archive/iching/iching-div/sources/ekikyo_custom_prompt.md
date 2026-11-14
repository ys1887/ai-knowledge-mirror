# 易経プロジェクト｜split-source EXTRACT 正本（v1.1）

## 目的

- このファイルは `iching-div` の split-source EXTRACT 運用正本です。
- 実行主体は prompt builder script であり、この文書は active source layout と出力契約を定義します。

## 前提

- v1 系では `EXTRACT` のみ実装します。
- `[MODE:GENERAL]` は認識しますが、未実装エラーで停止します。
- `MODE` 無記載はエラーです。
- `EXTRACT` で `TEMPLATE` 無記載はエラーです。
- fail-fast を徹底します。

## script の役割

- `MODE` / `TEMPLATE` / 卦 / 変爻 / 候補を解析する
- 固定 profile を解決する
- split asset の citation path / section path を選ぶ
- canonical source roots を execution text に明示する
- execution text を `stdout` に出す

## script がやらないこと

- provider 呼び出し
- `run`
- `validate`
- artifact 保存
- `run.json`
- 外部依存つき runtime

## active source layout

### 共通引用

- shared quotes は全 profile 共通です。
- active path:
  - `/home/ys/projects/iching-div/assets/canonical/quotes/quotes_honka.md`
  - `/home/ys/projects/iching-div/assets/canonical/quotes/quotes_koji.md`

### 解釈ソース

- `takashima`
  - `/home/ys/projects/iching-div/assets/canonical/interp/takashima/`
- `honda`
  - `/home/ys/projects/iching-div/assets/canonical/interp/honda/`
- `legacy`
  - Honda / Takashima の両 interpretation source を使う

### original reference bundle

- 取り込み元の参考原本は以下に隔離します。
  - `/home/ys/projects/iching-div/assets/originals/takashima_interp/`
- reference 用 custom prompt / template はここに保存し、active runtime path とは分けます。

### runtime split asset

- builder が section path を選ぶための active split asset は以下です。
  - `/home/ys/projects/iching-div/assets/split/honda/`
  - `/home/ys/projects/iching-div/assets/split/takashima/`

## profile

### legacy

- 実験用 profile
- 共通引用 source を使う
- Honda / Takashima の両 interpretation family を使う
- `EX_SIMPLE` と `EX_5` では `本田解釈` と `高島解釈` を両方出す
- `EX_COMPARE` では Honda 主導、Takashima は内部補強専用

### honda

- 共通引用 source を使う
- Honda interpretation family のみを使う
- final interpretation は `本田解釈` のみ

### takashima

- 共通引用 source を使う
- Takashima interpretation family のみを使う
- final interpretation は `高島解釈` のみ

## prompt 出力原則

- execution text には canonical source roots・citation path・section path を含める
- 最終回答の参照表示には citation path のみ使う
- section path は最終回答に出さない
- canonical answer は骨格参照であり、逐語一致の目標ではない

## active path summary

- custom prompt source:
  - `/home/ys/projects/iching-div/sources/ekikyo_custom_prompt.md`
- input templates:
  - `/home/ys/projects/iching-div/templates/`
- output format fragments:
  - `/home/ys/projects/iching-div/formats/extract/`
- examples:
  - `/home/ys/projects/iching-div/examples/extract/`
- holding area:
  - `/home/ys/projects/iching-div/work/holding/`
