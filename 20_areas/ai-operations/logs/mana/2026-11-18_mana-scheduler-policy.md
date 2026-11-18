# マナ ターミナル／タスクスケジューラ運用の変更記録（実施済み）

- 実施: 2026-11-18 16:05–16:20 / 実施者: ナユタ（nayuta）／本人承認済み
- 対象: `C:\Users\nekol\AppData\Local\hermes\profiles\mana` のみ
- 変更前の控え: `E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\mana\mana-scheduler-policy-20261118\`（`config.yaml.before`／`SOUL.md.before`、sha256 一致確認済み）
- 実施案: `20_areas/ai-operations/outputs/nayuta/2026-11-18_mana-scheduler-policy-plan.md`

## 1. 変更した内容

| ファイル | 変更 |
|---|---|
| `config.yaml` | `approvals.deny` に 60 パターン（`hermes config set` 経由）。`hooks.pre_tool_call` に 1 件（`mana_policy.py`、matcher `terminal\|execute_code\|computer_use\|write_file\|patch`、timeout 10、`fail_closed: true`） |
| `agent-hooks\mana_policy.py` | 新規。tier3=block／tier2=approve／tier1=許可を判定。block/approve 時のみ `state\policy-audit.jsonl` に記録 |
| `SOUL.md` | 「# ターミナルとタスクスケジューラの扱い」節を追加（承認3段階、`\Mana\` 規約、`/TR` 制限、読み戻し、作業記録、GUI は承認あり）。変更履歴に1行。BOM なし・CRLF 維持 |
| `shell-hooks-allowlist.json` | フック同意を1回記録（2026-11-18T07:10:41Z approved） |

変更していないもの: `approvals.mode`（smart）、モデル設定、`command_allowlist`、管理者権限の扱い、他 Bot のファイル、バックアップ処理、`profile.yaml`。

## 2. 試験結果

| 試験 | 結果 |
|---|---|
| フック単体（24ケース、実 stdin/stdout プロトコル） | 24/24 期待どおり（許可9・承認8・遮断7） |
| Hermes 実経路（`_spawn`→`_evaluate_result`） | 7/7 期待どおり。`approvals.deny` 実ガード 9/9 期待どおり |
| フォルダ `\Mana\` 作成 | `folder-created`（Schedule.Service COM、追加権限不要） |
| 自作タスク一巡（マナの実セッション、`-q`＝承認プロンプト無し環境） | 作成→読み戻し→実行→`ran.log`（`ran 2026/11/18 16:15:12.47`）→削除→削除後 query は「指定されたパスがありません」。**承認要求は一度も出なかった** |
| 恒常禁止（実セッション） | `diskpart /?` が `BLOCKED by mana policy: ... /\bdiskpart\b/ ...` で遮断。他 Bot プロフィールへの `ls` も遮断 |
| 承認エスカレーション（実セッション） | **未実施**。マナが SOUL 判断でコマンド自体を実行しなかった（機械側の判定を経由していない）。別途ハーネスで「フックが approve を返し、承認ゲートが『Asking the user for approval』を返す」ことを確認済み |

## 3. 実施中に判明した実務上の注意

- `schtasks /Create /TR "E:\...spaces...\x.cmd"` は、値に空白を含むパスだと**先頭の空白で切られる**（実測: `Execute=E:\Documents\Google` / `LastResult=2147942402`）。空白入りパスを実行先にするなら、PowerShell の `Register-ScheduledTask -Action (New-ScheduledTaskAction -Execute ...)` か、二重引用のエスケープが必要。SOUL の `/TR` 制限を運用するときはこの点に注意する。
- 単一クエリ実行（`-q`）では `pwsh -Command` が危険コマンド扱いで自動拒否される（`approvals.single_query_mode=deny` の仕様）。対話セッションでは本人の承認で通る。今回のフォルダ作成はナユタ側で実施した。

## 4. 残っている作業（未実施・要判断）

1. `99_backup\mana\` の `config.yaml`／`SOUL.md` 全文写しと COPY-NOTE の更新（マナ本人の通常作業。ナユタは他 Bot の `99_backup` を編集しない）。
2. `20_areas/ai-operations/agents/mana/profile.md`（登録簿）の承認条件欄の更新（マナ本人のフォルダ。別承認）。
3. マナのスキル `skills/note-taking/obsidian/references/windows-vault-mirror.md` に残る旧パス（`E:\Documents\Hermes Agent\mana\...`）と `C:\Users\nekol\Proton Drive` の記述整理（任意・別承認）。
4. 承認エスカレーションの対話セッションでの目視確認（Desktop のマナ会話で、`\Mana\` 外のタスク操作が承認待ちになること）。

## 5. 戻し方

1. `hermes -p mana config set approvals.deny '[]'`
2. `hermes -p mana config set hooks.pre_tool_call '[]'`
3. `agent-hooks\mana_policy.py` を削除（ディレクトリごと）
4. `hermes -p mana hooks revoke <上記パス>` で同意を削除
5. `SOUL.md` を `mana-scheduler-policy-20261118\SOUL.md.before` から復元（CRLF・BOMなしを維持）。`config.yaml` は `.before` と差分比較のうえ復元
6. `\Mana\` 配下のタスクを削除（現時点で 0 件）し、不要ならフォルダも削除
7. マナのセッションを開き直し、`approvals.deny` と `hooks` が空であることを読み戻す

## 6. 追記（2026-11-18、文言修正）

- `SOUL.md` の恒常禁止のうち 99_backup の記述が限定なしで「ターミナルからの直接操作」より広く読めたため、`AI_knowledge の 99_backup 配下へのターミナルからの直接操作（読み取り・削除・移動を含む）。99_backup の写し更新は、従来どおり意図的な変更作業のなかでファイル操作の道具（write_file 等）を用いて行い、ターミナル経由では行わない。` へ修正し、変更履歴に1行追記した。
- `approvals.deny` とフックの判定は変更していない（もともとターミナルのみ遮断、write_file／patch は許可）。フック単体試験の `write own 99_backup copy = allow` と `ls 99_backup = block` がこの分担と一致している。
- マナの新セッションで読み込みを確認（1) ターミナル操作は読み取り・削除・移動も禁止、2) 写し更新は write_file 等で行う、と正しく回答）。
- 未追随: 登録簿 `20_areas/ai-operations/agents/mana/profile.md` の 43 行目が同じ限定なしの文言のまま（マナ本人のフォルダのため、本人の追随が必要）。
