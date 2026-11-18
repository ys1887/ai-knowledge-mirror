# マナ ターミナル／タスクスケジューラ運用 実施案（承認前ドラフト）

- 作成: 2026-11-18 / ナユタ（nayuta）
- 対象: `C:\Users\nekol\AppData\Local\hermes\profiles\mana`（マナのみ。他 Bot には触れない）
- 位置づけ: **実施案**。承認まで実ファイルは変更していない（本調査は読み取りのみ）。
- モデル設定・`approvals.mode`（smart）・管理者権限の扱いは変更しない。

---

## 0. 追加調査の結果（依頼された確認事項）

### 0-1. 既存タスクの実行先（`Get-ScheduledTask` 全 203 件を機械的に列挙）

| 確認項目 | 結果 |
|---|---|
| 実行先に `E:\Documents\Hermes Agent` を含むタスク | **0 件**（`Execute`／`Arguments`／`WorkingDirectory` のいずれにも `Documents` を含む行は 0） |
| バックアップ系タスクの実体 | `\Hermes-Agent-Full-Backup` → `C:\WINDOWS\py.exe -3.13 "C:\Users\nekol\scripts\hermes-backup-daily.py"`（CWD `C:\Users\nekol\scripts`） |
| 同期系タスク | `\ai-knowledge-mirror-sync` → `powershell.exe -File "C:\Users\nekol\scripts\ai-knowledge-mirror-sync.ps1"` |
| Obsidian 系 | `\Obsidian Backup` → `C:\Users\nekol\scripts\obsidian-backup\obsidian-backup.cmd` |

→ **タスクの付け替えは不要。`E:\Documents\Hermes Agent` は削除して差し支えない**（タスク起点では）。

補足（削除前に知っておくべき2点）:

1. バックアップスクリプトのステージング先は `E:\Documents\Backup\Hermes Agent`（`hermes-backup-daily.py:17`）。**削除予定の `E:\Documents\Hermes Agent` とは別フォルダで、実在する**。名前が酷似しているため、削除操作の対象パスを取り違えないこと。当該フォルダを消すとバックアップが壊れる。
2. マナのスキル文書 `skills/note-taking/obsidian/references/windows-vault-mirror.md` が `E:\Documents\Hermes Agent\mana\obsidian-backup-report-2026-11-08.md` を参照している（歴史的記述）。同じ行に「`C:\Users\nekol\Proton Drive` を開くな」という禁止文も残っている。**SOUL ではなくスキル文書側に古い禁止・古いパスが残っている**ので、SOUL だけ直すと矛盾が残る。今回は対象外（マナのスキル編集は別承認）だが、実施案の最後に任意項目として挙げる。

### 0-2. 前提の再確認（実測）

