# AI Learning Log

## Purpose
- Keep a strict, reusable learning record separate from `ai-notes.md`.
- Capture mistakes, near-misses, and repeatable success patterns.
- Improve future preemption by tracking what changed after user feedback.

## Entry Rules
- Add entries only when strict triggers are met (see `AGENTS.md`).
- Keep entries concrete and non-sensitive.
- Prefer one event per entry.

## Entry Template
```md
### [YYYY-MM-DD] <type: mistake|near-miss|worked-well>
- context: <task and situation>
- signal: <what indicated risk/error>
- action: <what was done>
- result: <outcome and user impact>
- root cause: <why it happened or almost happened>
- new rule: <clear rule to apply next time>
- trigger phrase: <short cue to recall rule quickly>
- severity: <low|medium|high>
- repeat_count: <number>
```

## Log
- [2026-02-12] Initialized strict learning ledger template.
  - Added structure for mistakes, near-misses, and worked-well patterns.
  - Linked operation mode to strict triggers in `AGENTS.md`.

### [2026-02-12] <type: worked-well>
- context: User asked to split log-saving and log-organizing behavior, with default deletion after successful cleanup.
- signal: Trigger phrases such as "過去ログを整理" did not map cleanly to save-focused behavior.
- action: Separated responsibilities into `session-log-archiver` (save only) and `session-log-organizer` (daily consolidation + default delete).
- result: Intent mapping is clearer, destructive behavior is isolated to organizer flow, and docs/scripts now match requested operation.
- root cause: A single skill was carrying both append-safe save operations and cleanup operations with conflicting defaults.
- new rule: Keep non-destructive save operations and destructive cleanup operations in separate skills with separate trigger vocabularies.
- trigger phrase: "整理/まとめ" means organizer, "保存" means archiver.
- severity: medium
- repeat_count: 1

### [2026-02-12] <type: worked-well>
- context: User requested a destructive cleanup test that deletes old session-level logs after daily consolidation.
- signal: Operation involved irreversible deletion and needed proof that day-level outputs were rebuilt first.
- action: Removed existing daily outputs, ran organizer over date range, and verified resulting file set.
- result: New day-level full+summary files were recreated and 11 source files were deleted only after successful writes.
- root cause: N/A (verification-focused execution).
- new rule: For destructive log cleanup, execute in this order: remove stale daily outputs -> consolidate -> confirm final file list.
- trigger phrase: "整理して削除" requires post-run file-set verification.
- severity: high
- repeat_count: 1

### [2026-02-13] <type: near-miss>
- context: Custom skills were copied manually but `$` list still showed only system skills.
- signal: Runtime showed `HOME=/home/ys` while copied skills were under `/mnt/c/Users/nekol/.codex/skills`.
- action: Compared both runtime paths and synced custom skill folders into `/home/ys/.codex/skills`.
- result: Runtime path now includes custom `SKILL.md` files and visibility issue is resolved.
- root cause: Path mismatch between Windows-side deployment and active WSL runtime deployment.
- new rule: Always verify active `HOME` and check `~/.codex/skills` before concluding copy failure.
- trigger phrase: "手動コピーしたのに見えない" means path mismatch first.
- severity: medium
- repeat_count: 1

