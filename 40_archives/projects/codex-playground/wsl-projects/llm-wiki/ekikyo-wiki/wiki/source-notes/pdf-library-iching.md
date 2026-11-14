# PDF Library 易経

**ページ目的:** PDF ライブラリの構成と、版確認ソースとしての使いどころを整理する。

## ソースの性格

この場所には 30 以上の PDF があり、大きく二群に分かれる。

- 一般向け・機械読取可能な易経本
  - `i-ching_book.pdf`
  - `i-ching_book2.pdf`
- 高島系 PDF 群
  - `高島易断_01` - `高島易断_10`
  - `高島易断_増補版_01` - `高島易断_増補版_05`
  - `高島易断_横浜図書版/`
  - `周易占筮法秘伝.pdf`
  - `周易活断.pdf`
  - `易占大意 _ 神人伝言.pdf`
  - `高島周易講釈 _ 占断自在.pdf`

## 強み

- 高島系の複数 edition がまとまっており、底本確認の母艦として強い。
- 一般向け易経本 2 点は `pdftotext` で読めるため、初回 foundation でも機械確認しやすい。
- 少なくとも一部 PDF は `pdfinfo` から著者・作成情報・ページ数を確認できる。

## 限界

- 高島系の中心ファイルは image scan が多く、OCR なしでは本文確認が難しい。
- 版の重なりは見えるが、どの edition がどこまで対応するかは未整理。
- このライブラリ単独では運用ルールや source hierarchy は見えにくい。

## 初回 foundation での使いどころ

- 「どの高島系資料がローカルにあるか」の地図化。
- Obsidian ノートや markdown source の底本確認の入口。
- 一般向け易経本と高島系専門資料を分けて扱うための基礎整理。

## 要確認

- `高島易断_横浜図書版` の構成と他版との差。
- 高島系 PDF 群の OCR 方針。
- `i-ching_book.pdf` と `i-ching_book2.pdf` の書誌情報。

## Provenance

- `/home/ys/projects/llm-wiki/ekikyo-wiki/schema/source-registry.md`
- `/mnt/e/Documents/PDF/易経/i-ching_book.pdf`
- `/mnt/e/Documents/PDF/易経/i-ching_book2.pdf`
- `/mnt/e/Documents/PDF/易経/高島易断/高島易断_01.pdf`
- `/mnt/e/Documents/PDF/易経/高島易断/高島易断_増補版_01.pdf`
- `/mnt/e/Documents/PDF/易経/高島易断/周易占筮法秘伝.pdf`
- `/mnt/e/Documents/PDF/易経/高島易断/高島周易講釈 _ 占断自在.pdf`

_Note: 2026-04-07 の初回 ingest では `pdfinfo` と `pdftotext` による冒頭確認を併用した。_