- `C:\Users\nekol\Proton Drive` は存在しない（`C:\Users\nekol\Proton` は 0 バイトのファイル）。マナの SOUL に Proton の記載はない。
- `C:\Users\nekol\AppData\Local\hermes\profiles\` に `\Mana` タスクフォルダは未作成。ルートに `\ai-knowledge-mirror-sync`、`\Hermes-Agent-Full-Backup` ほか。
- マナの現行設定: `approvals.mode=smart` / `approvals.deny=[]` / `command_allowlist=[]` / `security.protected_instruction_files=true` / `terminal.backend=local`（bash, `schtasks`・`pwsh` 利用可）。

---

## 1. 仕組みの分担（確定案）

| 層 | 実装 | 役割 |
|---|---|---|
| 恒常禁止（承認でも不可） | `approvals.deny`（fnmatch・無条件・yolo でも有効） | ディスク操作、他 Bot プロフィール、認証ファイル、`99_backup` |
| 承認の線引き（①自作は素通し／②それ以外は承認） | `hooks.pre_tool_call` シェルフック `mana_policy.py`（`fail_closed: true`） | スケジューラ操作の自作判定、`/TR` 制限、GUI 経路、`execute_code` 内 subprocess、`write_file`/`patch` のパス検査 |
| 文章上の決め | `SOUL.md` | 3段階の承認条件、フォルダ規約、読み戻し、作業記録、GUI 操作は承認あり |

**deny で線引きが書けない理由（再掲）**: `approvals.deny` は一致したら無条件ブロックのみ。例外（自作タスクなら許可）を表現できないため、①/②の判定はフック側に置く。deny には「絶対に許可しないもの」だけを入れる。

---

## 2. 変更するファイル一覧

| # | ファイル | 種別 | 内容 |
|---|---|---|---|
| 1 | `profiles\mana\config.yaml` | 変更（`hermes config set` 経由、手編集しない） | `approvals.deny` に §3 の候補を設定。`hooks.pre_tool_call` に §4 のフック1件を登録 |
| 2 | `profiles\mana\agent-hooks\mana_policy.py` | 新規 | §4 のポリシーフック本体（標準ライブラリのみ） |
| 3 | `profiles\mana\SOUL.md` | 変更 | §5 のとおり承認3段階・フォルダ規約・読み戻し・記録・GUI 規定を追記（BOM/CRLF 維持） |
| 4 | `profiles\mana\shell-hooks-allowlist.json` | 追記（初回同意1回） | フックの `(event, command)` 同意。同意プロンプトで本人が承認した結果として生成 |
| 5 | `E:\...\ai-operations\outputs\mana\mana-scheduler-policy-20261118\` | 新規（控え） | 変更前の `config.yaml`／`SOUL.md` の全文写し＋差分＋README（戻し手順） |
| 6 | `E:\...\ai-operations\logs\mana\2026-11-18_mana-scheduler-policy.md` | 新規（マナの作業記録 兼 実施記録） | 変更内容・試験結果・戻し方・未確認事項 |
| 7 | `E:\...\AI_knowledge\changelog.md` | 末尾追記1行 | 構成・ルール変更としてナユタが追記 |

変更しないもの: `approvals.mode`、モデル設定、他 Bot のプロフィール、`profile.yaml`、バックアップ処理、`command_allowlist`。

---

## 3. `approvals.deny` 候補

判定は「コマンド文字列（小文字化・難読化解除後）に対する fnmatch」。`*` は区切り文字も含めて一致するため、パス系は両方の区切り文字形を入れる。

### 3-1. 他 Bot プロフィール（8 Bot × 2 区切り = 16）

```
*profiles/arcana*      *profiles\arcana*
*profiles/crown*       *profiles\crown*
*profiles/eve*         *profiles\eve*
*profiles/label*       *profiles\label*
*profiles/nayuta*      *profiles\nayuta*
*profiles/phantom*     *profiles\phantom*
*profiles/raven*       *profiles\raven*
*profiles/takina*      *profiles\takina*
```

### 3-2. Hermes の認証ファイル・`.env`（8）

```
*hermes/auth.json*           *hermes\auth.json*
*hermes/.env*                *hermes\.env*
*profiles/*/auth.json*       *profiles\*\auth.json*
*profiles/*/.env*            *profiles\*\.env*
```

### 3-3. `99_backup`（1）

```
*99_backup*
```
※ターミナルからの直接操作を止める。写しの更新は従来どおり `write_file` 等の意図的な作業で行う（フック側も deny 対象にしない）。

### 3-4. ディスク系（26）

```
*diskpart*            *format.com*          * format c:*        * format d:*
* format e:*          *format /fs*          *format /q*         *format-volume*
*clear-disk*          *initialize-disk*      *set-disk*          *new-partition*
*remove-partition*    *resize-partition*     *repair-volume*     *dd if=*
*dd of=*              *mkfs*                *mke2fs*            *fdisk*
*bcdedit*             *bootrec*             *bootsect*          *physicaldrive*
*sdelete*             *cipher /w*           *wmic diskdrive*    *wmic partition*
*fsutil*              *vssadmin delete*     *wbadmin delete*
```
方針: 読み取り専用の `format`／`fsutil` 相当も含めて一律禁止（安全側）。`Format-Table` 等の PowerShell 表示コマンドレットを巻き込まないよう、`*format*` 単独の広いグロブは使わない。

### 3-5. スケジューラ系（deny に入れるのは「常に不可」の4件のみ）

```
*schtasks*/create*/ru*system*
*schtasks*/create*/ru *system*
*register-scheduledtask*-user*system*
*register-scheduledtask*-user*nt authority*
```
`/ru SYSTEM` 等の特権プリンシパルは管理者権限領域なので常時禁止。**それ以外の登録・変更・削除・実行は §4 のフックで①②を判定**する（deny では「自作なら許可」が書けないため）。

---

## 4. フック `mana_policy.py` 仕様

### 4-1. 登録（`config.yaml`）

```yaml
hooks:
  pre_tool_call:
    - matcher: "terminal|execute_code|computer_use|write_file|patch"
      command: "C:/Users/nekol/AppData/Local/hermes/profiles/mana/agent-hooks/mana_policy.py"
      timeout: 10
      fail_closed: true
