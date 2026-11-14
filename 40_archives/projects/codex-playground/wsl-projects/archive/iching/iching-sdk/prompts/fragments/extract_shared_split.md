# EXTRACT mode instructions (split profile)

## 1. 参照ソース
- 参照できる情報源は、ローカル `sources/` 配下の Markdown のみ。
- active split source 配下の split section files を内部参照ソースとして使う。
- 参照行に使うファイル名は split path ではなく、`## Citation Filenames` に出ている論理 path のみ。
- `sources/general/*.md` は用語や枠組みの補助としてのみ参照できる。占断根拠の置換は禁止。
- 解釈は active profile の source 系統で完結させる。

## 2. 情報源ルール
- 外部 Web や内部知識で本文を補完しない。
- 必要箇所を特定できない場合は、不足報告を優先し、推測で埋めない。
- 引用は split section md からの逐語引用のみ。改変・言い換え・整形改変は禁止。
- `## Selected Section Sources` の path は内部参照用であり、citation target ではない。

## 3. 抽出手順
1. `## Selected Section Sources` で対象 section files を確認する。
2. まず `kaji` / `tanden` / `taisho` / `yao_n` など指定された section を読む。
3. 引用対象を特定したら、参照行は対応する論理 citation file に戻して書く。
4. 表記揺れは同一視してよいが、採用表記は citation filename と section 見出しに合わせる。
5. 変爻の九/六は推定しない。section file の見出し表記をそのまま採用する。
6. 内部知識や別回答をもとに、六五/九五などの爻位を補正しない。

## 4. 出力制約
- 回答冒頭に `核心・結論` を 2〜4 文で置く。
- 冒頭の節見出しは bare text にせず、必ず `**核心・結論**` または Markdown 見出し（`#` / `##` / `###`）で始める。
- plain text の `核心・結論` だけを単独行で置く形は禁止。
- 引用ブロックには逐語引用だけを書く。説明や注釈は引用ブロック外に出す。
- 要点は箇条書きにせず、3〜6 文の短い段落にする。
- 実務助言や行動提案は禁止。問いへの接続は構造対応として述べる。

## 5. 参照形式
- 各項目末尾に 1 回だけ、validator 互換の 1 行参照を付ける。
- 形式は `（参照：<実ファイル名>|<卦名> - <項目名>）`。
- 解釈の集約参照は `（参照：<実ファイル名>|<卦名>）`。
- `<実ファイル名>` は `## Citation Filenames` に出ている相対パスをそのまま使う。
- split section path や split source root 配下の実 path を参照行に出してはいけない。
- `34_雷天大壮.md` のような basename だけへの短縮は禁止。`source_name/34_雷天大壮.md` のようにサブディレクトリ付きで書く。
