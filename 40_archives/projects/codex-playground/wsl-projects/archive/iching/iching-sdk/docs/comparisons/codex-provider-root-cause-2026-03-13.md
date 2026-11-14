# Codex Provider Root Cause Ranking (2026-03-13)

## Summary

今回は `iching-sdk` を直すのではなく、`codex provider` が失敗する主因候補を順位付けするための切り分けだけを行った。

結論として、第一候補は `Honda/Takashima split profile` ではない。
最も強い候補は、Codex CLI 実行時の runtime filesystem 制約と state/snapshot 書き込み失敗である。

## Fixed Premises

成功 run と失敗 run を比較しても、次は共通していた。

- `resolved_codex_path = /home/ys/.nvm/versions/node/v22.21.1/bin/codex`
- `resolved_codex_version = codex-cli 0.114.0`
- `answer_command = codex exec --sandbox workspace-write`

したがって、「別の Codex binary を踏んでいた」「CLI version 差分で壊れた」は、今回の主因候補から一段下げてよい。

## New Observations

### 1. filesystem 制約は `/mnt/c` だけではない

このセッションでは `/mnt/c` は `ro` だった。

```text
C:\ on /mnt/c type 9p (ro, ...)
```

さらに `findmnt -T /home/ys/.codex` では、`/` 自体も `ro` だった。

```text
TARGET SOURCE   FSTYPE OPTIONS
/      /dev/sdd ext4   ro,...
```

そのため、`/mnt/c` だけでなく `/home/ys/.codex` も shell write probe で `Errno 30 Read-only file system` になった。

一方で workspace `/home/ys/projects/iching-sdk` には書けたため、このセッションは「repo workspace は writable、`.codex` 配下は read-only」という挙動になっている。

### 2. short probe でも state/snapshot failure は出る

短い direct probe:

```bash
printf 'Reply with exactly OK.\n' | codex exec --sandbox workspace-write -
```

でも、次が直ちに出た。

- `failed to open state db`
- `failed to initialize state runtime`
- `Failed to create shell snapshot`
- `state db discrepancy`

つまり、「短い実行は state failure が出ない」は今回のセッションでは成り立たなかった。
短い実行は単に SDK の `provider_sandbox_or_fs` 分類を通していないだけで、内部症状は fixture run と同型だった。

### 3. `--ephemeral` は state 依存を消さなかった

次を試した。

```bash
printf 'Reply with exactly OK.\n' | codex exec --sandbox workspace-write --ephemeral -
```

しかし `failed to open state db` と `Failed to create shell snapshot` は残った。
したがって、この CLI では `--ephemeral` を付けても state DB / snapshot 初期化が完全には無効化されていない。

### 4. `CODEX_HOME` は参照先を変えるが、失敗は残る

次を試した。

```bash
CODEX_HOME=/home/ys/.codex codex exec --sandbox workspace-write -
```

このとき runtime banner と警告先は `/mnt/c/Users/nekol/.codex` から `/home/ys/.codex` に切り替わった。
したがって `.codex` state 保存先は固定ではなく、少なくとも `CODEX_HOME` で参照先は変えられる。

ただし、失敗自体は残った。

- `failed to install system skills: ... Read-only file system`
- `failed to open state db at /home/ys/.codex/state_5.sqlite`
- `Failed to create shell snapshot ... Read-only file system`

つまり、state path を変えるだけでは解決しない。

### 5. `--add-dir` でも解消しなかった

次を試した。

```bash
CODEX_HOME=/home/ys/.codex codex exec --sandbox workspace-write --add-dir /home/ys/.codex -
```

runtime banner 上は writable 範囲に `/home/ys/.codex` が追加された。
それでも `state db` と `shell snapshot` は `Read-only file system` / `unable to open database file` のままだった。

したがって、少なくともこのセッションでは `--add-dir` だけで `.codex` 書き込み失敗は回避できていない。

## Candidate Ranking

### 確度高

1. `codex exec` の runtime filesystem 制約が第一原因
   - `/mnt/c` だけでなく `/home/ys/.codex` も read-only
   - short probe / fixture run / `CODEX_HOME` 変更後でも state DB と snapshot 書き込み失敗が再現
   - `run.json` の先頭 failure も `provider_sandbox_or_fs`

2. `stream disconnected` は一次原因より二次障害の可能性が高い
   - state DB / snapshot failure が sampling 開始前から出ている
   - その後に `stream disconnected` の再試行へ進む
   - したがって、接続断は独立原因である可能性も残るが、時系列上は後段

### 確度中

