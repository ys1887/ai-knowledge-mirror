# iching-sdk 開発振り返りまとめ

## はじめに

この文書は、今回 `iching-sdk` を作成したときに、

- 何を作ろうとしたのか
- どの順番で進めたのか
- その時に何を考えていたのか
- 最終的に何が完成し、何がまだ残っているのか

を、あとで読み返して理解しやすいように、日本語でまとめたものです。

今回の作業は、かなりの部分を Codex に任せながら進めました。そのため、途中で

- なぜこの作業が必要なのか
- なぜ今これをやっているのか
- なぜ別のやり方ではなくこのやり方を選んだのか

が見えにくかったと思います。

この文書では、単に「何を変更したか」を列挙するのではなく、

1. 最初に何が課題だったのか
2. それをどういう方針で解いていったのか
3. どこまでを今回の完成範囲としたのか
4. この先に何をやると自然なのか

が分かるように整理します。

なお、この文書は「今回の MVP を理解するためのまとめ」です。  
ここでいう MVP は「最小限だが、実際に使える形まで持っていった最初の完成版」という意味です。

## この文書の読み方

最初から順番に読んでもよいですし、あとで必要なところだけ拾い読みしても大丈夫です。

- まず全体像を知りたい場合
  - `結論の要約`
  - `作業前の課題`
  - `全体の流れ`
- 実装内容を知りたい場合
  - `実装内容の整理`
  - `どのファイルに何が入ったか`
- 今後の作業を知りたい場合
  - `この後やったほうがいいこと`
- 用語が分からない場合
  - `用語集`

## 結論の要約

### `iching-sdk` とは何か

`iching-sdk` は、易に関するローカルの素材群を、`./iching` という CLI から扱えるように整理したプロジェクトです。

今回の到達点は、

- ローカルの素材を使って
- `resolve -> select -> build-prompt -> answer -> validate`
  という流れで占いや一般質問の処理を行い
- 必要な artifact を保存し
- 後から検証し直せる

という形にすることでした。

### 今回完成したもの

今回、MVP として完成したものは大きく分けると次のとおりです。

1. `iching` CLI の基盤
   - `index`
   - `resolve`
   - `select`
   - `build-prompt`
   - `answer`
   - `run`
   - `validate`

2. `codex` を built-in provider として使う最小実装

3. `run.json` を中心とした artifact 保存と診断情報の整備

4. `validate --context <resolve.json|run.json>` による後追い検証

5. `iching.toml` の provider table 形式
   - `default_provider = "codex"`
   - `[providers.codex]`

6. README と skill の運用導線整理

7. `main` への squash merge と、MVP の締め作業

### まだやっていないもの

今回は、あえてやっていないこともあります。

- 新しい provider の追加
- HTTP API の提供
- 常駐サーバー化
- GUI 統合
- packaging の本格整備

これらは「できなかった」のではなく、「今の段階では優先しない」と判断して保留したものです。

## 作業前の課題

### もともと何が不足していたか

もともとの課題は、易に関する素材やルールはある程度揃っていても、

- どの順番で処理すればよいか
- どのコマンドがどの役割を持つか
- 回答後にどうやって検証するか
- 実行時に失敗したらどこを見ればよいか

が、運用としてまだ固まり切っていなかったことでした。

つまり、素材はあっても「使うための入口」が十分に整理されていなかった、という状態です。

### なぜ SDK 化したのか

今回の考え方は、「skill の本文に複雑な運用手順を抱え込ませる」のではなく、

- 実際のロジックは repo 側に寄せる
- skill は薄い起動ラッパーにする
- Codex でも Claude Code でも、同じ CLI を呼べるようにする

というものでした。

この考え方にすると、後から改善するときに、

- skill の本文だけ直すのではなく
- 実際のロジックを repo 側で一元管理できる

ようになります。

つまり、今回の `iching-sdk` は「単なるコマンド集」ではなく、
今後の運用を安定して育てていくための土台として作られました。

### なぜ API や常駐サーバーではなく CLI から始めたのか

これは今回かなり重要な判断でした。

最初から API やサーバーにすると、

- 設計の自由度が高すぎる
- 何を安定仕様にするべきかが早い段階では見えにくい
- まだ運用で本当に必要か分からないものまで先に作ってしまいやすい

という問題があります。

そこで今回は、まず

- 手元の Codex 環境で
- ローカル CLI として
- 必要な入出力契約だけを安定させる

ことを優先しました。

