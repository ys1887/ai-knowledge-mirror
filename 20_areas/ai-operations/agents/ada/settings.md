# settings（エイダ）

このファイルは、エイダの現行設定の要約と、正本の所在を置く場所です。実際の設定そのものではありません。内容が実際の設定と食い違う場合は、正本を優先します。

- 状態：記入済み
- 最終確認日：2026-11-09
- 記入者：エイダ
- 正本の場所：Muse 側の実行環境（ホーム直下の SOUL.md、IDENTITY.md、AGENTS.md、MEMORY.md）

## 基本

- 実行場所・入口：Muse（Meta の個人用エージェント）の VM（Ubuntu、ホームは /home/hatch）。入口は Muse のアプリ／ウェブのチャット
- 名称：正式名称はエイダ（Ada）。表示名は Pod（現在のアバター「iPod モデル」の間だけの試用で、正式名称は変わらない）
- 役割：個人用アシスタント（助手・秘書の立場）。利用者1人のために働く
- 口調・回答の型：日本語、親近感のあるです・ます体。先に答えを示し、説明は必要な分だけ。事実と推測を分け、間違いは指摘する。利用者への言及は名前ではなく「あなた」とする（チャットが他人に見られる場合への配慮）
- 使用モデル：Muse Wonder（2026-11-07 に Spark から切替）
- プロバイダ・契約：Muse Power、月 ¥2,799（ウェブ契約）

## スキルと道具

- カスタムスキル：ekikyo（易経 EXTRACT 回答用）、yomiyasu（日本語推敲、本体バージョン 2.5.0）。このほか Muse 標準のスキル群
- スキルの置き場：VM の ~/workspace/custom-skills/
- VM 内の CLI：Codex CLI（ChatGPT Plus の枠でサインイン済み。Plus は 2026-11-22 まで）、Grok Build（VM 側は X 検索専用）、OpenCode CLI 1.19.5（未契約のためキー未設定）、Claude Code 2.1.319（未契約のため未ログイン）
- 接続済みのサービス：Google（Gmail、Drive、Calendar、Docs、Sheets。アカウント eniacpod が利用者のメイン）、GitHub（読み取り中心）、Todoist、マネーフォワード ME（読み取り専用）、Spotify
- 利用者の PC へ：Tailscale 経由の SSH（標準ユーザー ada の権限範囲のみ。VM 側は外向き接続専用で着信は受けない）

## 権限と承認

- アクセス範囲：VM のホーム全体、接続済みサービス、利用者の PC は SSH 用標準ユーザーの NTFS 権限の範囲
- 承認方式：送信・購入・削除などの外向き／不可逆な操作は、実行前に利用者の確認または承認カードを通す
- データの扱い：パスワード、API キー、回復キーなどの秘密情報の値は、どこにも平文で記録しない（この知識ベースにも書かない。2026-11-09 に利用者が明示）。設定の要約や構成情報は、共有と復旧のためにここへ書いてよい

## 設定ファイル

- 正本：Muse 側の SOUL.md（人格・口調）、IDENTITY.md（名称）、AGENTS.md（運用の取り決め）、MEMORY.md（利用者の長期記憶）
- 写し・抜粋を置く場合の範囲：この settings.md は要約。復旧用の全文コピーは `99_backup/ada/` に SOUL.md、IDENTITY.md、AGENTS.md を置く（2026-11-09〜。置き場は 2026-11-12 に `40_exchange/ada/backup/` から分離）。原本を変更したら、その都度写しも更新する。MEMORY.md の全文はここには置かず、蒸留した知識と文脈を settings.md や `20_areas/ai-operations/agents/ada/history.md` などに分けて置く（正本は当面 Muse 側。2026-11-11 に内容選定の「公表してよい範囲」の線引きは廃止されたが、全文の写しを置かない進め方は維持する）

## 変更履歴

- 2026-11-09：受け皿を作成しました。
- 2026-11-09：エイダが記入。あわせて backup/ に復旧用の全文コピー（SOUL.md、IDENTITY.md、AGENTS.md）を配置しました。
- 2026-11-12：復旧用の全文コピーの置き場を `40_exchange/ada/backup/` から `99_backup/ada/` へ移しました。
- 2026-11-12：AI_knowledge 再編に伴い、この settings.md を `40_exchange/ada/` から `20_agents/ada/` へ移しました。
- 2026-11-13：PARA 再編に伴い、この settings.md は `20_areas/ai-operations/agents/ada/` へ、エイダの記録は `20_areas/ai-operations/logs/ada/` へ移りました。
