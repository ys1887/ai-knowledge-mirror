# Ameblo テーマ記事ダウンローダー

Ameblo のテーマ一覧ページから、記事リンクだけを収集して `md` ファイルとして保存する小さな CLI です。

## 使い方

```bash
python3 ameblo_md_downloader.py \
  --url "https://ameblo.jp/kokorokeiei/theme-10085932248.html" \
  --out ./downloads
```

収集対象の確認だけしたい場合は `--dry-run` を付けます。

```bash
python3 ameblo_md_downloader.py \
  --url "https://ameblo.jp/kokorokeiei/theme-10085932248.html" \
  --out ./downloads \
  --dry-run
```

## 動作

- テーマ一覧ページと「次ページ」リンクだけをたどります。
- 記事 URL は `entry-<数字>.html` 形式だけを対象にします。
- 保存は 1 記事 1 ファイルです。
- 同名があれば `-2`, `-3` を付けて別保存します。
- 画像は保存しません。

## テスト

```bash
python3 -m unittest discover -s tests
```