3. `workspace-write` sandbox の writable 範囲と Codex runtime の内部書き込み先が噛み合っていない
   - banner 上の writable list は限定的
   - `CODEX_HOME` を変えても `.codex` 本体への書き込みは通らない
   - `--add-dir` を足しても解消しないため、単純な allowlist だけではなさそう

4. `CODEX_HOME` は path 回避には使えるが、根本回避ではない
   - 参照先は確かに変わる
   - ただし、その参照先もこのセッションでは read-only で失敗する

### 保留

5. `Honda/Takashima split profile` が主因
   - 失敗は profile 固有より provider runtime 固有の症状に見える
   - ただし別セッションで writable 条件が揃った再測定までは、完全否定ではなく保留

6. `stream disconnected` が唯一の主因
   - 現時点では state/snapshot failure が先行しているため優先度は低い
   - ただし writable 条件を満たしたセッションでも同じ接続断が残るなら再浮上する

## Refutation Conditions

- runtime filesystem 制約が第一原因でないなら:
  - `.codex` 配下が writable なセッションでも同じ `state db` / `shell snapshot` failure が同順で再現する必要がある
- `stream disconnected` が第一原因なら:
  - state/snapshot failure を解消した条件でも、同じ direct probe と fixture run が同様に落ちる必要がある
- split profile が第一原因なら:
  - 同じ writable 条件で profile を変えたときだけ失敗率や failure sequence が有意に変わる必要がある

## Remaining Unknowns

- 過去の成功 run 時点で `/mnt/c` または `/` が writable だったか
- Codex desktop セッションごとの mount / sandbox 条件差分
- `stream disconnected` が writable 条件下でも残るか
- state DB を完全に使わない official runtime option が他にあるか

## Restart Recheck

再起動後の別セッションでも、filesystem 条件は変わらなかった。

- `/mnt/c` は引き続き `ro`
- `findmnt -T /home/ys/.codex` でも `/` は `ro`
- `/mnt/c/Users/nekol/.codex` と `/home/ys/.codex` の write probe はどちらも `Errno 30`

一方で、挙動の差分として次が確認できた。

1. short probe は成功した
   - `printf 'Reply with exactly OK.\n' | codex exec --sandbox workspace-write -`
   - したがって、read-only 条件でも短い `codex exec` は通る場合がある
2. full run は前段まで進んで provider 段階で停滞した
   - `/tmp` には `prompt.txt`, `resolve.json`, `select.json` が生成された
   - `resolve/select/build-prompt` と `/tmp` 出力は正常
   - ただし provider 実行は完走せず、`run.json` も生成されなかった

この再確認により、次がさらに強くなった。

- `iching-sdk` 前半ロジックや `/tmp` artifact 書き出しは主因ではない
- 問題の中心は `codex exec` の provider 実行段階にある
- read-only 条件は失敗要因として残るが、それだけで short probe を常に落とすわけではない
- 長めの provider 実行、streaming、state/snapshot、接続再試行の相互作用がより怪しい

## Close Decision

今回の調査はここで一区切りにする。

- `split profile` は第一候補から外す
- `codex provider` は当面 experimental 扱いに留める
- `iching-sdk` 本体改修は保留する
- runtime 条件が変わるまで、同系統の再実行は打ち止めにする

現時点の運用判断は次のとおり。

1. `resolve/select/build-prompt` は正常
2. `/tmp` 出力も正常
3. short probe は成功する場合がある
4. full run は provider 実行段階で停滞または失敗する
5. `.codex` 配下は再起動後も read-only で、state DB / snapshot の失敗要因は残っている

よって、現時点の主な原因候補の優先順位は次で固定する。

1. `codex exec` runtime の filesystem / state / snapshot 制約
2. 長めの実行時に顕在化する connection / streaming 不安定
3. `iching-sdk` の split profile や prompt 準備ロジック

## Reopen Condition

追加検証は今は行わない。

- 次回の再開条件は「`.codex` が writable なセッションを得たとき」
- そのときだけ short probe 1 本と `test_1.md` 1 本を再実施する
- writable 条件でも `stream disconnected` だけが残るなら、OpenAI 側または通信層の優先度を上げる

## Suggested Next Checks

次に再開する場合の確認順はこうなる。

次スレッドでは、修正ではなく次の確認順がよい。

1. 成功 run を取った時刻の mount 条件を可能な範囲で照合する
2. writable な別セッションで short probe を再実行する
3. writable 条件下で fixture run を再実行し、`state db` と `stream disconnected` の残り方を分離する
4. その後で初めて split profile 差分を再評価する