hooks_auto_accept: false        # 初回のみ同意プロンプト（本人が承認）
```
- `matcher` は tool 名への `fullmatch`。`hooks_auto_accept` は **false のまま**（同意は本人が1回だけ行う）。同意前はフックがスキップされるため、**試験の最初に同意を通す**のを必須手順にする。
- `fail_closed: true`：フックが落ちた／タイムアウトした場合は通さず止める。

### 4-2. 入出力

stdin に `{hook_event_name, tool_name, tool_input, cwd, profile, ...}`、stdout に判定 JSON。
- 何も出さない（exit 0）= 許可
- `{"action":"block","message":"..."}` = 恒常禁止（承認不可）
- `{"action":"approve","message":"...","rule_key":"mana:..."}` = 承認ゲートへエスカレーション（②）

### 4-3. 判定表

| 対象 | 条件 | 判定 |
|---|---|---|
| terminal / execute_code の文字列 | §3 の禁止パターンに一致 | **block** |
| terminal / execute_code | スケジューラ読み取り（`schtasks /query` `/show`、`Get-ScheduledTask`、`Export-ScheduledTask`） | 許可 |
| 〃 | 書き込み系（`schtasks /create /change /delete /run /end`、`Register-/Set-/Unregister-/Start-/Stop-/Enable-/Disable-ScheduledTask`）で、タスク名が `\Mana\` 配下 | タスク実行先の条件を満たせば許可 |
| 〃 | 同・実行先（`/tr`、`-Action`/`-Execute`）が**マナの領域外** | **approve**（承認へ） |
| 〃 | 同・タスク名が `\Mana\` 配下でない／名前から特定できない（`/tn` 省略・GUI 相当） | **approve** |
| computer_use | `tool_input` に「タスク スケジューラ」「Task Scheduler」「taskschd.msc」「Get-ScheduledTask」等を含む | **approve** |
| computer_use | 上記以外 | 許可（GUI 一般操作は SOUL の通常ルールに委ねる） |
| write_file / patch | パスが他 Bot プロフィール／`hermes` 直下の `auth.json`・`.env` | **block** |
| write_file / patch | パスが `99_backup` 配下 | 許可（写し更新は正当作業。ただし SOUL の意図的な変更作業に限る） |

「マナの領域」= `C:\Users\nekol\AppData\Local\hermes\profiles\mana`、`E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\mana`、`...\20_areas\ai-operations\logs\mana`、`...\20_areas\ai-operations\agents\mana`。
パス比較は小文字化・`\`→`/` 正規化・引用符除去のうえ前方一致。`/TR` に引数付きで書かれた場合（`"...\x.cmd" /arg`）は最初のトークンだけを見る。

### 4-4. 監査ログ

フックは block / approve を出したときだけ `profiles\mana\state\policy-audit.jsonl` に1行追記（日時・tool・判定・理由・コマンド先頭200字）。秘密情報の値は書かない。人向けの作業記録は SOUL の規定どおりマナが `logs\mana` に書く。

### 4-5. 既知の限界（文章で残す）

- フックは「実行されるコマンド文字列」しか見ない。マナが `.cmd`/`.ps1` を自分で書いてから実行する経路は内容を検査できない（書き込み先の制限で緩和するのみ）。
- `execute_code` 内の Python から `subprocess` で `schtasks` を呼ぶ経路は、`approvals.deny` では止まらない（コード側に deny 参照がない）。フックのコード文字列検査で塞ぐが、難読化されると完全ではない。
- Computer Use は対象ウィンドウを機械判定できないため、GUI 経由のスケジューラ操作は **SOUL の明文規定＋文字列ヒューリスティック**の二段構え。

---

## 5. SOUL 追記案（`# 事前承認` の直前 or 直後に新節）

