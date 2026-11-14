# AI_knowledge 内の git 全外し（2026-11-14 実施記録）

## 要点

- AI_knowledge 内にあった入れ子 git 12 件の `.git` をすべて削除し、通常フォルダにした。git の実体は Drive 外のコピー側に残っている。
- 削除前に 12 件全件の棚卸しを行い、コピーの完全性を検証したうえで実行した。失われた情報はない。
- 検証は 3 段で行い、すべて通過した：コピー側の照合、ミラー側の全走査、Drive API での残存確認（0 件）。

## 1. 背景と決定

- プロジェクトの置き場所の規則（2026-11-14 決定）：Drive 内で全てを管理しない。コード類は Drive 外で git 管理し、今後 git が必要なら Drive 外で行う。
- Drive 内の既存 git は完成済みのものが中心だったため、本人の案で整理した：対象 2 フォルダ（`40_archives/projects/codex-playground` と `30_resources/skills`）を Drive 外へコピーし、そのうえで Drive 内の git を削除する。GitHub 側との違いへの対応は、コピーした方のフォルダで行う。

## 2. 棚卸し（削除前の実測）

対象 12 件：skills（lib-skills）と、codex-playground 内の 11 件（bin、custom_prompts、ekikyo、ekikyo_project、firepanel、obsidian-plugin、wsl-projects 配下の apps、ekikyo、llm-wiki、archive 配下の ekikyo-sdk、iching）。

- 条件（GitHub に対応リポジトリがある、先端が一致、クリーン、未保存ブランチなし）をすべて満たし、そのまま消せたのは 3 件（custom_prompts、firepanel、llm-wiki）。
- 8 件には GitHub に無い情報が残っていた（大半は未コミットの変更のみ。wsl-projects の ekikyo は未 push のコミット自体、ekikyo-sdk は先端の一致が未確認）。
- lib-skills は現役の作業ツリー（未コミット 18 行、ブランチ 12 本）。
- 棚卸しの一覧は Muse 側の作業文書（ai-knowledge-git-inventory-2026-11-14/inventory.md）に置く。
- なお、PC のエイダ用アカウントからは GitHub への git 接続（ls-remote）が通らなかったため、先端の照合は GitHub コネクタ側で行った。

## 3. コピーと検証

- コピーは本人が robocopy で実施した。コピー先は `E:\Documents\git-copies\`（codex-playground と skills）。
- 検証（エイダ）：フォルダ単位で件数・容量が完全一致（codex-playground 24,981 件／453,048,203 バイト、skills 979 件／16,509,599 バイト）。リポジトリ単位でも、コピー側 12 件すべての先端コミットと未コミット変更行数が棚卸しの値と一致した。

## 4. 削除の実施

- エイダが PC ミラー側で `.git` 12 件を削除した（中身の合計 10,888 ファイル）。作業ファイルには触れていない。
- 削除後の件数は計算どおり（codex-playground 14,801 件、skills 271 件）。
- AI_knowledge 全体を走査し、名前が `.git` の項目は残っていない。残っている `.gitignore` 等は作業ファイルの一部として残した。
- Drive API でも `.git` フォルダの残存 0 件を確認した（削除直後は同期の反映途中で 6 件見えたが、数分後の再確認で 0 件）。

## 5. 現在の扱い

- AI_knowledge の中に git 管理は無い。今後 git が必要な作業は Drive 外で行う。
- lib-skills のリポジトリとしての実体は `E:\Documents\git-copies\skills`。Drive 内の skills は、git のない配布・保管エリアになった。
- codex-playground のリポジトリとしての控えは `E:\Documents\git-copies\codex-playground`。GitHub 側との違いへの対応は、そちらで行う。

## 追記：Drive 外コピーの git 調節（2026-11-14 19:20 完了）

- 未保存分はエイダがコピー側でスナップショット commit（`chore: snapshot local working state (2026-11-14)`）を作り、本人が Push した。全リポジトリで、GitHub 側のブランチ先端と PC 側の一致をエイダが検証した。
- 対象外だった 3 件（custom_prompts、firepanel、llm-wiki）は、もともと GitHub と一致していた。
- ekikyo_project の main だけは Push していない。GitHub 側が 1 commit 先行しており、PC 側の内容は GitHub の履歴に含まれているため、不足はない。
- ekikyo-sdk は GitHub 側にリポジトリが無かったため、本人が新規作成（Private、空）してから Push した。なお、iching リポジトリの中にある ekikyo-sdk はフォルダであり、独立リポジトリではない。
- lib-skills は、スキルが全 AI 共通になった実態に合わせ、GitHub 側の名前を `skills` へ改名した（Push を先に済ませてから改名）。コピー側の接続先 URL も新名に書き換え済み。`30_resources/skills` の一覧も現行の状態に更新した。

## 追記：コピー側フォルダの削除（2026-11-14 19:23）

- 調節の完了後、本人の指示で `E:\Documents\git-copies\` の 2 フォルダ（codex-playground、skills）をエイダが削除し、両方とも消えたことを確認した。
- 削除前に確認した根拠：全リポジトリの履歴と管理対象ファイルは GitHub にあり先端の一致を検証済み。stash は全リポジトリで無し。git 管理外のファイル（apps の `iching-calculator/archive/` 約 81 MB など）は、コピー元の Drive 側フォルダに同じ内容が残っている。
- 今後、これらのリポジトリで作業するときは GitHub から clone する。
