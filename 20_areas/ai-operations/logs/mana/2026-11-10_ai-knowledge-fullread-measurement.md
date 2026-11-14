# AI_knowledge 全文読み込みの消費測定

- 測定日：2026-11-10（日本時間）
- 実行者：マナ（Hermes Agent、`mana` プロフィールのこのセッション）
- 対象：`E:\Documents\Google Drive\AI_knowledge` 配下の測定時点の全ファイル
- 開始前の使用量取得：23:42:06.125542 JST（初回の時刻確認は23:41:57.748234 JST。使用量の基準値を取得した時刻を起点とする）
- 終了後の使用量取得：23:43:36.024636 JST
- 経過時間：89.899094 秒（使用量取得時刻間）
- 読み込み：33ファイル、合計179,967バイト。読めなかったファイルなし。

## セッション記録の使用量

| 項目 | 開始前 | 終了後 | 差分 |
|---|---:|---:|---:|
| 入力トークン（通常） | 24,461 | 86,862 | 62,401 |
| キャッシュ読みトークン | 61,109 | 691,953 | 630,844 |
| キャッシュ書き込みトークン | 0 | 0 | 0 |
| 出力トークン | 697 | 3,093 | 2,396 |
| 推論トークン（別掲、出力に加算しない） | 161 | 995 | 834 |
| API コール回数 | 4 | 17 | 13 |
| ツール呼び出し回数 | 4 | 17 | 13 |

値はこのプロフィールのローカル `state.db` の `sessions` 行に記録された、このセッションのスナップショット。プロバイダーの請求量ではなく、進行中のターンが即時反映される保証もない。実験前のスキル読み込みや確認も開始前の値に含まれ、開始後のファイル列挙、読み込み、使用量取得などの作業も差分に含む。キャッシュ読みはAPIコールで再利用した文脈を含むため、差分を「ファイル本文そのもののトークン数」とは解釈しない。読み込み中の出力にはファイル本文がツール結果として入るため、秘密情報等の値はこの記録へ転載しない。

**測定の締めは終了後の使用量取得時点。** このチャットでの測定報告と、この記録の新規作成、`exchange/mana/index.md` の追記、その確認にかかる消費は上表の差分に含めない。

## 読んだファイル（相対パス、測定時のバイト数）

| ファイル | バイト |
|---|---:|
| `README.md` | 7,843 |
| `common/2026-11-08_mail-migration-status.md` | 2,409 |
| `common/2026-11-08_yomiyasu-consultation.md` | 3,193 |
| `common/2026-11-09_x-activity-knowledge.md` | 1,057 |
| `common/changelog.md` | 4,741 |
| `common/index.md` | 634 |
| `common/settings-index.md` | 1,812 |
| `Context/2026-11_mail-backlog-index.md` | 100,096 |
| `Context/2026-11_mail-index.md` | 1,453 |
| `Context/2026-11_x-activity.md` | 1,040 |
| `Context/README.md` | 2,343 |
| `exchange/ada/2026-11-08_nikke-residual-checks.md` | 2,271 |
| `exchange/ada/2026-11-09_muse-pc-environment.md` | 5,988 |
| `exchange/ada/backup/AGENTS.md` | 6,456 |
| `exchange/ada/backup/IDENTITY.md` | 607 |
| `exchange/ada/backup/README.md` | 1,260 |
| `exchange/ada/backup/SOUL.md` | 3,372 |
| `exchange/ada/index.md` | 704 |
| `exchange/ada/settings.md` | 3,652 |
| `exchange/claude/index.md` | 1,167 |
| `exchange/claude/settings.md` | 1,186 |
| `exchange/codex/index.md` | 196 |
| `exchange/codex/settings.md` | 875 |
| `exchange/gemini/index.md` | 198 |
| `exchange/gemini/settings.md` | 884 |
| `exchange/mana/2026-11-09_hermes-profiles-and-shared-skills.md` | 6,782 |
| `exchange/mana/2026-11-09_hermes-storage-migration.md` | 4,108 |
| `exchange/mana/2026-11-10_ai-knowledge-rule-discrepancies.md` | 2,868 |
| `exchange/mana/index.md` | 719 |
| `exchange/mana/settings.md` | 8,427 |
| `templates/handoff.md` | 355 |
| `templates/record.md` | 330 |
| `templates/settings.md` | 941 |

読み込み対象に設定変更の指示として扱う内容はない。測定のため、設定は変更していない。
