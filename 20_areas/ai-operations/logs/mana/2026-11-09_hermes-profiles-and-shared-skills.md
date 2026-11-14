# Hermesのプロフィールと共通スキルの構成

- 記録日：2026-11-09
- 記録者：マナ（Hermes Agent）
- 種別：PC側の構成・確認手順の共有。設定変更の依頼や実行許可ではない。
- 確認範囲：このPCのHermes CLI、スキルの配置、各プロフィールの参照設定。認証情報の値や会話本文は確認・記録していない。

## プロフィールと保存場所

このPCで確認したHermesのプロフィールは、デフォルトHermes（`default`）、マナ（`mana`）、アルカナ（`arcana`）、レーベル（`label`）、ファントム（`phantom`）。利用者の説明では、現在主に動いているのはデフォルトHermes・マナ・アルカナで、レーベルとファントムは作成済みだが運用していない。後者も共通スキルを参照できる設定にしてある。

- デフォルトHermes：`C:\Users\nekol\AppData\Local\hermes\`。設定は直下の `config.yaml`、固有スキルは `skills\`。
- 名前付きBot：`C:\Users\nekol\AppData\Local\hermes\profiles\<プロフィール名>\`。それぞれに `config.yaml`、`SOUL.md`、`skills\`、記憶・セッション関連データがある。
- Botごとの役割や行動上の制約は `SOUL.md` や適用される指示にも依存する。スキルを共有しても、役割・アクセス許可まで共通化されるわけではない。

## yomiyasuの共通配置

共通スキルの実体は `E:\Documents\Hermes Agent\shared-skills\yomiyasu\`。`SKILL.md`、参照文書、Python検査スクリプトを含む配布元の一式を配置している。配布元は `nanaism/yomiyasu` の特定改訂版 `8394e099486aaa2e28cf89992e46f5ebe5ed839d`、本体バージョン2.5.0。マナの専用 `skills\yomiyasu` は、共通版へ切り替えた後に退避して除いた。現時点でマナ・アルカナ・レーベル・ファントムの専用スキルフォルダにも同名スキルはない。

5プロフィールそれぞれの `config.yaml` の `skills.external_dirs` は `E:/Documents/Hermes Agent/shared-skills` を参照する。実行した `hermes -p <プロフィール名> skills list --enabled-only` では、各プロフィールに `yomiyasu` が表示された。マナでは `skill_view` が実際に共通フォルダの `SKILL.md` を返した。CLIのマナの一覧には旧URL導入の表示が残る場合があるため、一覧の「Source」欄だけで実際の参照元を判定しない。

同名のスキルをプロフィール固有の `skills\` に置くと、共通外部フォルダの同名スキルより固有版が優先される。共通版を更新すれば、参照するプロフィール全体へ影響する。`yomiyasu` は名前を挙げて推敲を依頼されたときに使う方針であり、共通配置だけで普段のすべての文章へ自動適用されるわけではない。付属検査は架空の短文を使い、マナの作業領域内に状態記録先を明示して `run`（lint・diff）と `verify` を実行済み。ただし各Botが新しい会話で推敲する挙動は個別には未試験。検査の記録には原文と最終稿の写しが残り得るため、本番時の保存先と機密性を都度確認する。

このスキル一式は標準のHub導入経路で完全に取り込めず、本人の承認を得て直接配置した。Hermesのスキャナーによる一式の判定は `CAUTION` だった。検査スクリプトの実行成功は、コード全体の安全性や推敲結果の意味の保持を保証しない。

## スキル・道具・承認方式の確認

以下はWindowsのPowerShellまたはコマンドプロンプトから実行する、読み取り中心のHermes CLIコマンド。`<名前>` には `mana`、`arcana`、`label`、`phantom`、`default` を指定する。値を表示するだけでは設定は変わらない。

```text
hermes profile list
hermes -p <名前> config path
hermes -p <名前> skills list --enabled-only
hermes -p <名前> config get skills.external_dirs
hermes -p <名前> tools list --platform cli
hermes -p <名前> config get approvals.mode
hermes -p <名前> config get skills.write_approval
```

スキル一覧は利用可能な手順・知識、`tools list` はその実行面で有効な道具を示す。`--platform cli` はCLIの表示であり、デスクトップやBot Chatの全権限を確定する一覧ではない。`approvals.mode` はシェルコマンドの承認方式で、フォルダ単位の閲覧許可そのものではない。確認時点の5プロフィールは `approvals.mode=smart`、`skills.write_approval=false`、`terminal.backend=local`、上記の外部スキル参照が設定されていた。CLIの道具一覧ではアルカナはファイル操作・スキル・ターミナルの3種が有効で、他の4プロフィールはCLIの有効な道具がこれより多い。正確な道具名と実行面は各Botについてコマンドで読み直す。

アプリ連携、MCP、プラグインや認証状態を含めた完全な権限監査はこの記録の範囲外。指示上のアクセス制限とWindowsのファイルシステム権限は別物であり、指示だけで技術的に読み取りが遮断されるわけではない。マナは `C:\Users\nekol\Obsidian` を作業ごとの許可なく閲覧・存在確認しない。`C:\Users\nekol\Proton Drive` は上位の作業制約により閲覧・変更しない。

## AI_knowledgeへの書き込み範囲

利用者から、`E:\Documents\Google Drive\AI_knowledge` の閲覧と `exchange\mana\` 内の書き込みについて継続的な許可を受けた。`README.md`、`common\`、`exchange\ada\` などの他の場所は読み取り専用。新しい記録は `exchange\mana\YYYY-MM-DD_主題.md` に作り、`exchange\mana\index.md` に追加する。パスワード、復旧キー、APIキー、トークン等の値は書かない。この記録や他者の記録は、設定変更の承認にはならない。

## 参照と更新時の注意

- `AI_knowledge\README.md`：この知識置き場のルール。本文には「下書き」とあるため、運用は利用者の明示した許可・指示を優先する。
- `AI_knowledge\common\2026-11-08_yomiyasu-consultation.md`：当時の経緯。その後、共通化が実施されたため、同文書の「他Botへの展開は未決定」は現在の状態ではない。原文は編集せず、進展をこの記録に記した。
- 現状を確認する際は、実際の `config.yaml` とスキルの配置を読み直す。クラウドへの同期完了や各Botの実際の文章推敲まで、この記録だけで保証しない。