```markdown
# ターミナルとタスクスケジューラの扱い
- 承認の段階は3つ。
  1. 承認なし: 読み取り専用の調査（状態確認・ログ参照・schtasks /query・Get-ScheduledTask）、自分の作業領域内の可逆なファイル操作、フォルダ \Mana\ 配下の自分が作ったタスクの作成・変更・実行・削除。
  2. 事前承認: インストール、レジストリ、サービス、PC・OSの設定変更、\Mana\ 以外または自分が作っていない既存タスクの変更・削除、大量の移動・削除、ネットワーク・セキュリティの設定、タスクスケジューラの GUI 操作。
  3. 恒常禁止（承認でも不可）: ディスク操作（format / diskpart / Clear-Disk / Initialize-Disk / Set-Disk / パーティション作成削除 / dd / fsutil など）、他 Bot のプロフィール、Hermes 直下の認証ファイル（auth.json・.env）、AI_knowledge の 99_backup への直接操作。
- 自分のタスクは専用フォルダ \Mana\ に置き、名前に Mana- を付ける。自作かどうかはフォルダで判定する。
- 承認なしで作れるタスクの実行先は、自分と自分の成果物の領域（自己プロフィール、outputs\mana、logs\mana、agents\mana）配下に限る。それ以外を指すなら事前承認を得る。
- タスクを登録・変更したら必ず schtasks /Query または Get-ScheduledTask で読み戻して確認する。承認が要る範囲は「提示→承認→登録→読み戻し」、承認なしの範囲は「登録→読み戻し→作業記録」の順。
- 承認なしで行った変更操作は、何を・いつ・どういう結果だったかを logs\mana の作業記録に残す。
- スケジューラの GUI 操作は承認ありとして扱う。GUI で見るだけの確認は読み取りとみなすが、変更前に必ず承認を得る。
```

（既存の「事前承認」「作業範囲と記録」「変更履歴」は維持し、変更履歴に1行追記する。）

---

## 6. 試験手順（承認後）

1. **控え**（§2-5）を取得。`config.yaml` に秘密情報の値がないことをローカルで確認してから写す（値を出力しない）。`SOUL.md` は BOM/CRLF を保持して複製。
2. `hermes config set approvals.deny '<JSON配列>'` → `hermes config get approvals.deny` で読み戻し。
3. `hermes config set hooks.pre_tool_call '<JSON>'` → 読み戻し。
4. `mana_policy.py` を配置し、標準入力に固定 JSON を流して単体動作を確認（許可／block／approve の3系統）。
5. マナの新セッションを開き、**フック同意プロンプトを本人が1回承認**。`shell-hooks-allowlist.json` に登録されたことを確認。
6. `\Mana\` フォルダ作成（`pwsh` の Schedule.Service COM）。作れない場合は `Register-ScheduledTask -TaskPath '\Mana\'` で代替し、`schtasks /create` がフォルダを自動作成するかも併せて実測。
7. 自作タスク一巡（承認なしで通ること）:
   - `outputs\mana\schedtest.cmd` を作成（`echo ok`）
   - `schtasks /create /tn "\Mana\Mana-Selftest" /tr "E:\...\outputs\mana\schedtest.cmd" /sc once /st HH:MM /f`
   - `schtasks /query /tn "\Mana\Mana-Selftest" /fo list /v` で読み戻し
   - `schtasks /run /tn "\Mana\Mana-Selftest"` → 実行結果確認
   - `schtasks /delete /tn "\Mana\Mana-Selftest" /f` → `Get-ScheduledTask -TaskPath '\Mana\'` で消えたことを確認
   - ここまで各操作の時刻と結果を `logs\mana` に記録（SOUL の「登録→読み戻し→記録」を実地検証）
