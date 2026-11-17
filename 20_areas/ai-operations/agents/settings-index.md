# AI設定の一覧

各AIの現行設定は、agents の各AIのフォルダ内の固定ファイル `settings.md` にまとめます。このファイルは、その入口と比較表です。

| 参加者 | 設定ファイル | 実行場所 | モデル・プロバイダ | 最終確認日 | 状態 |
|---|---|---|---|---|---|
| エイダ | `ada/settings.md`（このフォルダ内） | Muse の VM（Ubuntu）／チャット | Muse Wonder／Muse Power | 2026-11-09 | 記入済み |
| マナ／Hermes Agent | `mana/settings.md`（このフォルダ内） | Windows PC の Hermes Agent（Desktop／Bot Chat、CLI） | GPT-6 Sol（プロバイダ nous） | 2026-11-09 | 記入済み |
| Codex | `codex/settings.md`（このフォルダ内） | 未記入 | 未記入 | 未記入 | 受け皿のみ |
| Claude | `claude/settings.md`（このフォルダ内） | 未記入 | 未記入 | 未記入 | 受け皿のみ |
| Gemini | `gemini/settings.md`（このフォルダ内） | 未記入 | 未記入 | 未記入 | 受け皿のみ |

## 更新ルール

- 各AIは、自分の `settings.md` だけを更新します。直接書けないAIの分は、受け皿（未記入のファイル）を置くところまでを代行できます。内容の記入を代行する場合は、本人の許可を得て、経路と出典を明記して行います。
- `settings.md` は現行設定の要約と正本の所在を書く場所です。実際の設定そのものではありません。内容が実際の設定と食い違う場合は、正本を優先します。
- パスワード、復旧キー、APIキー、トークン、認証ファイルの内容は書かないでください。設定ファイルの写しや抜粋を置く場合も、秘密情報を除いたものだけにします。
- 設定を変更したら、同じ作業の中で `settings.md` の最終確認日と変更履歴も更新します。

## 共通索引基盤：AutoRAG（2026-11-17、構築途中・利用不可）

- 実物最終確認日・台帳最終更新日：2026-11-17。本人承認の設定作成とイヴへの登録試行。接続が既定30秒でタイムアウトし、保存確認にnと回答して停止。イヴのMCP登録・索引はまだなく、マナを含む他Botは未登録。
- 設定正本：`C:\Users\nekol\.autorag\config.json`。workspaceは `C:\Users\nekol\.autorag\workspace` に明示設定。索引予定先はその `.autorag\` 配下だが未作成。モデル予定先はWindows既定の `C:\Users\nekol\AppData\Local\minsync\models`（未取得）。設定・workspaceは作成済み。
- 固定版：`@autorag/librarian@2.13.12`。`jikji=false`、`everything=false`、`fsearch=false`、`datasources={}`。検索rootはAI_knowledgeのみ。outputsは含め、99_backup・codex-sessions・メール/カレンダー形式・生成物・過去プロジェクトwork・スキルreceived/workを除外。正確なパターンとコマンドは下記報告書を参照。
- MCP予定設定：`AUTORAG_MCP_READ_ONLY=true`、`AUTORAG_MCP_TOOLS=autorag.status,autorag.search`。認証探索分離とnpm子プロセス設定を含むが、イヴconfigには未保存。利用・検索成功を意味しない。
- KB全体17,867ファイルの前後比較は追加・変更・削除0、新規Jikji map0。refresh未実行のため容量・時間は未計測。比較完了後にこの台帳等の意図した記録更新を実施。
- 更新は将来の手動CLI refreshのみを予定。定期実行・Marketplace一式・付属setupスキル・Desktopペイン・サービス接続は導入しない。再開には本人との相談が必要。
- 共有報告：`../outputs/nayuta/eve-autorag-introduction.md`。現在Bot側で外す登録はなく、生成物の削除は別途判断。将来のマナ利用は同じ設定・索引への登録を別途承認して追加する。この記録自体で権限・設定は変わらない。
