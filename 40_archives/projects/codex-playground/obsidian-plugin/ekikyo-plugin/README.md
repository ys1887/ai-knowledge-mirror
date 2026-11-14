# ekikyo-plugin

このリポジトリは、Obsidian 用の `ekikyo` プラグイン本体と、プラグインが参照する同梱データを管理するための作業用リポジトリです。

## データ運用

このリポジトリ内の `vendor/ekikyo/assets` は、`data/quote-dataset.json` を生成するための入力です。関連プロジェクトの assets と併用しているため、データ更新時は両方の差分を確認します。

- 関連プロジェクト側 assets:
  - `E:\Documents\Playground\ekikyo\assets`
- プラグイン repo 側 assets:
  - `vendor/ekikyo/assets`
- Obsidian プラグイン実体の配布先:
  - `C:\Users\nekol\Proton Drive\Obsidian\.obsidian\plugins\ekikyo`

## 標準フロー

1. 編集済みの場所を確認し、`E:\Documents\Playground\ekikyo\assets` と `vendor\ekikyo\assets` の差分を確認する。
2. 必要に応じて両方の assets を同期する。
3. データ変更に応じて `py scripts\generate_quote_dataset.py` を実行し、`data\quote-dataset.json` を再生成する。
4. Obsidian プラグイン実体
   `C:\Users\nekol\Proton Drive\Obsidian\.obsidian\plugins\ekikyo`
   へ必要ファイルを配布する。
5. このリポジトリで commit / push する。

## 直接編集してよい場所

- プラグイン実装コード
  - `main.js`
  - `manifest.json`
  - `package.json`
  - `versions.json`
- このリポジトリ固有の説明ファイル
  - `README.md`
  - `AGENTS.md`

## 原則直接編集しない場所

- `vendor/ekikyo/assets`
  - `data\quote-dataset.json` の生成入力。手動編集は原則避けるが、明示された場合はここで編集し、必要に応じて `E:\Documents\Playground\ekikyo\assets` へ戻す。
  - 現行の生成入力は `本文抜粋.md`、`占断抜粋.md`、`高島易断占例.md`、`takashima/` です。`honka.md` と `koji.md` は `archive/` に保管しています。
- `data/quote-dataset.json`
  - 原則として `scripts\generate_quote_dataset.py` により再生成する。

`vendor/ekikyo/assets/README.md` は assets ディレクトリ内部の説明です。repo 全体の運用説明はこの `README.md` と `AGENTS.md` で扱います。
