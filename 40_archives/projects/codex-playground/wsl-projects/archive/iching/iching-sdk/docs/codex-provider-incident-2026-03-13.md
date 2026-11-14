# Codex Provider Incident Report (2026-03-13)

## 背景

`iching-sdk` では `./iching run --provider codex` を使って Codex provider を呼び出している。  
今回の論点は、`Codexアプリ固有の不具合` を断定することではなく、`codex provider / runtime / 接続経路` にまたがる不安定として整理できるかどうかである。

比較の前提として、別プロジェクトである `ekikyo-sdk` は、少なくとも過去には Codexアプリ側でも動いていた。  
したがって、今回の現象は「Codexアプリという製品全体が常に壊れている」という見立てでは説明しにくい。

## 現象

今回 `iching-sdk` で観測された現象は次のとおり。

- Codexアプリでは provider 周りで停止する回があった
- CodexCLI でも provider failure は再現した
- `resolve/select/build-prompt` と `/tmp` artifact 出力は通る
- 問題は主に provider 実行段階で発生している
- 条件によっては占い回答まで届く回もあったが、再現性はまだ不安定

重要なのは、`アプリでは失敗、CLI では常に成功` ではない点である。  
CLI 側でも `websocket` / `HTTPS` 接続断や `.codex` 配下の state/snapshot 書き込み失敗が観測されている。

## 再現条件

外部共有向けには、再現コマンドは次の 2 本に絞る。

### 1. Short Probe

```bash
printf 'Reply with exactly OK.\n' | codex exec --sandbox workspace-write -
```

用途:

- Codex runtime 単体で最小の疎通を見る
- short probe 成功だけでは state/snapshot の健全性が保証されないことを確認する

### 2. Minimal SDK Run

```bash
./iching run \
  --input tests/fixtures/extract_cases/test_1.md \
  --profile honda \
  --provider codex \
  --out-dir /tmp/iching-codex-min-retry-test1
```

用途:

- `iching-sdk` 前段処理と provider 実行段階を分離して観察する
- `run.json`, `resolve.json`, `select.json`, `prompt.txt` を artifact として残す

## 観測ログ要約

代表症状として重要なのは次の 5 系統である。

- `failed to connect to websocket`
- `stream disconnected`
- `failed to open state db`
- `Failed to create shell snapshot`
- `Read-only file system`

今回の観測では、CLI 実測 1 周でも次の傾向が出た。

- `CodexCLI / 本田指定あり`: 約 31 秒で failure
- `CodexCLI / 本田指定なし`: 約 31 秒で failure
- どちらも `provider failure` は出た
- どちらも `./iching run` 系へは入っていない

つまり、少なくともこの実測では「本田指定の有無」より前に、provider 接続 / runtime 層で失敗している。

stderr と runtime diagnostics で特に意味が強い断片は次のとおり。

```text
failed to connect to websocket
stream disconnected before completion
failed to open state db at .../.codex/state_5.sqlite
Failed to create shell snapshot
Read-only file system (os error 30)
```

## 切り分け結果

現時点で強く言えることは次のとおり。

1. `iching-sdk` 前段処理は主因ではなさそう
   - `resolve/select/build-prompt` は完了している
   - `/tmp` への artifact 出力もできている
   - 最小ケースでも provider 実行段階で止まる

2. `Codexアプリだけ` の問題とは断定できない
   - CodexCLI 側でも provider failure が再現している
   - したがって、アプリ固有バグに限定するのは早い

3. `.codex` 配下の state DB / shell snapshot / websocket/HTTPS failure が観測されている
   - state runtime 初期化失敗
   - shell snapshot 書き込み失敗
   - websocket failure 後の reconnect
   - HTTPS fallback 後の `stream disconnected`

4. `アプリ vs CLI` だけではなく、provider runtime / 接続経路全体を見るべき段階に入っている

一方で、まだ弱い主張に留めるべき点は次のとおり。

- OpenAI 側が原因と断定はできない
- こちらのローカル環境だけが原因と断定もできない
- `本田プロファイル` 経路が完全な回避策とは言えない

## 現時点の有力仮説

優先度順の仮説は次のとおり。

1. `codex exec` runtime の filesystem / state / snapshot 制約
   - `.codex` 配下への書き込み失敗が繰り返し出ている
   - `state db` と `shell snapshot` の失敗が sampling 前後で観測されている

2. connection / streaming 不安定
   - websocket 接続失敗
   - HTTPS fallback 後の `stream disconnected`
   - ただしこれは一次原因ではなく、state/runtime failure の後段で悪化している可能性がある

3. `iching-sdk` 固有ロジック
   - 現時点では第一候補から外れる
   - 前段処理と artifact 出力が通っているため、主因としては弱い

## 未確定事項

まだ分かっていない点は次のとおり。

- `.codex` 配下への書き込み要件が、`workspace-write` 運用でどこまで必須なのか
- `--ephemeral` が state DB / shell snapshot 初期化をどこまで回避する想定なのか
- `CODEX_HOME` の変更で何が保証され、何が保証されないのか
- `stream disconnected` が state/snapshot failure の二次障害なのか、独立した transport failure なのか
- 過去に動いていた `ekikyo-sdk` 成功時点と、今回の mount / sandbox / writable 条件に差があったのか

## 相手に見てほしいポイント

外部レビューや OpenAI 相談時には、次を確認してもらいたい。

1. この挙動は仕様どおりか
   - `workspace-write` でも `.codex` 配下への書き込みが必要なのか

2. `.codex` の書き込み要件は何か
   - state DB
   - shell snapshots
   - system skills installation

3. `--ephemeral` や `CODEX_HOME` でどこまで回避できる想定か
   - 現観測では完全回避になっていない

4. websocket failure と state/snapshot failure の因果関係をどう見るべきか
   - どちらが一次原因として扱われるべきか

## 補足

現時点の運用判断としては、`iching-sdk` 本体改修を急ぐ段階ではない。  
まずは `codex provider` を experimental 扱いに留め、runtime 条件や書き込み条件に関する外部知見を得るほうが筋がよい。

## 詳細資料

- `docs/codex-provider-openai-report-2026-03-13.md`
- `docs/comparisons/codex-provider-root-cause-2026-03-13.md`
- `docs/comparisons/provider-matrix-harness.md`
- `docs/comparisons/provider-matrix-2026-03-13/app-manual.md`