これは、「大きく作る前に、まず実際に使える最小形を固める」という意図です。

## 全体の流れ

ここでは、指定された 5 つのセッションを「第1回〜第5回」として振り返ります。  
セッション名は記録から拾ったものを補助的に付けています。

### 第1回: SDK 標準運用フローの整理

- セッション ID
  - `019ccd87-ac20-7f41-af79-3f5ebd79729c`
- thread name
  - `Add iching SDK CLI plan`

#### この回の目的

最初の目的は、「新機能をいきなり大量に足す」ことではなく、
`iching-sdk` の標準運用フローを定義し、README に落とし込むことでした。

#### この回で決めたこと

この段階では、まず

- `resolve` で入力や mode を把握する
- `build-prompt` で実行用 prompt を作る
- 回答を得る
- `validate` で後からチェックする

という基本線を固める方針が整理されました。

また、EXTRACT と GENERAL で運用上の注意点が異なるため、
同じ CLI の上で mode ごとに分岐させる考え方もはっきりしました。

#### この回で実装・整備したこと

この流れで README 側の標準フローが整備され、CLI の役割分担が読みやすくなっていきました。

この段階では、まだ高レベルの実行体験を最終形まで固めるというより、
「入口と流れを理解できる状態にする」ことが中心でした。

#### なぜこの順番だったか

いきなり高度な実装に入るよりも、まず

- 何が前段処理で
- 何が後段処理で
- どこで検証すべきか

を言語化する方が、その後の実装がぶれにくくなります。

つまり、第1回は「骨組みを定義した回」でした。

### 第2回: `run` / `answer` まわりの仕様を固める

- セッション ID
  - `019ccde1-2f0e-7710-949c-a2d98a881c44`
- thread name
  - `Clarify iching-sdk run spec`

#### この回の目的

次の課題は、README 上の運用フローだけでなく、実際に

- `answer`
- `run`

という高レベルなコマンド体験をどう定義するかでした。

#### この回で決めたこと

ここで、

- `answer` は `prompt -> answer` に集中する
- `run` は一連の流れを 1 コマンドで包む
- 生成した結果や途中の情報は artifact として保存する

という役割分担が明確になっていきました。

中盤では `--answer-cmd` や `--answer-preset codex-exec` を使った運用も整えられ、
GENERAL / EXTRACT の成功例が README に追加されました。

#### この回で実装・整備したこと

この段階までに、

- `answer`
- `run`
- `answer-preset`
- GENERAL / EXTRACT の成功例

が揃い、MVP としてかなり使える感触が出てきました。

#### なぜこの順番だったか

最初から provider を複雑にせず、
まずは「外部コマンドを呼んで結果を受ける」という実用最小ルートを固めたからです。

この考え方により、

- 実際に回ることを優先できる
- テストしやすい
- 後で provider abstraction を入れやすい

という利点がありました。

### 第3回: `validate --context` と後追い検証の整備

- セッション ID
  - `019cce14-3b13-7a52-9295-ef15438fcd1a`
- thread name
  - `Plan next iching-sdk improvements`

#### この回の目的

次の焦点は、単に validate を回すだけでなく、
「どの文脈でその回答が作られたか」を後から再利用できるようにすることでした。

#### この回で決めたこと

ここで重要だったのは、

- `resolve.json`
- `run.json`

を使って、`validate` に追加の文脈を渡せるようにすることでした。

つまり、回答本文だけでは分からない比較占い・順位づけ・入力種別などの情報を、
artifact 側から補う考え方です。

#### この回で実装・整備したこと

主な実装は次のとおりです。

- `validate --context <resolve.json|run.json>` を追加
- `run.json` に hints を保存
- `run` 後の stricter な再検証を単体 `validate` でも再利用可能にする

この時点で、CLI は単に「実行して終わり」ではなく、
「後から見返し、もう一度点検できる」性質を持ち始めました。

#### なぜこの順番だったか

易の解釈や比較は、単に一度回答できれば終わりではありません。
後から「この比較の前提は何だったのか」を確認できることが重要です。

そのため、この回では「実行の再現性」と「検証の再利用性」を強める方向に進みました。

### 第4回: provider diagnostics と runtime config の整理

- セッション ID
  - `019cce3e-b353-76b3-b68c-6782e809aafb`
- thread name
  - `Improve diagnostics for codex`

#### この回の目的

MVP を実用レベルに近づけるうえで問題になったのが、
`codex` 実行時の失敗が見えにくいことでした。

つまり、失敗したときに

