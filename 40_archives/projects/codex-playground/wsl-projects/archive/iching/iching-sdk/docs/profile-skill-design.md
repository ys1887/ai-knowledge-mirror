# profile 別起動 skill 設計メモ

## 位置づけ

現時点では、`iching-sdk` の profile 別起動 skill はまだ実装しない。

ただし、将来必要になったときに迷わず追加できるよう、責務と境界だけ先に固定しておく。

このメモの前提は次のとおり。

- profile 別 skill は `./iching` CLI の薄い起動入口に留める
- durable なロジックは skill ではなく `iching-sdk` 本体に置く
- profile ごとの差分は、まず `--profile` と `iching.toml` で吸収する

## 基本方針

- 既存の共通 `iching-sdk` skill は維持する
- profile 別 skill は必要になった時点で追加する
- 最初から全 profile を作らず、実運用で必要になったものだけ作る

当面の profile 別 skill 名は次を想定する。

- `iching-sdk-honda`
- `iching-sdk-takashima`

## profile 別 skill の責務

profile 別 skill は、原則として次の 3 要素だけを持つ。

1. 対象 profile の明示
2. 既定コマンドの明示
3. 「ロジックは本体に置く」という制約

差分として許容するのは主に次だけとする。

- 既定 profile 名
- 想定する主コマンド例
- 必要な場合に限った参照 source 群の説明

## skill に持たせないもの

次は profile 別 skill に持たせない。

- provider の複雑な分岐
- profile ごとのエラー回復ロジック
- durable な業務ルール
- 本体未実装仕様の先取り
- README の CLI 契約の重複記述

複雑さが必要になった場合は、skill 側ではなく `iching-sdk` 側の CLI / config / prompt / validation を見直す。

## 本体側で維持すべき前提

profile 別 skill を後から追加しても破綻しないよう、本体側では次を維持する。

- `./iching run --profile <name>` で日常経路が完結する
- `README.md` と `tests/test_cli.py` が profile 挙動の正本である
- profile 差分が増えても、まず CLI / config で吸収する

## 実装トリガー

次のどれかが起きたら、その profile の skill を作ってよい。

- 同じ `--profile <name>` 起動を繰り返す
- profile ごとに参照 source や運用説明を毎回言い直している
- 共通 `iching-sdk` skill だと誤起動しやすい

逆に、次の間はまだ作らない。

- provider 周りの実運用が不安定
- profile ごとの使い分けが固まっていない
- 差分が単なる試行段階に留まっている

## skill 形状の最小案

profile 別 skill の本文は短く保つ。

想定する既定コマンドは次のとおり。

- EXTRACT: `./iching run --profile honda --input <path|->`
- 調査時: `./iching resolve --profile honda --input <path|->`
- 検証時: `./iching validate --profile honda --mode extract --input <path|-> [--context ...]`

`takashima` でも形は同じで、profile 名だけを変える。

## 導入時チェック

profile 別 skill を実際に作る段階では、最低限次を確認する。

- skill 記述がその時点の `README.md` 契約と矛盾しない
- profile 名が `iching.toml` / runtime config の実名と一致する
- `./iching run --profile <name>` の日常パスが成立している
- `validate` と `run.json` の見方が skill 文面と矛盾しない

## 補足

- 当面は `legacy` / `honda` / `takashima` を想定範囲とする
- profile ごとの差分は source selection と prompt 断片の違いが中心で、起動入口そのものは共通化できる前提とする
- 将来 profile 別 skill を追加しても、共通 `iching-sdk` skill は残す
