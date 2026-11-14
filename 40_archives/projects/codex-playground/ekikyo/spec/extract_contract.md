# 易経プロジェクト｜EXTRACT 正本

## 目的

- このファイルは `ekikyo` の EXTRACT 用の唯一の実行契約です。
- 旧運用メモはこの文書へ統合し、以後はこのファイルだけを参照します。
- ここでは細かい実行手順ではなく、EXTRACT で使う最小契約だけを保持します。

## 前提

- v1 系では `EXTRACT` のみ実装します。
- `GENERAL` に関する記述は無視します。
- `MODE` 無記載はエラーです。
- `EXTRACT` で `TEMPLATE` 無記載はエラーです。
- fail-fast を徹底します。

## helper script

- helper script は引用と高島本文を束ねた helper evidence を作ります。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、helper script は同じ evidence を実行用 prompt にも埋め込みます。
- helper script は実行用 prompt と helper evidence を組み立てます。
- helper script は最終回答の先頭に `## 質問文` を機械追記してよいです。
- 最終回答 md は script が classical block と `## 高島易断` を合成して完成させます。`EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、必要に応じて `## 占例抜粋` をその後ろに機械追記します。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` の実行用 prompt には、対応する変爻の `## 占例参考` を埋め込んでよく、判断の流れと帰結の組み方の参考として読めます。

## active source layout

### 共通引用

- shared quotes は本 repository の引用正本です。
- active path:
  - `/home/ys/projects/ekikyo/assets/honka.md`
  - `/home/ys/projects/ekikyo/assets/koji.md`
- canonical quote files are 3-line blocks: original text, reading, hiragana line.

### 解釈ソース

- active interpretation source:
  - `/home/ys/projects/ekikyo/assets/takashima/`

## responsibility boundary

- script が保証する範囲は、`MODE` / `TEMPLATE` 契約、source 選定、evidence bundle 生成、`## 質問文` の機械追記、本卦ブロックと変爻ブロックの引用抽出、classical block 機械差し込み、`## 高島易断` の機械追記です。
- LLM が担当する範囲は、`EX_COMPARE` の `**核心・結論**` と候補別 short prose 生成です。
- 人間レビューが担当する範囲は、解釈の妥当性、論点密度、言い回しの自然さ、問いへの当て方の適切さです。

## fixed interpretation family

- 共通引用 source を使う
- Takashima interpretation family のみを使う
- final interpretation は `高島解釈` のみ

## prompt 出力原則

- execution text には canonical source roots・citation path・internal file path を含める
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` の execution text には、script 抽出済みの本卦 block・変爻 block・高島本文 evidence を含める
- 最終回答の `## 参照` 節には citation path のみ使う
- internal file path は最終回答に出さない
- canonical answer は骨格参照であり、逐語一致の目標ではない
- file path が必要なら canonical source から直接参照する前提で扱う
- work/ の最終 md には runtime contract や internal path 一覧を含めない

## active path summary

- spec source:
  - `/home/ys/projects/ekikyo/spec/extract_contract.md`
- canonical quote source:
  - `/home/ys/projects/ekikyo/assets/honka.md`
  - `/home/ys/projects/ekikyo/assets/koji.md`
- canonical interpretation source:
  - `/home/ys/projects/ekikyo/assets/takashima/`
- output format:
  - `/home/ys/projects/ekikyo/formats/`
- canonical cases:
  - `/home/ys/projects/ekikyo/fixtures/`
- work area:
  - `/home/ys/projects/ekikyo/work/`

## answer 出力原則

- 実際の回答本文の形は、このファイルと 3 つの output template を正本とします。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` は本文中に手書き参照行を出しません。
- `## 質問文` は最終回答の先頭に機械的に差し込みます。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` は fixed quote section 群の後、`## 高島易断` の前に `## 参照` を 1 回だけ置きます。
- `## 参照` は script が機械的に組み立て、`- <citation path> | <卦名>` の bullet だけを並べます。
- `## 参照` では実際に使った卦の citation のみを input 順で列挙し、同一 file は重複排除します。
- 本卦 block・変爻 block・補助卦 block は source からの機械転記節です。script が最終 answer の該当見出し直下へそのまま差し込みます。
- `> `、空行、間の prose、`（占）` まで source 表記どおり保持します。
- `## 高島易断` 配下の細見出しは script が生成します。本卦側は `### <卦名>` と `#### 卦辞` / `#### 彖伝` / `#### 大象伝`、変爻側は `### 爻辞と小象伝（<爻名>）` を使います。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、LLM は本文 section を書きません。
- LLM は classical block を書かず、`EX_COMPARE` の `**核心・結論**` と候補別 short prose だけを書きます。
- `EX_SIMPLE` では、最終 md の末尾に script が `## 高島易断` 節を機械的に追記してよいです。
- `EX_SIMPLE2` でも、最終 md の末尾に script が `## 高島易断` 節を機械的に追記してよいです。
- `EX_5` でも、最終 md の末尾に script が `## 高島易断` 節を機械的に追記してよいです。
- さらに、`EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では `## 高島易断` の後ろに `## 占例抜粋` を必要に応じて機械追記してよいです。
- `## 占例抜粋` は `assets/高島易断占例.md` から本卦番号に対応する節を切り出した機械転記節であり、要約・解説・改変を入れません。
- `## 高島易断` と `## 占例抜粋` は LLM に書かせず、source からそのまま追記します。
- `EX_COMPARE` は比較形式を優先し、`## 高島易断` 節の対象外とします。
- `EX_COMPARE` は候補比較形式を優先し、各候補は変爻の引用ブロックを中心に据えます。本文中で本卦の長い古典引用や高島原文を展開しません。
- `EX_5` では、本卦と変爻が主軸です。之卦は変化後の着地点を補助的に示し、互卦・錯卦・綜卦は内在する別視点を補助的に示します。
- `EX_5` で変爻が1本のときは、その変爻を今回の主メッセージとして扱います。
- `EX_5` で変爻が2本以上のときは、本卦の卦辞を今回の主メッセージとして扱い、各変爻は補助証拠として扱います。
- `EX_5` で変爻がない場合は、本卦ブロックを主軸とし、之卦がなければ互卦・錯卦・綜卦を補助的に扱います。
- `EX_5` の fixed quote sections では、問いの具体内容・選択肢・状況説明を再掲しません。
- `EX_SIMPLE` は `変爻` が 1 本ある場合のみ受け付けます。`変爻：なし` や欠落はエラーです。
- `EX_SIMPLE2` は `変爻` が 1 本ある場合のみ受け付けます。`変爻：なし` や欠落はエラーです。
- `EX_5` で変爻がない場合は、`## 変爻` と `## 之卦` を出さず、本卦と補助卦だけで直接適用します。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、対応する変爻の占例がある場合、その占例は `## 占例参考` として判断の流れを学ぶための参考資料として読めます。
- 古典引用節は source block 全文の機械転記を維持します。

## stable acceptance checklist

- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` の最終 md に、手書き prose section はありません。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` の最終 md には script が `## 高島易断` を末尾追記できます。
- `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、さらに `## 占例抜粋` を末尾追記できます。
- `EX_COMPARE` は `## 高島易断` と `## 占例抜粋` の対象外です。
- validator は重く増やさず、この契約と既存 test と人間レビューで安定運用します。