### [2026-02-14] <type: near-miss>
- context: User requested "前日まで" consolidation with source deletion enabled.
- signal: Organizer failed on first pass because some target dates had already been consolidated and had no per-session source files.
- action: Detected failure quickly, narrowed range to dates with actual source logs (2026-02-12..2026-02-13), and re-ran.
- result: Daily outputs were produced and only valid source files were deleted after validation.
- root cause: Assumed contiguous date range always contains per-session source files.
- new rule: Before destructive consolidation, pre-scan target range for source existence and run only actionable dates.
- trigger phrase: "前日まで整理" requires source-presence precheck.
- severity: medium
- repeat_count: 1
### [2026-02-14] <type: mistake>
- context: User requested session-log save via skill after a long implementation thread.
- signal: User reported both files looked like summary, not full transcript quality.
- action: Re-saved with transcript-style full content under a new base and verified file contents.
- result: Full and summary are now clearly differentiated in structure and detail.
- root cause: Full payload was manually composed too tersely and drifted toward summary format.
- new rule: For `session-log-archiver`, full payload must be chronology/transcript-focused; summary payload keeps section digest.
- trigger phrase: "全文ログでない" means rebuild full with timeline detail immediately.
- severity: medium
- repeat_count: 1
### [2026-02-14] <type: worked-well>
- context: User required literal separation of full-log save and summary save quality.
- signal: Recent saved full logs were structurally summary-like despite separate files.
- action: Added strict content-role validation in `session-log-archiver` with explicit override flag.
- result: Misrouted payloads now fail fast (`full` summary-like / `summary` transcript-like) before writing files.
- root cause: File role was separated by filename only, without content-level quality guardrails.
- new rule: For log archiving, enforce content-role validation before base allocation and write.
- trigger phrase: "全文保存と要約保存の2種類" requires strict payload-role checks.
- severity: medium
- repeat_count: 1
### [2026-02-14] <type: worked-well>
- context: User required literal full-history save, not manually reconstructed narrative logs.
- signal: Repeated feedback that saved full logs still felt like summaries.
- action: Switched full-log source to optional raw history ingestion (`--full-from-history`) with session-id targeting.
- result: Full logs can now be generated directly from history entries, reducing manual reconstruction drift.
- root cause: Previous flow depended on assistant-authored full text, which introduced abstraction.
- new rule: When user asks for literal full save, use source-of-truth ingestion mode rather than narrative reconstruction.
- trigger phrase: "文字通り、全文保存" means history-source full generation.
- severity: high
- repeat_count: 1
### [2026-02-14] <type: near-miss>
- context: User requested immediate commit+push for repository cleanup.
- signal: Commit succeeded but push failed with `Could not resolve host: github.com` in restricted execution environment.
- action: Completed commit locally, verified branch state (`ahead 1`), and prepared direct user push command.
- result: Code changes are safely committed; only network-side publish step remains.
- root cause: Environment-level network restriction prevented remote reachability.
- new rule: For publish tasks, preflight remote reachability (`git ls-remote` or lightweight push check) before claiming end-to-end push completion.
- trigger phrase: "pushしてください" requires explicit remote reachability confirmation.
- severity: medium
- repeat_count: 1
### [2026-02-15] <type: mistake>
- context: Tried to make `/home/ys` always writable by adding a shell wrapper with `--add-dir /home/ys`.
- signal: `codex` startup failed with `Ignoring --add-dir ... because the effective sandbox mode is read-only`.
- action: Removed `--add-dir` from `~/.bashrc` wrapper and validated startup with plain `codex -C /home/ys`.
- result: Normal startup restored; write mode is now selected explicitly via `--full-auto` when needed.
- root cause: Assumed add-dir was universally safe regardless of effective sandbox mode.
- new rule: Never hardcode `--add-dir` in default launcher unless sandbox mode is guaranteed `workspace-write`.
- trigger phrase: "Ignoring --add-dir because ... read-only" means wrapper/options conflict first.
- severity: medium
- repeat_count: 1

### [2026-02-15] <type: worked-well>
- context: User needed consistent behavior across `/home/ys`, `workspace`, and `bin` after environment migration.
- signal: Policy drift and overlapping AGENTS scopes caused confusion about what rules were active.
- action: Re-layered AGENTS by responsibility (global default + minimal local overrides) and moved session-memory files to `~/.codex`.
- result: Rules are now predictable by directory, and session memory is globally available regardless of working path.
- root cause: Prior setup mixed global and local concerns in multiple files with overlapping ownership.
- new rule: Keep global AGENTS for cross-cutting policy; keep local AGENTS short and directory-specific.
- trigger phrase: "どのAGENTSが効いているか混乱" means re-check scope layering before adding new rules.
- severity: medium
- repeat_count: 1
### [2026-02-16] <type: near-miss>
- context: Moved XDG periodic check from Linux cron to Windows Task Scheduler.
- signal: Risk of duplicate runs if cron entry remains while Windows task is enabled.
- action: Removed cron line after task creation and verified `crontab -l` has 0 lines.
- result: Single scheduler source-of-truth established; duplicate execution avoided.
- root cause: Migration naturally spans two schedulers with overlapping command paths.
- new rule: During scheduler migration, always validate three points: new scheduler active, old scheduler disabled, shared log receives a single execution path.
- trigger phrase: "cronをタスクに変更" means old scheduler cleanup is mandatory.
- severity: medium
- repeat_count: 1

