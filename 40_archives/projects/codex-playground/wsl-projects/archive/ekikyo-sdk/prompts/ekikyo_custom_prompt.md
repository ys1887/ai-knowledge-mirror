# 易経プロジェクト｜Codex用 EXTRACT mirror 正本

## 目的

- このファイルは `ekikyo` の EXTRACT 用 mirror 正本です。
- 元の正本は ChatGPT project で使っている `ekikyo_custom_prompt.md` であり、このファイルはその EXTRACT 部分だけを Codex 用に mirror したものです。
- ここでは細かい実行手順ではなく、EXTRACT で使う最小契約だけを保持します。

## 前提

- v1 系では `EXTRACT` のみ実装します。
- `MODE` 無記載はエラーです。
- `EXTRACT` で `TEMPLATE` 無記載はエラーです。
- fail-fast を徹底します。

## helper script

- helper script は引用と高島本文を束ねた evidence bundle だけを作ります。
- helper script は最終回答本文を書きません。
- 最終回答 md は skill + LLM が別途 `work/YYYY-MM-DD_NN.md` に書きます。

## responsibility boundary

- script が保証する範囲は、`MODE` / `TEMPLATE` 契約、source 選定、evidence bundle 生成、raw 原文節の機械追記です。
- LLM が担当する範囲は、テンプレートで許可された `### 解釈` と `## 総合解釈` の prose 生成です。
- 人間レビューが担当する範囲は、解釈の妥当性、論点密度、言い回しの自然さ、問いへの当て方の適切さです。

## active source layout

### 共通引用

- shared quotes は本 repository の引用正本です。
- active path:
  - `/home/ys/projects/iching/ekikyo-sdk/assets/quotes/quotes_honka.md`
  - `/home/ys/projects/iching/ekikyo-sdk/assets/quotes/quotes_koji.md`

### 解釈ソース

- active interpretation source:
  - `/home/ys/projects/iching/ekikyo-sdk/assets/extract_takashima_split/`

## fixed interpretation family

- 共通引用 source を使う
- Takashima interpretation family のみを使う
- final interpretation は `高島解釈` のみ

## answer 出力原則

- 実際の回答本文の形は、このファイルと 3 つの output template を正本とします。
- `EX_SIMPLE` / `EX_5` は本文中に手書き参照行を出しません。
- `卦辞` `彖伝` `大象伝` `爻辞` `小象伝` の各節は引用のみです。
- 解釈文はテンプレートで指定された `### 解釈` と最終節にだけ置きます。
- `EX_SIMPLE` では、最終 md の末尾に script が `## 高島解釈原文` 節を機械的に追記してよいです。
- `EX_5` でも、最終 md の末尾に script が `## 高島解釈原文` 節を機械的に追記してよいです。
- `## 高島解釈原文` は source の機械転記節であり、要約・解説・改変を入れません。
- `## 高島解釈原文` は LLM に書かせず、source からそのまま追記します。
- `EX_COMPARE` は比較形式を優先し、`## 高島解釈原文` 節の対象外とします。
- 高島本文は、古典引用節とは別に、`### 解釈` と `## 総合解釈` の prose 内で短く引用または準引用してよいです。
- `EX_SIMPLE` / `EX_5` では、高島本文の短い語句や一節を本文中に織り込み、なぜその判断になるかの根拠を見せます。
- 高島本文の引用は長い blockquote にせず、本文中の短い鍵括弧引用または準引用を基本とします。
- `## 総合解釈` は短い締めではなく、今回の答えを確定する主たる最終判断節として書きます。
- `## 総合解釈` では、本卦と変爻を中心に、高島本文の論旨・比喩・警戒・勧めを積極的に再統合します。
- `## 総合解釈` では、本卦や変爻の `### 解釈` で用いた高島本文の内容を、今回の問いへの最終判断としてもう一度展開してよいです。
- `## 総合解釈` の段落は、4 段落以上であるだけでなく、役割が重複しない順序で組み立てます。
- 第1段落は結論の再掲ではなく、本卦の高島解釈が今回の問いで何を意味するかの再統合に専念します。
- 第2段落は変爻の高島解釈が今回の問いで何を意味するかの再統合に専念します。
- 最終判断や可否の言い切りは、第3段落以降に寄せます。
- `## 総合解釈` では、問いに必要な場合に限って、時期・開始条件・慎重条件などの具体条件を書きます。
- 古典引用節は quote-only を維持し、`## 総合解釈` でも引用節の現代語解説化は行いません。
- `work/` の最終 md には runtime contract や internal path 一覧を含めません。

## stable acceptance checklist

- `EX_SIMPLE` / `EX_5` の `## 総合解釈` は原則 4 段落以上を保ちます。
- `## 総合解釈` の第1段落は結論先出しではなく再統合から始め、第3段落以降で主判断を明示します。
- `EX_SIMPLE` / `EX_5` の最終 md には script が `## 高島解釈原文` を末尾追記できます。
- `EX_COMPARE` は `## 高島解釈原文` の対象外です。
- validator は重く増やさず、この契約と既存 test と人間レビューで安定運用します。
