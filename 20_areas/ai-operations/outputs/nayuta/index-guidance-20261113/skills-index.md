# skills 一覧

- 置き場所：`E:\Documents\Google Drive\AI_knowledge\30_resources\skills`（AI_knowledge 内。2026-11-12 に旧 `E:\Documents\AI\skills` から移管し、2026-11-13 に PARA 再編で現在地へ）
- ルール：skill を追加・移動・削除した側が、その作業の中でこの一覧も更新します
- 最終更新：2026-11-13

- Hermes Agent の共通スキル：`yomiyasu` v3.0.0。作成・保管先は `E:\Documents\Google Drive\AI_knowledge\30_resources\skills\yomiyasu\`、Hermes で使用するコピーは `C:\Users\nekol\AppData\Local\hermes\shared-skills\yomiyasu\` です。現在の6プロフィール（default、mana、arcana、label、phantom、nayuta）は `skills.external_dirs` でC側の `shared-skills` を参照します。新しいBotでは個別に参照設定を行います。
- E側のスキルを更新したら、C側へのコピーと内容照合を行ってから利用します。C側の共有版を変えると参照するBot全員に影響します。現行の2.5.0は `E:\Documents\Google Drive\AI_knowledge\20_areas\ai-operations\outputs\nayuta\yomiyasu-v2.5.0-backup-20261111-173121\` に退避しました。
- アルカナ用スキル：`ekikyo` v2.0.3。正本・使用版は `C:/Users/nekol/AppData/Local/hermes/profiles/arcana/skills/ekikyo/`、`E:/Documents/Google Drive/AI_knowledge/30_resources/skills/ekikyo/` は選別した保管コピーです。C側で変更した保管対象ファイルは内容確認後にE側へ反映し、対象ファイルの一致を照合します。E側にないC側固有ファイル（入力・作業用資産など）は一括コピーせず、保管対象を別途決めます。通常占断だけを扱い、MODE・TEMPLATE の表記と EXTRACT の機械組み立ては使いません。旧 EXTRACT 資産の切り分けと削除候補は、保管コピー内の `legacy/README.md` にあります。この保管コピーも git の管理対象外（未追跡）の置き物です
- この一覧は共有スキルの配置案内です。ほかのスキルの登録状況は各プロフィールで確認してください。旧 `E:\Documents\Hermes Agent\shared-skills\` は現行の参照先ではありません。
- lib-skills リポジトリ：2026-11-13 に `40_archives/projects/lib-skills` から中身一式（`.git` を含む）をここへ移しました（本人の指示）。そのため、このフォルダ自体が lib-skills の作業ツリーです。遠隔の正本は GitHub の `ys1887/lib-skills`、ブランチは `codex/karpathy-coding-guardrails`、未コミットの変更が残っています。中にある `README.md` と `AGENTS.md` はリポジトリ自身の説明で、スキルは各フォルダ（`codex/` 配下の10件を含む）が単位です。この一覧と yomiyasu はリポジトリの管理対象ではなく、git では未追跡の置き物として出ます