8. 承認エスカレーションの確認（承認プロンプトが出て、拒否したら実行されないこと）:
   - `schtasks /create /tn "Mana-Outside" /tr "C:\Windows\System32\notepad.exe" /sc once /st HH:MM`
   - `schtasks /create /tn "\Mana\Mana-BadTr" /tr "C:\Windows\System32\cmd.exe" /sc once /st HH:MM`
   - `schtasks /delete /tn "ai-knowledge-mirror-sync" /f`（既存タスクは実行しない。承認プロンプトで拒否して無変更を確認）
9. 恒常禁止の確認（承認でも不可・即ブロック）:
   - `schtasks /create /tn "\Mana\Sys" /tr "x" /ru SYSTEM`
   - `diskpart` / `format e:` / `fsutil volume diskfree c:`
   - `cat C:\Users\nekol\AppData\Local\hermes\auth.json`
   - `ls "C:\Users\nekol\AppData\Local\hermes\profiles\raven"`
   - `ls "E:\Documents\Google Drive\AI_knowledge\99_backup"`
   - `execute_code` で `subprocess.run(["schtasks","/query"])` → フックで block
   - Computer Use で `taskschd.msc` を開く指示 → approve へ
10. 設定が効いた状態での再起動確認（マナのセッションを開き直し、`hermes -p mana config get approvals.deny` を読み戻し）。
11. 結果を `logs\mana` と `changelog.md` に記録。残る未確認事項（GUI 経路、難読化されたコード等）を明記。

---

## 7. 戻し方

1. `hermes config set approvals.deny '[]'`
2. `hermes config set hooks.pre_tool_call '[]'`
3. `profiles\mana\agent-hooks\mana_policy.py` を削除（空ディレクトリも削除）
4. `shell-hooks-allowlist.json` から当該エントリを削除
5. `SOUL.md` を控えから復元（BOM/CRLF を保持）／`config.yaml` は控えと差分比較してから復元
6. 試験で作った `\Mana\` 配下タスクを全て削除（`schtasks /delete /tn "\Mana\<name>" /f`）し、`\Mana` フォルダも不要なら削除
7. マナのセッションを開き直し、`approvals.deny`・`hooks` が空であることを読み戻す
8. `changelog.md` に戻しの1行を追記（履歴は消さない）

---

## 8. リスクと判断事項

- **過剰ブロックの可能性**: `*fsutil*`・`* format e:*` 等は読み取り目的でも止まる。安全側に倒した結果であり、必要になれば個別に緩める（緩和は承認事項）。
- **フック同意前は無防備**: `hooks_auto_accept: false` のため、同意前のセッションではフックがスキップされる。試験手順5を飛ばさないこと。
- **deny とフックの二重管理**: 盤面が2か所になるため、片方だけ直すと食い違う。SOUL と本記録に「正は config.yaml の deny ＋ フックの判定表」と明記する。
- 任意項目（今回は実施しない）: マナの `skills/.../windows-vault-mirror.md` に残る旧パス（`E:\Documents\Hermes Agent\mana\...`）と `C:\Users\nekol\Proton Drive` の記述整理。マナ本人のスキル編集になるため別承認。


---

## 実施結果（2026-11-18 追記）

本実施案は本人承認のうえ実施済み。結果・試験ログ・戻し方は
`20_areas/ai-operations/logs/mana/2026-11-18_mana-scheduler-policy.md` に記録した。

- `approvals.deny` 60 パターン（`config.yaml` 2368 行目以降）／`hooks.pre_tool_call` 1 件（同意記録済み）
- フック単体 24/24、実経路 7/7 ＋ deny 実ガード 9/9 が期待どおり
- 実セッションで自作タスクの一巡（作成→読み戻し→実行→削除）が承認なしで成功、`diskpart` と他Botプロフィール参照は遮断
- 未実施: 承認エスカレーションの対話セッションでの目視（-q ではマナが SOUL 判断でコマンドを実行しなかった）
- 実務上の発見: `schtasks /TR` は空白入りパスで切れる（`Register-ScheduledTask` を使う）
