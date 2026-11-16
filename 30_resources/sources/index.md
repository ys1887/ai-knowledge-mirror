# 資料一覧

`30_resources/sources`（このフォルダ）にある資料と、大きさや形式の都合で外部を正本とする資料の索引です。ここでいう sources は原資料・参照資料の意味で、ソースコードの置き場ではありません。資料を追加した者が、自分の追加分をその場でここへ書いてください。

| 資料 | 場所 | 用途・使うAI | 種別 | 正本 | 更新担当 | 最終確認日 |
|---|---|---|---|---|---|---|
| Linux and the Unix Philosophy（Mike Gancarz、2003） | `linux-and-the-unix-philosophy.md`（同フォルダ） | PC の操作・設定の考え方の土台として参照する。本人の提示した資料 | 確定資料 | ここ | エイダ | 2026-11-13 |
| The Art of Unix Programming（Eric S. Raymond、2003） | `the-art-of-unix-programming.md`（同フォルダ） | Gancarz の原則の下の層として、設計・実装を考えるときに参照する。本人が 2026-11-15 に提示した資料 | 確定資料 | ここ | エイダ | 2026-11-15 |
| A Philosophy of Software Design（John Ousterhout、2018） | `a-philosophy-of-software-design.md`（同フォルダ） | コードを書く・書かせる場面の設計の層として、複雑さの低減とモジュール設計を考えるときに参照する。本人が 2026-11-15 に提示した資料 | 確定資料 | ここ | エイダ | 2026-11-15 |
| The Pragmatic Programmer（David Thomas／Andrew Hunt、2019、第2版） | `the-pragmatic-programmer.md`（同フォルダ） | 作法・運用の層として、道具の習慣や仕事の進め方を考えるときに参照する。本人が 2026-11-15 に提示した資料 | 確定資料 | ここ | エイダ | 2026-11-15 |
| X アーカイブ（本人の投稿テキストと自投稿メディア） | `x-archive/`（同フォルダ内） | 本人の過去の発言と関心を、話題が出たときに検索して原文を引く。全AIが参照する | 現行資料 | 本人の PC `E:\Documents\archives` の公式アーカイブ ZIP | エイダ | 2026-11-13 |
| 英語教材（Essential Grammar in Use、English Grammar in Use、The Oxford 3000） | `english-textbooks/`（同フォルダ内、索引は `english-textbooks/index.md`） | イギリス英語学習の教材。エイダ（🇬🇧 English）と Hermes の語学担当 Bot が参照する。原本は編集・削除・移動しないこと | 現行資料 | ここ（本人の決定で原典 PDF もここに置く。エイダ側 `workspace/user/files/` にも控えあり） | エイダ | 2026-11-16 |

- 現行資料：内容が変わり得る資料。更新担当を決め、実物を確認した日を最終確認日にします。
- 確定資料：過去の記録や成果物のように、内容を差し替えない資料。
- 秘密情報の値は、資料にも索引にも書かないでください。
- `linux-and-the-unix-philosophy.md` は、本人が提示した PDF から機械的に変換したものです。表と図のレイアウトは再現していません。原本の PDF は本人の手元にあります。
- `the-art-of-unix-programming.md` は、本人が 2026-11-15 に提示した PDF（549ページ）から機械的に変換したものです。表と図のレイアウトは再現していません。原本の PDF は Muse 側の `workspace/user/files/The_Art_of_Unix_Programming.pdf` に保管しています。本文は Creative Commons BY-ND 1.0 で公開されたものなので、この md は本人のナレッジベース内部での参照用に限り、外部へ配らないでください。
- `a-philosophy-of-software-design.md` は、本人が 2026-11-15 に提示した PDF（初版、188ページ、calibre 変換版）から機械的に変換したものです。図の画像は再現しておらず（この本では図が重要なので、図が要る箇所は PDF を見てください）、表のレイアウトも再現していません。原本の PDF は Muse 側の `workspace/user/files/A_Philosophy_of_Software_Design.pdf` に保管しています。著作権は著者にあります（Copyright © 2018 John K. Ousterhout）。この md は本人のナレッジベース内部での参照用に限り、外部へ配らないでください。
- `the-pragmatic-programmer.md` は、本人が 2026-11-15 に提示した PDF（第2版、497ページ、calibre 変換版）から機械的に変換したものです。図の画像は再現しておらず、表のレイアウトも再現していません。サイドバーの囲みは本文として取り込み、章頭の引用は引用ブロックとして残しています。原本の PDF は Muse 側の `workspace/user/files/The_Pragmatic_Programmer__20th_Anniversary_Edition.pdf` に保管しています。著作権は Pearson Education にあります（Copyright © 2020 Pearson Education, Inc.）。この md は本人のナレッジベース内部での参照用に限り、外部へ配らないでください。
- 上の書籍4冊の md は、2026-11-15 に本人の指示で、著者紹介と連絡先メール等の部分を除いてあります（Gancarz と Ousterhout の著者紹介、Ousterhout の感想送付先の段落群、Thomas＆Hunt の出版社の販売窓口と感想送付先・献辞・巻頭の推薦文）。謝辞も同日に削除しました（Gancarz、Raymond、Thomas＆Hunt の謝辞。Ousterhout には謝辞の記載がありませんでした）。原本 PDF は無変更で、削除箇所は各 md の冒頭注記にも記録してあります。
- `x-archive/` は、本人の決定で 2026-11-13 に配置しました。投稿テキスト全件（24,467件）と自投稿・返信のメディア269件です。リポストのメディアは容量の都合で入れておらず、正本の ZIP にのみあります。範囲と注意は `x-archive/index.md` に書いています。

## Hermes の入力資料について

- Hermes の Bot が参照する資料（旧 `E:\Documents\AI\inputs` の代替）も、ここに置きます。旧 inputs フォルダは空だったため、2026-11-12 にエイダが削除済みです。2026-11-13、本人承認により Hermes 側のレーベルの SOUL と登録簿の資料参照先を `30_resources/sources` に更新し、ファイルを読み戻しました。新規CLIでの資料読み取りとDesktop／Bot Chatでの参照動作は未確認です
- Bot の入力資料で「原本は編集・削除・移動しない」扱いのものは、この索引の行にその旨を書いてください
