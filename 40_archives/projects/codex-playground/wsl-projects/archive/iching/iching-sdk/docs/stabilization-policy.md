# iching-sdk 安定化フェーズ運用メモ

## 位置づけ

現時点の `iching-sdk` は、易経 SDK として「未完成」ではなく、初版安定版として運用を始めてよい段階にある。

前提は次のとおり。

- 重大な不具合や想定外ケースがまだ残っていないこと
- current contract は CLI 入出力、marker 契約、最低出力契約、validator 互換 citation を中心に維持すること
- 当面の主題は新機能追加ではなく、比較運用による品質固定であること

## 当面の方針

安定化フェーズでは、大きな構造変更を止め、次を主作業とする。

1. `ChatGPT` プロジェクト、`ekikyo-sdk`、`iching-sdk` の 3 系統で同一入力の出力を比較する
2. 差分が出たら、すぐ修正せず先に分類する
3. 修正が必要と判断した差分だけを検証資産へ戻す

比較時の主な確認観点は次のとおり。

- 解釈の芯がずれていないか
- citation の使い方が validator 契約とずれていないか
- 節構成が template ごとの最低契約から崩れていないか
- `EX_COMPARE` の順位づけや推薦理由が不自然でないか
- `EX_5` の補助卦の扱いに欠落や過剰がないか

## 差分分類

比較で見つかった差分は、少なくとも次の 4 区分で扱う。

### 1. 許容できる表現差

- 文体、言い回し、段落の切り方などの差
- 契約を満たし、解釈の芯もずれていないもの

原則として即修正しない。必要なら acceptance の目視観点に補足する。

### 2. prompt 細分化で意味がずれた差

- fragment 分離後に強調点や解釈の主筋が変わったもの
- `EX_SIMPLE`, `EX_5`, `EX_COMPARE` の枝ごとの差が不自然に出るもの

主に prompt fragment と canonical answer の見直し候補とする。

### 3. validator で拾えていない差

- required sections を欠くのに通ってしまう
- citation 形式や compare 最低要件の不足を runtime で検出できていない

主に validator, manifest, fixture の見直し候補とする。

### 4. 仕様未確定の差

- どちらを正とするかがまだ設計上決まっていないもの
- 当面の current contract には直接書いていないもの

すぐ実装修正せず、保留事項として記録する。

## 反映先の原則

差分を直す場合は、原因に応じて反映先を絞る。

- prompt 起因の意味ずれ
  - `prompts/fragments/`
  - canonical answer
  - 必要なら acceptance 観点
- 契約差、検出漏れ
  - validator
  - `tests/fixtures/extract_cases/manifest.json`
  - fixture
  - README / docs
- 仕様未確定
  - このメモか別の保留メモに記録し、再検討条件が来るまで凍結

変更時の基本確認範囲は README の maintenance notes を起点に決める。

## フェーズ整理

### フェーズ1: 初版安定版として運用開始

- 現在の `iching-sdk` を初版安定版として扱う
- mode 名、template 名、CLI 契約の大改修は止める

### フェーズ2: 出力比較による品質確認

- 3 系統で同一入力を比較する
- 契約差と品質差を切り分ける

### フェーズ3: 小さな修正と検証資産の拡充

- 必要な差分だけ fixture / canonical answer / validator / docs に反映する
- acceptance ケースと確認観点を増やす
- エラーメッセージや説明文の小改善を行う

### フェーズ4: 運用手順の固定

- 比較確認のやり方を定型化する
- 変更時に何を確認するかを揃える

### フェーズ5: CLI 契約や保留事項の再検討

当面は後回しにし、次の条件が来たときにだけ再検討する。

- CLI を直接触る場面が増える
- 外部ラッパーが増える
- template 以外の入力経路を持つ
- mode 不一致事故が実際に起きる

profile 別起動 skill については、現時点では実装を保留し、責務だけを
[`docs/profile-skill-design.md`](/home/ys/projects/iching-sdk/docs/profile-skill-design.md)
に固定する。必要になるまでは共通 `iching-sdk` skill を維持し、差分は
CLI の `--profile` と runtime config に寄せる。

## 保留事項

### `override_mode` / `--mode`

現時点では保留とする。

仮置きの方向性は次のとおり。

- `--mode` 自体は当面残してよい
- 本文 marker を override しない
- 本文の `[MODE:...]` と CLI 指定が不一致ならエラー

ただし、今の優先度は CLI 契約の再設計より比較運用と安定化にある。

## 今はやらないこと

- mode / template 名の変更
- 大規模な抽象化
- 他 AI 前提の拡張設計
- SDK 全体の汎用化
- CLI 契約の全面改修

## 補足

- 比較占いの正規ルートは `EXTRACT + [TEMPLATE:EX_COMPARE]` とする
- GENERAL は一般質問モードとして保ち、比較占いの保守起点にはしない
- canonical answer は理想回答例、`manifest.json` は最低保証、acceptance docs は目視確認観点という分担を維持する