- `codex` が入っていないのか
- 認証が足りないのか
- コマンドはあったが実行に失敗したのか

を区別しづらかったのです。

#### この回で決めたこと

ここで「provider failure taxonomy」を整えました。

具体的には、

- `provider_missing`
- `provider_auth`
- `provider_execution_failed`

のように分類し、
stderr の短い要約と `run.json` の詳細を対応させる方針にしました。

また、この流れで runtime config の形も見直されました。

- 旧 top-level `provider` / `codex_*`
- 新しい `default_provider` / `[providers.codex]`

を共存させつつ、今後は provider table 形式を主ルートにする考え方が固まりました。

#### この回で実装・整備したこと

この回の成果はかなり大きく、次のような整備が入りました。

- `run.json` に diagnostics を保存
  - `error_type`
  - `error_summary`
  - `error_source`
  - `error_stderr`
- provider failure taxonomy の導入
- `iching.toml` の provider table 形式サポート
- runtime config の内部表現を provider 構造へ寄せる
- `answering.py` の provider registry 化
- `cli.py` の provider option handling の一般化
- opt-in smoke test の整備

#### なぜこの順番だったか

MVP を「使える」と言うには、
成功することだけでなく、失敗したときに原因が追えることが必要です。

この回は、まさに「成功系だけの MVP」から
「失敗時も扱える MVP」に進めた回でした。

### 第5回: MVP を閉じる準備と正式化

- セッション ID
  - `019cce60-9e8e-7f33-8ffd-64b1c3b3659c`
- thread name
  - `Document MVP closing checklist`

#### この回の目的

最後の大きなテーマは、「これをどう閉じるか」でした。

つまり、

- まだ実装を続けるのか
- docs を整えて一旦締めるのか
- `main` に取り込むのか

を判断する段階に入りました。

#### この回で決めたこと

ここでの重要な判断は、

- もう新機能を増やすより
- CLI 契約と運用導線を整理し
- MVP を正式な基準版として `main` に取り込む

という方針でした。

README もこの判断に合わせて再整理されました。

#### この回で実装・整備したこと

- README を MVP handoff 向けに再構成
  - `MVP Scope`
  - `公開契約`
  - `最短運用`
  - `provider failure の見方`
  - `MVP 完了チェックリスト`
  - `受け入れ基準`
- `main` へ squash merge
  - 基準コミット: `586b728 feat: merge iching-sdk mvp`
- ブランチ cleanup
- README の short path spot check
- `iching-sdk` skill 文言を provider-first 契約に合わせて更新
  - skill 側追従コミット: `6cee6ed docs: align iching-sdk skill wording`

#### なぜこの順番だったか

MVP は「機能がある」だけでは足りません。
後から見たときに、

- 何が安定仕様か
- どこまでが今回の完成範囲か
- 何をまだやらないのか

が分かる必要があります。

そのため最後は、機能追加よりも「正式化と整理」を優先しました。

## 実装内容の整理

ここでは、今回できあがった中身を機能ごとに整理します。

### 1. CLI 基盤

CLI として以下のコマンドが整いました。

- `index`
- `resolve`
- `select`
- `build-prompt`
- `answer`
- `run`
- `validate`

この基盤ができたことで、「何をどこでやるか」がコマンドレベルで分かるようになりました。

### 2. `resolve` / `select` / `build-prompt`

この部分は、回答生成の前段処理です。

- `resolve`
  - 入力の種類や mode を判定する
- `select`
  - 参照すべき source files を選ぶ
- `build-prompt`
  - 実行用 prompt を組み立てる

特に `build-prompt` に `Selected Sources` が入るようになったことは重要でした。  
これにより、「どの資料を見る前提の prompt なのか」が後から分かります。

### 3. `answer` / `run`

この 2 つは高レベルの入口です。

- `answer`
  - 既にある prompt を使って回答を得る
  - artifact 管理はしない
- `run`
  - 一連の流れを 1 コマンドでまとめて実行する
  - artifact を保存する

これにより、用途に応じて

- 普段は `run`
- 中身を見たいときは modular workflow

という使い分けができるようになりました。

### 4. `validate --context`

これは今回の重要機能の 1 つです。

普通の `validate` は回答本文だけを見ますが、
`--context` を付けることで

- その回答がどういう入力から来たか
- 比較や順位づけの文脈は何だったか

を補って検証できます。

これにより、`run` のときと同じ条件で、後からもう一度厳しめに確認できるようになりました。

