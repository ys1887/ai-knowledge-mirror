# Honda-First Stability Check (2026-03-13)

## Summary

`legacy` は今回の確認対象から外し、`honda` を main profile として acceptance を見た。

結果として、`honda` の軽量ケース 2 本はどちらも provider failure で停止した。  
失敗は profile 固有ではなく、Ubuntu 側 Codex CLI を呼んだ後の runtime 環境で起きている。

今回の観測では、主な failure type は `provider_sandbox_or_fs` で、最初の短い要約は次だった。

```text
codex sandbox or filesystem issue (exit code 1):
WARNING: proceeding, even though we could not update PATH: Read-only file system (os error 30)
```

同時に `error_stderr` には、

- `unable to open database file`
- `stream disconnected before completion`

も含まれていた。

したがって、今回の主問題は `honda` split profile ではなく、Codex CLI の sandbox / state DB / connection 層にある。

## Cases

| case | template | profile | result | elapsed | error_type | selected files |
|---|---|---|---|---:|---|---:|
| `test_1.md` | `EX_SIMPLE` | `honda` | failed | 28.36s | `provider_sandbox_or_fs` | 1 |
| `test_2.md` | `EX_5` | `honda` | failed | 27.95s | `provider_sandbox_or_fs` | 4 |

Artifacts:

- `test_1`: `/tmp/iching-honda-first/honda-test1`
- `test_2`: `/tmp/iching-honda-first/honda-test2`

## Shared Observations

両ケースで共通していた点は次のとおり。

- `resolved_codex_path` は `/home/ys/.nvm/versions/node/v22.21.1/bin/codex`
- `resolved_codex_version` は `codex-cli 0.114.0`
- `answer_command` は `exec --sandbox workspace-write`
- `--ask-for-approval` は入っていない
- `error_source` は `provider`
- `validate_exit_code` は `null`

つまり、Ubuntu 側 Codex CLI 固定そのものは効いている。  
一方で、その先の runtime で read-only filesystem / state DB / connection の複合 failure が起きている。

## Why Takashima Was Not Run

今回の plan では、`takashima` は `honda` で通ったケースを追従確認する位置づけだった。  
しかし `honda` の軽量ケース 2 本が同型の provider failure で止まったため、今回は `takashima` へ進めていない。

この時点で `takashima` を回しても、

- profile 差分の確認
- provider 環境 failure の確認

が混ざりやすく、判断材料としては弱い。

## Current Interpretation

いまの最も筋の良い読みは次のとおり。

1. `honda` split profile の source selection と prompt build は通っている
2. Ubuntu 側 Codex CLI への固定も通っている
3. 失敗は `codex exec` 開始後の runtime 環境で起きている
4. よって次の主課題は profile 追加改修ではなく provider 実行環境の安定化

## Next Steps

次に見るべき順番はこうなる。

1. `provider_sandbox_or_fs` の代表症状を優先的に潰す
   - `Read-only file system`
   - `.codex/state_5.sqlite` の `unable to open database file`
2. そのうえで `test_1` を再実行する
3. `honda` の軽量ケースが通ったら `test_2` に戻る
4. そこまで通った後で `takashima` の `test_1`, `test_2` を同条件で追従確認する
5. `test_3`, `test_4` は connection / latency の重い観測ケースとして最後に回す

## Rust Note

Rust 化は今回の failure の直接解ではない。  
この failure は Python 実装より下の Codex CLI runtime にあるため、まず provider 環境の安定化が先。

ただし、将来 Rust を検討するなら候補は次のような pure processing 寄りの領域になる。

- index / select
- validation
- citation parsing

一方で、当面 Rust に向かないのは次の領域。

- provider orchestration
- `codex exec` 呼び出し
- prompt / config 契約がまだ揺れている部分
