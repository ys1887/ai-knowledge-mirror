# EXTRACT acceptance flow

この文書は、EXTRACT の代表ケースを `iching-sdk` skill で実際に流し、出力品質を確認するための受け入れ手順です。質問文は Codex のこのスレッドに直接貼り付けて投入する前提にします。

- EXTRACT 入力は常に `[MODE:EXTRACT]` と `TEMPLATE` を明示した fixture を使います。
- 比較占いは `[TEMPLATE:EX_COMPARE]` のみを正規ルートとします。
- marker 契約は `MODE = 最初の非空行`, `TEMPLATE = [MODE:EXTRACT]` 直後の header block です。
- canonical answer は理想回答例です。SDK 契約の主判定は `manifest.json` の required sections と validator 互換 citation に置きます。

## 1. 代表ケース

- 標準ケース
  - `tests/fixtures/extract_cases/test_1.md`
- 複雑ケース
  - `tests/fixtures/extract_cases/test_2.md`
  - `tests/fixtures/extract_cases/test_3.md`
- 比較占いケース
  - `tests/fixtures/extract_cases/test_4.md`

これらは実際に易経プロジェクトで使用したケースを元に、iching-sdk の完成形回答を canonical fixture として整えたものです。CLI/validator では `test_*_answer_canonical.md` を理想回答例として扱い、最低契約は `manifest.json` に寄せます。

## 2. 進行順

1. 標準ケースを先に確認する。
2. 標準ケースで構造と参照形式が安定した後に、補助卦ありケースへ進む。
3. 比較占いは `test_4.md` を使い、順位節、候補ごとの根拠、まとめ表まで確認する。

## 3. 最低保証と推奨要素

- `EX_SIMPLE`
  - 最低保証: `核心・結論`, `本卦`, `変爻`
  - 推奨要素: `彖伝`, `大象伝`, `本田解釈`, `高島解釈`
- `EX_5`
  - 最低保証: `核心・結論`, `本卦`, `変爻`
  - 補助卦入力がある場合の最低保証: `補助卦` 相当の節
  - canonical answer では `補助卦` 総合見出しではなく `之卦` / `互卦` / `錯卦` / `綜卦` の個別節で表れることがあります
  - 推奨要素: 各補助卦の役割差が分かる解釈、本田解釈, 高島解釈
- `EX_COMPARE`
  - 最低保証: `核心・結論`, `吉凶順位`, 候補別詳細 2 件以上, `まとめ` 表
  - 推奨要素: 推薦候補の明示、順位理由の厚み、避けたい候補への短い注意
- `本卦` / `変爻` は見出しだけではなく、易の根拠を伴う解釈節として読めることを期待します。
- `彖伝` / `大象伝` / `小象伝` / `文言伝` は推奨要素であり、現段階では最低保証には含めません。

## 4. skill 対話の確認観点

- `核心・結論` が冒頭にある
- `本卦` と `変爻` の節が崩れていない
- `文言伝` は必要な場合だけ出る
- 複雑ケースでは、補助卦入力があると `補助卦` 相当の節が出る
- 比較ケースでは `吉凶順位` と候補別詳細、まとめ表が揃う
- 参照行が validator 互換形式
- 取得できない情報を推測で埋めていない
- 長文化しても主筋が本卦・変爻から逸れていない

## 5. このスレッドでの投入方法

1. まず `test_1.md` の質問文をこのスレッドにそのまま貼る。
2. 標準ケースが安定してから `test_2.md` と `test_3.md` を貼る。
3. 比較占いを確認するときは `test_4.md` を貼る。
4. 出力は本文一致でなく、上の確認観点で見る。
5. 気になった差分は、`構造`, `参照形式`, `冗長さ`, `補助卦の扱い`, `比較の厚み` のどれかで記録する。
6. 回答の確認や CLI 検証では `test_*_answer_canonical.md` を使う。

## 6. CLI 補助確認

代表ケースごとに次を確認する。

```bash
./iching build-prompt --input tests/fixtures/extract_cases/test_1.md
./iching run --input tests/fixtures/extract_cases/test_1.md --provider codex
./iching validate --mode extract --input out/run/<timestamp>/answer.md --context out/run/<timestamp>/run.json
./iching validate --mode extract --input tests/fixtures/extract_cases/test_1_answer_canonical.md
./iching resolve --input tests/fixtures/extract_cases/test_4.md > /tmp/test_4_resolve.json
./iching validate --mode extract --input tests/fixtures/extract_cases/test_4_answer_canonical.md --context /tmp/test_4_resolve.json
```

`run` が難しい場面では、少なくとも `build-prompt` で prompt 断片の組み立てと `Selected Sources` を確認する。EXTRACT の `Selected Sources` は、本田・高島の 2 系統に加えて、その質問で必要な卦だけに絞られていることを確認する。

最低保証に差分が出た場合は、次の順で修正箇所を確認する。

1. `prompting` と `resolving` の marker / template 契約
2. validator の required sections 判定
3. fixture と canonical answer
4. `tests/fixtures/extract_cases/manifest.json`
5. README とこの文書
