# ekikyo.jp カテゴリ記事ダウンローダー

`https://ekikyo.jp/archives/category/takashimaekidan` のカテゴリ記事だけを収集して、`md` ファイルとして保存する CLI です。

## 使い方

```bash
cd /home/ys/projects/ekikyo-md-downloader

python3 ekikyo_md_downloader.py \
  --url "https://ekikyo.jp/archives/category/takashimaekidan" \
  --out ./downloads
```

収集対象だけ確認したい場合は `--dry-run` を付けます。

```bash
python3 ekikyo_md_downloader.py \
  --url "https://ekikyo.jp/archives/category/takashimaekidan" \
  --out ./downloads \
  --dry-run
```

## 動作

- カテゴリページとページングだけをたどります。
- 記事 URL は `https://ekikyo.jp/archives/<数字>` 形式だけを対象にします。
- 保存は 1 記事 1 ファイルです。
- 同名なら `-2`, `-3` を付けて別保存します。
- 画像は保存しません。

## テスト

```bash
python3 -m unittest discover -s tests -v
```
