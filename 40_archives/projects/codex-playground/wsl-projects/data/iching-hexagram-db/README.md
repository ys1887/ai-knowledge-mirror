# iching-hexagram-db

易経の卦データをまとめたJSONファイル置き場です。

## ファイル

- `base_hexagrams.json`: 卦一覧を配列で持つ基本データ (`{"hexagrams": [...]}`)
- `64ka_optimized.json`: 二進数をキーにした高速参照向けのデータ

## データ形式

- 二進数は6文字 (`0` または `1`)
- 並び順は左から右へ、初爻(1) から上爻(6)
- `base_hexagrams.json` は卦情報をレコードの配列として保持
- `64ka_optimized.json` は同じ内容を二進数キーのマップとして保持
- `64ka_optimized.json` には追加で `下卦` / `上卦` / `下卦記号` / `上卦記号` が入っています

## 補足

- このリポジトリは小さなデータ置き場として維持しています。
- `base_hexagrams.json` は最小構成、`64ka_optimized.json` は参照用の付加情報つきです。