### 5. `run.json` の診断情報

`run.json` は、今回かなり大事な artifact になりました。

保存される主な情報は、

- 実際に使った command
- provider
- provider options
- selection summary
- validation summary
- error diagnostics

です。

特に error diagnostics として

- `error_type`
- `error_summary`
- `error_source`
- `error_stderr`

が入るようになったことで、失敗時の切り分けがしやすくなりました。

### 6. `codex` provider MVP

回答生成の built-in provider として、今回は `codex` のみを対象にしました。

これは意図的な絞り込みです。

最初から複数 provider を本格実装すると複雑になりすぎるため、
まずは `codex exec` を呼ぶ最小実装で、

- 実際の運用
- 診断
- 設定

を固めることを優先しました。

### 7. `iching.toml` と provider table

設定ファイルとして `iching.toml` を使えるようにし、

```toml
default_provider = "codex"

[providers.codex]
model = "gpt-5"
sandbox = "workspace-write"
approval_policy = "never"
```

という形を推奨ルートにしました。

同時に、過去の互換性のために旧 top-level `provider` / `codex_*` も当面残しました。

これは、「今後 provider を増やす余地を残しつつ、今の利用者を壊さない」ための折衷案です。

### 8. README 整理

README は最終的に、

- scope
- current contract
- 最短運用
- provider failure の見方
- MVP 完了チェックリスト
- 受け入れ基準

が先に読める構成になりました。

これにより、「README を読めば、今どこまでできているかが分かる」状態になりました。

### 9. skill 追従

`iching-sdk` の runtime skill と source-of-truth skill も更新しました。

ここでの意図は、skill の説明が古いままになって、

- preset ベースで読むべきなのか
- provider ベースで読むべきなのか

がズレることを防ぐことでした。

そのため skill の文言も、provider-first の current contract に合わせて整えました。

## 設計意図

ここでは、「なぜこの設計にしたのか」をまとめます。

### なぜ provider-first にしたか

中盤までは `codex-exec` preset が自然な入口でしたが、
最終的には provider-first に寄せました。

理由は、

- 今後の拡張の軸を provider に置いた方が自然
- runtime config と相性がよい
- `default_provider` と組み合わせると日常運用が簡単になる

からです。

### なぜ `codex-exec` preset を残したか

ただし、古い運用や互換性のために `codex-exec` は残しています。

これは「完全に古いものを捨てた」のではなく、

- 推奨は provider
- 互換のため preset も残す

という移行しやすい形を選んだ、ということです。

### なぜ local CLI を current contract にしたか

これは今回の全体方針そのものです。

最初に安定させるべきなのは、

- 手元で実際に使う入口
- 実際にテストできる契約

であり、今回はそれが local CLI でした。

API などに先に広げるよりも、まず CLI を確実にする方が、今後の土台として強いと判断しました。

### なぜ out-of-scope を強く固定したか

これは、プロジェクトが広がりすぎるのを防ぐためです。

`iching-sdk` は作ろうと思えばいくらでも広げられます。  
しかし、最初の段階で

- 新 provider
- API
- server
- GUI

まで考え始めると、MVP がいつまでも閉じません。

そのため今回は、「今はやらないもの」をはっきり書き、
完成範囲を守るようにしました。

## どのファイルに何が入ったか

ここでは、主要ファイルの役割を簡単に説明します。

### `iching_sdk/cli.py`

CLI 全体の入口です。

- 各サブコマンドの引数を定義する
- 実際の処理関数へ振り分ける
- provider 関連の CLI オプションを扱う

今回ここに入った重要な責務は、
provider-first の CLI 契約を表現することでした。

### `iching_sdk/answering.py`

回答生成の層です。

- provider や preset を解決する
- 外部コマンドを実行する
- provider failure を分類する

今回ここは、単なる `codex` 直書きから、
provider registry 的な形へ整理されました。

### `iching_sdk/config.py`

runtime config の読み込みと解決を担当します。

- `iching.toml` を読む
- 旧 config と新 config を吸収する
- CLI 指定と config 指定の優先順位を整理する

ここは、今後の provider 拡張余地を残すための重要ファイルです。

### `iching_sdk/running.py`

`run` の中核です。

- `resolve`
- `select`
- `build-prompt`
- `answer`
- `validate`

を順番に実行し、artifact を保存します。

今回ここには、`run.json` の要約や error diagnostics がかなり入りました。

### `iching_sdk/validation.py`

回答の検証を担当します。

