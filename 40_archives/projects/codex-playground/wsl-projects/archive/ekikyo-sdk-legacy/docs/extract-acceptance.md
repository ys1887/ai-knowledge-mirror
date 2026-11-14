# EXTRACT acceptance flow

この文書は、EXTRACT の代表ケースを `ekikyo-sdk` skill で実際に流し、出力品質を確認するための受け入れ手順です。質問文は Codex のこのスレッドに直接貼り付けて投入する前提にします。

## 1. 代表ケース

- 標準ケース
  - `tests/fixtures/extract_cases/test_1.md`
- 複雑ケース
  - `tests/fixtures/extract_cases/test_2.md`
  - `tests/fixtures/extract_cases/test_3.md`
- 比較ケース
  - `tests/fixtures/extract_cases/test_4.md`

代表ケースの入出力対応は `tests/fixtures/extract_cases/manifest.json` を基準にする。実際の受け入れでは canonical answer の完全一致ではなく、節構成と参照形式の整合を優先して確認する。

## 2. 進行順

1. 標準ケースを先に確認する。
2. 標準ケースで構造と参照形式が安定した後に、補助卦ありケースへ進む。
3. 最後に比較ケースで `核心・結論` / `吉凶順位` / 候補別節 / `まとめ` 表の並びを確認する。

## 3. skill 対話の確認観点

- `核心・結論` が冒頭にある
- `本卦` と `変爻` の節が崩れていない
- `文言伝` は必要な場合だけ出る
- 複雑ケースでは `補助卦` が入力に応じて出る
- 比較ケースでは `吉凶順位` と候補別節と `まとめ` 表が揃う
- 参照行が validator 互換形式
- 取得できない情報を推測で埋めていない
- 長文化しても主筋が本卦・変爻から逸れていない

## 4. このスレッドでの投入方法

1. まず `test_1.md` 相当の質問文をこのスレッドにそのまま貼る。
2. 次に `test_2.md`, `test_3.md` 相当の補助卦ありケースを貼る。
3. 最後に `test_4.md` 相当の比較ケースを貼る。
4. 出力は本文一致でなく、上の確認観点で見る。
5. 気になった差分は、`構造`, `参照形式`, `冗長さ`, `補助卦の扱い`, `比較順位` のどれかで記録する。

## 5. CLI 補助確認

代表ケースごとに次を確認する。

```bash
./iching build-prompt --input tests/fixtures/extract_cases/test_1.md
./iching run --input tests/fixtures/extract_cases/test_1.md --provider codex
./iching validate --mode extract --input out/run/<timestamp>/answer.md --context out/run/<timestamp>/run.json
```

比較ケースでは次も補助確認に使える。

```bash
./iching build-prompt --input tests/fixtures/extract_cases/test_4.md
```

`run` が難しい場面では、少なくとも `build-prompt` で prompt 断片の組み立てと `Selected Sources` を確認する。