### [2026-02-16] <type: near-miss>
- context: Creating task with `Register-ScheduledTask` initially returned access denied (`0x80070005`).
- signal: API-based creation failed while command-line scheduler path could still create daily task.
- action: Used `schtasks /Create` for initial task creation, then `Set-ScheduledTask` to attach advanced triggers/settings.
- result: Task configured with daily + logon triggers and verification succeeded (`LastTaskResult=0`).
- root cause: Privilege/context mismatch between registration methods in this environment.
- new rule: If `Register-ScheduledTask` fails with access denial, fallback to `schtasks` for creation and re-apply advanced settings via `Set-ScheduledTask`.
- trigger phrase: "HRESULT 0x80070005" indicates method fallback, not immediate abort.
- severity: medium
- repeat_count: 1

### [2026-02-19] <type: near-miss>
- context: First push of a newly created private repo was rejected by GitHub GH007 (private email protection).
- signal: `remote rejected ... push declined due to email privacy restrictions`.
- action: Recreated local git metadata with noreply commit identity, then pushed again.
- result: Initial branch push succeeded with upstream tracking.
- new rule: Before first push in fresh repos, set a noreply-compatible `user.email` locally if account privacy enforcement is enabled.
- severity: low
- repeat_count: 1

### [2026-02-23] <type: near-miss>
- context: First push of new `Chienomori` repo after `gh repo create --push` was rejected by GitHub GH007 (private email protection).
- signal: Remote rejected `HEAD -> master` with "push declined due to email privacy restrictions".
- action: Set local noreply email, then amended the existing commit with `git commit --amend --no-edit --reset-author` before retrying push.
- result: Push to `origin/master` succeeded and upstream tracking was established.
- new rule: If GH007 occurs after a commit already exists, changing `user.email` alone is insufficient; amend (or rewrite) affected commit author metadata before retrying push.
- severity: low
- repeat_count: 2

### [2026-03-11] <type: near-miss>
- context: `iching-sdk` skill produced unstable EXTRACT answers when users started a fresh thread and relied on skill-chat output instead of the CLI workflow.
- signal: `EX_SIMPLE` sometimes looked acceptable, but `EX_5` and `EX_COMPARE` drifted in structure and repeated the same malformed answer across repeated prompts.
- action: Re-centered acceptance on `./iching run`, marked the old consolidated prompt as reference-only, and updated the skill text to forbid direct EXTRACT chat answers before the CLI path.
- result: The documented quality-guaranteed path is now explicit and the skill wording matches the SDK runtime contract.
- root cause: Acceptance and skill guidance had drifted toward direct-thread observation, which bypassed the SDK runtime prompt fragments and validator artifacts.
- new rule: When an SDK skill wraps a CLI, treat chat-only answers as non-authoritative unless the skill explicitly delegates to the CLI artifacts path.
- trigger phrase: "skill starts answering directly" means wrapper contract drift first.
- severity: medium
- repeat_count: 1

### [2026-04-17] <type: near-miss>
- context: Synced ekikyo asset changes into the plugin repo and deployment target.
- signal: One takashima file briefly landed in the asset root because the destination subdirectory was omitted.
- action: Removed the misplaced copy and recopied the file into takashima/ on both destinations.
- result: Final copies match the source layout and content.
- root cause: Used a file-path rsync target without preserving the source subdirectory.
- new rule: When copying nested asset files, confirm the destination directory level before running rsync.
- trigger phrase: nested file copy means re-check target directory.
- severity: low
- repeat_count: 1

### [2026-10-04] <type: near-miss>
- context: Generated an EX_COMPARE answer from five Takashima changing-line sources.
- signal: One manually copied Japanese reading line in the 九三 source block differed from the canonical source.
- action: Compared every quoted changing-line block against `assets/takashima/`, corrected the line, and reran the final checks.
- result: Final output contains exact source quote/readings; 76 prompt-builder tests pass under UTF-8 output settings.
- new rule: For EX_COMPARE, compare each quote and reading line against the canonical file before delivery, not only the original Chinese line.
- severity: low
- repeat_count: 1
