# background review モデル振り分け：事前確認

確認日：2026-11-17。対象はdefault。事前確認のみで、設定変更・数日観察は未実施。

## 結論

- 導入済み版はv0.23.2（local ae2a81ccc00e）。
- 設定キーは `auxiliary.background_review.model` と `auxiliary.background_review.provider`。
- この版ではモデル名だけを設定しても、providerがautoのままだと別モデルに切り替わらない。別モデルへ振り分けるには具体的なproviderとmodelの両方が必要。
- defaultの正本にはauxiliaryブロック自体が未設定。解決値はbackground_review.enabled=true、provider=auto、model=""、timeout=120、reasoning_effort=""。
- 現在の本体の設定値はgpt-6.1-sol／openai-codex／codex_responses。reviewはそのセッションの実際の本体モデル・プロバイダを引き継ぐため、セッション単位の上書きがあればその実行中モデルに従う。
- 既存Codexログインのアカウント向けモデル一覧取得はHTTP 401となり、実利用可能モデルの一覧は確定できなかった。ゼロモデルという意味ではない。

## 実装確認

`agent/background_review.py` の `_resolve_review_runtime`（329–367行）を確認し、実際にPythonが読み込むランタイム側ソースと調査側ソースのバイト一致を確認。

ルーティング条件：
1. providerが空またはauto、またはmodelが空なら、親セッションの実行中モデルを使う。
2. providerとmodelが親と同じなら同一モデル経路を使う。
3. 具体的なproviderと別のmodelの両方があれば、resolve_runtime_providerでそのルートを解決する。
4. ルート解決に失敗すると警告して本体モデルへ戻る。設定値の確認だけで安いモデルが実際に動いたとは判断できない。

別モデル経路では古い会話をダイジェストにし、直近の会話を維持する。同一モデル経路はフル会話のキャッシュ再利用を想定する。将来の品質比較には、モデルだけでなく入力文脈の違いも影響し得る。

将来承認する場合の設定例（未適用、利用可否未確定）：

```yaml
auxiliary:
  background_review:
    provider: openai-codex
    model: gpt-6-luna
```

戻す際は、今回のように元が未設定ならmodelとproviderの追加指定を両方外す。本体・他の補助スロットは変更しない。

## defaultの現在値

正本：`C:\Users\nekol\AppData\Local\hermes\config.yaml`

| 項目 | 解決値 |
|---|---|
| model.default | gpt-6.1-sol |
| model.provider | openai-codex |
| model.api_mode | codex_responses |
| auxiliary.background_review.enabled | true |
| auxiliary.background_review.provider | auto |
| auxiliary.background_review.model | 空文字 |
| auxiliary.background_review.timeout | 120 |
| auxiliary.background_review.reasoning_effort | 空文字 |
| auxiliary.curator.provider / model | auto / 空文字 |
| auxiliary.review.provider / model | auto / 空文字 |
| delegation.auto_resume | false |
| delegation.max_spawn_depth | 1 |

config checkは終了0。取得処理の前後でdefaultのconfigハッシュ一致を確認。

## モデル一覧の取得結果と限界

- `hermes -p default auth status openai-codex` はlogged in。
- 導入済み認証ヘルパーのread_only経路と、既存プールの読み取り専用フォールバックを確認・使用した範囲で、アカウント向けCodexカタログ取得結果はHTTP 401のままだった。
- トークン更新、再ログイン、他アプリからの認証取り込みは行っていない。秘密の値・アカウント識別子は出力・保存していない。
- 原因は未確定。logged in表示は、保存された資格情報があることと、カタログへのリクエストが認証成功することを同時に保証しない。
- Hermesの `get_codex_model_ids` は、ライブ取得失敗時に静的候補・ローカルキャッシュへフォールバックする。さらに将来互換のモデル名と900k派生名を合成するため、その一覧を「このログインで使えるモデル」とは扱わなかった。
- 推論呼び出しやbackground reviewの実行試験は行っていない。

## 公開情報による暫定候補（利用可能一覧ではない）

| 候補 | 位置づけ | このログインでの利用可否 | 枠 |
|---|---|---|---|
| gpt-6-luna | 第1候補。公式に効率重視・大量の定型的処理向けと説明。公開のWork/Codex利用量目安もSolより多い | 未確認 | 公開情報では通常のWork/Codexの共通使用量枠。同じ5時間枠がある契約ならその枠内での消費軽減を期待する候補であり、別枠化ではない。本人の契約への具体的適用とHermes上の実消費は未確認 |
| gpt-5.6-luna | 代替候補。公開資料にCodexでの置換先として登場し、API側も低価格帯。現行Lunaとの優劣は実機未測定 | 未確認 | 個別の現在の消費係数・別枠の有無は未確認。別枠の節約源としては計画に算入しない |

APIのドル単価と、ChatGPTログインによるCodexの含まれる使用量枠は別の指標。API単価をそのまま5時間枠の倍率に換算しない。

OpenAIの公開説明では、契約により5時間・週の両方の窓がある一方、Pro 100/200/500には現在5時間上限がないとされる。本人の現在の契約・上限は今回調査していないため、契約を推測していない。

古いCodexモデル紹介ページにはgpt-5.4-miniが推奨として残る一方、現行Help Centerは2026-08-31以降ChatGPTログインではgpt-5.4/miniを利用不可としている。この食い違いもあり、5.4-miniを今回の確実な候補にはしない。

## 次の判断に必要なもの

利用可能モデルの確定には、401の解消後にアカウント向けカタログを再取得する必要がある。認証更新・再ログインが必要かは別途相談し、今回は行わない。カタログ掲載を確認できても、レビューとしての動作・関所へ上がる案の品質・枠消費の比較は将来の承認後の試験項目。

設定・写し・登録簿・changelogは変更していない。数日観察の開始や予約もしていない。

## 参照

- 導入済み `agent/background_review.py`：ルーティング条件、解決失敗時の本体フォールバック、別モデル時の会話ダイジェスト。
- 導入済み `hermes_cli/codex_models.py`：ライブ取得・静的フォールバック・合成モデルの区別。
- 導入済み `hermes_cli/auth_codex.py`：read_only経路はトークン更新・取り込み・認証保存をしない。
- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
- https://help.openai.com/en/articles/11369540-codex-usage-limits
- https://developers.openai.com/api/docs/models/gpt-6-luna
- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/codex/models/

ライブ取得の非秘密結果はナユタの自己scratch `background-review-preflight/catalog.json` に保存。共有先には認証値や会話本文を置いていない。
