# 易経プロジェクト｜ソース・インデックス

- このファイルは、登録済みソースの一覧と探索起点を示すためのインデックスである。
- このプロジェクトは EXTRACT 専用であり、占い結果の整理・抽出・解釈に用いる。

## 1-1. EXTRACTソース

### 引用用ソース

- quotes_honka.md  
  - 本卦・之卦・互卦・錯卦・綜卦の引用用
  - 各卦は見出しごとにまとまっている
  - EX_SIMPLE では、該当する卦見出しから次の卦見出し直前までの block を、そのまま引用用 block として扱う

- quotes_koji.md  
  - 変爻の引用用
  - 各卦の下に各爻が見出しごとにまとまっている
  - EX_SIMPLE では、該当する爻見出しから次の爻見出し直前までの block を、そのまま引用用 block として扱う

### 解釈用ソース（高島）

- 1–8：takashima_interp_01-08.md
- 9–16：takashima_interp_09-16.md
- 17–24：takashima_interp_17-24.md
- 25–32：takashima_interp_25-32.md
- 33–40：takashima_interp_33-40.md
- 41–48：takashima_interp_41-48.md
- 49–56：takashima_interp_49-56.md
- 57–64：takashima_interp_57-64.md

### 補助ソース

- jokaden.md  
  - 序卦伝
  - 必要な場合のみ、流れを見る補助として参照する

- bungenden.md  
  - 文言伝
  - 乾為天・坤為地に関係する場合のみ、必要に応じて補助的に参照する

- keijiden.md  
  - 繋辞伝
  - 卦や易全体の原理を補助的に確認したい場合のみ参照する
  - 独立した主軸ソースとしては扱わず、必要な範囲に限って補助的に用いる

## 1-2. EXTRACT出力テンプレート

- ex_simple_output_template.md：EX_SIMPLE 用
- ex_5_output_template.md：EX_5 用
- ex_compare_output_template.md：EX_COMPARE 用
