# Shakespeare 全集コーパス（Project Gutenberg）

シェイクスピアの原文テキスト一式。ホームズ全集（`sherlock-holmes/`）と同じ形で、1作品1ファイル＋この索引で構成する。読み取り専用として扱い、必要な作品だけを索引から引いて読む。

## 出典と取得

- 出典：Project Gutenberg（全作品パブリックドメイン）
- 取得日：2026-11-19
- 取得経路：www.gutenberg.org がメンテナンス中だったため、Project Gutenberg の公式代替ホスト gutenberg.pglaf.org から取得した。本文ファイルは本家と同一の正本
- 底本系統：Gutenberg 公式の案内で「最も完全」とされる 1500 番台シリーズを正本とし、詩篇の一部（ソネット集 #1041、『ヴィーナスとアドーニス』#1045）は同案内が併せて推す番号で補った
- 各ファイルは Gutenberg のヘッダとライセンス文を含む原文のまま。語数はファイル全体の概数（ヘッダ等を含む）

## 構成

- `works/`：戯曲38＋詩篇5＝43ファイル
- `apocrypha/`：外典5ファイル（下記の注意参照）
- `raw/`：取得した Gutenberg 原ファイル51件の控え（重複版を含む）

## 戯曲（works/、38作）

| ファイル | 作品 | PG# | 語数 |
|---|---|---:|---:|
| king-henry-vi-part-1.txt | King Henry VI, Part 1 | 1500 | 25,929 |
| king-henry-vi-part-2.txt | King Henry VI, Part 2 | 1501 | 30,012 |
| king-henry-vi-part-3.txt | King Henry VI, Part 3 | 1502 | 29,190 |
| king-richard-iii.txt | King Richard III | 1503 | 34,441 |
| the-comedy-of-errors.txt | The Comedy of Errors | 1504 | 19,267 |
| titus-andronicus.txt | Titus Andronicus | 1507 | 24,783 |
| the-taming-of-the-shrew.txt | The Taming of the Shrew | 1508 | 25,326 |
| the-two-gentlemen-of-verona.txt | The Two Gentlemen of Verona | 1509 | 21,602 |
| loves-labours-lost.txt | Love's Labour's Lost | 1510 | 25,647 |
| king-john.txt | King John | 1511 | 25,040 |
| king-richard-ii.txt | King Richard II | 1512 | 26,620 |
| romeo-and-juliet.txt | Romeo and Juliet | 1513 | 29,005 |
| a-midsummer-nights-dream.txt | A Midsummer Night's Dream | 1514 | 20,335 |
| the-merchant-of-venice.txt | The Merchant of Venice | 1515 | 25,451 |
| king-henry-iv-part-1.txt | King Henry IV, Part 1 | 1516 | 28,889 |
| the-merry-wives-of-windsor.txt | The Merry Wives of Windsor | 1517 | 26,736 |
| king-henry-iv-part-2.txt | King Henry IV, Part 2 | 1518 | 30,731 |
| much-ado-about-nothing.txt | Much Ado about Nothing | 1519 | 25,710 |
| king-henry-v.txt | King Henry V | 1521 | 30,567 |
| julius-caesar.txt | Julius Caesar | 1522 | 24,057 |
| as-you-like-it.txt | As You Like It | 1523 | 26,196 |
| hamlet.txt | Hamlet | 1524 | 34,989 |
| twelfth-night.txt | Twelfth Night | 1526 | 24,402 |
| troilus-and-cressida.txt | Troilus and Cressida | 1528 | 30,693 |
| alls-well-that-ends-well.txt | All's Well That Ends Well | 1529 | 27,657 |
| measure-for-measure.txt | Measure for Measure | 1530 | 26,024 |
| othello.txt | Othello | 1531 | 30,965 |
| king-lear.txt | King Lear | 1532 | 30,723 |
| macbeth.txt | Macbeth | 1533 | 21,432 |
| antony-and-cleopatra.txt | Antony and Cleopatra | 1534 | 29,814 |
| coriolanus.txt | Coriolanus | 1535 | 32,498 |
| timon-of-athens.txt | Timon of Athens | 1536 | 22,887 |
| pericles-prince-of-tyre.txt | Pericles, Prince of Tyre | 1537 | 22,813 |
| cymbeline.txt | Cymbeline | 1538 | 32,036 |
| the-winters-tale.txt | The Winter's Tale | 1539 | 29,189 |
| the-tempest.txt | The Tempest | 1540 | 20,583 |
| king-henry-viii.txt | King Henry VIII | 1541 | 28,999 |
| the-two-noble-kinsmen.txt | The Two Noble Kinsmen | 1506 | 28,931 |

## 詩篇（works/、5作）

| ファイル | 作品 | PG# | 語数 |
|---|---|---:|---:|
| the-sonnets.txt | The Sonnets | 1041 | 20,712 |
| venus-and-adonis.txt | Venus and Adonis | 1045 | 13,230 |
| the-rape-of-lucrece.txt | The Rape of Lucrece | 1505 | 18,081 |
| the-phoenix-and-the-turtle.txt | The Phoenix and the Turtle | 1525 | 3,421 |
| a-lovers-complaint.txt | A Lover's Complaint | 1543 | 5,617 |

## 外典（apocrypha/、5作）

シェイクスピアの名で伝わったが、今日では単独作とは認められないもの。出典として使うときは外典である旨を明示する。

| ファイル | 作品 | PG# | 語数 | 備考 |
|---|---|---:|---:|---|
| the-passionate-pilgrim.txt | The Passionate Pilgrim | 1544 | 6,190 | 1599年にシェイクスピア名義で刊行。他者の詩を含む |
| sonnets-on-sundry-notes-of-music.txt | Sonnets on Sundry Notes of Music | 1546 | 4,421 | 『情熱の巡礼者』の詩に曲を付けた楽譜集（1600年）由来 |
| mucedorus.txt | Mucedorus | 1545 | 16,560 | 帰属は否定されている |
| sir-thomas-more.txt | Sir Thomas More | 1547 | 24,403 | 複数作者の合作。一場面（Hand D）がシェイクスピア筆とされる |
| locrine.txt | Locrine | 1548 | 20,054 | 「W.S.」名義で刊行された外典 |

## 除外した重複版（raw/ に控えあり）

- Much Ado about Nothing #1520 と Twelfth Night #1527：ファイル内に「改訂版が別にある」旨の注記がある旧版のため、正本は #1519／#1526 を採用
- The Two Noble Kinsmen #1542：Brooke 編『Shakespeare Apocrypha』（1908）由来の別版のため、正本は #1506 を採用

## 注意

- 『二人の貴公子』（The Two Noble Kinsmen）と『ヘンリー八世』はフレッチャーとの合作、『ペリクリーズ』も合作とされるが、現代の標準全集に含まれるため works/ に置いた
- 原文は初期近代英語。現代の校訂版（Folger、Arden 等）の注や解説には編集者の権利が残るため、このコーパスには含めない