- citation の妥当性
- mode に応じたルール
- context を使った追加検証

今回の重要点は `validate --context` の追加でした。

### `README.md`

利用者向けの入口です。

今回 README は、

- 運用説明
- 契約の明文化
- MVP の締め

という意味で大きな役割を持ちました。

### `tests/test_cli.py`

CLI 全体の回帰テストです。

今回の開発では、かなりの変更をこのファイルで支えました。

- 成功系
- 失敗系
- config
- provider failure
- artifacts
- smoke test

などが集約されています。

### `lib-skills/codex/iching-sdk/SKILL.md`

skill の source-of-truth です。

ここは「実装そのもの」ではなく、
どの repo を使い、どの入口を標準とするかを説明するファイルです。

最終的に、provider-first の current contract に合わせて更新されました。

## テストと確認

### 何をテストしたか

今回の中心的な回帰確認は、

```bash
python3 -m unittest -q tests.test_cli
```

でした。

このテストは、CLI 全体の多くの動作をカバーしています。

### どこまで自動化されたか

かなりの部分が自動テストで確認できるようになりました。

例えば、

- `run` の artifact 生成
- `answer` の実行フロー
- `validate` の結果
- `provider` 設定
- `run.json` の内容

などです。

### smoke test が opt-in である理由

`codex` の実 CLI を本当に起動する smoke test は、
環境依存の要素が強いです。

例えば、

- `codex` が未導入
- 認証不足
- ローカル権限の問題

などで落ちる可能性があります。

そのため通常の回帰テストには含めず、

```bash
ICHING_RUN_CODEX_SMOKE=1 python3 -m unittest -q tests.test_cli
```

を明示したときだけ動く opt-in にしました。

これは「普段の開発を不安定にしない」ための判断です。

### `85 tests, OK (skipped=1)` の意味

最終段階での基準的な結果は、

- 85 個のテストが走った
- 全体は成功
- 1 件は skip

という意味です。

この skip は通常、opt-in smoke が未実行など、意図した条件によるものです。

つまり、これは「テスト不足で飛ばされた」というより、
「環境依存の確認は別扱いにしている」という設計です。

## Git の流れ

### なぜ作業ブランチで積み上げたか

途中までは `codex/iching-sdk-mvp` というブランチで進めました。

理由は、

- 仕様がまだ揺れる段階だった
- 大きめの変更が続いた
- `main` を早く汚さない方が安全だった

からです。

### なぜ最後に `main` へ squash merge したか

最後は `main` に squash merge しました。

理由は、

- MVP の積み上げ履歴を 1 本の意味あるコミットにまとめたかった
- `main` を「基準版」として読みやすく保ちたかった

からです。

その結果、`iching-sdk` 側の基準コミットは

- `586b728 feat: merge iching-sdk mvp`

になりました。

### skill source repo と runtime copy をどう同期したか

skill には 2 つの場所があります。

1. source-of-truth
   - `/home/ys/projects/lib-skills/codex`
2. runtime copy
   - `/mnt/c/Users/nekol/.codex/skills`

今回はまず source-of-truth を更新し、その内容を runtime 側へ同期しました。

skill 側の更新コミットは

- `6cee6ed docs: align iching-sdk skill wording`

です。

## 今の完成状態

### `iching-sdk` repo の状態

- repo
  - `/home/ys/projects/iching-sdk`
- branch
  - `main`
- 基準コミット
  - `586b728 feat: merge iching-sdk mvp`
- working tree
  - clean

### skill source repo の状態

- repo
  - `/home/ys/projects/lib-skills/codex`
- branch
  - `main`
- 最新関連コミット
  - `6cee6ed docs: align iching-sdk skill wording`
- working tree
  - clean

### runtime skill の状態

- path
  - `/mnt/c/Users/nekol/.codex/skills/iching-sdk/SKILL.md`
- source-of-truth と同期済み

## この後やったほうがいいこと

ここでは、今後の候補を優先度ごとに分けて書きます。

### 今すぐ不要

今の段階では、無理に着手しなくてよいものです。

- 新 provider 実装
- HTTP API
- 常駐サーバー化
- GUI 統合

これらは scope を広げる話なので、今の完成感を崩しやすいです。

### 次にやるなら

次フェーズとして自然なのは、このあたりです。

#### 1. docs の追加整理

README はかなり整理されましたが、
より詳しい運用解説を `docs/` に分ける余地はあります。

意図:

- README は短く保つ
- 詳細な解説は別文書に逃がす

