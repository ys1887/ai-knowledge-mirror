# Codex App Provider Matrix

Codex アプリ側は手動記録する。各 run は必ず新規セッションで実施する。

## Fixed Prompts

### Codexアプリ / 本田指定あり

```text
/home/ys/projects/iching-sdk を対象に、本田プロファイルで占ってください。テーマは「今後の占い運用はCodexCLI中心に寄せるべきか、それともCodexアプリ中心を維持するべきか」です。計画ではなく最終的な占い回答だけを出してください。
```

### Codexアプリ / 本田指定なし

```text
/home/ys/projects/iching-sdk を対象に、占いの最終回答だけを出してください。テーマは「今後の占い運用はCodexCLI中心に寄せるべきか、それともCodexアプリ中心を維持するべきか」です。計画や仕様整理は不要です。
```

## Runs

| scenario | iteration | final answer | provider failure log | `./iching run` path | major files read | notes |
|---|---:|---|---|---|---|---|
| Codexアプリ / 本田指定あり | 1 |  |  |  |  |  |
| Codexアプリ / 本田指定あり | 2 |  |  |  |  |  |
| Codexアプリ / 本田指定なし | 1 |  |  |  |  |  |
| Codexアプリ / 本田指定なし | 2 |  |  |  |  |  |
