# 旧 EXTRACT 資産の切り分け

新版（v2.0.0）は、通常の占断だけを扱います。旧版にあった EXTRACT（`[MODE:EXTRACT]` と `[TEMPLATE:...]` で振り分け、引用・高島本文をスクリプトで機械組み立てする方式）の資産は、新版には含めていません。この文書は、その切り分けと、削除候補・影響・戻し方の記録です。

## 新版に含めたもの

| 旧版の所在 | 新版での扱い |
|---|---|
| `references/library/`（22ファイル） | そのまま `references/library/` に収録。資料不足の場合の参照ライブラリとして継続使用 |
| `references/normal-mode.md` | 内容を `references/reading-rules.md` に改訂・統合（MODE 振り分けの記述を除き、正確さと断定の調整、根拠の厚みの規則を追加） |
| `references/extract-ranking.md` | 重み付けを `references/comparison.md` に引き継ぎ、比較の物差しと僅差の場合の注意を追加 |
| `SKILL.md`（v1.0.0） | 全面改訂（v2.0.0）。通常占断の手順だけを定義 |

## 新版に含めなかったもの（旧 EXTRACT 専用）

| 資産 | 内容 | 件数（Hermes パッケージ側） |
|---|---|---|
| `spec/extract_contract.md` | EXTRACT の実行契約の正本 | 1 |
| `formats/` | 出力形式の正本（shared、ex_simple_single、ex_simple2_single、ex_5_single、ex_compare_single） | 5 |
| `scripts/` | 組み立て・骨組み・次ファイル名決定などの実行用スクリプト | 11 |
| `assets/` | 引用の正本 `honka.md`、`koji.md`、高島解釈 `takashima/`（64卦）、`高島易断占例.md`、`README.md` | 68 |
| `fixtures/` | 再現テスト用の入力と canonical answer | 11 |
| `tests/test_build_extract_prompt.py` | EXTRACT プロンプト生成のテスト | 1 |
| `received/`、`work/` | EXTRACT の入力保存と回答の出力先（入出力記録） | 場所のみ（中身は各導入先に残る） |

## 原本の所在（戻し先）

削除はまだ行っていません。旧資産の原本は、次の場所にそのまま残っています。

1. **アルカナの現行導入先（C側）**：`C:\Users\nekol\AppData\Local\hermes\profiles\arcana\skills\ekikyo\`。新版へ入れ替えるまでは旧版がそのまま動きます。
2. **Hermes 導入パッケージ（エイダ側の控え）**：`~/workspace/goals/hermes-agent-study/files/hermes-ekikyo-bot-package/skill/ekikyo/`（2026-11-02 作成の配布物一式。Bot の SOUL.md や導入手順も含む）。
3. **エイダの Muse 版スキル**：`~/workspace/custom-skills/ekikyo/`。EXTRACT の正本・スクリプト・入出力記録（received 5件、work 5件）を含む現行一式。今回の作業では変更していません。

## 削除候補と影響、戻し方

新版の導入と確認が終わった後に、次が削除候補になります。**この文書の提示時点では、どれも削除していません。** 削除は本人の承認を得てから行います。

| 削除候補 | 影響 | 戻し方 |
|---|---|---|
| C側の現行導入先にある旧 EXTRACT 資産（`spec/`、`formats/`、`scripts/`、`assets/`、`fixtures/`、`tests/`、`received/`、`work/`） | EXTRACT 形式での回答ファイル生成（EX_SIMPLE、EX_SIMPLE2、EX_5、EX_COMPARE の機械組み立て）ができなくなります。通常占断と比較占い（文章での順位付け）には影響しません | 上記2または3の控えから、対象フォルダをそのままコピーして戻します。`SKILL.md` も旧版（v1.0.0）に戻します |
| Drive 側 `30_resources/skills/` の lib-skills 作業ツリー内にある旧 `ekikyo` フォルダ | 2026-11-13 の確認では、Drive 側では中身が空でした。削除対象の実物はありません。GitHub の `ys1887/lib-skills` 側の同名フォルダは、この配布とは別の管理物です | 対象外（GitHub 側は従来どおり） |

## 注意

- このフォルダ（新版の配布物）は、`30_resources/skills/` の lib-skills 作業ツリーの中では、yomiyasu と同様に git の管理対象外（未追跡）の置き物として扱われます。
- エイダの Muse 版スキル（上記3）は今回の対象外です。Muse 側で EXTRACT を使う場合は、従来どおりそちらを使います。