#### 2. 運用メモ整備

たとえば、

- よく使うコマンド例
- 失敗時の見方
- EXTRACT / GENERAL のコツ

のような「人間向けの運用メモ」は、あとで役立ちます。

意図:

- コードを読まなくても日常運用しやすくする

#### 3. packaging の小さな検討

今は `./iching` を repo 直下から使う前提ですが、
将来のために

- どう配るとよいか
- `pyproject.toml` を入れるべきか

を検討する価値はあります。

ただし、これは「実装」より先に「方針を考える」段階で十分です。

#### 4. opt-in smoke の再確認

必要なら、実際の `codex` CLI と認証が揃った環境で、
opt-in smoke を改めて回しておくと安心です。

意図:

- 実環境での最小疎通を確認する

### 将来

将来的には、次のような発展もありえます。

- provider の追加
- API 提供
- より高度な config
- packaging 本実装

ただし、これらは今回の MVP を壊さない前提で、別フェーズとして考えるべきです。

## 用語集

### provider

回答生成を担当する実行手段のことです。  
今回の built-in provider は `codex` のみです。

### preset

互換性のために残している、あらかじめ決められた実行コマンドの別名です。  
今回の代表は `codex-exec` です。

### artifact

実行の途中や結果として保存されるファイルです。  
例: `resolve.json`, `prompt.txt`, `run.json`, `report.json`

### runtime config

実行時に参照する設定のことです。  
今回の代表は `iching.toml` です。

### squash merge

作業ブランチ上の複数コミットを、`main` には 1 コミットとしてまとめて取り込む方法です。

### smoke test

細かい挙動全体ではなく、「最低限、起動して動くか」を確認する簡易テストです。

### current contract

「今の段階で、安定仕様として扱う約束」のことです。  
今回の `iching-sdk` では local CLI が current contract です。

## 参考資料

### 今回の 5 セッション ID

1. `019ccd87-ac20-7f41-af79-3f5ebd79729c`
2. `019ccde1-2f0e-7710-949c-a2d98a881c44`
3. `019cce14-3b13-7a52-9295-ef15438fcd1a`
4. `019cce3e-b353-76b3-b68c-6782e809aafb`
5. `019cce60-9e8e-7f33-8ffd-64b1c3b3659c`

### 主要コミット

- `586b728 feat: merge iching-sdk mvp`
- `6cee6ed docs: align iching-sdk skill wording`

中盤の重要な積み上げとしては、引き継ぎメモに残っている以下も重要です。

- `80b1f6a feat: add validate context support`
- `7ada3d1 feat: classify codex provider failures`
- `fbc8115 feat: persist run failure diagnostics`
- `d446a76 test: add opt-in codex smoke coverage`
- `9e43a23 feat: support provider-table runtime config`
- `ee144ff refactor: structure runtime provider config`
- `601681e refactor: add provider registry for answering`
- `99759a4 refactor: generalize cli provider option handling`
- `bb16eee docs: clarify local-cli scope`

### 参照した主なファイル

- `/home/ys/projects/iching-sdk/README.md`
- `/home/ys/projects/iching-sdk/iching`
- `/home/ys/projects/iching-sdk/iching_sdk/cli.py`
- `/home/ys/projects/iching-sdk/iching_sdk/answering.py`
- `/home/ys/projects/iching-sdk/iching_sdk/config.py`
- `/home/ys/projects/iching-sdk/iching_sdk/running.py`
- `/home/ys/projects/iching-sdk/iching_sdk/validation.py`
- `/home/ys/projects/iching-sdk/tests/test_cli.py`
- `/home/ys/projects/lib-skills/codex/iching-sdk/SKILL.md`

## 最後に

今回の `iching-sdk` 作業は、
単にコマンドを増やしただけではありませんでした。

本当にやったことを一言で言うなら、

「易のローカル運用を、再利用しやすい CLI として整理し、あとから見ても運用意図が追える形まで持っていった」

ということです。

途中では、

- 流れの文書化
- 高レベルコマンドの整備
- validate の強化
- diagnostics の強化
- provider 設計
- README / skill / Git の整理

を順番に積み重ねていきました。

その結果、今は

- 実際に使える
- 失敗時も見やすい
- 後から理解し直しやすい
- 次フェーズへ進みやすい

という、よい区切りの状態になっています。

もし将来この文書を読み返して「なぜこうなっているのか」が少しでも分かりやすくなっていれば、このまとめの役割は果たせています。
