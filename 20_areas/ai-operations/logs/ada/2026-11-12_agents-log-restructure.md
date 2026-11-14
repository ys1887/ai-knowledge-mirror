# AI_knowledge 再編の実施記録（20_agents 化・settings 集約・log 化）

- 日付：2026-11-12
- 実施：エイダ（ユーザーの指示と承認による）
- 設計：同日の設計メモ「AI_knowledge 再編の設計（3点セット）」に基づきます

## 実施した内容

- フォルダ改名：`20_bots` → `20_agents`（対象を Hermes の Bot から、利用者が運用してきた Bot と AI 全般へ拡大）、`40_exchange` → `40_log`。フォルダとファイルの ID は不変です
- フォルダ新設：`20_agents` に codex、claude、gemini
- settings.md 5件（エイダ、マナ、codex、claude、gemini）を、参加者フォルダから `20_agents` の各 AI のフォルダへ移動しました
- 文書の更新：ルート README（構成図、ルール、読み順、マナの書き込み範囲）、`00_home/settings-index.md`、`20_agents/index.md`（定義の拡大と、一覧へのエイダ・Codex・Claude・Gemini の追加）と `_template.md`、各 profile（出典と現行パス）、エイダの history、`30_context/README.md`、各参加者の index、`00_home/changelog.md` と `00_home/work-log.md` への記録
- 定期ジョブ：朝のスペース系一括更新の指示文にある Hermes Bots の正本パスを `20_agents/` へ更新しました
- スペース：AI_knowledge の参加者メモと変更履歴を追随しました。スペース「Hermes Bots」は Hermes 分の表示のままとし、正本は `20_agents` の登録簿です

## 決めた運用形態

- 登録簿の一覧には全 AI を載せ、種別は役割の記述で区別します
- profile.md は登録側の要約、settings.md はその AI 自身が書く現行設定の要約です。Hermes の各 Bot は settings.md を作らず、マナだけが両方を持ちます
- Hermes 側へは、完成した構成と運用ルールを指示文で引き渡しました（Hermes 側の SOUL 等の旧パス参照は、Hermes 側で順次更新します）

## 残っていること

- `40_log/claude/index.md` の settings の記載は、Claude のフォルダのため触っていません（実物は `20_agents/claude/settings.md`）。Claude 側での更新待ちです
- Hermes 側のローカルファイル（SOUL、記憶ファイル）の旧パス参照の更新は、引き渡し文に基づき Hermes 側で実施します
