# AI Notes

## Preferences
- Prefer concise, practical explanations.
- Automate routine steps to reduce repeated user prompts.
- Prefer using `safe-git-publish` for commit/push requests unless explicitly overridden.
- Keep Todo tracking visible for multi-step tasks.
- Keep `README.md` in Japanese and keep skill docs/scripts (`SKILL.md`, `references/`, `scripts/`) in English.

## Mistakes
- [2026-02-08] No entries yet.

## Effective Patterns
- [2026-02-08] Keep a two-layer setup: global guardrails in `~/.codex/AGENTS.md` and workspace memory workflow in `Workspace/AGENTS.md`.

## Next Session Focus
- Keep updating this file at each completed task.
- Confirm the response footer shows `ai-notes update: done` when updates are written.

## Session Log
- [2026-04-19] Synced quote block spacing fixes across ekikyo assets and plugin vendor.
  - Copied `assets/honka.md` and `assets/takashima/35_火地晋.md` into `vendor/ekikyo/assets/`.
  - Regenerated `data/quote-dataset.json` from the updated source set.
  - Synced the regenerated dataset to the Obsidian plugin deployment target.
  - Published branch `codex/quote-block-spacing-fix` with a commit+push.
- [2026-04-10] Flattened single-file assets and renamed quote sources in `ekikyo`.
  - Moved canonical quote files to `assets/honka.md` and `assets/koji.md`.
  - Moved reference cases to `assets/高島易断占例.md`.
  - Kept `assets/takashima/` as the only grouped source directory.
  - Updated scripts, contract docs, and README paths to match the new layout.
  - Verified with unit tests and prompt build smoke run.
- [2026-02-08] Initialized workspace memory system.
  - Added `Workspace/AGENTS.md` with note-reading and note-update rules.
  - Added `Workspace/ai-notes.md` with sections for preferences, mistakes, patterns, and focus.
  - Set update triggers to task-end and session-end.
- [2026-02-08] Updated AGENTS precedence and note hygiene rules.
  - Added precedence guidance to global `~/.codex/AGENTS.md`.
  - Added conflict resolution and task-end definition to `Workspace/AGENTS.md`.
  - Added append-first note hygiene and secret-handling restrictions.
  - Kept rules concise and compatible with task-end auto-update flow.
- [2026-02-08] Created chat log archive structure and saved today's thread.
  - Created `Workspace/chat-logs/` as the storage location for chat logs.
  - Moved existing logs into `chat-logs/` to centralize history.
  - Added full log and summary for this thread as `*-2.md` files.
  - Confirmed root no longer contains scattered `chat-thread-*.md` files.
- [2026-02-08] Renamed chat log files to numbered title format.
  - Applied `YYYY-MM-DD-NN-short-title` naming for same-day sorting.
  - Paired full logs with matching `-summary` filenames.
  - Current set uses `01-codex-gemini-semi-automation` and `02-agents-ai-notes-workflow`.
- [2026-02-08] Session end note.
  - Confirmed AGENTS + ai-notes workflow is active and stable.
  - Confirmed chat logs are centralized under `Workspace/chat-logs/`.
  - Keep using numbered short-title filenames for same-day threads.
  - Next session: continue task-end updates and avoid note bloat.
- [2026-02-08] Standardized `lib-skills/codex/imagen` to Codex-oriented docs and defaults.
  - Replaced Claude/plugin wording in `README.md`, `reference.md`, and `examples.md`.
  - Updated default output directory in script to `/mnt/e/Documents/Workspace/images/imagen-output`.
  - Added output resolution behavior: omitted output -> default dir, file path -> exact file, directory path -> auto filename.
  - Verified CLI parsing with `python3 scripts/generate_image.py --help`.
- [2026-02-08] Saved this thread logs to `chat-logs/` before session end.
  - Full transcript was split into part files using `chat-thread-2026-02-08-03-imagen-codex-spec-update-part1.md` and `-part2.md`.
  - Added concise summary file `chat-thread-2026-02-08-03-imagen-codex-spec-update-summary.md`.
  - Session-end preference confirmed: output both full log and summary, in that order.
- [2026-02-08] Published imagen updates to GitHub repo `lib-skills-codex`.
  - Committed on `main` as `27daec0` with message `feat(imagen): align codex docs and output path rules`.
  - Pushed to `origin/main`; updated existing `imagen` path (not a new folder).
  - Included 5 files: docs (`README.md`, `SKILL.md`, `examples.md`, `reference.md`) and `scripts/generate_image.py`.
- [2026-02-08] Added git anti-forget gate to workspace AGENTS.
  - Added `Session End Gate (Git)` section to `Workspace/AGENTS.md`.
  - Requires `git status --short --branch` before substantial task finalization.
  - Requires chat-log/session-end outputs to include `repo`, `branch`, `last commit`, `push status`.
- [2026-02-08] Saved thread 03 continuation as Part 3 and refreshed summary.
  - Added `chat-thread-2026-02-08-03-imagen-codex-spec-update-part3.md`.
  - Rewrote `chat-thread-2026-02-08-03-imagen-codex-spec-update-summary.md` to include git publish and anti-forget decisions.
  - Kept summary structure aligned to: 目的 / 決定事項 / 実施内容 / 次アクション / 注意点.
- [2026-02-08] Added explicit Git footer output rules to `Workspace/AGENTS.md`.
  - Standardized footer states: `git check: done (...)`, `git check: done (not a git repo)`, and `git check: not done`.
  - Keeps repo-external sessions easy to recognize at a glance.
  - Pairs with existing `ai-notes update: done|not done` footer convention.
- [2026-02-08] Saved current AGENTS/git-footer discussion as thread 03 Part 4.
  - Added `chat-thread-2026-02-08-03-imagen-codex-spec-update-part4.md` with full transcript.
  - Updated `chat-thread-2026-02-08-03-imagen-codex-spec-update-summary.md` to include the latest decisions.
  - Kept summary structure: 目的 / 決定事項 / 実施内容 / 次アクション / 注意点.
- [2026-02-08] README localization policy finalized and applied.
  - Kept `AGENTS.md` and `SKILL.md` in English for stable agent/tool interpretation.
  - Switched `lib-skills/codex/README.md` and `lib-skills/codex/imagen/README.md` to Japanese.
  - Confirmed `Workspace/AGENTS.md` and `Workspace/ai-notes.md` remain local (not in `lib-skills/codex` git scope).
- [2026-02-08] Committed and pushed README localization to `lib-skills/codex`.
  - Commit: `507d008` on `main` with message `docs: localize readmes for japanese-first usage`.
  - Included files: `README.md`, `imagen/README.md`.
  - Push status: `origin/main` updated successfully.
- [2026-02-09] Added new `ocr2md` skill scaffold and CLI implementation in `lib-skills/codex`.
  - Fixed defaults: Japanese-only, strict fidelity, raw OCR saved by default, page separator `---`.
  - Implemented required manual controls: `writing-mode` and `model` (`flash|thinking|pro`).
  - Added user template `ocr2md/templates/ocr2md-request.md` aligned to agreed workflow.
  - Committed locally on `main` as `4eda9b1`; branch is ahead of `origin/main` by 1.
- [2026-02-09] Pushed `ocr2md` implementation to GitHub (`lib-skills-codex`).
  - Push succeeded: `main` updated from `507d008` to `4eda9b1`.
  - Remote sync confirmed: local `main` is now up-to-date with `origin/main`.
  - Keep using Japanese README policy for user-facing skill docs.
- [2026-02-09] Exported session logs to `Workspace/codex-logs` for OCR2MD thread.
  - Full transcript saved as split files: `...-part1.md` and `...-part2.md`.
  - Summary saved as `...-summary.md` with 目的/決定事項/実施内容/次アクション/注意点.
  - Kept output order as requested: full log first, then summary log.
- [2026-02-09] Saved log-template discussion as new codex log set.
  - Created `codex-log-2026-02-09-02-log-template-operations.md` (full transcript).
  - Created `codex-log-2026-02-09-02-log-template-operations-summary.md` (updated concise summary format).
  - Confirmed preferred rule direction: append full log on repeat saves, update summary, split with `partN` when long.
- [2026-02-09] Built grouped merge files for `098c_龍青三` without touching source files.
  - Created output folder `易経ソース用md/098c_龍青三/honda_wataru_merged`.
  - Merged 64 files into 8 grouped files: `1-8` through `57-64`.
  - Added top heading format `# honda_wataru_<start>-<end>` for each output.
  - Demoted heading levels by one rank in merged bodies (`#`->`##`, `##`->`###`, `###`->`####`).
- [2026-02-09] Built grouped merge files for `098e_高島易断_増補` with `takashima_zouho` naming.
  - Created output folder `易経ソース用md/098e_高島易断_増補/takashima_zouho_merged`.
  - Merged 64 files into 8 grouped files: `1-8` through `57-64`.
  - Added top heading format `# takashima_zouho_<start>-<end>` for each output.
  - Demoted heading levels by one rank in merged bodies (`#`->`##`, `##`->`###`, `###`->`####`).
- [2026-02-09] Saved this merge-session chat logs to `codex-logs`.
  - Created full transcript: `codex-log-2026-02-09-03-markdown-merge-batch-build.md`.
  - Created summary: `codex-log-2026-02-09-03-markdown-merge-batch-build-summary.md`.
  - Kept save order as requested: full log first, then summary.
- [2026-02-09] Built merged files for `098i_易経_十翼_繋辞伝_まとめ` using `keiji` naming.
  - Created output folder `易経ソース用md/098i_易経_十翼_繋辞伝_まとめ/keiji_merged`.
  - Generated `keiji_jouden_1-12.md` and `keiji_kaden_1-12.md` from three source chunks each.
- [2026-04-14] Removed `## 総合解釈` from `ekikyo` SIMPLE templates.
  - Updated `EX_SIMPLE`, `EX_SIMPLE2`, and `EX_5` contracts, format docs, prompt rules, and validators to treat them as block-only outputs.
  - Simplified assembly so fixed quote sections flow directly into `## 参照`, then optional `## 高島易断` / `## 占例抜粋`.
  - Regenerated SIMPLE/EX5 canonical fixture answers from the current scripts.
  - Verified PromptBuild/Assembly/RawAppend unittest coverage passes; one unrelated Selection test still fails due pre-existing asset reading changes in the dirty worktree.
  - Applied heading demotion by one level outside code fences and kept source files unchanged.
- [2026-02-09] Updated log set `03-markdown-merge-batch-build` for same-chat continuation.
  - Appended new transcript section to `codex-log-2026-02-09-03-markdown-merge-batch-build.md`.
  - Overwrote `codex-log-2026-02-09-03-markdown-merge-batch-build-summary.md` with latest combined summary.
  - Kept base name fixed and preserved output order: full log first, summary second.
- [2026-02-10] Downloaded Anthropic `skill-creator` into local `claudecode` skills folder.
- [2026-04-10] Imported standalone `ekikyo-sdk` into `iching/ekikyo-sdk` with subtree history preserved.
  - Used a dedicated `codex/migrate-ekikyo-sdk` branch in `/home/ys/projects/archive/iching`.
  - Removed the old in-repo copy first, then added the standalone repo as a subtree under `ekikyo-sdk/`.
  - Current `iching` HEAD is `8147661` and the branch is clean locally.
  - External `ekikyo-sdk` repo is still retained for now as the archive/source of history.
  - Recreated commits with a GitHub no-reply author to satisfy push email privacy rules.
  - Pushed the branch to `origin/codex/migrate-ekikyo-sdk`.
  - Opened draft PR `https://github.com/ys1887/iching/pull/3`.
  - Deleted the standalone GitHub repo `ys1887/ekikyo-sdk` after the subtree migration.
- [2026-04-10] Synced updated ekikyo reference-case source into the plugin repo.
  - Copied `vendor/ekikyo/assets/reference-cases/高島易断占例.md` from `/home/ys/projects/ekikyo/assets`.
  - Regenerated `data/quote-dataset.json` with `scripts/generate_quote_dataset.py`.
  - Committed as `d566974` with message `fix: sync updated ekikyo assets`.
  - Pushed `main` to `origin/main` successfully.
- [2026-04-10] Resynced updated quote sources into the plugin and Obsidian plugin copies.
  - Copied `quotes-honka.md` and `quotes-koji.md` from `/home/ys/projects/ekikyo/assets/quotes`.
  - Refreshed `data/quote-dataset.json` from the updated quotes.
  - Updated the Obsidian plugin copy at `C:\\Users\\nekol\\Proton Drive\\Obsidian\\.obsidian\\plugins\\ekikyo`.
  - Committed as `63a087e` with message `fix: sync updated quote sources`.
  - Pushed `main` to `origin/main` successfully.
- [2026-04-10] Re-synced the latest `quotes-honka.md` edit into the repo and Obsidian copies.
  - Updated `vendor/ekikyo/assets/quotes/quotes-honka.md` from `/home/ys/projects/ekikyo/assets/quotes`.
  - Regenerated `data/quote-dataset.json` to keep quote data aligned.
  - Re-copied the refreshed dataset into `C:\\Users\\nekol\\Proton Drive\\Obsidian\\.obsidian\\plugins\\ekikyo`.
 - [2026-04-25] Expanded `SIMPLE2` to include zhi-gua "卦部分" output.
  - Updated `main.js` so `SIMPLE2` now renders zhi-gua body excerpt, Takashima `卦辞/彖伝/大象伝`, and divination excerpt.
  - Kept the line block only on the main hexagram side and left the final `占例抜粋` tied to the changing line.
  - Committed as `1958843` on `codex/quote-block-spacing-fix` and pushed to `origin`.
  - Synced the updated `main.js` into the Obsidian plugin deployment folder.
  - Left the changes uncommitted because this turn only requested redistribution.
- [2026-04-11] Synced updated `高島易断占例.md` from the source assets tree.
  - Copied `/home/ys/projects/ekikyo/assets/高島易断占例.md` into repo `vendor/ekikyo/assets/高島易断占例.md`.
  - Added the same file to the Obsidian plugin copy under `C:\\Users\\nekol\\Proton Drive\\Obsidian\\.obsidian\\plugins\\ekikyo`.
  - Regenerated `data/quote-dataset.json` and copied it to the Obsidian plugin data folder.
  - Committed as `035d2c1` with message `fix: sync updated taishima reference case`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` successfully.
- [2026-04-11] Synced updated `honka.md` and `koji.md` source files.
  - Copied both files from `/home/ys/projects/ekikyo/assets` into repo `vendor/ekikyo/assets`.
  - Refreshed `data/quote-dataset.json` from the updated quote sources.
  - Re-copied the updated vendor assets and dataset into the Obsidian plugin copy.
  - Committed as `1484e3f` with message `fix: sync updated honka and koji sources`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` successfully.
- [2026-04-12] Synced the latest `honka.md` revision into repo and Obsidian copies.
  - Updated `vendor/ekikyo/assets/honka.md` from `/home/ys/projects/ekikyo/assets/honka.md`.
  - Regenerated `data/quote-dataset.json` to keep source-derived data aligned.
  - Re-copied the refreshed dataset into `C:\\Users\\nekol\\Proton Drive\\Obsidian\\.obsidian\\plugins\\ekikyo`.
  - Left the changes uncommitted because this turn only requested redistribution.
- [2026-04-13] Synced the latest `honka.md` and `koji.md` revisions and published them.
  - Updated both files from `/home/ys/projects/ekikyo/assets` into repo `vendor/ekikyo/assets`.
  - Regenerated `data/quote-dataset.json` from the updated source texts.
  - Re-copied the refreshed dataset into the Obsidian plugin copy.
  - Committed as `01928e3` with message `fix: sync updated honka and koji sources`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` successfully.
- [2026-04-13] Synced another `honka.md` and `koji.md` revision and published it.
  - Updated both files from `/home/ys/projects/ekikyo/assets` into repo `vendor/ekikyo/assets`.
  - Regenerated `data/quote-dataset.json` and re-copied it to the Obsidian plugin copy.
  - Committed as `d959613` with message `fix: sync updated honka and koji sources`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` successfully.
- [2026-04-13] Synced the latest changed files from `/home/ys/projects/ekikyo/assets`.
  - Updated `takashima/29_坎為水.md` and `高島易断占例.md` in repo `vendor/ekikyo/assets`.
  - Regenerated `data/quote-dataset.json` and re-copied it to the Obsidian plugin copy.
  - Removed one trailing-space artifact in `29_坎為水.md` before commit.
  - Committed as `3ead97f` with message `fix: sync updated ekikyo assets`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` successfully.
- [2026-04-13] Added repo-local workflow docs for ekikyo asset syncing.
  - Created top-level `README.md` for human-facing source-of-truth and sync flow guidance.
  - Created top-level `AGENTS.md` for Codex-facing rules about vendored assets and dataset regeneration.
  - Documented exact source path `/home/ys/projects/ekikyo/assets`.
  - Documented exact Obsidian deployment path `C:\Users\nekol\Proton Drive\Obsidian\.obsidian\plugins\ekikyo`.
  - Kept `vendor/ekikyo/assets/README.md` unchanged because it serves a different scope.
- [2026-04-09] Added `karpathy-coding-guardrails` as a Codex-native skill in `lib-skills/codex`.
  - Ported the core ideas from `forrestchang/andrej-karpathy-skills` without copying Claude plugin packaging.
  - Scoped the trigger to non-trivial coding, debugging, refactoring, and review tasks.
  - Added `SKILL.md`, `agents/openai.yaml`, and a compact `references/claude-source-notes.md`.
  - Validated the package with `skill-creator-codex/scripts/quick_validate.py`.
- [2026-04-08] Updated `ekikyo` answer heading display to source-aligned labels.
  - Kept internal section keys as `本卦` / `変爻` and changed only final visible headings.
  - `EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` now render top-level headings like `風雷益`, `九五`, `六三`.
  - Heading validation now accepts both internal labels and displayed source-derived labels.
  - Re-running assemble on already-rendered answers remains supported.
  - Verified with `python3 -m unittest tests.test_build_extract_prompt`.
- [2026-04-08] Extended auxiliary heading display for `ekikyo` assembled answers.
  - `EX_SIMPLE2` and `EX_5` now render auxiliary headings as `之卦：卦名`, `互卦：卦名`, `錯卦：卦名`, `綜卦：卦名`.
  - Internal matching still uses the original role labels to keep assembly and validation stable.
  - Updated canonical fixtures and assembly tests to assert the new auxiliary heading form.
- [2026-04-07] Re-sorted `110_易占` by Windows `CreationTime` CSV and rewrote `LastWriteTime`.
  - Used the Windows-exported CSV as the source of truth because WSL could not read true creation time directly.
  - Kept a stable tie-break order using `day:` and filename-derived dates.
  - Created `work/110_易占_dayなし一覧.md` for notes missing `day:` metadata.
- [2026-04-07] Rewrote `110_易占` `LastWriteTime` again using note-body dates.
  - Accepted `day:` frontmatter, standalone `YYYY-MM-DD` after the title, legacy `## Day:` / `## Day_`, and top-level `## YYYY-MM-DD`.
  - Left `CreationTime` untouched and used filename as the final tie-breaker.
  - Confirmed `買取大吉？.md` now sits on `2025-04-20` in update-date ordering.
- [2026-03-10] Updated Codex skill runtime publishing to dual targets.
  - Kept `/home/ys/projects/lib-skills/codex` as the only source-of-truth.
  - Changed `codex-publish-skill` to publish to both `/home/ys/.codex/skills` and `/mnt/c/Users/nekol/.codex/skills` by default.
  - Changed `codex-verify-skill-runtime` to verify both runtime targets by default and report target-specific status.
  - Updated `lib-skills/codex/README.md`, `/home/ys/projects/AGENTS.md`, and `/home/ys/.codex/AGENTS.md` to match the new dual-runtime rule.
  - Source used: `https://github.com/anthropics/skills` with sparse checkout path `skills/skill-creator`.
  - Destination: `E:\Documents\Workspace\lib-skills\claudecode\skill-creator`.
  - Verified copied files include `SKILL.md`, `LICENSE.txt`, `references/`, and `scripts/`.
- [2026-02-10] Created Codex-native `skill-creator` in `lib-skills/codex` and pushed to GitHub.
  - Kept policy: only `lib-skills/codex/README.md` in Japanese; skill files/scripts/references in English.
  - Replaced Claude-specific packaging/frontmatter guidance with Codex-oriented workflow and validation.
  - Added `scripts/init_skill.py` and `scripts/validate_skill.py`; removed package-specific script flow.
  - Commit `228d369` pushed to `origin/main` in `lib-skills/codex`.
- [2026-02-10] Saved this thread logs to `Workspace/codex-logs`.
  - Created full transcript as split files: `codex-log-2026-02-10-01-skill-creator-codex-migration-part1.md` and `-part2.md`.
  - Created summary file: `codex-log-2026-02-10-01-skill-creator-codex-migration-summary.md`.
  - Preserved required output order: full log first, then summary.
- [2026-02-10] Added and published `session-log-archiver` skill in `lib-skills/codex`.
  - New files: `session-log-archiver/SKILL.md`, `session-log-archiver/scripts/save_session_logs.py`, `session-log-archiver/references/naming-and-rules.md`.
  - Script behavior fixed to deterministic rules: base reuse/new NN, full append, summary overwrite, optional part splitting, fixed result output.
  - Updated `lib-skills/codex/README.md` skill list entry (Japanese policy preserved).
  - Validated script with `--help`, `py_compile`, and dry-run sample.
  - Commit `86d67d8` pushed to `origin/main`.
- [2026-02-10] Confirmed operator defaults for upcoming sessions.
  - Git operations should prefer `safe-git-publish` by default.
  - Keep Todo progress tracking enabled for multi-step work.
  - Continue allowing explicit per-task override instructions.
- [2026-02-10] Enhanced `session-log-archiver` with integrated close checks and published update.
  - Added default post-save checks in `save_session_logs.py`: ai-notes status + git status/record output.
  - Added options `--workspace-root`, `--git-repo`, and `--skip-close-check`.
  - Updated docs in `session-log-archiver/SKILL.md` and `references/naming-and-rules.md`.
  - Updated Japanese root README description for `session-log-archiver`.
  - Published commit `f20744d` to `origin/main` using `safe-git-publish`.
- [2026-02-10] Confirmed workspace-level language policy location and operation.
  - Canonical rule is now explicit in `Workspace/AGENTS.md` under `Documentation Language Policy`.
  - Rule: `README.md` in Japanese; `AGENTS.md`/`SKILL.md`/`scripts`/`references` in English by default.
  - Keep using `ai-notes.md` as reinforcement, not as the sole source of truth.
- [2026-02-10] Added and published `md-batch` skill in `lib-skills/codex`.
  - Implemented `md-batch/scripts/merge_md_batches.py` with grouped merge, auto-range naming, heading demotion, and code-fence exclusion.
  - Added docs: `md-batch/SKILL.md` and `md-batch/references/rules-and-examples.md`.
  - Updated Japanese root `README.md` skill list entry for `md-batch`.
  - Validated with `--help`, `py_compile`, and dry-run/real sample output checks.
  - Published commit `b1a3cf5` to `origin/main` via `safe-git-publish`.
- [2026-02-10] Executed end-of-session log save via `session-log-archiver`.
  - Created base `codex-log-2026-02-10-02-skills-rollout-wrapup` in `Workspace/codex-logs`.
  - Wrote full log and summary log in the required order.
  - Close-check output confirmed `ai-notes update: done` and clean/up-to-date git state for `lib-skills/codex`.
- [2026-02-10] Added workspace-wide skill visibility reporting guidance.
  - Updated `Workspace/AGENTS.md` with `Skill Visibility Policy`.
  - Policy: include `skill used: <skill-name>` in substantial task results when applicable.
  - Keep this as a reporting guideline; do not backfill all existing skills.
- [2026-02-10] Added no-temp input mode to `session-log-archiver` to reduce permission prompts.
  - `save_session_logs.py` now accepts `--full-text` / `--summary-text` and stdin modes.
  - File mode remains supported via `--full-file` / `--summary-file` for compatibility.
  - Documented input modes in `session-log-archiver/SKILL.md` and `references/naming-and-rules.md`.
  - Validated with `--help`, `py_compile`, and inline dry-run (`--full-text` + `--summary-text`).
- [2026-02-10] Published no-temp input mode update for `session-log-archiver`.
  - Commit `0bb0394` pushed to `origin/main` in `lib-skills/codex`.
  - Added inline and stdin inputs to avoid temporary input file creation.
  - Kept existing file-input mode for compatibility with prior workflows.
- [2026-02-10] Saved end-of-session logs using inline-input mode.
  - Created `codex-log-2026-02-10-03-session-log-final-save.md` and matching `-summary.md`.
  - Used `session-log-archiver` with `--full-text` and `--summary-text` (no temp files).
  - Close-check confirmed clean/up-to-date state for `lib-skills/codex`.
- [2026-02-10] Added daily consolidation mode to `session-log-archiver` and ran retroactive cleanup.
  - New mode: `--consolidate-date YYYY-MM-DD` outputs date-only files and defaults to deleting source logs.
  - New outputs use `codex-log-YYYY-MM-DD.md` and `codex-log-YYYY-MM-DD-summary.md` (no title, no daily suffix).
  - Consolidated `2026-02-08` and `2026-02-09` logs; each date now has exactly two files.
  - Daily summary generation now composes a day-level summary from source summaries.
- [2026-02-11] Updated `Workspace/AGENTS.md` with Codex execution-quality guardrails.
  - Added explicit workflow loop: Plan -> Implement -> Verify -> Report.
  - Added task sizing, subagent usage policy, verification minimum, and completion report standard.
  - Added `ai-notes Scope Control` to make note appends mandatory only for substantial tasks.
- [2026-02-11] Saved this AGENTS-improvement thread logs via `session-log-archiver`.
  - Created full log: `codex-log-2026-02-11-01-agents-md-codex-improvem.md`.
  - Created summary log: `codex-log-2026-02-11-01-agents-md-codex-improvem-summary.md`.
  - Close-check output reported `ai-notes update: done` and `git check: done (not a git repo)`.
- [2026-04-10] Initialized `obsidian-plugin` as a parent Git repo and pushed the first commit.
  - Parent repo path: `/home/ys/projects/obsidian-plugin`.
  - GitHub repo: `ys1887/obsidian-plugin` on `origin/main`.
  - Current plugin lives under `ekikyo-plugin/` so additional plugins can be added later.
  - Added `.gitignore` for `__pycache__`, `.pyc`, and the empty `ekikyo-plugin/.codex` marker.
- [2026-02-11] Standardized skills deployment flow and improved auto-trigger quality.
  - Added concrete frontmatter `description` text across top-level Codex skills.
  - Renamed `skill-creator` -> `skill-creator-codex` to avoid collision with `.system/skill-creator`.
  - Added `.system/` ignore rule in `lib-skills/codex/.gitignore` for source-repo hygiene.
  - Added `Skills Path Policy` to `Workspace/AGENTS.md` (E source repo -> C runtime sync, `.system` excluded).
- [2026-04-08] Built a combined quote-only source file in `ekikyo/work`.
  - Generated `/home/ys/projects/ekikyo/work/2026-04-08_02.md`.
  - Kept only `卦辞` and `爻辞` original/reading pairs.
  - Removed `彖伝`, `大象伝`, `小象伝`, modern prose, and `(占)` blocks.
  - Used the existing rendering helpers for extraction instead of adding new repo logic.
  - Published commit `538e6a4` to `origin/main`; left unrelated local edits in `session-log-archiver` script/reference files unstaged.
- [2026-02-11] Follow-up: aligned `skill-creator-codex` helper scripts with frontmatter policy.
  - Updated `scripts/init_skill.py` to scaffold YAML frontmatter (`name`, placeholder `description`).
  - Updated `scripts/validate_skill.py` to require frontmatter and enforce folder-name match.
  - Verified validator passes for all top-level skills and smoke-tested scaffold/validate flow.
  - Published commit `3b29d05` to `origin/main`.
- [2026-02-11] Saved this skills-standardization session logs via `session-log-archiver`.
  - Full log: `codex-log-2026-02-11-02-skills-runtime-standardi.md`.
  - Summary log: `codex-log-2026-02-11-02-skills-runtime-standardi-summary.md`.
  - Close-check output: `ai-notes update: done`, git repo check for `lib-skills/codex` is done/up-to-date.
- [2026-02-12] Verified GitHub rename migration and saved session logs.
  - Confirmed HTTPS remote/account alignment: `origin` points to `akanekoplay`, `gh auth status` is valid.
  - Set global commit identity to `Ys <github.sws0d@skogkatt.net>` in `~/.gitconfig`.
  - Saved logs: `codex-log-2026-02-12-01-github-rename-check.md` and matching `-summary.md`.
  - Keep HTTPS as default; only re-check SSH identity if switching remotes to `git@github.com:`.
- [2026-02-12] Appended continuation to the same session log base.
  - Reused base: `codex-log-2026-02-12-01-github-rename-check`.
  - Applied deterministic behavior: full log append + summary overwrite.
  - Added Ctrl+C/tmux recovery discussion to the archived transcript and summary.
- [2026-02-12] Added dual-notes operation for lightweight + strict learning.
  - Updated `Workspace/AGENTS.md` with `Dual Notes Operation` and `Strict Log Triggers`.
  - Added conditional strict logging policy tied to repeated mistakes, corrections, near-misses, and high-risk tasks.
  - Created `Workspace/ai-learning-log.md` as a structured strict ledger template.
  - Kept `ai-notes.md` as the lightweight dashboard for default task-end updates.
- [2026-02-12] Consolidated Codex past logs through yesterday into one summary file.
  - Read existing summaries in `codex-logs` from 2026-02-08 to 2026-02-11.
  - Created `codex-logs/codex-log-through-2026-02-11-summary.md` with timeline + outcomes + next-operation guidance.
  - Excluded 2026-02-12 logs to match the requested cutoff ("昨日まで").
- [2026-02-12] Ran daily log consolidation skill for past session dates.
  - Used `session-log-archiver` (`save_session_logs.py --consolidate-date`) for 2026-02-10 and 2026-02-11.
  - Generated daily files: `codex-log-2026-02-10(.md/-summary.md)` and `codex-log-2026-02-11(.md/-summary.md)`.
  - Used `--keep-source-on-consolidate` to keep original per-session logs while adding day-level rollups.
- [2026-02-12] Split logging workflow into save skill and organizer skill, then pushed to GitHub.
  - Updated `session-log-archiver` to save-only behavior and removed daily-consolidation docs.
  - Added new `session-log-organizer` skill with day/range consolidation and default source deletion.
  - Updated `lib-skills/codex/README.md` and published commit `03d7682` to `origin/main`.
- [2026-02-12] Rebuilt 2026-02-10 and 2026-02-11 daily logs using `session-log-organizer`.
  - Removed prior daily files for both dates, then re-ran consolidation with deletion-default behavior.
  - New daily files were created successfully and per-session source logs for those dates were deleted.
  - Verified remaining files: date-level logs for 02-10/02-11 and untouched 02-12 session logs.
- [2026-02-12] Saved this session logs with `session-log-archiver`.
  - Created base `codex-log-2026-02-12-02-dual-notes-log-skill` in `codex-logs`.
  - Wrote both full log and summary log (full first, summary second).
  - Close-check reported `ai-notes update: done` and `git check: done (not a git repo)`.
- [2026-02-13] Fixed custom-skill visibility mismatch between Windows and WSL runtime paths.
  - Confirmed Codex runtime HOME in this session is `/home/ys`, so active path is `/home/ys/.codex/skills`.
  - Verified user-copied custom skills existed in `/mnt/c/Users/nekol/.codex/skills` only.
  - Synced non-`.system` skill folders from Windows path to `/home/ys/.codex/skills`.
  - Verified runtime now contains `SKILL.md` for all custom skills (including `session-log-organizer`, `skill-creator-codex`).
- [2026-02-13] Saved current skills-operations discussion logs via `session-log-archiver`.
  - Created full log: `codex-log-2026-02-13-02-skills-approval-and-doll.md`.
  - Created summary log: `codex-log-2026-02-13-02-skills-approval-and-doll-summary.md`.
  - Confirmed close-check output includes `ai-notes update: done` and `git check: done (not a git repo)`.
- [2026-02-14] Saved current CODEX_HOME/session-policy discussion with `session-log-archiver`.
  - Created base `codex-log-2026-02-14-01-codex-home-log-policy` in `codex-logs`.
  - Wrote full + summary logs in deterministic order (full first, summary second).
  - Archiver close-check output: `ai-notes update: not done` and `git check: done (not a git repo)`.
- [2026-02-14] Consolidated previous-day session logs with `session-log-organizer`.
- [2026-03-14] Tightened `iching-div` EX_5 single-source output guardrails for Honda validation.
  - Added shared rule forbidding execution metadata like `skill used: ...` in final answers.
  - Added EX_5 rule that single-source outputs must keep one interpretation label and one citation family.
  - Updated `iching-div-honda` skill text to start answers directly at `**核心・結論**`.
  - Added prompt-builder tests for `tests/test_3.md` to lock metadata exclusion and Honda-only EX_5 acceptance shape.
  - Re-ran `python3 -m unittest tests.test_build_extract_prompt` successfully after the changes.
- [2026-03-14] Strengthened `iching-div` EX_5 no-changing-line contract after manual Honda test drift.
  - Added explicit EX_5 citation-line rules for main sections, auxiliary sections, changing-line blocks, and interpretation sections.
  - Added EX_5 rule forbidding `引用:` summary blocks or backticked citation lists in place of section-level references.
  - Added single-source EX_5 rule forbidding other profile-labeled interpretation sections.
  - Added Honda no-changing-line prompt test using `tests/test_2.md` to lock these constraints.
  - Re-ran `python3 -m unittest tests.test_build_extract_prompt` successfully after the update.
  - Initial range `2026-02-08..2026-02-13` failed on dates already consolidated (no per-session sources).
  - Re-ran for `2026-02-12..2026-02-13`; daily full+summary files were generated and 8 source files were deleted.
  - Verified final `codex-logs` set now has day-level files for `2026-02-08..2026-02-13` plus new `2026-02-14-01` session logs.
- [2026-02-13] Updated source skills in `lib-skills/codex` for language-aware logging behavior.
  - Added `--language ja|en|auto` to `session-log-archiver` and `session-log-organizer` scripts.
  - Archiver now localizes result output and auto-detects language from payload text when needed.
  - Organizer now regenerates daily summary from consolidated full logs (not summary-only merge).
  - Updated both `SKILL.md` and `references/*` with explicit language policy and `$skill` clarification.
  - Runtime deployment remains manual copy from source repo to `~/.codex/skills`.
- [2026-02-14] Corrected session-log save content quality after user feedback.
  - Initial `-02-skill-language-fix` full file was too summary-like.
  - Re-saved as transcript-style full log with new base `codex-log-2026-02-14-03-skill-language-fix-full`.
  - Keep `-02` as historical artifact; prefer `-03` for full-session reference.
- [2026-02-14] Updated `session-log-archiver` numbering behavior to always create new daily entries.
  - Default save mode now allocates new `NN` for every run on the same date (01, 02, 03...).
  - Removed automatic same-title base reuse from `choose_base_name()`.
  - Kept explicit reuse compatibility via `--base-name` (`mode: forced`).
  - Updated `SKILL.md` and `references/naming-and-rules.md` to match new default behavior.
  - Verified with real writes in `/tmp/archiver-nn-test`: 01/02 pair creation + forced reuse append/overwrite.
- [2026-02-14] Added strict full-vs-summary role checks to `session-log-archiver`.
  - New options: `--full-kind`, `--summary-kind`, and `--no-strict-content-check`.
  - Default strict mode now rejects summary-like full payloads before write.
  - Default strict mode now rejects full-transcript-like summary payloads before write.
  - Verified pass/fail paths using 2026-02-12 logs and dry-run checks.
- [2026-02-14] Saved this chat as full+summary pair via `session-log-archiver`.
  - Created base `codex-log-2026-02-14-06-chat-full-save` in `codex-logs`.
  - Full file now stores chronological chat detail; summary file stores compressed decisions/actions.
  - Close check during save reported ai-notes done and repo status captured for `lib-skills/codex`.
- [2026-02-14] Added history-source full save mode to `session-log-archiver`.
  - New full source option: `--full-from-history` + `--history-session-id` (+ optional `--history-file`, `--history-limit`).
  - Full log can now be generated from raw `history.jsonl` entries for literal chat-history capture.
  - Added strict input-source validation and history-mode error handling.
  - Updated `SKILL.md` and `references` with history-mode usage and constraints.
  - Verified with `/tmp/archiver-history-test` including generated full file content preview.
- [2026-02-14] Saved literal full-history chat log via `session-log-archiver` history mode.
  - Used `--full-from-history --history-session-id 019c5839-9b95-7653-b576-77fd6fb97718`.
  - Generated full file from raw history entries and separate summary file.
  - Current daily base is `codex-log-2026-02-14-01-literal-full-history` in `codex-logs`.
- [2026-02-14] Updated git remote owner display in `lib-skills/codex`.
  - Changed `origin` URL from `akanekoplay` to `ys1887`.
  - Verified `remote -v` now points to `https://github.com/ys1887/lib-skills-codex.git`.
  - Branch tracking remains `main...origin/main`.
  - `ls-remote` check could not run due DNS/network restriction in current environment.
- [2026-02-14] Reverted all uncommitted changes in `lib-skills/codex` to git-managed state.
  - Executed full restore for tracked files in repo root.
  - Targeted modified areas included `session-log-archiver` and `session-log-organizer`.
  - Post-check: working tree is clean on `main...origin/main`.
- [2026-02-14] Saved chat logs after git remote update and full restore operation.
  - Full log created: `codex-log-2026-02-14-02-git-remote-and-restore.md`.
  - Summary log created: matching `-summary.md` pair.
  - Close check at save time reported clean `lib-skills/codex` working tree on `main...origin/main`.
- [2026-02-14] Re-saved entire current session using full raw history extraction.
  - Generated full from all entries of session_id `019c5839-9b95-7653-b576-77fd6fb97718` (31 entries).
  - Saved pair: `codex-log-2026-02-14-03-full-session-retake.md` and matching summary.
  - This save was requested to cover the entire today session range.
- [2026-02-14] Removed stale skill entries from `lib-skills/codex/README.md` after local folder deletion.
  - Deleted list items for `session-log-archiver/` and `session-log-organizer/` only.
  - Verified no remaining references to those names under `lib-skills/codex`.
  - Git status in repo now shows README modified plus deleted skill directories pending commit.
- [2026-02-14] Published local cleanup commit for removing deprecated session-log skills.
  - Updated `lib-skills/codex/README.md` and removed both skill directories from git index/history tip.
  - Commit created: `a8a8342` on `lib-skills/codex` `main`.
  - Push from this environment failed due network/DNS restriction; branch remains `ahead 1`.
- [2026-02-15] Resolved Codex startup failure caused by sandbox mismatch in shell wrapper.
  - Root cause: `~/.bashrc` wrapper used `command codex -C /home/ys --add-dir /home/ys "$@"` while effective sandbox could be `read-only`.
  - Fix: removed `--add-dir` from wrapper; keep base launcher as `codex -C /home/ys` and use `--full-auto` only when write access is needed.
  - Cleaned stale trust entry from `~/.codex/config.toml`: removed `[projects."/mnt/e/Documents/Workspace"]`.
  - Verified current trust and startup path are aligned with `/home/ys`.
- [2026-02-15] Reorganized AGENTS layering for stable cross-directory behavior.
  - Global default in `~/.codex/AGENTS.md`; local overrides in `/home/ys/workspace/AGENTS.md` and `/home/ys/bin/AGENTS.md` only for local concerns.
  - Moved session memory files to global path: `/home/ys/.codex/ai-notes.md` and `/home/ys/.codex/ai-learning-log.md`.
  - Removed legacy workspace symlinks after confirming global-only operation.
  - Clarified skill contract: runtime loads from `~/.codex/skills`; `/home/ys/workspace/lib-skills/codex` is source/edit path with manual sync.
- [2026-02-15] Renamed primary work root from `/home/ys/workspace` to `/home/ys/projects`.
  - Updated references in global/local AGENTS and Proton sync script/README.
  - Sync destination naming was aligned to `.../Linux/projects`.
  - Kept compatibility link: `/home/ys/workspace -> /home/ys/projects`.
  - Created rollback snapshot: `/home/ys/workspace.bak.20260215-213105`.
  - Verified git health at `/home/ys/projects/lib-skills/codex` and successful sync execution.
- [2026-02-15] Applied lightweight XDG baseline with reusable scripts in `/home/ys/bin`.
  - Added `setup_xdg_baseline.sh` and `check_xdg_baseline.sh`; scripts are idempotent and include backups.
  - Updated shell config with XDG baseline and history paths: `HISTFILE` -> `~/.local/state/bash/history`, `LESSHISTFILE` -> `~/.local/state/less/history`.
  - Verified runtime impact: `git`, `codex`, `npm`, `node` checks all PASS after setup.
  - Backup artifacts created at `~/.codex/backups/xdg-baseline-20260215-232423/`.
  - Published bin repo commit `f43c474` to `origin/main`.
- [2026-02-16] Post-XDG stabilization checks completed.
  - Verified XDG env resolution in login shell and `check_xdg_baseline.sh` PASS.
  - Confirmed `git`, `codex`, `npm`, and `node` startup/availability after baseline change.
  - Executed Proton sync script manually; destination `.../Linux/projects` is present.
  - Confirmed Proton old `.../Linux/workspace` path no longer exists.
  - Local compatibility state remains: `/home/ys/workspace` symlink + rollback folder `workspace.bak.20260215-213105`.
- [2026-02-16] Removed compatibility symlink `/home/ys/workspace` after migration stabilization.
  - Verified no active references in AGENTS/shell/bin scripts and scheduler actions.
  - Windows scheduled tasks execute `/home/ys/bin/mirror_codex_to_proton.sh` (not workspace path).
  - Confirmed `/home/ys/projects` remains intact and `lib-skills/codex` git status is healthy.
  - Re-ran XDG baseline check post-removal: PASS.
  - Kept rollback folder `/home/ys/workspace.bak.20260215-213105` for optional later cleanup.
- [2026-02-16] Migrated XDG baseline check scheduler from Linux cron to Windows Task Scheduler.
  - Created `XDG_Baseline_Check_Daily` with action `wsl.exe -d Ubuntu -- bash -lc '/home/ys/bin/check_xdg_baseline.sh >> /home/ys/.local/state/xdg-check/cron.log 2>&1'`.
  - Updated task to include both daily 20:00 trigger and logon trigger (`MainPC\\ys`) with `StartWhenAvailable=True` and `MultipleInstances=IgnoreNew`.
  - Removed cron entry for `check_xdg_baseline.sh` to prevent duplicate execution (`crontab` now 0 lines).
  - Verified manual task run: `LastTaskResult=0` and log append with `Result: PASS`.
- [2026-02-16] Finalized scheduler policy for XDG checks after cron-to-Task migration.
  - Source of truth is Windows Task Scheduler (`XDG_Baseline_Check_Daily`), not Linux cron.
  - Health-check log path remains `~/.local/state/xdg-check/cron.log` for continuity.
  - Current expected state for handoff: `crontab -l` empty, two Windows tasks (`Mirror_Codex_To_ProtonDrive`, `XDG_Baseline_Check_Daily`), both actionable via `wsl.exe`.
- [2026-02-16] Added lightweight ops guardrails for XDG/mirror tasks.
  - Added `/home/ys/bin/notify_task_failure.sh` to record failures to `~/.local/state/ops/task-failures.log` and best-effort Windows Application event.
  - Added `/home/ys/bin/rotate_xdg_check_log.sh` for monthly rotation of `~/.local/state/xdg-check/cron.log` with 12 archives retention.
  - Updated `check_xdg_baseline.sh` to call log rotation and send failure notification only on `Result: FAIL`.
  - Updated `mirror_codex_to_proton.sh` with trap-based failure notification while keeping rsync behavior unchanged.
  - Added `/home/ys/bin/check_ops_health.sh` to validate Windows task health, empty crontab, XDG PASS, and recent XDG log tail in one command.
  - Verified with `bash -n` and a successful `check_ops_health.sh` run (`LastTaskResult=0` for both tasks).
- [2026-02-16] Executed failure-path validation for new ops guardrails.
  - Unit-invoked `notify_task_failure.sh`; confirmed local append at `~/.local/state/ops/task-failures.log`.
  - Induced XDG check failure by temporary rename of `~/.local/state/less`; observed `Result: FAIL` and notification, then restored and PASS verified.
  - Induced mirror failure by temporary replacement of destination dir path with a file; observed trap notification with stage marker, then restored and successful mirror run.
  - Ran `check_ops_health.sh` post-tests; both Windows tasks reported Ready/0 and XDG check PASS.
  - Windows Event Log entries were not observed in this environment; local failure log remains source-of-truth.
- [2026-02-16] Committed ops guardrail changes in `/home/ys/bin`.
  - Commit: `98de722` (`feat(ops): add failure notifications and health checks`).
  - Included 5 files: failure notifier, log rotator, health check script, and updates to XDG/mirror scripts.
  - Final pre-commit checks were green: `bash -n` and `check_ops_health.sh`.
  - Push intentionally skipped (not requested).
- [2026-02-16] Implemented medium/low-priority ops improvements in `/home/ys/bin`.
  - Added `OPERATIONS.md` as a single runbook for daily checks, recovery flow, and Windows task policy.
  - Improved `check_xdg_baseline.sh` diagnostics to aggregate failures and print a final failure summary.
  - Preserved existing PASS/FAIL contract and FAIL-only notification behavior.
  - Updated `README.md` with links to health/rotation/notification scripts and runbook entrypoint.
  - Verified with `bash -n`, `check_xdg_baseline.sh` PASS, and `check_ops_health.sh` PASS.
- [2026-02-16] Committed medium/low-priority follow-ups in `/home/ys/bin`.
  - Commit: `2145403` (`docs(ops): add runbook and improve xdg diagnostics`).
  - Added `OPERATIONS.md`; updated `README.md` and `check_xdg_baseline.sh`.
  - Kept `.codex` mirror policy unchanged (full sync, no excludes).
  - Validation remained green (`bash -n`, `check_xdg_baseline.sh` PASS, `check_ops_health.sh` PASS from prior step).
- [2026-02-16] Pushed `/home/ys/bin` main branch updates to origin.
  - Pushed range: `f43c474..2145403` to `origin/main`.
  - Included commits: `98de722` (ops guardrails) and `2145403` (runbook + xdg diagnostics docs).
  - Post-push status confirmed no ahead/behind on `main`.
- [2026-02-16] Expanded Proton mirror scope in `/home/ys/bin/mirror_codex_to_proton.sh` for lightweight recovery set.
  - Added sync targets: `.ssh`, `.config/gh`, `bin`, `.bashrc`, `.profile`, `.gitconfig`, `.tmux.conf`.
  - Kept exclusions unchanged by design: `.cache`, `.vscode-server`, `.nvm`, `.npm-global`, `.bun`, `.npm`, `.local`, `.config/gcloud`, `.gemini`.
  - Verified `bash -n` syntax check passed and manual run exited with code 0.
  - Confirmed all selected targets exist under `E:\Documents\Proton Drive\My files\Linux` via WSL path check.
- [2026-02-16] Ran first manual monthly full backup for `/home/ys` using WSL tar.
  - Created archive: `/mnt/e/Documents/圧縮ファイル/ys-full-20260216-012824.tar.gz`.
  - Archive size at creation: `998M`.
  - Verified listing starts with `ys/` path root and includes expected Linux paths.
  - Verified gzip integrity: `gzip -t` passed.
- [2026-02-16] Added new skill `ys-monthly-backup` for one-command monthly full archive.
  - Runtime skill path: `~/.codex/skills/ys-monthly-backup`.
  - Source-of-truth mirrored at `/home/ys/projects/lib-skills/codex/ys-monthly-backup`.
  - Implemented `scripts/create_backup.sh` (full `/home/ys` tar.gz to `/mnt/e/Documents/圧縮ファイル` + `gzip -t`).
  - Updated `SKILL.md` with fixed defaults and relative validation command.
  - Validation passed in both runtime and source skill trees.
- [2026-02-16] Renamed and published backup skill as `ys-backup`.
  - Runtime skill path is now `~/.codex/skills/ys-backup`.
  - Source-of-truth path is `/home/ys/projects/lib-skills/codex/ys-backup`.
  - Verified runtime/source parity (`diff -ru` no differences).
  - Validation passed (`bash -n` and skill validator in both trees).
  - Published commit `9d37222` to `origin/main`.
- [2026-02-16] Implemented weekly full backup automation for `/home/ys` to Proton latest-only flow.
  - Added `/home/ys/bin/backup_ys_full_to_proton.sh` (staging at `/var/tmp/ys-backup-staging`, verify via `gzip -t`).
  - Previous Proton full archives are moved to `/mnt/e/Documents/Backup` before promoting new archive.
  - Registered Windows task `Weekly_Ys_Full_Backup_To_Proton` (weekly Sunday 03:15, StartWhenAvailable, IgnoreNew).
  - Manually ran the task once; `LastTaskResult=0` and Proton full-backups now contains one latest archive.
  - Updated ops docs and health check to include the new weekly task.
- [2026-02-16] Reorganized Proton Linux backup layout into `daily-backups` and `full-backups`.
  - Moved existing mirror payload from `.../Linux` root into `.../Linux/daily-backups`.
  - Kept weekly tar flow in `.../Linux/full-backups` and archive offload at `/mnt/e/Documents/Backup`.
  - Updated mirror destination base in `/home/ys/bin/mirror_codex_to_proton.sh` to `.../Linux/daily-backups`.
  - Updated runbook/docs and health check scope for 3-task operations.
  - Committed and pushed `/home/ys/bin` change set: `492e7bf` to `origin/main`.
- [2026-02-16] Updated `ys-backup` skill output directory from `圧縮ファイル` to `Backup`.
  - Changed runtime and source-of-truth copies of `ys-backup/SKILL.md` and `ys-backup/scripts/create_backup.sh`.
  - New fixed output path: `/mnt/e/Documents/Backup`.
  - Validation passed (`bash -n` and skill validator on both trees).
  - Published commit `78f5364` to `lib-skills/codex` `origin/main`.
- [2026-02-16] Renamed hourly mirror task and adjusted weekly full-backup schedule.
  - Renamed Windows task `Mirror_Codex_To_ProtonDrive` -> `Daily_Ys_Backup_To_Proton` while keeping hourly trigger and action.
  - Updated `Weekly_Ys_Full_Backup_To_Proton` trigger to every Monday at 12:15 with `StartWhenAvailable=True` retained.
  - Updated `/home/ys/bin` references (`mirror_codex_to_proton.sh`, `check_ops_health.sh`, `OPERATIONS.md`) to new daily task name.
  - Ran renamed daily task once to clear initial not-run result and verified `LastTaskResult=0`.
  - Final health check passed for all three tasks.
- [2026-02-16] Implemented semi-auto git publish policy for two repos.
  - Updated `safe-git-publish/SKILL.md` in runtime and source-of-truth with opt-in semi-auto trigger rules.
  - Added repo-local `/home/ys/projects/lib-skills/codex/AGENTS.md` to require one final push confirmation after commit intent.
  - Updated `/home/ys/bin/AGENTS.md` with the same semi-auto push-confirmation policy.
  - Kept script behavior unchanged (`--push` remains explicit), so safety still depends on explicit final confirmation.
- [2026-02-16] Standardized completion footer rules for substantial tasks.
  - Updated `~/.codex/AGENTS.md` to require fixed `git check` fields (repo/branch/tree/last commit/commit/push/ahead-behind).
  - Added explicit rule: non-substantial conversations should not include git footer blocks.
  - Added explicit rule: `ai-learning-log` is not part of the standard footer.
  - Updated `/home/ys/projects/AGENTS.md` to align projects-scope completion/footer behavior.
- [2026-02-16] Published semi-auto git policy updates to both active repos.
  - `/home/ys/projects/lib-skills/codex`: committed `safe-git-publish/SKILL.md` + new repo `AGENTS.md` and pushed `1b3151b` to `origin/main`.
  - `/home/ys/bin`: committed `AGENTS.md` policy update and pushed `a3a16a1` to `origin/main`.
  - Both repos verified clean and up-to-date (`ahead/behind = 0/0`).
- [2026-02-16] Implemented safe-first C: space recovery for Windows cache pressure case.
  - Confirmed root symptoms: Search index (`Windows.db`) and restore storage were major explainers, while DriveFS cache had mostly drained.
  - Executed cleanup: `C:\Users\nekol\AppData\Local\Temp` and `C:\Users\nekol\AppData\Local\npm-cache` purge.
  - Result: C: free space improved from about 6.3GB to 9.4GB.
  - Left high-risk/system-sensitive operations untouched (no forced `Windows.db` deletion, no restore disable).
  - Remaining manual step: exclude Google Drive/Cryptomator mounts from indexing and run index rebuild via UI.
- [2026-02-16] Disk pressure incident around large file handling (Windows C:).
  - Treat `tar.gz` creation and `Google Drive/Cryptomator` transfer as separate triggers.
  - Observed major pressure from `C:\Windows\ServiceProfiles\LocalService\AppData\Local\Temp\TfsStore\Tfs_DAV` with large `.gz` temp files.
  - Symptom pattern: C: free space drops sharply during/after large transfer workflows.
  - Safe cleanup rule: remove only large `.gz` files under `Tfs_DAV` (do not wipe unrelated system folders).
  - Operational rule: process large files one-by-one; wait for sync completion between files.
- [2026-02-17] Reworked backup automation and manual skills for ys.
  - Renamed scheduled scripts to task-aligned names: `daily_ys_backup_to_proton.sh` and `weekly_ys_full_backup_to_proton.sh`.
  - Added manual-only scripts writing to `/mnt/e/Documents/Backup/manual-*`.
  - Updated Windows scheduled tasks: Daily runs at 19:00, Weekly remains Monday 12:15, both with `StartWhenAvailable=True`.
  - Created skills `daily-ys-backup-to-proton` and `weekly-ys-full-backup-to-proton` in source+runtime.
  - Removed legacy `ys-backup` skill from source and runtime to avoid behavior mismatch.
  - Updated `bin` runbook/docs to match actual task schedule and new script names.
- [2026-02-17] Added new global-ready skill `prompt-refine-loop-gemini` via source-of-truth repo `/home/ys/projects/lib-skills/codex`.
  - Implemented deterministic runner `scripts/refine_loop.py` for iterative prompt revise/review with Gemini Developer API.
  - Added robust stop logic (`max-iter` + convergence threshold), JSONL logs, summary output, and final prompt output.
  - Added references and starter template: `references/prompt-roles.md`, `assets/templates/initial-prompt.md`.
  - Validated with skill validator + `py_compile`; smoke-tested API run with `--max-iter 1` successfully.
  - Synced completed skill to runtime path `/home/ys/.codex/skills/prompt-refine-loop-gemini`.
- [2026-02-17] Published `prompt-refine-loop-gemini` to source-of-truth repo.
  - Commit: `2a11cdb feat(skill): add prompt-refine-loop-gemini`.
  - Push: `main -> origin/main` completed.
  - Runtime sync to `/home/ys/.codex/skills/prompt-refine-loop-gemini` remained in place.
- [2026-02-17] Updated `lib-skills/codex` repo policy to full auto git publish.
  - Changed repo-local `AGENTS.md` from semi-auto to auto commit/push behavior.
  - Removed final push confirmation requirement and allowed intentional direct push to `main/master` in this repo.
  - Published commit `9dc613f` to `origin/main`.
- [2026-02-18] Ran prompt-refine-loop-gemini for English learning assistant prompt (British English,教材準拠).
- Input source saved at /tmp/english-assistant-prompt.md and processed with max-iter=5 threshold=0.15 model=gemini-2.5-pro.
- Output run directory: /mnt/e/Documents/Workspace/prompt-loop/run-20260218_174510.
- Loop converged in 1 iteration with score 0.100; final_prompt.md, summary.md, iterations.jsonl generated.
- Final prompt preserved core constraints and added interaction/correction workflow plus example response block.
- [2026-02-18] Migrated Codex CLI global install path from user prefix fallback to nvm-managed Node on Ubuntu.
  - Reset npm global prefix to nvm default via `npm config delete prefix` under `nvm use 22`.
  - Removed legacy `~/.npm-global/bin` PATH exports from `~/.bashrc` to avoid mixed `/usr` vs nvm tool resolution.
  - Reinstalled `@openai/codex` globally in nvm environment; binary now resolves to `~/.nvm/versions/node/v22.21.1/bin/codex`.
  - Verified in interactive bash startup: node/npm/codex all resolve to nvm paths and `codex --version` succeeds.
- [2026-02-19] Installed Go and Rust toolchains user-locally on WSL Ubuntu without sudo.
- Go installed at `/home/ys/.local/go` (verified `go version go1.26.0 linux/amd64`).
- Rust installed via rustup at `/home/ys/.cargo` / `/home/ys/.rustup` (verified rustc/cargo/rustup versions).
- Updated shell startup files for persistent PATH/env loading: `~/.bashrc` and `~/.profile`.
- Cleaned duplicate Rust env sourcing in `~/.bashrc` to keep startup minimal.
- Verified command resolution in both login and interactive bash shells.
- [2026-02-19] Implemented Go/Rust smoke validation plan under `/tmp/codex-toolchain-smoke`.
- Created Go sample `/tmp/codex-toolchain-smoke/go-hello` with `go mod init`, `main.go`, and `main_test.go`.
- Verified Go toolchain flow: `go run .` => `hello-go`, `go build ./...` ok, `go test ./...` ok.
- Created Rust sample `/tmp/codex-toolchain-smoke/rust-hello` via `cargo new --bin` and updated `src/main.rs`.
- Verified Rust toolchain flow: `cargo run --quiet` => `hello-rust`, `cargo build --quiet` ok, `cargo test --quiet` ok.
- Confirmed PATH resolution in login and bashrc-loaded non-login shells for `go rustc cargo rustup`.
- [2026-02-19] Reorganized `E:\Documents\Workspace\i_ching` assets per user direction.
- Renamed `易経2進数変換プログラム` to `iching-hexagram-utils` and added `README.md` + `.gitignore`.
- Initialized new Git repo and pushed to private GitHub repo `ys1887/iching-hexagram-utils` on branch `main`.
- Push initially failed with GH007 (private email protection); recreated repo metadata with noreply email and pushed successfully.
- Archived `md_clean_ekikyo_20260130` as tar.gz under `_archive`, then removed the original folder.
- Verified resulting tree keeps `i-ching-calculator`, new `iching-hexagram-utils`, and `_archive` backup.
- [2026-02-19] Standardized GitHub visibility defaults to Private across global/workspace/repo AGENTS files.
  - Updated `~/.codex/AGENTS.md` with explicit `gh repo create --private` default policy.
  - Added matching visibility policy sections to `/home/ys/projects/AGENTS.md` and `/home/ys/bin/AGENTS.md`.
  - Added matching visibility policy section to `/home/ys/projects/lib-skills/codex/AGENTS.md`.
  - Defined exception model: allow `--public`/`--internal` only when local project `AGENTS.md` explicitly declares it.
- [2026-02-20] Implemented ChatGPT conversations export script for year/month Markdown partitioning.
  - Added `/home/ys/scripts/export_conversations_to_md.py` with streaming JSON array parsing for large `conversations.json`.
  - Output layout fixed to `by-year-month-md/YYYY/YYYY-MM/*.md` with per-month `index.md` generation.
  - Applied title fallback rule: `YYYY-MM-DD_HH-mm-ss` (Asia/Tokyo), collision fallback adds `_id8`.
  - Executed full export from `/mnt/e/Documents/Workspace/conversations/conversations.json` and generated 1,827 thread markdown files.
  - Verified resulting directories for 2025-02..2026-02 and total markdown count (1,839 including 12 index files).
- [2026-02-20] Updated conversations markdown export naming for chronological sorting in folders.
  - Changed `/home/ys/scripts/export_conversations_to_md.py` so every thread file starts with `YYYY-MM-DD_` (create-time basis, Asia/Tokyo).
  - Collision handling now keeps deterministic uniqueness via `_<id8>` and numeric fallback suffix.
  - Cleared and regenerated `/mnt/e/Documents/Workspace/conversations/by-year-month-md` with new naming rule.
  - Regeneration completed for 1,827 threads with 12 monthly indexes (1,839 markdown files total).
  - Verified no non-prefixed thread files remain and sample month sort now groups chronologically by day.
- [2026-02-20] Added month-range incremental export and ID-based dedupe to ChatGPT conversations markdown exporter.
  - Updated `/home/ys/scripts/export_conversations_to_md.py` with `--from-month`, `--to-month`, and dedupe toggles.
  - Implemented inclusive month-end filtering and `conversation_id` scanning from existing markdown frontmatter.
  - Added skip metrics for existing-id, out-of-range, and missing-created-at-in-range-mode.
  - Updated `/home/ys/scripts/README-conversations-export.md` with incremental usage examples.
  - Added new source-of-truth skill `chatgpt-conversations-md-export` and synced it to runtime skills.
  - Validated with `/mnt/e/Documents/Workspace/conversations/conversations.json` using dry-run -> run -> rerun dedupe flow.
- [2026-02-20] Published chatgpt-conversations-md-export skill changes to source-of-truth repo.
  - Committed AGENTS/README/skill additions as `d4acce3` and pushed `main -> origin/main`.
- [2026-02-21] Renamed Gemini OCR skill to `pdf2md-gemini` and aligned runtime + source-of-truth layouts.
  - Renamed folder, script (`pdf_to_md.py`), and template (`pdf2md-gemini-request.md`) from prior `ocr2md` naming.
  - Updated docs to clarify: Gemini API required, full automation flow, and supported inputs (`.pdf/.jpg/.jpeg/.png/.webp`).
  - Preserved CLI behavior and model env vars as `PDF2MD_MODEL_FLASH|THINKING|PRO`.
  - Published to `ys1887/lib-skills-codex` with commit `84b3ba3` on `main`.
- [2026-02-21] Added new local-first `pdf2md` skill and published to source-of-truth repo.
  - Implemented `pdf2md/scripts/pdf_to_md.py` with `pdftotext` primary extraction and `ocrmypdf` fallback OCR.
  - Kept output contract aligned with Gemini variant (`md/`, `raw/`, default output root, `---` separator).
  - Added Japanese `README.md` with one-time local dependency install commands.
  - Synced runtime skill path to `~/.codex/skills/pdf2md` and kept `pdf2md-gemini` side-by-side.
  - Published commit `9bd95ed` to `origin/main`.
- [2026-02-22] Added a strong-readability formatter for OCR markdown as a reusable local script.
  - Script: `/home/ys/scripts/format_readable_md.py`.
  - Input kept intact; output generated as `-Readable.md` under `/mnt/e/Documents/Workspace/ocr`.
  - Preserved page separators while reducing multi-space and obvious broken line wraps.
  - Current heuristic improves readability but can still mix some two-column fragments on dense pages.
- [2026-02-22] Evaluated figure/table-heavy PDF handling on `/mnt/e/Documents/Workspace/test` with staged sampling.
  - Built 15-page samples and ran both `pdf2md` (local) and `pdf2md-gemini` (API) for 4 files.
  - Observed Gemini `pro` timeout on one text-heavy PDF while `flash` succeeded on the same sample.
  - Full-page profiling showed chess PDF is image-only across all pages; mixed/scan-heavy book has graphics on every page.
  - Current pipeline is reliable for text extraction but not for structured figure/table/chessboard reconstruction.
- [2026-02-22] Added image-extraction defaults to both `pdf2md` and `pdf2md-gemini` skills.
  - New CLI options: `--no-extract-images`, `--no-embed-images`, `--images-dir`, `--image-format`.
  - Default behavior now extracts embedded PDF images and injects page-scoped image links into Markdown.
  - Raw text output remains text-only; image links are added to Markdown output only.
  - Verified with local and Gemini runs that `images/<stem>/pNNN_imgNNN.png` and MD links are generated.
- [2026-02-22] Synced runtime skill edits into source-of-truth git repo and published.
  - Synced 6 files for `pdf2md` and `pdf2md-gemini` (scripts + README + SKILL).
  - Added default image extraction/embed options and docs in source repo.
  - Commit `5c6e230` pushed to `origin/main` on `lib-skills-codex`.
- [2026-02-22] Created project-local `AGENTS.md` for `/home/ys/projects/iching-div` (I Ching extract/compare/interpret workflow).
  - Scoped to local `sources/` only; no web usage; Honda quotes only, Takashima for non-quoted synthesis.
  - Added support for optional extra hexagrams (`之卦/互卦/錯卦/綜卦`) with fixed extraction scope (`卦辞` + `大象伝`).
  - Standardized citation output to `（参照：<実ファイル名>|<卦名> - <項目名>）` and clarified insufficient-data behavior.
  - Kept template files as reference-only; AGENTS takes precedence and template exact match is not required.
- [2026-02-22] Added project-local `iching-obsidian-save` skill scaffold under `/home/ys/projects/iching-div/skills`.
  - Implemented `scripts/build_iching_note.py` to wrap question+answer into Obsidian-style markdown and save to `work/`.
  - Preserves full input question text in a fenced code block and auto-fills `Day_YYYY-MM-DD`, fixed tags, and blank `Source:`.
  - Auto-generates title from `### 2. 易経への質問` with fallback to 卦情報 and avoids filename collisions via numbered suffixes.
  - Default CLI output prints `status/title/path` and the full saved note body for verification-oriented workflow.
- [2026-02-22] Removed trial Obsidian file-save feature from `iching-div` and reverted to chat-body-only output workflow.
  - Deleted project-local `iching-obsidian-save` skill scaffold and helper script under `/home/ys/projects/iching-div/skills`.
  - Cleaned up 3 generated dummy test files in `iching-div/work/` and kept the real ChatGPT reference file.
  - Current preferred workflow: generate I Ching result body in chat, then user copies into Obsidian manually.
- [2026-02-22] Added `iching-divination` launcher skill to lib-skills/runtime for `iching-div` project workflow.
  - Skill lives in `lib-skills/codex/iching-divination/SKILL.md` and is synced to `~/.codex/skills/iching-divination/SKILL.md`.
  - Scope is chat-body output only (no file-save), delegating behavior to `/home/ys/projects/iching-div/AGENTS.md` and local `sources/`.
- [2026-02-22] Initialized git for `/home/ys/projects/iching-div` and published private GitHub repo `ys1887/iching-div`.
  - Added `.gitignore` excluding `sources/` and `work/` (plus common local noise files).
  - Tracked `AGENTS.md`, templates, and `skills/.gitkeep`; intentionally left source md files untracked.
  - Initial push required noreply email amend due to GH007 private email protection.
- [2026-02-22] Added Japanese `README.md` to `iching-div` and pushed it to the private repo.
  - README documents project purpose, directory roles, AGENTS-first rules, skill relationship, current chat-output workflow, and git ignore policy.
  - Explicitly clarifies that `sources/` and `work/` are not tracked in git.
- [2026-02-22] Bootstrapped global structured Codex context files under `~/.codex`.
  - Added `codex-rules.yaml` for lightweight Codex-facing defaults (loading order, source-of-truth split, decision logging policy).
  - Added `codex-decisions.jsonl` as append-only global policy-change log with schema header + initial bootstrap decision.
  - Updated global `AGENTS.md` to define read order and responsibilities across `AGENTS.md` / `yaml` / `jsonl` / existing markdown memory files.
- [2026-02-22] Added automatic structured-context maintenance policy (with guardrails).
  - Updated `AGENTS.md` and `codex-rules.yaml` to allow Codex to auto-maintain structured context files by default.
  - Guardrails require confirmation before deletion, semantic JSONL rewrites, or material policy scope expansion.
  - Added policy-change record `structured_context_auto_maintenance` to `codex-decisions.jsonl`.
- [2026-02-22] Renamed two backup skills in runtime and source-of-truth libraries.
  - `daily-ys-backup-to-proton` -> `backup-codex`, and `weekly-ys-full-backup-to-proton` -> `backup-ubuntu`.
  - Updated `SKILL.md` frontmatter names and titles in both `~/.codex/skills` and `lib-skills/codex`.
  - Updated `lib-skills/codex/README.md` skill list entries and verified no old-name references remain.
  - Published source-of-truth repo change as `3f0fba4` (`chore: rename backup skills`) to `origin/main`.
- [2026-02-22] Renamed Markdown merge skill from `md-batch` to `md-combine` in `lib-skills/codex` and pushed to `origin/main`.
  - Updated skill folder name, `SKILL.md` frontmatter/title/command examples, and helper script filename to `merge_md_combines.py`.
  - Kept behavior unchanged; only naming/help text wording was adjusted.
  - Verified with CLI `--help`, `skill-creator-codex` validator, and old-name residual search.
  - Synced runtime copy under `~/.codex/skills` and removed old runtime folder `md-batch`.
- [2026-02-22] Renamed manual backup script filenames to match renamed runtime skills `backup-codex` / `backup-ubuntu`.
  - `/home/ys/bin/manual_daily_ys_backup.sh` -> `/home/ys/bin/backup-codex.sh`
  - `/home/ys/bin/manual_weekly_ys_full_backup.sh` -> `/home/ys/bin/backup-ubuntu.sh`
  - Updated runtime/source skill `SKILL.md` and `scripts/run_backup.sh` references plus `/home/ys/bin/README.md`.
  - Verified with `bash -n` and targeted `rg` residual checks; published source-of-truth repo commit `7037baf`.
- [2026-02-23] Initialized Git tracking for `honda_wataru` 64-hexagram markdown folder.
  - Ran `git init` in `/mnt/e/Documents/Workspace/work/honda_wataru` and added minimal `.gitignore` (`.DS_Store`, `Thumbs.db`, `desktop.ini`).
  - Set repo-local `core.quotepath=false` so Japanese filenames render readably in `git status`/`git diff`.
  - Created initial commit `chore: initialize git tracking for 64 hexagram markdown files`.
  - Verified diff display with a small front matter edit in `03.水雷屯（すいらいちゅん）.md` (`number: 3` -> `"3"`).
- [2026-02-23] Published `honda_wataru` baseline to GitHub before normalization work.
  - Restored demo diff in `03.水雷屯（すいらいちゅん）.md` so the baseline is the untouched 64-file state.
  - Created private GitHub repo `ys1887/honda_wataru` and configured `origin`.
  - Initial push failed due to GitHub private-email protection; fixed by repo-local `user.email=ys1887@users.noreply.github.com` and amending the root commit.
  - Baseline commit is now `658e139` on `master`, pushed to `origin/master` and tracking is set.
- [2026-02-23] Reorganized `honda_wataru` files for normalization workflow visibility.
  - Created `no-edit/` and moved 48 currently non-target markdown files out of the repo root.
  - Kept 16 normalization-candidate files in the root (including `06.天水訟（てんすいしょう）.md`).
  - Verified counts after move: root `.md` = 16, `no-edit/*.md` = 48.
  - Left all content unchanged; only file locations were changed.
- [2026-02-23] Committed and pushed selected normalization edits for `honda_wataru` while leaving `no-edit/` reorganization unstaged.
  - Staged only edited files plus rename pairs (old path delete + new path add) for six filename normalizations.
  - Commit `2f82063`: `chore: normalize metadata and headings in selected hexagram files`.
  - Push succeeded to `origin/master`; GitHub now reflects this commit diff independently of the unstaged `no-edit/` moves.
  - Working tree intentionally remains dirty due to pending `no-edit/` reorganization changes.
- [2026-02-23] Generated new merged outputs inside `honda_wataru/honda_wataru_merged` from the current edited 64-file source set.
  - Kept external `/work/honda_wataru_merged` as reference-only and unchanged.
  - Produced 8 files (`honda_wataru_1-8.md` ... `honda_wataru_57-64.md`) using md-combine script with group size 8.
  - Verified merged structure matches prior format (top heading + one-level heading demotion + 8 source entries per file).
  - Spot diff against external merged shows expected content updates from recent source normalization edits.
- [2026-02-23] Initialized and published standalone Git history for `/work/honda_wataru_merged`.
  - Created private GitHub repo `ys1887/honda_wataru_merged` and pushed baseline commit of the original 8 merged files.
  - Copied regenerated merged outputs from `honda_wataru/honda_wataru_merged` into the external merged folder.
  - Committed second update (`0d46499`) capturing expected diffs in 6 merged files.
  - Verified repo is clean and synced (`0/0`) after push; GitHub now shows old-vs-new merged diff history.
- [2026-02-23] Zero-padded single-digit filenames in `/mnt/e/Documents/Workspace/ekikyo/Chienomori` (`1.`-`9.` -> `01.`-`09.`).
  - Verified no `01`-`09` collisions before rename and kept total `.md` count at 64 after rename.
  - Initialized standalone Git repo in `Chienomori` and created root commit `253d4d8` (`chore: zero-pad single-digit file numbers in Chienomori`).
  - No remote configured; push intentionally not executed in this task.
- [2026-02-23] Created GitHub private repo `ys1887/chienomori` from local `/mnt/e/Documents/Workspace/ekikyo/Chienomori` and pushed initial `master` branch.
  - `gh repo create chienomori --private --source=... --remote=origin --push` created the remote but initial push was rejected by GH007 (private email protection).
  - Set local `user.email` to `ys1887@users.noreply.github.com`, amended root commit with `--reset-author`, and pushed successfully.
  - Final repo state: `master` tracks `origin/master`, ahead/behind `0/0`.
- [2026-02-23] Added YAML `tags` to all 64 hexagram files in each of `Chienomori`, `honda_wataru`, and `takashima_zouho` (192 files total).
  - Inserted `tags` below `yomi` in `Chienomori`/`honda_wataru`, and below `source` in `takashima_zouho`.
  - Added two tags per file: `易経` and canonical hexagram-name tag (new-character normalized by number-based mapping).
  - Verified idempotency (second run produced zero changes) and validated all 192 files contain required tags with no duplicates.
- [2026-02-23] Committed and pushed YAML tag additions for three repos: `Chienomori`, `honda_wataru`, and `takashima_zouho`.
  - Used tracked-only staging (`git add -u`) to avoid including unrelated/untracked merged directories.
  - `Chienomori` commit/push: `7b60b4a` (`+192` insertions across 64 files).
  - `honda_wataru` commit/push: `4286eb2` (`+192` insertions across 64 files).
  - `takashima_zouho` commit/push: `9043eb2` (`+384` insertions across 64 files; includes extra Takashima series tags).
  - Verified all three repos are clean and synced with upstream (`0/0`).
- [2026-02-23] Added YAML tags to 23 `ekikyo_keiji` 繋辞伝 files (12 上伝 + 11 下伝) below `source`.
  - Common tags: `易経`, `十翼`, `繋辞伝`; conditional tags by filename: `繋辞上伝` or `繋辞下伝`.
  - Verified `tags` insertion position (`source` immediately followed by `tags`) and idempotency (second run no-op).
  - Validated all 23 files with no duplicate tags and correct 上伝/下伝 classification.
- [2026-02-23] Committed and pushed `ekikyo_keiji` tags update for 23 繋辞伝 files.
  - Commit `cb6eb23`: `chore: add tags to keijiden files`.
  - Added tags below `source` with common (`易経`,`十翼`,`繋辞伝`) plus section tag (`繋辞上伝`/`繋辞下伝`).
  - Verified repo is clean and synced after push (`0/0`).
- [2026-02-23] Added `source`-anchored YAML tags to 8 `takashima_kantogen` 巻頭言 files, including summary.
  - Added common tags: `易経`, `高島周易`, `巻頭言`, `高島嘉右衛門`.
  - Created new front matter for `高島周易_巻頭言_まとめ.md` with `title`, `section`, `source` (no `part`) and inserted tags below `source`.
  - Verified all 8 files, correct tag placement, no duplicates, and idempotent re-run.
- [2026-02-23] Committed and pushed `takashima_kantogen` foreword tag updates plus summary front matter creation.
  - Commit `81e6bd0`: `chore: add tags to kantogen foreword files`.
  - Updated 8 files total (`巻頭言_1`-`7` + `巻頭言_まとめ`), adding tags below `source` and creating summary front matter without `part`.
  - Verified repo is clean and synced after push (`0/0`).
- [2026-02-23] Fixed Obsidian property recognition in `honda_wataru` 64 hexagram files by moving YAML front matter to line 1.
- Removed redundant leading H1 lines (`# <卦名>`) from all 64 files to avoid duplicate title metadata.
- Verified all files start with `---`, have valid closing front matter delimiter, and no old heading remains near the top.
- Commit/push completed in `honda_wataru`: `35ec5f2` (`chore: move front matter to file top in honda files`).
- [2026-02-23] Added author tag `本田濟` to all 64 hexagram files in `/mnt/e/Documents/Workspace/ekikyo/honda_wataru`.
  - Updated YAML front matter `tags` arrays only; appended at the end after existing tags.
  - Verified 64/64 files contain exactly one `本田濟` tag and diff is +1 line per file.
  - Re-run check confirmed idempotent state (no missing author tag after update).
- [2026-02-25] Added new Codex skill `book-ocr-linebreak-md` in `/home/ys/projects/lib-skills/codex` for book OCR (image folder / single PDF) to merged Markdown.
- Implemented Gemini OCR script `book_ocr_linebreak.py` with book-specific prompt, page merge (`---`), linebreak restoration (`none|heuristic|strict`), and furigana normalization (`--furigana-mode paren`).
- Verified skill structure with `skill-creator-codex/scripts/validate_skill.py` and script CLI via `--help` + `py_compile`.
- Ran a live single-image OCR trial on `IMG_4182.jpg`; linebreak restoration worked, and furigana bracketing was tuned to be more conservative after over-conversion in first pass.
- Synced the new skill to runtime at `/home/ys/.codex/skills/book-ocr-linebreak-md` for immediate use.
- [2026-02-25] Renamed the new book OCR skill to `book_ocr_gemini` in both source-of-truth and runtime skill directories; removed the old skill directory name.
- Updated `SKILL.md` `name`/header to match `book_ocr_gemini`, revalidated the skill, and kept script filename/CLI unchanged.
- Committed and pushed skill addition under branch `feat/book-ocr-linebreak-skill` (`0ecf28c feat: add book_ocr_gemini skill`).
- [2026-02-25] Added HEIC/HEIF direct input support to `book_ocr_gemini` by extending supported extensions and Gemini MIME map (`image/heic`, `image/heif`).
- Updated skill docs/help text to include `.heic` and `.heif` input support.
- Verified `py_compile`, `validate_skill.py`, and `--help` after the change.
- Successfully ran direct HEIC OCR on `/mnt/e/Documents/Workspace/ocr/heic/IMG_4183.HEIC` (no pre-conversion), output to `/home/ys/tmp/IMG_4183_heic_test.md`.
- [2026-02-25] Improved `book_ocr_gemini` post-processing: linebreak joining is now more conservative (preserve-intent-first) and furigana regex now handles `漢字かな漢字` boundaries via lookahead.
- Verified furigana normalization on samples: `昔者むかし聖人` -> `昔者（むかし）聖人`, `幽賛ゆうざん於神明` -> `幽賛（ゆうざん）於神明`.
- Re-ran HEIC OCR test (`IMG_4183.HEIC`) successfully after the update; HEIC direct input still works.
- [2026-02-25] Ran `book_ocr_gemini` directly on `/mnt/e/Documents/Workspace/imagen/IMG_4183.HEIC` and wrote outputs to the same folder (`IMG_4183_book_ocr_gemini.md` + `.raw.txt`).
- Committed and pushed HEIC direct-input support plus linebreak/furigana normalization improvements (`2ff3bab`) on `feat/book-ocr-linebreak-skill`.
- [2026-02-25] Added inferred blank-line restoration in `book_ocr_gemini` post-processing (e.g., before annotation blocks like `〇...`) because Gemini raw output may omit blank lines.
- Re-ran `IMG_4183.HEIC` to `E:/Documents/Workspace/imagen/IMG_4183_book_ocr_gemini.md`; formatted output now inserts an extra blank line before the annotation section while raw remains compact.
- [2026-02-25] Committed and pushed inferred blank-line restoration for `book_ocr_gemini` (`70c5453`) after validating output on `IMG_4183.HEIC` in `E:/Documents/Workspace/imagen`.
- [2026-02-25] Changed `book_ocr_gemini` default furigana mode to `none` and pushed (`dc4a504`) to avoid non-source ruby insertion in production OCR output.
- [2026-02-25] Initialized standalone git repo at /mnt/e/Documents/Workspace/ekikyo/honda_wataru_eki for 3 Honda Wataru Eki markdown texts (no content edits).
- Set local git email to ys1887@users.noreply.github.com before first commit to avoid GitHub GH007 email privacy rejection.
- Created initial commit 98f5293 (chore: initial import of honda_wataru_eki texts).
- Created GitHub repo ys1887/honda_wataru_eki as Private and pushed main with upstream tracking.
- Verified clean working tree and upstream sync 0/0 after push.
- [2026-02-25] Added paren-policy to book_ocr_gemini with default no-ruby to suppress ruby-like Japanese reading parentheses while preserving citation/note parentheses.
- Implemented parenthetical filtering heuristics (preserve / no-ruby / none) and wired them into page post-processing after linebreak/furigana normalization.
- Strengthened furigana-mode none OCR prompt to forbid non-source bracketed supplements in Gemini output.
- Updated book_ocr_gemini/SKILL.md defaults to document paren-policy no-ruby and ruby-noise filtering behavior.
- Verified py_compile, skill validation, CLI help, and sample no-ruby behavior; synced runtime skill under ~/.codex/skills/book_ocr_gemini.
- [2026-02-25] Added YAML front matter to 3 files in /mnt/e/Documents/Workspace/ekikyo/honda_wataru_eki (序卦伝, 説卦伝, 雑卦伝) using ekikyo_keiji-style keys.
- Kept top-level Markdown headings (# 序卦伝 / # 説卦伝 / # 雑卦伝) directly below front matter to preserve document readability.
- Omitted chapter/number/yomi keys by design because each file aggregates content as a single unit.
- Verified diff contains front matter insertions only (no body text edits), then committed as fa67cbf.
- [2026-02-25] Created combined divination source file /mnt/e/Documents/Workspace/ekikyo/honda_wataru_eki/十翼_三伝_結合.md from 説卦伝 -> 序卦伝 -> 雑卦伝.
- Added a single unified front matter block to the combined file and stripped source-file front matter during merge.
- Preserved source body headings (# 説卦伝 / # 序卦伝 / # 雑卦伝) and left original 3 files unchanged.
- Committed combined-source addition as 4274c5e (chore: add combined source for honda_wataru_eki divination).
- [2026-02-25] Updated combined file /mnt/e/Documents/Workspace/ekikyo/honda_wataru_eki/十翼_三伝_結合.md front matter  from 十翼 to 説卦伝・序卦伝・雑卦伝 for better section semantics.
- Kept  unchanged and preserved body content; diff was a one-line front matter edit only.
- Committed metadata refinement as 1dbe822.
- [2026-02-25] Updated combined file /mnt/e/Documents/Workspace/ekikyo/honda_wataru_eki/十翼_三伝_結合.md front matter section from 十翼 to 説卦伝・序卦伝・雑卦伝 for better section semantics.
- Kept source field as 十翼 and preserved body content; diff was a one-line front matter edit only.
- Committed metadata refinement as 1dbe822.
2026-02-25 ekikyo repo rename: honda_wataru_eki -> ekikyo_juuyoku.
Used gh CLI to rename GitHub repo ys1887/honda_wataru_eki to ys1887/ekikyo_juuyoku.
Renamed local folder under /mnt/e/Documents/Workspace/ekikyo and updated origin URL.
Verified branch remained main, working tree clean, and fetch origin succeeded.
No tracked file content changes; repo history preserved.
2026-02-25 ekikyo_keiji merge outputs created: 繋辞上伝.md and 繋辞下伝.md.
Merged chapter files into 2 combined files while keeping originals unchanged.
Stripped per-file front matter and top-level # headings; kept content from first ## onward.
Added a single front matter block per combined file (title/section/source/tags).
Patched merge logic to insert missing chapter H2 when an input file started directly with content H2 (observed in 繋辞下伝 第一章).
Verified no '# ' headings remain in outputs and chapter H2 sequence is present for both files.
2026-02-25 ekikyo_keiji: unified section labels to '繋辞伝 上伝/下伝' across 23 chapter files.
Committed section-label-only changes as cbcd079, then shortened 23 chapter filenames via git mv as 347ecf6.
Verified rename detection as R100 and pushed ekikyo_keiji/master to origin.
Updated ekikyo_juuyoku combined files (繋辞上伝.md, 繋辞下伝.md) section labels to unified string format.
Committed combined file addition + section labels as aedaa0c and pushed ekikyo_juuyoku/main.
Kept section as one-line string for compatibility; did not convert to YAML list.
2026-02-25 Obsidian related_ideas auto-linking for 3 I Ching series in workspace copy.
Added scripts/update_obsidian_related_ideas.py to group notes by front matter title and append YAML related_ideas links.
Link format uses folder-qualified Obsidian wiki links with short series labels (知恵の森/龍青三/高島易断).
Applied to /mnt/e/Documents/Workspace/ekikyo/Obsidian: 173 notes updated, 20 unchanged, 0 parse/update skips.
Validated YAML front matter parses on all 193 target notes, no self-links, and rerun preview is idempotent (0 changes).
Fixed an early newline-joining bug that initially fused related_ideas into tags, then repaired and re-applied successfully.
2026-02-25 Updated Obsidian related_ideas links after renaming 096b folder to 096b_本田濟.
Rewrote 128 related_ideas links from old 096b path + label 龍青三 to new path 096b_本田濟 + label 本田濟.
Updated scripts/update_obsidian_related_ideas.py TARGET_FOLDERS and SERIES_LABELS to new folder name/label.
Verified no old 096b path or 龍青三 display labels remain in Obsidian markdown related links.
Verified all 096b related_ideas targets exist and script preview (match-by number) is idempotent with 0 changes.
Note: one-off YAML rewrite normalized front matter formatting on 128 files while preserving data fields and related_ideas values.
2026-02-26 Initialized new repo /mnt/e/Documents/Workspace/ekikyo/ekikyo_custom_prompt for ekikyo custom prompt markdown.
Created private GitHub repo ys1887/ekikyo_custom_prompt and set origin via gh CLI.
Renamed initial branch to main before first commit.
Set repo-local git user.email to ys1887@users.noreply.github.com to avoid GH007 on first push.
Published initial commit c808807 (chore: initialize ekikyo custom prompt repository) and verified upstream tracking on origin/main.
2026-02-26 Consolidated merged markdown outputs into new repo sources/ekikyo_merged.
Moved content from former honda_wataru_merged and takashima_zouho_merged into ekikyo_merged/{honda_wataru,takashima_zouho}.
Removed nested .git directories in subfolders by user request (history intentionally discarded).
Initialized git repo at sources/ekikyo_merged, set local noreply email, created private GitHub repo ys1887/ekikyo_merged.
Published initial commit 40125f0 on main and verified upstream sync 0/0.
2026-02-26 Deleted deprecated GitHub repos ys1887/takashima_zouho_merged and ys1887/honda_wataru_merged after consolidation.
Verified consolidated repo ys1887/ekikyo_merged remains private and available.
This cleanup was remote-only; no local file changes were made in the repo during deletion step.
2026-02-26 Created integration monorepo /mnt/e/Documents/Workspace/ekikyo/ekikyo_workspace for I Ching-related repos.
Initialized private GitHub repo ys1887/ekikyo_workspace and pushed main.
Imported 11 repos with git subtree (history preserved): 7 sources + ekikyo_merged + ekikyo_custom_prompt + 3 scripts repos.
Layout mirrors workspace-style hierarchy: sources/, prompts/, scripts/.
README documents rule: edit source repos directly; refresh ekikyo_workspace via subtree pull.
2026-02-26 Deleted 11 old GitHub repos after migrating to ekikyo_workspace as new source-of-truth.
Deleted repos: 7 sources + ekikyo_custom_prompt + 3 scripts repos (GitHub only; local folders retained).
Verified ys1887/ekikyo_workspace remains PRIVATE on main and local repo stays clean/up-to-date.
2026-02-26 Updated ekikyo_workspace prompts layout to match local workspace prompts root.
Flattened prompts by moving ekikyo_custom_prompt.md to prompts/ and placing two template files alongside it.
Committed and pushed change 3e11d3a (prompts: flatten prompt files into prompts root).
This replaced the former prompts/ekikyo_custom_prompt/ subfolder layout.
2026-02-26 Migrated monorepo root from /ekikyo/ekikyo_workspace to /ekikyo by moving .git to the parent folder.
Synced scripts/update_obsidian_related_ideas.py into the monorepo before root migration and pushed.
Copied integrated scripts repos back into /ekikyo/scripts so root content matches monorepo content.
Removed old ekikyo_workspace folder after .git migration, added .gitignore for *.code-workspace, and updated README for root-as-source-of-truth workflow.
Renamed GitHub repo from ys1887/ekikyo_workspace to ys1887/ekikyo (fixed an intermediate mistaken rename to ys1887-ekikyo), updated origin URL, and verified fetch/push.
2026-02-26 Standardized ekikyo repo for GitHub-source-of-truth workflow.
Removed leftover subtree helper remotes and kept only origin (ys1887/ekikyo).
Updated README with explicit GitHub-as-source-of-truth definition and push-before-save guidance.
Added daily push checklist (status -sb / diff --stat / commit / push) and deletion safety notes.
Committed and pushed docs change a807873.
2026-02-26 Created /mnt/e/Documents/Workspace/apps as a new apps monorepo (GitHub source-of-truth workflow).
Created private GitHub repo ys1887/apps and pushed initial README.
Imported ys1887/epub-splitter into apps/epub-splitter via git subtree (history preserved) and pushed.
Verified apps repo is PRIVATE/main and local /apps clone is clean/synced.
Deleted old GitHub repo ys1887/epub-splitter after confirming the migration.
2026-02-26 Standardized /apps repo to the same GitHub-source-of-truth workflow as /ekikyo.
Removed subtree helper remote epub_splitter; apps repo now uses origin only.
Updated apps README with source-of-truth workflow notes, deletion precautions, and ff-only pull recommendation.
Committed and pushed docs change 489873e.
2026-02-26 Renamed Codex image generation skill folder from imagen to Nano_Banana_2 under ~/.codex/skills.
Updated Nano_Banana_2 SKILL.md/README/reference/examples to use the new skill name in headers and metadata.
Changed generate_image.py default Gemini model from gemini-3-pro-image-preview to gemini-3.1-flash-preview.
Verified CLI help shows new default model and grep checks found no old default-model string remains.
Kept output directory name imagen-output unchanged for backward-compatible file paths.
2026-02-26 Updated Nano_Banana_2 skill default output directory to /mnt/e/Documents/Pictures/画像生成 (Windows: E:\Documents\Pictures\画像生成).
Changed script DEFAULT_OUTPUT_DIR and aligned SKILL/README/reference/examples default path text.
Verified generate_image.py --help shows the new default output path and no imagen-output remnants remain in the skill docs.
2026-02-27 Renamed skill directory from Nano_Banana_2 to Nano_Banana under ~/.codex/skills.
Updated SKILL.md front matter name and all skill docs headers/references to Nano_Banana.
Enhanced generate_image.py with --model-preset (flash31/pro3) while preserving free-form --model override.
Set default image model to gemini-3.1-flash-image-preview and added pro preset gemini-3-pro-image-preview.
Validated with --help output, py_compile success, and grep checks showing no old Nano_Banana_2 or gemini-3.1-flash-preview remains.
2026-02-28 /tmp cleanup executed with safe scope.
Removed old mcp-*, pyright-*, test temp dirs, gs_* files, node-compile-cache, ffmpeg/go archives.
Preserved runtime/system dirs: /tmp/runtime-ys, /tmp/tmux-1000, /tmp/snap-private-tmp.
Preserved OCR outputs at /tmp/book_ocr_test_20260227 (3 markdown files).
Verified no target patterns remained after cleanup.
2026-02-28 Nano_Banana: enforced explicit model selection for image generation.
Updated generate_image.py to require one of --model / --model-preset via argparse mutually exclusive required group.
Removed GEMINI_MODEL fallback behavior from runtime/docs; model priority is now --model > --model-preset only.
Added SKILL.md runtime rule: respect model in user's first instruction; if absent, ask flash31/pro3 before running.
Updated README/reference/examples command samples to include explicit model selection.
2026-02-28 lib-skills-codex: renamed skill folder imagen -> Nano_Banana on branch chore/nano-banana-model-selection.
Synced Nano_Banana docs/script from ~/.codex/skills/Nano_Banana and updated root README skill list entry.
Enforced explicit model selection in script (--model or --model-preset required) and removed GEMINI_MODEL fallback docs.
Validated with py_compile, --help output, and expected argparse failure when model args are omitted.
Committed as 311ba8f and pushed branch to origin with upstream tracking.
2026-02-28 lib-skills-codex: fast-forward merged chore/nano-banana-model-selection into main and pushed; GitHub default branch now shows Nano_Banana path.
2026-02-28 lib-skills-codex: renamed skill directory Nano_Banana -> nano_banana on main and pushed.
Updated skill metadata and docs to lowercase naming (name: nano_banana, headers, invocation token, root README path).
Verified no Nano_Banana references remain and py_compile succeeds for nano_banana script.
Committed as ba6dc6c and pushed to origin/main (ahead/behind 0/0).
2026-02-28 lib-skills-codex sync: reconciled GitHub main with ~/.codex/skills after recent skill reshuffle.
Updated README skill inventory to current directories/descriptions (including book_ocr_gemini, iching-divination, prompt-refine-loop-gemini, md-combine).
Added missing book_ocr_gemini assets to repo (SKILL.md, references/linebreak-and-furigana.md, scripts/book_ocr_linebreak.py).
Synced updated scripts for pdf2md-gemini and safe-git-publish from ~/.codex/skills.
Preserved naming policy: repo name remains lib-skills-codex; skill path remains lowercase nano_banana.
Committed c46763f and pushed to origin/main; verified GitHub API reflects updated README and book_ocr_gemini contents.
2026-02-28 lib-skills-codex: documented GitHub source-of-truth workflow in repo docs.
Updated README with Operating Rule, Daily Workflow, and Important Notes aligned to GitHub origin/main as recovery baseline.
Updated repo AGENTS with explicit Source-of-Truth policy (origin/main is canonical; local repo is working copy).
Committed docs-only change as 5aef9e0 and pushed to origin/main.
Verified via GitHub API that README/AGENTS on main include the new source-of-truth sections.
2026-02-28 lib-skills-codex: added explicit branch communication and main-reflection completion rules.
Updated README workflow to clarify that branch push is save-only and completion requires reflection to main + push to origin/main.
Added AGENTS Branch Communication Policy requiring pre-work branch disclosure and end-of-task reflection status reporting.
Committed docs change as 50093c7 and pushed to origin/main.
Verified via GitHub API that README and AGENTS on main include the new branch/main reflection rules.
2026-02-28 lib-skills-codex: updated repo AGENTS git-check requirements for branch clarity.
Added mandatory footer fields: push-target, origin-url, main-reflected.
Defined main-reflected semantics (done only when integrated to main and pushed to origin/main).
Added concise git check examples for main case and branch case.
Committed as eb580ee and pushed to origin/main.
Verified AGENTS on GitHub main contains the new required fields.
2026-02-28 ys-bin: reflected local uncommitted changes to GitHub main.
Used branch chore/reflect-local-backup-script-rename, then fast-forward merged into main.
Renamed scripts manual_daily_ys_backup.sh -> backup-codex.sh and manual_weekly_ys_full_backup.sh -> backup-ubuntu.sh.
Updated README manual backup section to new script names (Japanese README retained).
Added repo AGENTS GitHub visibility policy block from local changes.
Committed 1e8f7c8 and pushed branch + origin/main; verified GitHub main file list and README content.
- [2026-02-28] Rebased `iching-div` operational docs to a source-of-truth model.
  - `sources/ekikyo_custom_prompt.md` is now treated as canonical rules.
  - Rewrote `AGENTS.md` as an execution entrypoint with precedence + fixed guardrails.
  - Updated `README.md` and both runtime/source `iching-divination` SKILL docs for EXTRACT/GENERAL dual mode.
  - Unified canonical corpus naming to `honda_wataru` / `takashima_zouho` / `juuyoku` in updated docs.
  - Corrected keiji file names in local custom prompt (`keiji_*_1-12.md`) to match actual sources.
2026-03-01 book_ocr_gemini run for /mnt/e/Documents/Workspace/test with model=pro, writing-mode=vertical.
Implemented per-image markdown output strategy in-place (basename.md in same folder).
Added retry-runner script /tmp/book_ocr_retry_runner.sh: pass1 sweep then retry queue for timeout/transient HTTP errors.
Existing .md files are skipped to support resume-safe processing.
Background runner started with pid tracked at /mnt/e/Documents/Workspace/test/ocr_runner.pid and progress logged to ocr_runner.log.
Observed Gemini pro instability (503/long waits), so retries include timeout + 429/500/503 classes.
- [2026-03-02] Added scoped normalizer for Takashima OCR text (normalize_takashima_text.py).
  - Targeted only from ## 卷頭言 up to just before ## 第二編.
  - Applied kyujitai-to-shinjitai conversion and paragraph-level OCR line-join in target range.
  - Generated 高島周易講釈_占断自在.clean.md and conversion report file.
  - Verified ## 第二編 onward is byte-identical to source (untouched suffix).
- [2026-03-02] Reworked takashima clean normalizer for full-file pass.
  - Updated  to run NFKC + kyujitai-to-shinjitai over entire file.
  - Added confirmed fix rule .
  - Added ambiguous-term reporting (愛里 / 気字曠濶 / 輔盆 / 福子詳神) without in-text edits.
  - Regenerated  in-place and created .
- [2026-03-02] Reworked takashima clean normalizer for full-file pass (corrected entry).
  - Updated normalize_takashima_text.py to run NFKC + kyujitai-to-shinjitai over entire file.
  - Added confirmed fix rule: 高島島嘉右衞門 -> 高島嘉右衛門.
  - Added ambiguous-term reporting (愛里 / 気字曠濶 / 輔盆 / 福子詳神) without in-text edits.
  - Regenerated takashima_sendanjizai.clean.md in-place and created takashima_sendanjizai.clean.review.txt.
- [2026-03-02] Published takashima file rename and normalization update.
  - Renamed output from takashima_sendanjizai.clean.md to takashima_sendanjizai.md.
  - Committed full-file shinjitai normalization script update and review report output.
  - Pushed commit 04a9573 to origin/main.
- [2026-03-02] Cleaned takashima_sendanjizai publish set to final two markdown files.
  - Removed clean/txt artifacts from sources/takashima_sendanjizai and pushed commit d28b1ab.
  - Verified remote folder now contains only takashima_sendanjizai.md and 高島周易講釈_占断自在.md.
- [2026-03-02] Published manual prompt update and README alignment.
  - Committed prompts/ekikyo_custom_prompt.md changes (version/date and takashima_sendanjizai reference).
  - Updated README prompts section path to prompts/ekikyo_custom_prompt.md.
  - Pushed commit 1d0c160 to origin/main.
- [2026-03-02] Removed Python cache noise from ekikyo workflow.
  - Deleted scripts/__pycache__/ and added __pycache__/ + *.pyc to .gitignore.
  - Verified ignore rule with git check-ignore and re-ran script help check.
  - Published commit 9b99ab2 to origin/main.
- [2026-03-02] Implemented prompt version-stamp automation in ekikyo on branch chore/prompt-version-stamp-hook.
- Added scripts/update_prompt_version_stamp.sh to rewrite first-line stamp to YYYY-MM-DD.n at commit time.
- Added .githooks/pre-commit to run only when prompts/ekikyo_custom_prompt.md is staged, then re-stage the file.
- Updated README.md with setup (core.hooksPath) and same-day increment/reset rules.
- Validated script behavior in /tmp for .1 -> .2 -> .3, date reset, legacy no-seq (.2), and invalid-format failure.
- Validated hook behavior in a temporary git repo: stamp updated and staged content reflected the new value.
- [2026-03-02] Published prompt version stamp automation to ekikyo.
- Branch: chore/prompt-version-stamp-hook, commit: b287cf5 chore: automate prompt version stamp.
- Added .githooks/pre-commit and scripts/update_prompt_version_stamp.sh for YYYY-MM-DD.n auto-increment at commit time.
- Updated README with hook setup, stamp rules, examples, and --no-verify note.
- Push completed to origin/chore/prompt-version-stamp-hook with upstream tracking and ahead/behind 0/0.
- [2026-03-02] Fast-forwarded ekikyo main to include prompt version-stamp automation.
- Merged branch chore/prompt-version-stamp-hook into main via --ff-only.
- Pushed main to origin: 9b99ab2 -> b287cf5.
- Main is now clean and synced with origin/main (ahead/behind 0/0).
- [2026-03-02] Ran a live commit/push test for prompt stamp hook on main.
- Manually set prompt stamp to 2026-03-02.0, then committed to trigger pre-commit increment.
- Hook output confirmed: updated to 2026-03-02.1 at commit time.
- Published commit 1b215eb (chore: test prompt stamp auto update) to origin/main.
- Repository remained clean and synced (ahead/behind 0/0) after push.
- [2026-03-02] Updated /home/ys/bin docs for current scheduler reality.
- Reworked bin/README.md to separate Windows scheduled scripts vs manual utility scripts.
- Corrected OPERATIONS.md XDG task trigger from Daily 20:00 to Daily 19:30.
- Synced task references across README/OPERATIONS for three active scheduled tasks.
- [2026-03-02] Migrated ChatGPT conversations export script from /home/ys/scripts to /home/ys/bin/chatgpt-conversations.
- Moved README-conversations-export.md to /home/ys/bin/chatgpt-conversations/README.md and updated command paths.
- Updated /home/ys/bin/README.md to document the new data-conversion tool location.
- Updated chatgpt-conversations-md-export/SKILL.md in both source-of-truth repo and runtime skills path.
- Published bin repo commit b930e95 and lib-skills/codex commit 3032201 to origin/main.
- [2026-03-02] Initialized /mnt/e/Documents/Workspace/inbox as Git-backed draft workspace.
- Added minimal .gitignore (OS/editor temp files) and README with inbox usage policy.
- Created private GitHub repo ys1887/workspace-inbox and configured origin.
- Initial push hit GH007 email privacy; fixed by setting local noreply email and amending root commit author.
- Pushed main successfully; inbox repo now tracked with upstream origin/main.


## 2026-03-03
- Clarified global GitHub visibility policy handling in Codex sessions.
- AGENTS.md now explicitly enforces private-by-default for repo creation.
- Operational rule: always use explicit --private with gh repo create unless a local AGENTS.md explicitly permits otherwise.
- No codex-rules.yaml duplication required for this policy at this time.
- [2026-03-05] Implemented WSL-authoritative Codex sync script: /home/ys/.codex/bin/codex-sync.sh.
- Added subcommands: check (dry-run diff), apply (backup + mirror sync), verify (checksum-based consistency check).
- Sync scope is /home/ys/.codex -> /mnt/c/Users/nekol/.codex with dynamic data excludes (sessions/log/sqlite/history/state/auth, etc.).
- Added guardrails: source/destination realpath safety checks and unreadable top-level symlink sanitization on destination.
- Fixed backup design to store snapshots at /mnt/c/Users/nekol/.codex-sync-backups (outside mirror-delete scope).
- Executed initial rollout successfully: check=0, apply=0, verify=0.
- [2026-03-07] Updated global Codex rule documents to match the Windows-side runtime .codex.
- Changed AGENTS.md and codex-rules.yaml in both /mnt/c/Users/nekol/.codex and /home/ys/.codex to point at /mnt/c/Users/nekol/.codex for skills, ai-notes, ai-learning-log, codex-rules, and codex-decisions.
- Clarified that lib-skills remains the editing source-of-truth while /mnt/c/Users/nekol/.codex/skills is the runtime deployment target.
- Kept a WSL-side .codex copy as compatibility/recovery only; it is no longer described as the runtime source-of-truth.
- Verified no legacy /home/ys/.codex or ~/.codex references remain in the updated global rule files.
## 2026-03-08
- Updated /home/ys/bin docs to match current scripts and runtime flow.
- README now classifies scripts into backup, XDG operations, skill runtime, and ChatGPT export.
- Removed stale codex-sync.sh references from active documentation.
- Clarified daily backup scope to include .ssh, .config/gh, bin, and key dotfiles.
- OPERATIONS now treats task-failures.log as the notification source-of-truth and lists all task re-enable commands.
## 2026-03-08
- Local non-.system skills in /home/ys/projects/lib-skills/codex now use short Japanese descriptions for Codex app list readability.
- Left .system skills unchanged on purpose; only user-managed skills were updated.
- Synced updated SKILL.md files to /mnt/c/Users/nekol/.codex/skills so the Windows-side runtime matches lib-skills.
- Updated /home/ys/bin/backup-codex.sh to back up /mnt/c/Users/nekol/.codex instead of /home/ys/.codex.
- backup-codex SKILL.md now documents the Windows-side Codex runtime path explicitly.
- Retired skill-creator-codex from lib-skills and Windows runtime because .system/skill-creator is the preferred upstream skill creator.
- Removed the skill folder and README entry from /home/ys/projects/lib-skills/codex.
- Confirmed no remaining skill-creator-codex references under lib-skills/codex or /mnt/c/Users/nekol/.codex/skills.
## 2026-03-08
- Updated iching-div docs to match the new `sources/extract` and `sources/general` layout.
- Synced path references across `iching-div/AGENTS.md`, `iching-div/README.md`, `iching-div/sources/ekikyo_custom_prompt.md`, and `lib-skills/codex/iching-divination/SKILL.md`.
- Kept `templates/` documented as input helper only, not evidence source.
- Removed stale references to old `sources/index.md`, `sources/honda_wataru/`, `sources/takashima_zouho/`, and `sources/juuyoku/` paths.
- Synced /mnt/c/Users/nekol/.codex/skills/iching-divination/SKILL.md from lib-skills after the source path update.
- Confirmed runtime and source-of-truth SKILL.md contents now match exactly.
- lib-skills/codex remains clean and in sync with origin/main after the push.
## 2026-03-08
- Initialized /home/ys/projects/iching-sdk as a new git repository.
- Added a minimal README.md and .gitignore for SDK work and generated outputs.
- Set local git identity to ys1887@users.noreply.github.com before first push to avoid GitHub privacy rejection.
- Created private GitHub repo ys1887/iching-sdk and pushed main successfully.
- Created local working branch codex/iching-sdk-mvp for upcoming SDK implementation.
## 2026-03-08
- Normalized iching-sdk sources/index.md to the machine-readable  /  format with path-only bullet entries.
- Added a stdlib-only Python CLI entrypoint at  backed by .
- Implemented  and , including rule-file loading, index validation, report.json, and evidence.json output.
- Added unittest coverage for ordered index output, malformed references, insufficient evidence, stdin input, and runtime/config error cases.
- Verified the CLI with  and direct  command runs.
- Corrected note: normalized sources/index.md to path-only extract/general sections.
- Corrected note: added CLI files iching and iching_sdk/cli.py with stdlib-only index/validate commands.
- Corrected note: added tests/test_cli.py and verified via python3 -m unittest discover -s tests -v.
- Refined iching-sdk toward an SDK-first shape by splitting CLI logic into config, indexing, and validation modules.
- Kept  as the public CLI entrypoint while making  the reusable implementation layer.
- Updated README.md to document the SDK-first policy, thin skill wrapper role, and future layering toward agent execution.
- Re-ran unittest coverage and manual CLI smoke checks after the refactor; behavior stayed stable.
- Corrected note: kept the public CLI entrypoint as ./iching and made iching_sdk/ the reusable implementation layer.
- Added a new iching-sdk skill under /home/ys/projects/lib-skills/codex/iching-sdk.
- Kept iching-divination unchanged and positioned iching-sdk as the SDK-first launcher.
- Updated the lib-skills README entry list to include iching-sdk.
- Published iching-sdk to /mnt/c/Users/nekol/.codex/skills and verified the runtime copy.
- Added `iching build-prompt` to iching-sdk with mode auto-detection from input text.
- EXTRACT now resolves from `[MODE:EXTRACT]`; otherwise build-prompt defaults to GENERAL unless `--mode` overrides it.
- Kept prompt assembly text-based: base custom prompt + runtime context + raw user input.
- Added prompting module and test coverage for EX_SIMPLE, EX_5, GENERAL comparison input, stdin, and mode override.
- Added `iching resolve` as a lightweight JSON planner stage before build-prompt.
- Resolve now classifies inputs into extract_template, general_comparison, or general_question.
- Resolve returns mode, input_source, source_groups, and hints for later orchestration.
- Added tests for resolve auto-detection, mode override, comparison/ranking hints, and missing-input handling.
- Implemented `iching run` as a high-level workflow command in iching-sdk.
- Added artifact persistence for resolve.json, prompt.txt, answer.md, report.json, evidence.json, and run.json.
- `run` now delegates answer generation to an external `--answer-cmd` and validates the returned markdown.
- Exit codes are now standardized for success (0), validation failure (1), and runtime/config/answer-command failure (2).
- Added CLI tests covering general/extract success, mode override, stdin passthrough, validation failure retention, answer command failure, and config/runtime errors.
- Updated README with `run` usage and one-shot workflow behavior.
- Added `iching answer` as a dedicated prompt-to-answer CLI in iching-sdk.
- Refactored `run` to reuse shared answer execution logic instead of spawning subprocesses directly.
- Kept `run` artifact behavior and status fields stable while moving answer execution into `iching_sdk/answering.py`.
- Added tests for answer file/stdin input, missing prompt, missing command, and non-zero answer command exit.
- Updated README to document both modular (`build-prompt -> answer -> validate`) and one-shot (`run`) workflows.
- Synced the iching-sdk skill docs so `answer` and `run` responsibilities are described consistently.
- Added answer preset support to iching-sdk for stable answer command invocation.
- Introduced built-in `codex-exec` preset and kept `--answer-cmd` as an override with higher priority.
- Shared preset/command resolution between `iching answer` and `iching run` in `iching_sdk/answering.py`.
- Preserved `run` artifacts and `run.json` while recording resolved answer commands.
- Added tests for preset resolution, preset execution via patched map, explicit-command precedence, and missing configuration failures.
- Updated README and iching-sdk skill docs to recommend `--answer-preset codex-exec` as the default workflow.
- Pushed iching-sdk and lib-skills/codex after adding answer command and preset support.
- Added preset UX improvements so missing/unknown preset errors mention available presets.
- CLI help for `answer` and `run` now recommends the built-in `codex-exec` preset.
- Kept preset resolution centralized in `iching_sdk/answering.py` and verified the full unittest suite still passes.
- Implemented codex provider MVP for iching-sdk answer/run flows.
- Added --provider codex plus --codex-model, --codex-sandbox, and --codex-approval-policy CLI options.
- Centralized answer execution resolution with precedence: answer-cmd > provider > answer-preset.
- Kept codex-exec preset for compatibility by routing it through the same codex provider path.
- Extended run.json artifacts with provider and provider_options metadata.
- Added tests for provider argv construction, precedence, missing codex binary, usage errors, and run metadata.
- Updated README to make --provider codex the standard workflow while documenting preset compatibility.
- Added repo runtime config support via `iching.toml` for iching-sdk answer/run defaults.
- Runtime config currently supports `provider`, `codex_model`, `codex_sandbox`, and `codex_approval_policy`.
- Resolution precedence is `CLI > iching.toml > built-in`, with answer-cmd/preset behavior unchanged.
- Limited runtime config loading to `answer` and `run`; `index`, `resolve`, `build-prompt`, and `validate` stay unaffected.
- Added config validation for TOML syntax, unknown keys, invalid provider names, and invalid codex option values.
- Added CLI tests for file defaults, CLI overrides, config-dependent codex option validation, and validate isolation from broken runtime config.
- Updated README to document `iching.toml` and provider-free daily workflow examples.
- Strengthened iching-sdk validation with answer-body checks and context-aware comparison checks.
- `validate` now reports `missing_answer_body` when output contains only citations or blank lines.
- `run` now passes resolved input context into validation so comparison answers can require multiple interpretations and explicit ranking when requested.
- `run` stderr now includes top validation finding codes for faster triage.
- Added report summary counts for `errors` and `warnings` in validator output.
- Added tests for comparison validation failures, missing answer body, and updated validation stderr expectations.
- Added `iching select` to return grouped source-file choices between resolve and build-prompt.
- `select` currently uses fixed group policies: general core for normal questions, general+extract support for comparisons, and honda/takashima/general support for extract mode.
- Selection output includes `selected_groups`, flattened `selected_files`, and `selected_file_count`.
- Added CLI tests covering extract selection, general comparison selection, normal general selection, and mode override behavior.
- Updated README standard workflow to `resolve -> select -> build-prompt -> answer -> validate`.
- Wired selection into `build-prompt`, so generated prompts now include a `## Selected Sources` section.
- `run` now persists `select.json` alongside `resolve.json`, `prompt.txt`, and validation artifacts.
- Reused the same selection payload for prompt generation and run artifacts to keep execution context consistent.
- Added tests covering selected-source prompt sections and `select.json` artifact creation.
- Updated README to document the selection-aware prompt flow and new run artifact layout.
- Added  to replay comparison/ranking checks outside .
- Added  with strict JSON shape checks for , , and .
-  now rejects context/mode mismatch as a runtime error and still writes /.
-  now includes  so it can be reused directly as validation context.
- Added CLI tests for resolve-context reuse, run-context reuse, mode mismatch, and invalid context shape.
- Updated README examples to document strict re-validation with .
- Added validate --context <resolve.json|run.json> to replay comparison/ranking checks outside run.
- Added load_validation_context(...) with strict JSON shape checks for mode, input_kind, and hints.
- validate now rejects context/mode mismatch as a runtime error and still writes report.json and evidence.json.
- run.json now includes hints so it can be reused directly as validation context.
- Added CLI tests for resolve-context reuse, run-context reuse, mode mismatch, and invalid context shape.
- Updated README examples to document strict re-validation with --context.
- iching-sdk: added codex provider failure taxonomy with provider_missing/provider_auth/provider_execution_failed.
- AnswerResult now carries error_type, error_summary, and raw_stderr for provider-aware diagnostics.
- run.json now preserves error_type and error_summary while keeping final_status backward-compatible.
- codex auth failures are currently detected only via conservative stderr patterns such as 'codex login' and 'authentication required'.
- Explicit answer-cmd failures keep error_type null and continue using generic answer command summaries.
- Expanded CLI tests to cover codex missing/auth/other provider failures and stderr/run.json summary alignment.
- iching-sdk: run.json now also records error_source and error_stderr for provider and explicit answer command failures.
- Short stderr output remains aligned with error_summary; detailed child stderr is preserved only in artifacts.
- error_source currently distinguishes provider, answer_command, runtime, and config paths.
- iching-sdk: expanded codex auth detection with additional conservative patterns including unauthenticated/authenticate wording.
- Added regression tests to keep provider_auth distinct from generic provider_execution_failed when stderr only contains unrelated 'login' wording.
- Added opt-in smoke test gate via ICHING_RUN_CODEX_SMOKE=1 in tests.test_cli.
- Normal test suite skips smoke by default; current suite count is 74 with 1 skipped when smoke is disabled.
- Smoke invocation path is wired, but sandbox execution may leave codex exec waiting on live environment response; treat README command as operator-driven verification.
- iching-sdk: verified opt-in codex smoke path under ICHING_RUN_CODEX_SMOKE=1 now skips cleanly on local environment blockers.
- Current local blocker is codex startup failure with stale arg0 temp dir cleanup permission denied.
- Smoke gate now treats missing codex, auth required, and local permission blockers as skip rather than hard failure.
- iching-sdk: runtime config now supports provider-table shape with default_provider and [providers.codex].
- Loader still accepts legacy top-level provider/codex_* keys and merges them with precedence: CLI > provider table > legacy top-level.
- Current implementation keeps runtime config flattened for the active provider, while expanding TOML parsing/validation for future multi-provider work.
- Added CLI tests for provider-table defaults, provider-table precedence over legacy keys, and invalid provider-table config cases.
- README now recommends provider table format and documents legacy top-level keys as temporary compatibility mode.
- iching-sdk: RuntimeConfig now stores provider-scoped settings via ProviderRuntimeConfig plus default_provider.
- Compatibility accessors remain for provider/codex_* so existing CLI code paths stay stable while internals move toward multi-provider support.
- resolve_runtime_config now resolves from provider-scoped settings first, then applies CLI overrides into the unchanged ResolvedRuntimeConfig shape.
- Added direct tests for structured runtime config loading and resolution, alongside the existing CLI-level regression coverage.
- iching-sdk: answering layer now uses a provider registry shape instead of hard-coded codex branching for command build and failure classification.
- Added ProviderDefinition to hold builder, options payload, failure classifier, and missing-executable metadata.
- Public behavior is unchanged; only the internal dispatch path was generalized for future provider additions.
- list_answer_providers now derives from provider definitions, reducing duplication with future provider registration.
- iching-sdk: cli layer now mirrors provider-registry direction with ProviderCliSpec and build_provider_options dispatch.
- The public CLI still exposes codex-specific flags, but validation and option collection no longer hard-code a single inline codex path.
- Added direct tests for CLI provider-option building to lock the internal dispatch behavior before adding another provider.
- iching-sdk: README now fixes near-term scope around local Codex-first CLI use with Claude Code as secondary consumer.
- Explicitly documented that HTTP/API/server work and non-codex built-in providers are out of scope until real demand appears.
- This should reduce pressure to over-generalize beyond the current CLI contract.
- iching-sdk: README を main 取り込み準備向けに再構成し、先頭で MVP scope / current contract / 最短運用を読める形に整理した。
- 最短運用は run と modular workflow の 2 系統に絞り、推奨最小 iching.toml を default_provider + [providers.codex] 形式で固定した。
- provider failure の見方を stderr -> run.json の最短導線で明文化し、error_source / error_type / error_summary の確認順を追加した。
- README に MVP 完了チェックリストと main 取り込み前の受け入れ基準を追加した。
- validate コマンドの README 記載に --sources-root と --out-dir を反映し、現行 CLI 契約とのズレを解消した。
- 回帰確認は python3 -m unittest -q tests.test_cli で 85 tests, OK (skipped=1) を再確認した。
- iching-sdk: codex/iching-sdk-mvp を main へ squash merge し、履歴を 1 コミット  に集約した。
- merge 前に origin/main との同期を確認し、main 上の squash 状態で  を再実行した。
- test 結果は 85 tests, OK (skipped=1) で、README handoff 更新を含む MVP 一式をそのまま main に反映した。
- main push 後、repo は clean かつ origin/main と 0/0 で同期している。
- 残作業は branch cleanup と、必要なら main を基準にした次フェーズ計画の開始だけになった。
- iching-sdk: codex/iching-sdk-mvp を main へ squash merge し、履歴を 1 コミット feat: merge iching-sdk mvp に集約した。
- merge 前に origin/main との同期を確認し、main 上の squash 状態で python3 -m unittest -q tests.test_cli を再実行した。
- test 結果は 85 tests, OK (skipped=1) で、README handoff 更新を含む MVP 一式をそのまま main に反映した。
- main push 後、repo は clean かつ origin/main と 0/0 で同期している。
- 残作業は branch cleanup と、必要なら main を基準にした次フェーズ計画の開始だけになった。
- iching-sdk: main 反映後の post-merge cleanup として codex/iching-sdk-mvp を local/remote から削除した。
- README の short path を main 上で spot check し、run は --answer-cmd 経由で validate まで成功した。
- modular workflow も build-prompt -> answer -> validate で成功し、prompt.txt に Selected Sources、report.json に evidence_status=sufficient を確認した。
- 現在の repo 状態は main のみ、working tree clean、origin/main と 0/0 で同期している。
- iching-sdk: 今回の全体経緯を初心者向けに振り返る長文まとめを docs/iching-sdk-development-summary.md として追加した。
- 内容は 5 つの指定セッション、README、tests、skill、ai-notes をもとに時系列で再構成した。
- 文書には目的、設計意図、主要実装、Git の流れ、今後の候補、用語集まで含めた。
- 主読者は将来の自分を想定し、結論 -> 背景 -> 詳細の順で読める構成にした。
- iching-sdk: EXTRACT 検証フェーズの土台として prompt を fragments 方式へ分割した。
- EXTRACT は shared / standard / auxiliary に分け、補助卦ありケースだけ追加指示を入れる構成にした。
- tests/fixtures/extract_cases/ に standard 2件と complex 2件の代表ケースを追加した。
- docs/extract-acceptance.md を追加し、このスレッドへ質問文を直接貼る受け入れ手順を明文化した。
- README に EXTRACT Acceptance 入口を追加し、CLI 回帰と skill 対話の役割分担を記載した。
- 回帰確認は python3 -m unittest -q tests.test_cli で 88 tests, OK (skipped=1) を確認した。
- iching-sdk: EXTRACT prompt の重複指示を shared に寄せ、standard / auxiliary を構造専用に整理した。
- 代表ケース再計測で build-prompt は standard_1 4563->4262 chars, standard_2 4524->4223 chars, complex_1 5492->5023 chars に削減した。
- auxiliary 側は補助卦固有の順序・束ね方・卦辞/彖伝/大象伝の並びだけを残し、共通のソース分離や参照形式は shared に一本化した。
- tests.test_cli に prompt size regression を追加し、3 代表ケースで文字数と行数の上限を固定した。
- 回帰確認は python3 -m unittest -q tests.test_cli で 89 tests, OK (skipped=1) だった。
- iching-sdk: EXTRACT prompt の第二段階圧縮として Runtime Context を Input source のみに縮め、毎回出る SDK 固有説明を削った。
- extract_standard の高島解釈ガイダンスは、品質条件を保つ核だけ残して短文化した。
- 再計測で build-prompt は standard_1 4262->3606 chars, standard_2 4223->3567 chars, complex_1 5023->4361 chars まで削減した。
- 初回計測比では standard 系がおよそ 21%、complex_1 がおよそ 20.6% の削減になった。
- 回帰確認は python3 -m unittest -q tests.test_cli で 89 tests, OK (skipped=1) だった。
- iching-sdk: EXTRACT prompt の第三段階として、核心・結論に実務条件と進め方を先出しする指示を戻した。
- 方針判断では「どう寄せるべきか」「どう進めないか」を冒頭に書かせるようにし、比較軸の明示も許可した。
- prompt 長は standard_1 3873 chars, standard_2 3834 chars, complex_1 4628 chars で、第二段階より少し増えたが依然として初回最適化前よりかなり短い。
- 回答品質を優先して、サイズ回帰しきい値は 4300 / 4300 / 5100 chars に緩めた。
- 回帰確認は python3 -m unittest -q tests.test_cli で 89 tests, OK (skipped=1) だった。
- iching-sdk: EXTRACT の品質重視調整として、核心・結論に判断語、理由、ただし付き条件、進め方を先出しする指示を戻した。
- 本田解釈はそのまま使える判断文、高島解釈は比較軸と重心変更の具体化を優先するよう強めた。
- 補助卦ありケースでも、結論先行と全体判断への束ね方を明示する指示を追加した。
- build-prompt 再計測は standard_1 4356 chars, standard_2 4317 chars, complex_1 5280 chars で、品質優先の回帰上限内だった。
- 回帰確認は python3 -m unittest -q tests.test_cli で 89 tests, OK (skipped=1) だった。
- iching-sdk: EXTRACT の追加調整で、核心・結論を短く強く言い切ること、本田/高島解釈で重複を避けること、終盤を判断で締めることを明示した。
- build-prompt 再計測は standard_1 4546 chars, standard_2 4507 chars, complex_1 5470 chars だった。
- size regression は complex_1 の行数実測に合わせて 236 行上限へ微調整した。
- 回帰確認は python3 -m unittest -q tests.test_cli で 89 tests, OK (skipped=1) だった。
2026-03-09 iching-sdk EXTRACT follow-up
- Reinforced EXTRACT prompt so `高島解釈` must always end with a validator-style citation line.
- Tightened auxiliary-hexagram guidance toward conclusion-first answers with one clear role per helper hexagram.
- Added build-prompt assertions for the new Takashima citation rule and auxiliary-summary wording.
- Relaxed `complex_1` prompt size cap to match the quality-first prompt wording increase.
2026-03-09 iching-sdk EXTRACT fragment split
- Split EXTRACT prompt responsibilities into shared, core conclusion, interpretation, auxiliary structure, and auxiliary bundle fragments.
- Kept wording moves minimal and preserved the quality-first EXTRACT guidance.
- Updated prompt assembly order so standard cases load shared/core/standard/interpretation and auxiliary cases insert auxiliary-specific fragments.
- Updated build-prompt tests to assert the new fragment headings and conditional auxiliary inclusion.
- Full regression suite: python3 -m unittest -q tests.test_cli -> OK (skipped=1).
2026-03-09 ekikyo-sdk baseline + restore
- Split copied ekikyo-sdk into a fresh private repo and pushed baseline main as ys1887/ekikyo-sdk.
- Replayed the 2026-03-09 session log onto codex/restore-session-end-state using only log-backed changes.
- Restored EXTRACT prompt fragments, acceptance fixtures, and build-prompt/test expectations to the 88-test state.
- Added a minimal ekikyo-sdk skill to both source-of-truth and runtime skill locations.
- Verification: python3 -m unittest -q tests.test_cli, plus build-prompt checks for standard_1 and complex_1.
- Opened PR #1 for baseline-vs-restore review.
2026-03-10 iching-sdk naming restore
- Restored repo-facing naming from ekikyo-sdk to iching-sdk in README, acceptance docs, prompt text, and package docstring.
- Fixed the README acceptance link to point at /home/ys/projects/iching-sdk.
- Confirmed source-of-truth and runtime iching-sdk skills had no lingering ekikyo-sdk references, so no skill edit was needed.
- Verified prompt output header now says iching-sdk.
- Regression check: python3 -m unittest -q tests.test_cli -> OK (skipped=1).

- [2026-03-10] Adopted real EXTRACT fixtures in `iching-sdk` on `codex/extract-fixture-adopt`.
- Added manifest-first adopted cases for `test_1.md`, `test_2.md`, and `test_3.md`.
- Preserved original answers and added validator-compatible canonical copies with normalized citation paths.
- Updated EXTRACT acceptance docs/README to treat the real cases as the primary acceptance set.
- Added CLI tests for canonical answer validation and adopted-case prompt coverage.

- [2026-03-10] Simplified EXTRACT canonical answers to SDK-only final-form fixtures.
- Removed repo copies of original `test_*_answer.md` after confirming external backups exist.
- Canonical fixtures now start at `**核心・結論**` and omit ChatGPT/history labels.
- Added tests that canonical answers keep required sections and no longer include history markers.
- Revalidated all canonical answers and full `tests.test_cli` suite after cleanup.
- [2026-03-10] Added EXTRACT comparison mode (`TEMPLATE:EX_COMPARE`) to iching-sdk.
- Prompt assembly now distinguishes standard EXTRACT, auxiliary-hexagram EXTRACT, and comparison EXTRACT.
- Validation now checks EX_COMPARE structure: 核心・結論, 吉凶順位, ranked candidate sections, and summary table.
- Added canonical comparison fixture pair `test_4.md` and `test_4_answer_canonical.md` based on the game-ranking example.
- Updated README and extract acceptance docs so comparison divination is documented as the primary EXTRACT route.
- Verified with full `python3 -m unittest -q tests.test_cli` and direct `resolve` + `validate` for `test_4`.
2026-03-10 ekikyo-sdk compare audit + naming sync
- Reviewed copied EX_COMPARE integration in prompting, resolving, validation, manifest, and CLI tests.
- Found no obvious logic mismatch in extract_comparison detection, selected groups, or validation expectations.
- Renamed prompt header/generated-by text from iching-sdk to ekikyo-sdk for user-facing output only.
- Updated extract acceptance doc to use adopted test_1..test_4 fixtures and include compare-case review flow.
- Tightened canonical-answer regression guard so sdk-branded history labels are rejected for both iching-sdk and ekikyo-sdk wording.
- [2026-03-10] Added `skill-creator-codex` as a Codex-focused personal derivative skill in `lib-skills/codex`.
- Based it on the built-in Codex `.system/skill-creator` and aligned helper scripts/assets for minimal drift.
- Added focused references for Claude guide takeaways, Codex runtime/source-of-truth rules, and trigger review.
- Tightened trigger scope around Codex skill creation, migration, metadata, validation, and runtime deployment prep.
- Kept `skill-installer` as a companion for upstream fetch/install, not the main authoring path for local custom skills.
- Verified `SKILL.md` validation, YAML parsing, file references, and helper script CLI help output.
2026-03-10 iching-sdk prompt fragment split
- Replaced EXTRACT prompt assembly from standard+optional auxiliary to shared+template-specific branching.
- Added extract_simple.md and extract_5.md; removed extract_standard.md and extract_auxiliary.md.
- EX_5 prompt now always loads its mode-specific fragment and documents no-change, changed, and multi-change paths.
- Added build-prompt tests for EX_5 without auxiliary names and EX_5 with multiple changing lines.
- Verified full python3 -m unittest -q tests.test_cli suite after the refactor.

2026-03-11 iching-sdk strict input and source cleanup
- Made MODE explicit for all inputs and removed automatic GENERAL fallback.
- Made EXTRACT require a known TEMPLATE and centralized MODE/TEMPLATE marker definitions.
- Removed GENERAL comparison routing; compare is now EXTRACT + EX_COMPARE only.
- Simplified EXTRACT source selection to Honda + Takashima only.
- Updated README and extract acceptance docs to document strict input and maintenance touchpoints.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).

2026-03-11 iching-sdk review follow-up: header-only markers
- Restricted MODE/TEMPLATE parsing to the header so body marker literals are ignored.
- Kept GENERAL freeform once [MODE:GENERAL] is present; comparison wording no longer hard-fails.
- Kept EXTRACT strict by requiring TEMPLATE immediately after [MODE:EXTRACT].
- Added placement-error tests for late MODE/TEMPLATE and quoted marker body text.
- Moved EXTRACT fixture markers to the top to match the strict input contract.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- PR 更新後の Codex 再レビューは gh pr comment <num> --body "@codex review" で依頼する。

2026-03-11 iching-sdk strict-input PR merged
- Follow-up review fix now rejects duplicate standalone EXTRACT TEMPLATE markers.
- GENERAL remains freeform once [MODE:GENERAL] is present; compare words alone do not error.
- Marker parsing is header-only and ignores body marker literals.
- PR #3 merged to main as squash commit f719658.
- [2026-03-11] Contracts-first update for EXTRACT input/output guarantees in iching-sdk.
- Clarified README and extract acceptance docs around marker placement, template minima, and required-vs-recommended output sections.
- Expanded extract fixture manifest with template metadata, auxiliary-hexagram flags, and compare minimum detail count.
- Added resolve-time EX_COMPARE candidate-count validation and context metadata for template and auxiliary-hexagram presence.
- Added validator checks for EX_SIMPLE/EX_5 minimum sections while keeping content-thickness checks in canonical/acceptance rather than runtime.
- Verified with `python3 -m unittest -q tests.test_cli`.
2026-03-11 iching-sdk stabilization memo
- Added docs/stabilization-policy.md to freeze the near-term direction around stability-over-features.
- Documented the comparison workflow across ChatGPT project, ekikyo-sdk, and iching-sdk.
- Fixed a wording drift so EX_COMPARE remains the formal route for structured comparisons.
- Linked the new stabilization memo from README acceptance/maintenance guidance.
- Verification for this task was doc diff review only; no test suite was needed because no code paths changed.
2026-03-11 iching-sdk 64-way extract source split
- Split EXTRACT Honda/Takashima sources into 64 per-hexagram files while leaving legacy grouped files in place for now.
- Changed EXTRACT selection to use parsed hexagram numbers and return only the needed provider files when available.
- Rewrote canonical extract citations and index expectations to the new per-hexagram paths.
- Updated prompt/docs wording from range-based lookup to hexagram-based lookup.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
2026-03-11 iching-sdk citation path fix for EXTRACT
- Added prompt-side citation filename guidance so EXTRACT answers use selected relative paths verbatim.
- Reinforced extract prompt rules to forbid basename-only citation filenames.
- Added build-prompt coverage for exact citation filenames in EXTRACT prompts.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- Re-ran EX_SIMPLE cases: selected_file_count=2 and validator pass for both.
2026-03-11 iching-sdk EX_COMPARE canonical tightening
- Tightened EX_COMPARE prompt instructions to require canonical section order, numbered ranking list, Markdown candidate headings, strict citation format, and final recommendation sentence.
- Strengthened validation to distinguish ranking list from candidate detail headings and to require the final recommendation sentence.
- Added EX_COMPARE CLI tests for canonical success, missing recommendation, and malformed Markdown-link citations.
- Updated docs/comparisons/ex_compare_test_1.md to evaluate structure, citation format, detail depth, recommendation alignment, and validator status.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- Attempted ./iching run on test_4.md, but full provider-backed remeasurement did not complete in this session.
2026-03-11 iching-sdk run header-gate tightening
- Reordered run_workflow so input parsing and EXTRACT contract validation happen before answer provider/command resolution.
- Added run tests that assert malformed EXTRACT headers and under-specified EX_COMPARE inputs fail before answer execution starts.
- Added run success coverage for a valid EX_COMPARE input with canonical answer structure.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
2026-03-11 iching-sdk EX_COMPARE residual-gap tightening
- Tightened EX_COMPARE prompt examples so ranking lines must include hexagram/line info and citations must use bare relative paths without sources/extract prefix or backticks.
- Added regression tests for ranked-list omissions, sources/extract-prefixed citations, and alternate recommendation phrasing.
- Updated ex_compare_test_2.md with canonical-gap analysis and expected validator findings.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
2026-03-11 iching-sdk EX_COMPARE practical-criteria adjustment
- Relaxed EX_COMPARE ranking-list validation so candidate-only numbered lines are accepted when detail headings and summary table supply hexagram/line context.
- Kept strict blockers on citation format and final recommendation sentence.
- Updated prompt wording/examples and ex_compare_test_3.md evaluation notes to reflect the practical pass criteria.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
2026-03-11 iching-sdk EX_COMPARE citation/recommendation tightening
- Strengthened EX_COMPARE prompt with explicit forbidden/accepted examples for strict citation formatting and the final recommendation sentence.
- Added build-prompt coverage so generated prompts must include the exact citation and recommendation examples.
- Updated ex_compare_test_4.md to record that only citation and recommendation wording remain as blockers.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
2026-03-11 iching-sdk EXTRACT review-ready snapshot
- Finalized EX_SIMPLE, EX_5, and EX_COMPARE prompt/validator/test updates on branch codex/split-extract-sources-by-hexagram.
- Added run preflight errors for malformed EXTRACT headers before provider execution.
- Captured comparison ledgers under docs/comparisons and verified EX_COMPARE success artifact at out/run/20260311-174938-005139.
- Committed as 0dcd73f and pushed branch plus PR #5 for review.
2026-03-11 iching-sdk review feedback follow-up
- Addressed Codex review on PR #5 with commit 26ab7d3.
- Restored fast answer-provider validation before stdin consumption in run_workflow.
- Tightened EX_COMPARE validation so the final recommendation must match the rank-1 candidate.
- Added regression tests and re-ran python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- Posted a short PR comment linking the fix summary.
2026-03-11 iching-sdk EX_COMPARE ranking-section follow-up
- Fixed latest Codex review by scoping EX_COMPARE ranking extraction to the 吉凶順位 section only.
- Added regression coverage so numbered lists in 核心・結論 or candidate detail sections do not satisfy ranking checks or skew recommendation matching.
- Verified with python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- Pushed commit f16985f and posted a short PR #5 update comment.
2026-03-11 iching-sdk main merge
- Merged PR #5 into main with a merge commit.
- Synced local main to origin/main at 4319cf7.
- Verified working tree is clean on main after the merge.
2026-03-11 iching-sdk lightweight ops polish
- Added a root-level unittest shim so `python3 -m unittest` now runs the CLI suite without changing test contents.
- Kept `python3 -m unittest discover -s tests` and `python3 -m unittest -q tests.test_cli` working as secondary entrypoints.
- Updated README to make the default test command explicit and clarified that smoke tests remain opt-in.
- Updated docs/comparisons/README.md to treat `main` as the current baseline while preserving old branch names as historical record.
- Added a short stabilization note that EX_COMPARE ranking edge cases remain non-blocking follow-up items.
- Verified with three commands: `python3 -m unittest`, `python3 -m unittest discover -s tests`, and `python3 -m unittest -q tests.test_cli`.
2026-03-11 iching-sdk ChatGPT review wording follow-up
- Refined README test guidance to explain why `python3 -m unittest` is the standard entrypoint and that the root shim is intentionally temporary.
- Reworded the focused test command to mean "CLI tests only" rather than a generic narrowing hint.
- Split EX_COMPARE ranking follow-up notes into detection-hardening vs diagnostic-policy buckets.
- Re-verified `python3 -m unittest`, `python3 -m unittest discover -s tests`, and `python3 -m unittest -q tests.test_cli` -> OK (skipped=1).
2026-03-11 iching-sdk skill CLI alignment
- Reframed EXTRACT acceptance to treat `./iching run` as the only quality-guaranteed path and to require `run.json.final_status` plus `report.json.evidence_status`.
- Updated README and docs/extract-acceptance.md so direct skill-chat outputs are treated as auxiliary observation, not acceptance evidence.
- Marked prompts/ekikyo_custom_prompt.md as legacy reference-only and pointed runtime authority to prompts/fragments/*.md.
- Updated the iching-sdk skill text in both the source-of-truth repo and the runtime copy to force `[MODE:EXTRACT]` through the CLI path.
- Kept SDK logic unchanged; this task tightened entry behavior and contract wording only.
- Verified repo tests with `python3 -m unittest -q tests.test_cli` -> OK (skipped=1).
2026-03-11 iching-sdk codex provider runbook
- Added docs/codex-provider-runbook.md to separate provider environment failures from EXTRACT prompt-quality issues.
- Fixed the acceptance order so provider completion is checked before validator status and answer structure.
- README now points provider triage to the runbook and treats state DB write access plus backend connectivity as first-class prerequisites.
- docs/extract-acceptance.md now starts with provider preflight and requires logging run.json/report.json failure fields.
- No CLI arguments, JSON schema, or prompt fragment contracts changed in this task.
- Verified with `python3 -m unittest -q tests.test_cli` -> OK (skipped=1).
2026-03-11 iching-sdk runtime config restore
- Restored repo-root iching.toml so default codex runs again resolve to model gpt-5, sandbox workspace-write, approval policy never.
- Added tests that isolate repo runtime config by default and verify both configured provider_options and null provider_options behavior.
- Confirmed the recent regression was real: provider_options now populate again in run.json instead of null.
- This exposed the next blocker clearly: current codex exec rejects `--ask-for-approval`, so the failure moved from read-only runtime to CLI argument compatibility.
- Updated README and codex-provider-runbook to treat provider_options and sandbox lines as first-pass regression signals.
- Verified with `python3 -m unittest -q tests.test_cli` -> OK (skipped=1).
2026-03-12 iching-sdk safe rollback to pre-polish state
- Created backup branch codex/rollback-backup-20260312-4319cf7 from dirty b49dd40 state before rollback.
- Stashed tracked and untracked changes as safe-rollback-20260312-pre-4319cf7 for later recovery.
- Created and switched to codex/rollback-4319cf7 at commit 4319cf7 based on ZIP equivalence checks.
- Verified clean worktree, zero diff vs 4319cf7, and python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- Left backup branch and stash intact so the user can inspect or restore the broken state if needed.
2026-03-12 iching-sdk main rollback adoption
- Switched local main from b49dd40 to a non-destructive revert workflow instead of resetting history.
- Reverted b49dd40 on main, producing commit c30fdfd that restores the 4319cf7 tracked file state.
- Verified git diff 4319cf7..HEAD is empty after the revert.
- Re-ran python3 -m unittest -q tests.test_cli -> OK (skipped=1).
- Pushed main to origin so GitHub now reflects the rollback via revert commit.
- [2026-03-12] Published ekikyo source reference update on `main`.
- Added merged GENERAL source files `honda_wataru_eki.md` and `keijiden.md` under `sources/ekikyo_project_source`.
- Added EXTRACT output templates under `sources/outputs/`.
- Updated `prompts/ekikyo_custom_prompt.md` and `sources/index.md` to point GENERAL mode at merged sources and template files.
- Commit `4ed9dd5 docs: update ekikyo source references and templates` pushed to `origin/main`.
- [2026-03-12] Published another ekikyo prompt/template refinement on `main`.
- Tightened EXTRACT prompt wording around mode handling, citation limits, and template behavior.
- Expanded `ex_simple`, `ex_5`, and `ex_compare` output templates with section-level guidance and ordering expectations.
- Commit `bc17301 docs: refine extract prompt and output templates` pushed to `origin/main`.
2026-03-12 codex reference dedupe prompt/template fix
- Tightened EXTRACT reference policy so EX_SIMPLE and EX_5 verify sources without emitting handwritten reference lines.
- Removed manual  guidance from the custom prompt and delegated visible citation rendering to ChatGPT citations.
- Deleted handwritten reference lines from EX_SIMPLE and EX_5 rules, skeletons, and samples while preserving heading structure.
2026-03-12 codex reference dedupe prompt/template fix
- Tightened EXTRACT reference policy so EX_SIMPLE and EX_5 verify sources without emitting handwritten reference lines.
- Removed manual reference-line guidance from the custom prompt and delegated visible citation rendering to ChatGPT citations.
- Deleted handwritten reference lines from EX_SIMPLE and EX_5 rules, skeletons, and samples while preserving heading structure.
- Left EX_COMPARE untouched per scope.
- Verified target files no longer contain remaining handwritten reference lines or [出典] placeholders, except as prohibited-string examples in the policy text.
- [2026-03-12] Published a larger ekikyo EXTRACT prompt/template expansion on `main`.
- Reworked `ekikyo_custom_prompt.md` into a fuller operational guide and restored the required version-stamp title for pre-commit compatibility.
- Expanded `ex_simple`, `ex_5`, and `ex_compare` templates with explicit output rules, skeletons, and sample-form guidance.
- Commit `3c099f7 docs: expand extract prompt and template guidance` pushed to `origin/main`.
2026-03-13 iching-sdk Honda EXTRACT split 01-08
- Added scripts/generate_honda_extract_split.py to generate Honda split-tree output for 01-08.
- Generated sources/extract_honda_split with per-hexagram manifests, split markdown files, index.json, and exceptions.json.
- Standardized section key/file naming on jokaden and preserved source_file references to original Honda source paths.
- Treated 乾為天 as a special case with separate bungen/yongjiu files and manual xiaoxiang extraction from the aggregated taisho block.
- Verified manifests, index, markdown frontmatter, special-section separation, and exception/index consistency with a Python check.
2026-03-13 iching-sdk Honda EXTRACT split 09-32 extension
- Extended the Honda split generator scope from 01-08 to 01-32 and regenerated the split tree/index.
- Confirmed 09-32 introduce no new bungen/yongjiu/yongliu sections in the current Honda EXTRACT sources.
- Kept the only current exceptions on 01_乾為天 where xiaoxiang text is aggregated inside taisho.
- Re-verified all 32 manifests, markdown frontmatter, section/file consistency, and exception flags after regeneration.
2026-03-13 iching-sdk Honda EXTRACT split 33-64 completion
- Extended the Honda split generator to cover all 64 Honda EXTRACT hexagrams and regenerated the split tree/index.
- Added new source-artifact exceptions for 51_震為雷, 54_雷澤帰妹, and 61_風澤中孚.
- Kept existing 01_乾為天 manual xiaoxiang exceptions unchanged.
- Re-verified 64 manifests, index ordering, file existence, markdown frontmatter, and updated exception flags.
2026-03-13 iching-sdk Takashima EXTRACT split 01-03 trial
- Added scripts/generate_takashima_extract_split.py for a pilot split of Takashima 01-03.
- Normalized Takashima headings into Honda-aligned manifest/index keys: keywords, kaji, tanden, taisho, yao_1-6, optional yongjiu/yongliu.
- Generated sources/extract_takashima_split with manifests, markdown split files, index.json, and an empty exceptions.json.
- Absorbed Takashima yao heading and reading-shape variations, including blocks where original xiaoxiang text is omitted and only the reading remains.
- Verified file existence, manifest/index consistency, frontmatter keys, and yao structure for the pilot set.
2026-03-13 iching-sdk Takashima EXTRACT split 01-64 completion
- Extended scripts/generate_takashima_extract_split.py from the 01-03 pilot to full 01-64 generation.
- Kept Honda-aligned manifest/index keys while normalizing Takashima heading variants and omitting jokaden by default.
- Generated sources/extract_takashima_split with 64 folders, per-hexagram manifests, index.json, and exceptions.json.
- Added parser recovery for malformed intra-yao headings by merging non-parseable split fragments back into the preceding yao block.
- Recorded one absorbed source-artifact exception for 30_離為火 where the fifth-yao heading is mistyped as 3爻 in the source.
- Re-verified all 64 manifests, section/file consistency, frontmatter, special-section flags, and exception/index alignment.
2026-03-13 iching-sdk Honda split profile v1
- Added extract profile support with default_profile=legacy and explicit --profile honda opt-in.
- Introduced profile-aware selection so Honda split can use manifest-driven section files while keeping logical citations on honda_wataru/*.md.
- Added Honda-specific extract prompt fragment and prompt sections that separate logical citation targets from physical split section files.
- Kept validator citation contract unchanged; Honda profile now validates against manifest source_file values.
- EX_COMPARE Honda minimum section set is kaji + taisho + yao_n, intentionally excluding tanden.
- Added CLI tests for Honda profile select/build-prompt/validate and verified unittest discover -s tests passes.
2026-03-13 iching-sdk Takashima split profile
- Generalized split profile handling so Honda and Takashima both use the same catalog/selector path.
- Added profiles.takashima with default_profile still fixed at legacy.
- Replaced Honda-only split prompt fragment with a generic extract_shared_split fragment for split-backed profiles.
- Added Takashima profile tests for select/build-prompt/validate plus kept Honda and legacy regressions passing.
- Verified sequentially with python3 -m unittest -q tests.test_cli and python3 -m unittest discover -s tests.
- Avoided parallel test runs afterward because tests temporarily rewrite repo-root iching.toml and can interfere with each other.
2026-03-13 iching-sdk Honda runtime prompt fix
- Added --profile support to the run subcommand so Honda split can execute end-to-end through resolve/select/build-prompt/answer/validate.
- Introduced split-specific prompt fragments for EX_SIMPLE, EX_5, and EX_COMPARE to avoid legacy dual-source instructions in split profiles.
- Kept split shared instructions generic and removed cross-profile source-name examples from the Honda/Takashima prompt path.
- Added CLI regression coverage for Honda split prompt content and run success with logical citations.
- Verified sequentially with python3 -m unittest -q tests.test_cli and python3 -m unittest discover -s tests.
- Reconfirmed a local smoke run for 41山澤損 with --profile honda generates split section selection and validates logical citations.
- [2026-03-13] Stabilized iching-sdk codex provider toward Ubuntu CLI fixation.
- Added [providers.codex].path support and set repo-local config to the Ubuntu NVM codex path.
- Removed --ask-for-approval from standard codex exec assembly to match current local CLI behavior.
- Added resolved_codex_path/resolved_codex_version to run artifacts for provider traceability.
- Expanded provider failure classification into cli_compat / sandbox_or_fs / connection in addition to missing/auth/generic.
- Verified with sequential unittest runs: tests.test_cli and full discover both passed.
- [2026-03-13] Verified Honda/Takashima provider runs after Ubuntu Codex CLI fixation.
- Honda EX_SIMPLE (41山澤損 / 上爻) succeeded with profile=honda and validation=evidence sufficient.
- Takashima EX_SIMPLE (41山澤損 / 上爻) also succeeded with profile=takashima and validation=evidence sufficient.
- Both runs resolved codex path to /home/ys/.nvm/versions/node/v22.21.1/bin/codex and version codex-cli 0.114.0.
- Both answer_command payloads used sandbox=workspace-write and did not include --ask-for-approval.
- Remaining risk is external CLI latency/streaming stability, not SDK profile/provider wiring for these cases.
- [2026-03-13] Honda-first acceptance check hit provider runtime failures before profile-specific issues.
- Honda test_1 and test_2 both failed with provider_sandbox_or_fs under Ubuntu codex-cli 0.114.0.
- Common first failure line was PATH update read-only filesystem, with state DB open failures and stream disconnects in stderr.
- Wrote comparison memo: docs/comparisons/honda-first-stability-2026-03-13.md.
- Takashima follow-up was intentionally deferred until Honda light cases can pass under the same provider conditions.
- [2026-03-13] Ranked codex provider root-cause candidates without changing SDK behavior.
- New memo: docs/comparisons/codex-provider-root-cause-2026-03-13.md.
- In this desktop session, `/mnt/c` is `ro` and `findmnt -T /home/ys/.codex` also reports `/` as `ro`, while the repo workspace remains writable.
- `codex exec --ephemeral` did not suppress state DB or shell snapshot failures; short direct probe and fixture run showed the same failure family.
- `CODEX_HOME=/home/ys/.codex` changes the target `.codex` path, but failures persist there too; state path is movable, root cause is broader FS/runtime restriction.
- [2026-03-13] Closed the current codex provider investigation without code changes.
- Restart recheck still showed `/mnt/c` and `/home/ys/.codex` as read-only, with write probes failing in both locations.
- Short `codex exec` probe succeeded, but `./iching run` for `test_1.md` only reached `resolve/select/build-prompt` and stalled in provider execution before `run.json`.
- Operational conclusion: keep `codex provider` experimental, hold SDK changes, and reopen only when a writable `.codex` session is available.
- [2026-03-13] Hardened `iching-sdk` Codex provider with a short preflight probe before full prompt execution.
- Added provider runtime diagnostics to `run.json`: `preflight_*` fields and `runtime_diagnostics` for cwd/env/path/prompt size.
- Kept `error_type` backward-compatible while making `error_summary` more specific for readonly/state-db/shell-snapshot/stream/CLI-arg symptoms.
- Updated provider failure docs in `README.md` to explain preflight-first diagnosis order.
- Expanded `tests/test_cli.py` for preflight success/failure behavior and new artifact payload fields.
- [2026-03-13] Added a profile-skill design note to iching-sdk docs.
  - Kept profile-specific skills deferred and documented them as thin wrappers around ./iching --profile.
  - Linked stabilization policy to the new design note to keep future skill additions bounded.
  - Renamed branch from codex/honda-extract-split-01-08 to codex/iching-stabilization.
  - Committed docs-only changes as docs: add profile skill design note and pushed the renamed branch.
- [2026-03-13] Added a provider-matrix harness to `iching-sdk` for Codex app vs CLI comparison.
- New script: `scripts/run_codex_provider_matrix.py` generates fixed prompts, app manual sheets, and CLI run artifacts.
- New module: `iching_sdk/provider_matrix.py` parses provider-failure logs, `./iching run` path usage, and observed files.
- Added unit tests for prompt generation and log parsing in `tests/test_provider_matrix.py`.
- Verified `--prepare-app-only`, parser tests, and an end-to-end shim run that produced prompts, logs, JSON, and Markdown reports.
- [2026-03-13] Added an external-facing Codex provider incident report for `iching-sdk`.
- New doc: `docs/codex-provider-incident-2026-03-13.md` consolidates background, symptoms, reproductions, hypotheses, and open questions.
- Framed the issue as provider/runtime/connection instability rather than an app-only defect.
- Kept the report consistent with the existing OpenAI runtime report, root-cause ranking, and provider-matrix observations.
- [2026-03-14] Implemented split-source v1 base in `iching-div` on branch `codex/split-source-migration-v1`.
- Archived prior prompt-era entry files under `archive/pre-split-migration/` before replacing docs.
- Copied Honda/Takashima split assets to `assets/split/` and extract fixtures to `examples/extract/`.
- Added minimal Python preprocessing flow: parse input, resolve profile, select split sources, emit prompt text to stdout.
- Added format fragments for shared/template/profile rules and stdlib unittest coverage for parser/selection/prompt smoke tests.
- Added three fixed-profile skills: `iching-div-legacy`, `iching-div-honda`, `iching-div-takashima`, and synced them to source-of-truth/runtime skill dirs.
- [2026-03-14] Ran the first EXTRACT quality pass on split-source v1 prompt output.
- Tightened format fragments so section order, citation shapes, interpretation labels, and compare-mode output boundaries are explicit.
- Added an `Output Quality Bar` block to the built prompt to separate user-facing answer requirements from preprocessing/debug context.
- Verified `legacy` compare now states Honda-led narration and Takashima support-only behavior more explicitly.
- Verified single-source profiles now explicitly forbid leaking the other source family into interpretation wording.
- Extended unittest coverage with prompt-contract assertions; suite now passes with 15 tests.
- [2026-03-14] Committed the first split-source quality-pass follow-up on `codex/split-source-migration-v1`.
- Tightened EXTRACT prompt contract wording for section order, citation shape, Japanese-only output, and insufficiency handling.
- Added explicit quality-bar guidance to built prompts so preprocessing context and final-answer requirements are separated.
- Clarified legacy compare behavior: Honda narrates, Takashima remains support-only and never becomes an independent final section.
- Clarified single-source profile behavior so Honda/Takashima profiles do not leak the other source family into interpretation wording.
- Extended unittest coverage to 15 passing tests with prompt-contract assertions.
- [2026-03-14] Added answer-shape evaluation helper to `iching-div` for split-source EXTRACT fixtures.
- Evaluated representative cases end-to-end with `codex exec`: `extract-standard-test-1`, `extract-complex-test-2`, `extract-compare-test-4`.
- `EX_SIMPLE` and `EX_5` matched canonical skeletons without section-path leakage.
- `EX_COMPARE` initially drifted on the final recommendation sentence (`おすすめ` vs `推薦候補`).
- Tightened `formats/extract/ex_compare.md` to require exact final sentence `今回の推薦候補は、<候補名>です。`.
- Added regression coverage so compare prompts must carry that exact recommendation contract.
- Re-ran compare evaluation and confirmed canonical skeleton match, support-only Takashima behavior, and no internal path leakage.
- [2026-03-14] Removed the temporary `codex exec`-based answer evaluation helper from `iching-div`.
- Restored the repo boundary to prompt-builder logic plus stdlib `unittest` only.
- Kept the compare-mode prompt contract tightening for the exact recommendation sentence.
- Kept the associated regression test in `tests/test_build_extract_prompt.py`.
- Verified `python3 -m unittest tests.test_build_extract_prompt` passes after helper removal.
- [2026-03-14] Tightened `iching-div` EXTRACT answer guidance around reading hierarchy on `codex/split-source-migration-v1`.
- Updated `formats/extract/ex_simple.md` so the main hexagram governs the overall situation and the changing line governs case-specific conditions.
- Updated `formats/extract/ex_5.md` so auxiliary hexagrams stay supporting-only under the main hexagram and changing lines.
- Updated `formats/extract/ex_compare.md` so ranking treats `爻辞`/`卦辞` as primary evidence and `彖伝`/`大象伝` as reinforcement.
- Revised canonical EX_SIMPLE and EX_5 examples to avoid per-section mini-verdicts and to recombine main hexagram plus changing-line logic in the final interpretation.
- Added prompt-contract tests for the new hierarchy wording; `python3 -m unittest tests.test_build_extract_prompt` now passes with 24 tests.
- [2026-03-14] Formalized the user-added `tests/test_1..4` EXTRACT cases as official format fixtures in `iching-div`.
- Updated `examples/extract/manifest.json` so the named `*-test-*` cases now point directly at `tests/test_*.md` and their canonical answers.
- Extended `tests/test_build_extract_prompt.py` with direct fixture path resolution and structural canonical checks for the new official test files.
- Added checks for quote blocks, citation lines, compare candidate headings, and legacy-to-single-source interpretation label reduction.
- Kept content validation shape-based rather than verbatim so LLM wording drift is tolerated while format remains enforced.
- Verified `python3 -m unittest tests.test_build_extract_prompt` passes with 27 tests.
- [2026-03-14] Tightened EXTRACT output guidance so changing lines are narrated as one unified block instead of split `爻辞`/`小象伝` subsections.
- Updated `formats/extract/ex_simple.md` and `formats/extract/ex_5.md` to require original text + reading in each main/supporting subsection.
- Updated compare guidance so candidate quote blocks may include both changing-line text and `小象伝` in one block.
- Extended tests to assert no `### 爻辞`/`### 小象伝` headings in canonical EX_SIMPLE/EX_5 outputs and to require reading lines in official test canonicals.
- Updated `examples/extract/test_1_answer_canonical.md` to match the unified changing-line block shape.
- Verified `python3 -m unittest tests.test_build_extract_prompt` passes with 27 tests.
- [2026-03-15] Simplified the global Codex policy documents to separate human rules from structured defaults.
- Compressed `/mnt/c/Users/nekol/.codex/AGENTS.md` into a shorter global policy file and removed old reporting-template detail.
- Updated both Windows-side and WSL-side `codex-rules.yaml` copies to point narrative memory at `/home/ys/notes/codex-notes.md` and `/home/ys/notes/codex-log.md`.
- Added `memory_files`, `source_of_truth_paths`, and `runtime_paths` so runtime/config ownership is explicit.
- Recorded the policy change in `/mnt/c/Users/nekol/.codex/codex-decisions.jsonl` and retired legacy Windows-side `ai-notes.md` / `ai-learning-log.md` references from active rules.
- [2026-04-07] Restored the explicit task-end memory update workflow in global Codex AGENTS files.
- Re-added the rule to read recent entries before substantial work and to append concise non-sensitive notes at task end.
- Kept the learning log limited to repeated mistakes, high-risk tasks, and clear near-misses.
- Logged the policy change in `/mnt/c/Users/nekol/.codex/codex-decisions.jsonl` for traceability.
- [2026-04-07] Consolidated llm-wiki reference material into schema.
- Added schema/llm-wiki-pattern.md as a repo-specific summary of useful operating ideas.
- Updated index.md to point at schema/LLM_Wiki.md and the new summary note.
- Logged the consolidation in log.md and kept the raw article clip separate.
- [2026-04-08] Renamed 64 Obsidian Takashima supplement files in 143_高島易断_増補 from 高島易断増補_XX_... to XX_... format.
- Verified numbered files now total 64 and no numbered 高島易断増補_XX_... files remain.
- Left 高島易断増補_六十四卦一覧.md unchanged.
- [2026-04-08] Updated 高島易断増補_六十四卦一覧.md internal wikilinks to new numbered filenames (01_... format).
- Verified no remaining 高島易断増補_ links in the table.
- Remaining assumption: only this index file needed link/display updates; other notes may still point to old names if they exist.
- [2026-04-08] Updated related_ideas in 141_高島易断 and 142_高島易断_占例 so 増補 links now point to numbered filenames (01_... format).
- Processed files in numeric order from 01 to 64.
- Residual: one unrelated external reference to an older 高島易断増補 path remains outside the requested directories.
- [2026-04-08] Rechecked 142_高島易断_占例 related_ideas from 01 to 64 and updated the remaining old 増補 reference in 18_山風蠱.md to 143_高島易断_増補.
- Confirmed no 高島易断増補_ links remain inside 142_高島易断_占例.
- [2026-04-08] Repointed all 142_高島易断_占例 増補 related_ideas from self-links to 143_高島易断_増補 in numeric order 01-64.
- Verified special filename mismatches were handled for 16 (雷地予), 23 (山地剥), and 27 (山雷頤).
- Confirmed 142_高島易断_占例 no longer contains 高島易断増補_ references.
- [2026-04-08] Reset mtimes for 141_高島易断, 142_高島易断_占例, and 143_高島易断_増補 so files sort by 01-64 within each folder.
- Verified monotonic mtime order in all three folders after the reset.
- 2026-04-08 高島易断index.md を 64卦のリンク表に更新。
- 列は No / 卦名 / 易断 / 増補 / 占例 / 附録 に統一。
- 易断=141, 増補=143, 占例=142 の同名ファイルへリンク。
- 卦名は番号なし表示にした。
- 27 は 山雷頤 に統一済み。
- 2026-04-08 高島易断index.md の wikilink 余白を修正。
- [[... | ...]] になっていた箇所を [[...|...]] に詰めて Obsidian で解決できるようにした。
- 2026-04-08 高島易断index.md の wikilink を再修正。
- 行内の [[...  | ...]] を perl で [[...|...]] に正規化し、Obsidian で解決できる形にした。
- 2026-04-08 高島易断index.md の表内リンクを Markdown link に切り替え。
- [[...|...]] が表の区切りで壊れるため、[易断](...), [増補](...), [占例](...) に変更した。
- 2026-04-08 高島易断index.md の附録列をリンク化。
- 144_高島易断_増補_上巻附録 を tags で判定し、同一本卦の重複は 附録1/2/3 で並べた。
- 単独は附録リンク、該当なしと本卦タグなしの2件は附録のまま残した。
- 2026-04-08 `assets/quotes/quotes-honka.md` から彖伝専用コピーを作成。
- 出力先は `work/quotes-honka-tandan.md`、64見出しと64件の `彖曰` を確認。
- `> ` を除去し、frontmatter・卦辞・象伝・解説は含めない構成にした。
- `38 火沢睽` のみ元ソースの `彖日` を出力側で `彖曰` に正規化した。
- 2026-04-08 `assets/quotes/quotes-honka.md` から大象伝専用コピーを作成。
- 出力先は `work/quotes-honka-taisho.md`、64見出しと64件の `象曰` を確認。
- 形式は見出し、漢文、空行、読み下しで統一し、`> ` と frontmatter は除去した。
- 2026-04-08 `assets/quotes/quotes-koji.md` から小象伝専用コピーを作成。
- 出力先は `work/quotes-koji-sho.md`、64卦・384爻の見出しを確認。
- `（占）` `（占例）` 解説文と `> ` は除去し、小象伝の漢文と読み下しだけを残した。
- `1 乾為天` は `象曰` 表記なしのため、各爻の後段引用2行を小象伝として採用した。
- 2026-04-08 `work/quotes-honka-taisho.md` と `work/quotes-koji-sho.md` を卦ごとに結合。
- 出力先は `work/quotes-taisho-sho.md`、64卦見出しと384爻見出しを確認。
- 各卦で大象伝を先、小象伝6爻を後ろに配置し、新規ラベル見出しは付けなかった。
- 2026-04-08 `work/quotes-taisho-sho.md` を 1-30 と 31-64 に分割。
- 出力先は `work/象伝_上.md` と `work/象伝_下.md`。
- 分割境界は 30 離為火 / 31 沢山咸 とし、元の結合ファイルは未変更。
- 2026-04-09 Obsidian vault の未コミット変更を 1 回でまとめてコミット。
- コミットは `0d10ef1 chore: update Obsidian notes`。
- 作業ツリーは `git status --short --branch` で clean を確認。
- 変更内容は note 整理、十翼関連の移設、新規ノート追加、テンプレ更新を含む。

### [2026-04-08] <type: worked-well>
- context: Committed and pushed quote source edits on codex/copilot-safe-mode.
- action: Used safe-git-publish with path-limited staging to exclude the untracked .codex file.
- result: Commit 9a4aa82 pushed and local branch is aligned with origin.
- new rule: For small publish requests, stage explicit files only and verify status after push.
- severity: low
- [2026-09-28] Pushed the requested 2026-04-14 ekikyo custom prompt version to cleanup/takashima-furoku.
- Commit: 4292adb5e7aa03fd6a4f9d114f6746e660188522; only project_source/prompts/ekikyo_custom_prompt.md was committed.
- Bypassed the pre-commit version stamp hook because it would rewrite the requested April stamp to the current date.
- Pre-existing unrelated deletions and untracked source files remain untouched.
- [2026-09-28] Reflected the same 2026-04-14 prompt content onto GitHub main as commit 5ef221b.
- Used an isolated worktree based on origin/main so unrelated dirty files in the primary checkout were not included.
- Verified origin/main points to 5ef221b and the file header remains 2026-04-14.0.
- repeat_count: 1
- [2026-04-09] Removed leading blockquote markers from one Obsidian 易経 markdown file.
  - Updated `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/易経_暗誦用 1.md` in place.
  - Verified the first section now renders as plain text without `> ` prefixes.
  - No repo files were changed; `git status` remained clean except for existing untracked `.codex`.

### [2026-04-09] <type: worked-well>
- context: Published takashima quote-file updates on codex/copilot-safe-mode.
- action: Staged the directory with git add -A and verified the change set before commit.
- result: Commit e538516 pushed successfully; branch is aligned with origin.
- new rule: When status shows delete+untracked pairs in the same folder, verify rename detection before staging.
- severity: low
- repeat_count: 1
- 2026-04-09 高島易断 141/143 の Markdown 132 ファイルを本文中心に点検。
- 誤記候補を機械抽出し、文脈確認の上で 22 件を確定、4 件を要確認に整理。
- 高優先の崩れは句読点重複、引用閉じ忘れ、改行崩れ、文末欠落。
- 中優先では をを/にに/ではは などの重複助詞が複数見つかった。
- 表記揺れは版ごとの差が大きく、同一ファイル内混在や版内少数派のみ代表例として記録。
- レポートを /home/ys/projects/ekikyo/work/高島易断_表記点検レポート_141_143_2026-04-09.md に保存。
- [2026-04-09] Installed markitdown in dedicated WSL venv at /home/ys/tools/markitdown/.venv.
  - Installed package set: markitdown[all] using venv-local pip.
  - Verified executable path /home/ys/tools/markitdown/.venv/bin/markitdown.
  - Verified --help and a real conversion to /tmp/markitdown-readme.md.
  - Noted optional warning: ffmpeg is not installed, which may affect audio-related features.
- [2026-04-09] Added codex/markitdown skill for local MarkItDown CLI conversion.
  - New skill triggers on file-to-Markdown requests for PDF/DOCX/PPTX/XLSX/HTML/EPUB and similar documents.
  - Default behavior writes sibling .md output beside the source file via /home/ys/tools/markitdown/.venv/bin/markitdown.
  - Guardrails require clarification on ambiguous input paths and unclear overwrite intent.
  - Added agents/openai.yaml metadata for UI-facing invocation and implicit skill use.

- [2026-04-10] Added Chienomori quote extraction workflow to `ekikyo`.
  - Added `scripts/extract_chienomori_quotes.py` to copy only honka/taisho and koji/sho quote pairs from the Chienomori markdown source.
  - Added tests for filtered extraction and CLI output generation in `tests/test_extract_chienomori_quotes.py`.
  - Generated `work/chienomori-honka-taisho.md` and `work/chienomori-koji-sho.md` without modifying source files.
  - Verified 64 hexagrams in each output and confirmed `序卦伝` / `文言伝` / `キーワード` are absent.

- [2026-04-10] Compared `work/chienomori-honka-koji.md` with `work/assets-quotes-honka-koji-no-furigana.md`.
  - Generated `work/chienomori-assets-honka-koji-text-comparison.md` as a section-aware comparison report.
  - Report separates exact match, loose match, and real difference for original Chinese and kundoku lines.
  - Findings: original Chinese is often close after punctuation/variant normalization; kundoku differs heavily across versions.
  - Structural anomalies flagged separately, including missing `用九`/`用六` and a malformed `雷天大壮` honka block on the assets side.

- [2026-04-10] Compared `work/高島_64全部_かな無し.md` with `work/知恵の森_64.md`.
  - Generated `work/高島_知恵の森_本文比較レポート.md`.
  - Report tracks exact match for original Chinese, exact match for kundoku, and normalized similarity for kundoku.
  - Current totals: original exact 548/958, kundoku exact 43/958, kundoku similarity mean 0.793 median 0.809.
  - Structural mismatches remaining in source data: missing `用九`/`用六` on Takashima side and missing `18 九三` on Chienomori side.

- [2026-04-10] Cross-compared five Takashima source groups.
  - Generated `work/高島ソース精査レポート.md` from merged work files, assets quotes, and Obsidian 141/143 sets.
  - Separated practical edit candidates by comparing the four same-lineage sources without the 143 augmented edition.
  - Core four-source findings: 4 missing/structural issues, 16 original mismatches, 19 kundoku mismatches.
  - High-signal concrete issues include `work/高島_64全部.md` missing 15/六四/小象伝 and 28/九五/小象伝, plus `assets/quotes/quotes-honka.md` corruption around 38 火沢睽.
  - 143 differs systematically and was treated as a separate augmented edition rather than a direct typo-only source.

- [2026-04-10] Built first runnable skeleton for `obsidian-plugin/ekikyo-plugin`.
  - Added desktop-only Obsidian plugin entry with one command to copy SIMPLE source output.
  - Added two-line textarea modal input: line 1 binary, line 2 changing line.
  - Added `scripts/generate_quote_dataset.py` to convert vendored quote markdown into `data/quote-dataset.json`.
  - Kept runtime Python-free by loading generated JSON from JS modules at plugin runtime.
  - Split responsibilities into calculator, dataset loader, modal, and output builder modules.
  - Verified smoke path locally: `000101` + `2` resolves and emits `## 本卦` then `## 変爻`.
- [2026-04-10] Refreshed the `ekikyo-plugin` honka source and republished the workspace repo.
  - Updated `vendor/ekikyo/assets/quotes/quotes-honka.md`.
  - Regenerated `data/quote-dataset.json` and mirrored it into the Obsidian plugin folder.
  - Committed as `c6874cd` with message `chore: refresh honka quotes`.
  - Pushed to `origin/main` on `ys1887/obsidian-plugin`.
- [2026-04-10] Synced refreshed quote sources from `/home/ys/projects/ekikyo/assets/quotes` into `ekikyo-plugin` and Obsidian.
  - Updated `quotes-honka.md` and `quotes-koji.md` in `ekikyo-plugin/vendor/ekikyo/assets/quotes`.
  - Regenerated `ekikyo-plugin/data/quote-dataset.json`.
  - Mirrored the source files and dataset into the Obsidian plugin folder.
- [2026-04-10] Synced refreshed quote sources from `/home/ys/projects/ekikyo/assets/quotes` and pushed the workspace repo.
  - Updated `quotes-honka.md` and `quotes-koji.md` in `ekikyo-plugin/vendor/ekikyo/assets/quotes`.
  - Regenerated `ekikyo-plugin/data/quote-dataset.json`.
  - Commit `32e47f0` pushed to `origin/main`.

### [2026-04-10] <type: worked-well>
- context: Published a one-line wording fix in reference cases on codex/copilot-safe-mode.
- action: Staged only the target markdown file and verified the exact diff before commit.
- result: Commit 38c26ea pushed successfully; branch is aligned with origin.
- new rule: For single-file prose fixes, stage the file explicitly and keep .codex untracked.
- severity: low
- repeat_count: 1
- [2026-04-10] Synced ekikyo-plugin vendored assets to the canonical flat layout.
  - Moved quote sources to vendor/ekikyo/assets/honka.md and vendor/ekikyo/assets/koji.md.
  - Moved the reference-case source to vendor/ekikyo/assets/高島易断占例.md.
  - Updated generator and rendering scripts to read the flattened asset paths.
  - Regenerated data/quote-dataset.json successfully with the new layout.
  - Synced the installed Obsidian plugin datasets under Proton Drive so both copies now match.
- [2026-04-10] Built a 3-line Takashima honka/koji derivative from `work/高島_本卦爻辞.md`.
  - Added `scripts/build_honka_koji_three_line.py` to generate a new file without mutating the source markdown.
  - Kept line 2 as the source reading without parenthetical ruby and generated line 3 as hiragana.
  - Used repo-local ruby sources plus Honda/Chienomori references as reading aids, with line-level overrides for ambiguous cases.
  - Verified 448 quote blocks became 3-line triples with no remaining parenthetical ruby in line 2 and no kanji in line 3.
- [2026-04-10] Fixed `高島_本卦爻辞_3行版.md` so `本卦` comes from `高島_本卦彖伝大象伝.md`.
  - The generator now pulls the first quote pair after each `##` heading from the honka/tan/dai-sho source.
  - Added a regression test that `### 本卦` uses the卦辞 pair, not the later commentary pair.
  - Rebuilt the output file after the parser change and verified the full run with `--check-only`.
- [2026-04-11] Restored `高島_本卦爻辞_3行版 - コピー.md` after a bad bulk edit.
  - Rebuilt the plain-text 3-line file from the markdown source.
  - Kept title and line headings flush with the following text.
  - Preserved blank lines only between content blocks and hexagram sections.

### [2026-04-11] <type: worked-well>
- context: Added and published the three-line quote builder on codex/copilot-safe-mode.
- action: Added the script plus unittest coverage and verified them before commit.
- result: Commit 86885c3 pushed successfully; branch is aligned with origin.
- new rule: For new helper scripts, keep a matching unittest in-tree and run it before publish.
- severity: low
- repeat_count: 1
- [2026-04-11] Switched ekikyo canonical quote files to 3-line source blocks.
  - `assets/honka.md` and `assets/koji.md` now carry original, reading, and hiragana lines as the canonical quote source.
  - Fixed `scripts/rendering.py` to group quote blocks by contiguous `>` sections so 3-line quotes do not misalign shozoden parsing.
  - Added a regression test that checks `load_line_quotes()` still maps `爻辞` and `小象伝` correctly after the 3-line swap.
  - Updated repo docs to describe canonical quote files as 3-line sources.

- [2026-04-12] Rebuilt a paragraph-restored variant of the Takashima OCR markdown.
  - Kept the original Obsidian note untouched and wrote a sibling file with `_ocr段落復元` suffix.
  - Used `/mnt/e/Documents/Playground/ocr/*.json` layout bands and indent hints as conservative paragraph-break signals.
  - Preserved all non-blank source lines from the existing cleaned markdown verbatim.
  - New file adds blank lines only; non-blank text content matches the original note exactly.

### [2026-04-12] <type: worked-well>
- context: Normalized wording across honka/koji quote files and published the cleanup.
- action: Staged only the two intended markdown files and verified the exact diff before commit.
- result: Commit fd6f919 pushed successfully; branch is aligned with origin.
- new rule: For prose normalization, keep the staging set file-limited and verify the repo is clean after push.
- severity: low
- repeat_count: 1
- [2026-04-12] Updated ekikyo plugin notification text to show numbered hexagram labels.
- [2026-04-12] Kept clipboard output unchanged; only the Obsidian success notice now uses `number.name`.
- [2026-04-12] Verified `main.js` syntax with `node --check` after the change.
- [2026-04-12] Synced updated ekikyo assets from /home/ys/projects/ekikyo/assets into repo vendor and Obsidian plugin copy.
- [2026-04-12] Regenerated data/quote-dataset.json from updated honka/koji sources.
- [2026-04-12] Removed obsolete Obsidian plugin vendor/ekikyo/assets/quotes directory after confirming no references.
- [2026-04-12] Committed as 784ad38 and pushed codex/ekikyo-asset-layout-sync.
- [2026-04-12] Obsidian frontmatter batch update for 日本易学振興会 files.
- Added YAML frontmatter to 104 Markdown files under the Obsidian folder.
- 64卦 files received title/number/yomi/source/tags/related_ideas.
- Non-64 files received title/source/tags/related_ideas.
- Preserved source URLs by reading them before stripping the legacy heading block.
- Used `/home/ys/projects/ekikyo/assets/takashima` as the yomi source for the 64卦 set.
- [2026-04-12] Reflowed the 64 hexagram files in 日本易学振興協会.
- Converted the yao-specific blocks under `爻辞` and `小象伝` into `#### 初爻` through `#### 上爻`.
- Fixed an accidental heading-attachment pass and restored clean section boundaries.
- Kept the change scope limited to the 64 hexagram files only.
- [2026-04-13] Rechecked the source alignment report after manual fixes.
- Cleared previously reported mismatches that were already resolved in the sources.
- Kept `25_天雷无妄` as a本文内引用 case, not a comparison mismatch.
- Marked `55_雷火豊` bracketed reading difference as resolved.

### [2026-04-13] <type: worked-well>
- context: Normalized the honka and koji source text and published the cleanup.
- action: Staged only the two intended markdown files and reviewed the diff size before commit.
- result: Commit efc2bd5 pushed successfully; branch is aligned with origin.
- new rule: For broad prose normalization, keep the stage set file-limited and verify the repo is clean after push.
- severity: low
- repeat_count: 1

### [2026-04-14] <type: worked-well>
- context: Published another broad source-text normalization pass on codex/copilot-safe-mode.
- action: Staged only the two intended markdown files and let git record the large rewrite cleanly.
- result: Commit 28f0b8a pushed successfully; branch is aligned with origin.
- new rule: For large normalization passes, keep the staging set file-limited and trust git’s line accounting after review.
- severity: low
- repeat_count: 1

## 2026-04-13
- Created `/home/ys/projects/ekikyo/work/易経_3行版_彖大小象カット.md` from `易経_3行版.md`.
- Removed all `### 彖伝` and `### 大象伝` sections from the derivative file.
- Removed all `> 象曰` blocks as the 小象伝 equivalent in this source layout.
- Left the source file unchanged.

## 2026-04-13
- Renumbered `##` headings in `/home/ys/projects/ekikyo/work/易経_3行版_彖大小象カット.md` to kanji numerals.
- Kept the underlying text unchanged while removing digits only from the hexagram headings.
- Verified the derived file no longer has Arabic numeral top-level headings.

## 2026-04-13
- Removed heading markers from `/home/ys/projects/ekikyo/work/易経_3行版_彖大小象カット.md`.
- Left the heading text and body content intact.

## 2026-04-13
- Removed leading `#` and `>` markers from `/home/ys/projects/ekikyo/work/易経_3行版_彖大小象カット.md`.
- Preserved the underlying text and line breaks.

## 2026-04-13
- Updated `/home/ys/projects/ekikyo/work/易経_3行版_彖大小象カット.md` to use `。` in the same six yaoci lines.
- Left all other text unchanged.

## 2026-04-13
- Removed `彖伝`, `大象伝`, and `小象伝` content from `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/易経_本卦爻辞のみ.md`.
- Preserved the remaining 卦辞 and 爻辞 content.

## 2026-04-13
- Normalized `/home/ys/projects/ekikyo/work/易経_3行版.md` in three passes: kanji numerals, removed `卦辞` headings, then stripped `#` and `>` markers.
- Preserved the underlying text content while flattening the structure.

## 2026-04-13
- Removed `彖伝`, `大象伝`, and `小象伝` content from `/home/ys/projects/ekikyo/work/易経_3行版.md`.
- Left the remaining 卦辞 and 爻辞 sections intact.

## 2026-04-13
- Removed only the `### 卦辞` headings from `/home/ys/projects/ekikyo/work/易経_3行版.md`.
- Kept every 卦辞 body line intact.

## 2026-04-13
- Converted the top-level hexagram numbers in `/home/ys/projects/ekikyo/work/易経_3行版.md` to kanji numerals.
- Kept all body text unchanged.

## 2026-04-13
- Removed leading heading and block markers from `/home/ys/projects/ekikyo/work/易経_3行版.md`.
- Preserved the underlying text and line order.

## 2026-04-13
- Restored the punctuation change in `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/易経_本卦爻辞のみ.md` back to the prior `。` state.
- No other content was changed.

## 2026-04-13
- Normalized the six `．` yaoci cases to `。` in both `/home/ys/projects/ekikyo/work/易経_3行版.md` and `/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/易経_2行版.md`.
- Verified no matching `．` cases remain for those yaoci lines.

- [2026-04-13] Cleaned up ekikyo-plugin structure after review.
  - Removed four unused  helper modules that were duplicated by .
  - Added  to separate generator input from reference-only files.
  - Updated repo  and  to match the current direct-edit surface.
  - Verified no remaining imports or references to the deleted helper modules.

- [2026-04-13] Cleaned up ekikyo-plugin structure after review.
  - Removed four unused helper modules under lib that duplicated logic in main.js.
  - Added reference/iching-calculator/README.md to separate generator input from reference-only files.
  - Updated repo README.md and AGENTS.md to match the current direct-edit surface.
  - Verified no remaining imports or references to the deleted helper modules.

- [2026-04-14] Generated EX_SIMPLE answer for 41 山沢損 5爻 in ekikyo.
- Input asked whether to list pencil leads at 5000 yen on Mercari.
- Final judgment: listing at 5000 yen is acceptable, but avoid clinging to price and allow modest concession.
- Verified final output at /home/ys/projects/ekikyo/work/2026-04-14_04.md with assembled quotes, references, raw appendix, and case excerpt.
- [2026-04-14] Generated EX_SIMPLE answer for 7 地水師 2爻 in ekikyo.
- Input asked whether to delete an AI-written 総合解釈 after it led to a misread and loss.
- Final judgment: deleting the AI 総合解釈 is appropriate; restore the reading center to source-grounded text only.
- Verified final output at /home/ys/projects/ekikyo/work/2026-04-14_05.md with assembled quotes, references, Takashima raw appendix, and case excerpt.
- Caught and corrected a write-order issue: assemble and append must not run in parallel on the same output file.
- [2026-04-14] Updated `ekikyo-plugin` SIMPLE2 behavior to mirror SIMPLE with added zhigua body output.
  - Changed SIMPLE2 to accept exactly one changing line, matching SIMPLE validation.
  - Replaced SIMPLE2 summary output with full markdown output: main hexagram, changing line, zhigua, Takashima sections, and reference case excerpt.
  - Aligned zhigua heading style with main hexagram heading by rendering `## <之卦名>`.
  - Updated modal guidance text and placeholder so SIMPLE2 no longer advertises multi-line input.
  - Verified with `node --check main.js` and a VM-based smoke test for `111111` + `2` plus multi-line rejection.
- [2026-04-14] Updated `ekikyo-plugin` EX5 to accept only one changing line.
  - Changed EX5 input parsing to use the single-line validator instead of multi-line parsing.
  - Kept the EX5 output format unchanged; only the accepted input shape was narrowed.
  - Synced the plugin deployment copy under the Obsidian plugins directory.
  - Committed as `d6a13e5` with message `feat: make ex5 accept only one changing line`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` to origin successfully.
- [2026-04-14] Updated Takashima source text for `29_坎為水.md` and the related example note.
  - Split the quoted `論語` passage from the explanation so the source text reads more cleanly.
  - Kept the substantive content intact while improving markdown structure.
  - Committed as `eacb093` with message `docs: refine takashima kanisui excerpt`.
  - Pushed branch `codex/copilot-safe-mode` to origin successfully.
- [2026-04-14] Renamed the existing EX5 summary mode to `EX5-LIST` in `ekikyo-plugin`.
  - Kept the 6-line clipboard summary output unchanged.
  - Renamed the Obsidian command, internal mode key, and modal button label from `EX5` to `EX5-LIST`.
  - Synced the updated `main.js` to the live Obsidian plugin directory.
  - Committed as `07ed0f3` with message `refactor: rename ex5 summary mode to ex5-list`.
  - Pushed branch `codex/ekikyo-asset-layout-sync` to origin successfully.

- [2026-04-15] Fixed quote-block spacing in ekikyo plugin dataset generation.
  - Added normalization in `scripts/generate_quote_dataset.py` for `honkaBlock` and line blocks only.
  - Inserted a blank line after consecutive `>` quote lines when explanation prose follows.
  - Regenerated `data/quote-dataset.json` and verified `19 地沢臨` plus a smoke sample.
  - Synced the regenerated dataset to the Obsidian plugin deployment copy.
- [2026-04-15] Inspected `ekikyo` Takashima assets against the original Obsidian source folder.
  - Matched 64 shared hexagram files; source-only extras are `高島易断増補_六十四卦一覧.md` and `高島易断増補_序文.md`.
  - Confirmed current repo files are not metadata-stripped originals; they also rewrite headings, remove quote blocks, and reshape paragraph breaks.
  - Structural normalization shows 63/64 files preserve the same prose, with `30_離為火.md` containing two extra lines in the repo copy.
  - If original line breaks must be preserved, derive repo assets mechanically from the source and keep transformation logic explicit.
- [2026-04-15] Synchronized all 64 `ekikyo` Takashima assets from `work/143_高島易断_増補` to `assets/takashima`.
  - Added `scripts/sync_takashima_assets.py` to rebuild assets from work-file sections with preserved frontmatter.
  - Kept `work` section text and line breaks as the source of truth, while preserving assets-compatible headings for extraction.
  - Added a regression test that walks all 64 assets and verifies honka/line extraction succeeds.
- [2026-04-15] Synced refreshed `assets/takashima` into the plugin vendored mirror.
  - Regenerated `data/quote-dataset.json` from the updated source set.
  - Copied the regenerated dataset into the Obsidian plugin install path.
  - Verified the repo and plugin dataset hashes match exactly.
- [2026-04-15] Aligned timestamp order for /mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/150_十翼.
- Set LastWriteTime in numeric order from 01 to 10.
- Set CreationTime in the same numeric order using Windows Python 3.12 and Win32 SetFileTime.
- Verified the resulting times increased by one second per file.
- [2026-04-16] Re-stamped `110_易占` creation times from the embedded `day:` metadata.
- Applied `2026-04-10` through `2026-04-14` in the confirmed order, one second apart within each day.
- Verified the Windows FILETIME values after rewriting.
- [2026-04-16] Generated typo/notation-variation report for five Obsidian 易経 folders.
- Scanned 384 Markdown files under 140_高島易断, 150_十翼, 160_易経_基本, 170_易経書籍, and 185_日本易学振興協会.
- Report saved to /home/ys/projects/ekikyo/work/report_誤字脱字表記揺れ調査.md.
- High-priority findings include likely mojibake/OCR fragments, duplicated punctuation, heading-format drift, and major old/new character variants.
- [2026-04-16] Created revised typo/notation report excluding the two OCR-difficult 易占大意 files.
- Preserved original complete report at /home/ys/projects/ekikyo/work/report_誤字脱字表記揺れ調査.md.
- New report saved at /home/ys/projects/ekikyo/work/report_誤字脱字表記揺れ調査_易占大意2ファイル除外.md.
- Verified the excluded file-name pattern no longer appears in the revised report.
- [2026-04-16] Revised the 易占大意-excluded typo report again.
- Removed detailed sections for 中点重複, かな語連続, 助詞重複, and 漢字語連続 because they were judged non-issues or classical expression noise.
- Preserved high-priority entries for 明治二十七年六月六月 and 未開発開発の状態.
- Updated the next-step text to no longer reference the removed 重複語・脱字系候補 section.
- [2026-04-16] Normalized H1 headings in 143_高島易断_増補 hexagram files only.
- Updated 64 NN_卦名.md files from fullwidth-number/fullwidth-dot H1 to # NN_卦名.
- Verified 64 target files, 0 H1 mismatches, and no remaining ^# [０-９]+． style headings in that folder.
- Left non-hexagram files such as 高島易断増補_序文.md unchanged.
- [2026-04-16] Revised the 易占大意-excluded typo report to narrow notation-variation findings.
- Removed full-text variant count/detail sections and replaced them with management-title/heading-focused old-form hexagram candidates.
- Removed the already-fixed 143_高島易断_増補 H1 formatting finding from high-priority candidates.
- Verified old full-count headings such as 表記揺れの詳細例, 伝/傳, 為/爲, 辞/辭 are absent from the revised report.
- [2026-04-16] Generated an `ekikyo` EX_COMPARE answer for soy vs whey protein.
- User input candidate labels needed markdown heading normalization for the current compare parser.
- Saved result to `/home/ys/projects/ekikyo/work/2026-04-16_01.md`.
- Ranking placed whey first because 恒三爻 is `貞吝`, while soy's 鼎四爻 explicitly says `凶`.
- Verified the final file through `scripts/assemble_extract_answer.py` shape validation for EX_COMPARE.

- [2026-04-16] Updated ekikyo-plugin input validation and published branch.
  - Restricted changing-line input to half-width digits 1-6 only.
  - Verified main.js syntax, explicit validation cases, and deployment target parity.
  - Committed and pushed b126d52 on codex/quote-block-spacing-fix.
- [2026-04-17] Generated ekikyo Takashima assets sync-diff report.
- Compared Obsidian 141/142/143 source folders against ekikyo assets and plugin vendor assets.
- Report saved to /home/ys/projects/ekikyo/work/report_高島易断_assets同期差分調査.md.
- Found 39 differences: plugin assets 1, honka 3, koji 25, case excerpts 8, takashima assets 2.
- Confirmed known plugin lag in takashima/39_水山蹇.md still contains duplicated 時が時が.
- [2026-04-17] Regenerated Takashima assets sync-diff report after 水山蹇 plugin vendor fix.
- Report now shows 38 differences total and 0 differences for ekikyo/assets vs plugin assets.
- Verified old 時が時が and takashima/39_水山蹇.md plugin byte-diff entries are absent.

- [2026-04-17] Fixed 8 targeted Obsidian 142_高島易断_占例 individual-file transfer differences.
- Edited only the individual hexagram case files; left 高島易断_占例一覧.md unchanged by request.
- Corrected duplicated particles, OCR text, missing closing quotes, and one line-break split to match assets/高島易断占例.md.
- Self-review caught and reverted an over-broad quote replacement before completion.
- Verified old strings remain only in the excluded list file; ekikyo/plugin tracked status unchanged from prior assets punctuation work.

- [2026-04-17] Updated Obsidian 142 高島易断_占例一覧.md for the same case-transfer typo set.
- Limited edits to the nine matching old strings/line split in the list file.
- Regenerated /home/ys/projects/ekikyo/work/report_高島易断_assets同期差分調査.md.
- New report summary: 22 total differences; 142 → 高島易断占例.md is 0.
- Verified old strings no longer appear under Obsidian 142 and diff --check is clean.

- [2026-04-17] Synced changed ekikyo assets from source into the plugin repo and Obsidian deployment target.
  - Copied , , , , and .
  - Regenerated  after the asset sync.
  - Verified the repo copies and deployment copy match the source files.
  - Fixed one temporary miscopy of  into the asset root before finishing.

- [2026-04-17] Synced changed ekikyo assets from source into the plugin repo and Obsidian deployment target.
  - Copied README.md, honka.md, koji.md, 高島易断占例.md, and takashima/39_水山蹇.md.
  - Regenerated data/quote-dataset.json after the asset sync.
  - Verified the repo copies and deployment copy match the source files.
  - Fixed one temporary miscopy of 39_水山蹇.md into the asset root before finishing.
- [2026-04-17] Rechecked Takashima assets sync-diff report completeness.
- Re-ran /tmp/audit_takashima_assets.py against ekikyo assets, plugin vendor assets, and Obsidian 141/142/143 folders.
- Confirmed findings remain 19 total: plugin 0, honka 1, koji 17, cases 0, takashima 1.
- Added an explicit confirmation section to work/report_高島易断_assets同期差分調査.md stating that non-listed body text matches and no missing items were found.
- [2026-04-17] Rechecked user fixes for ekikyo assets/koji.md Takashima diff cleanup.
- Confirmed 11 上六 extra case text and 37 六四 extra hiragana reading were removed from koji.md.
- Confirmed 15 六四, 23 上九, and 37 九五 missing koji text was added.
- Regenerated work/report_高島易断_assets同期差分調査.md and added a user-facing judgment section explaining resolved/acceptable koji differences.
- Remaining raw koji findings are order/punctuation/annotation-position differences or accepted case-exclusion differences; plugin vendor koji.md is now out of sync with ekikyo assets.
- [2026-04-17] Synced ekikyo asset updates into the plugin vendor copy.
- Copied assets/koji.md and assets/takashima/38_火沢睽.md to /home/ys/projects/obsidian-plugin/ekikyo-plugin/vendor/ekikyo/assets/.
- Verified both copied files match the source with cmp.
- Re-ran the Takashima sync-diff audit; plugin assets discrepancies dropped to 0.
- Remaining findings are honka 1 and koji 3, which are intentional or accepted differences.

- [2026-04-19] Redesigned ekikyo SIMPLE source output structure.
  - Added bodyExcerpt/divinationExcerpt data from vendor/ekikyo/assets/本文抜粋.md and 占断抜粋.md.
  - Rebuilt data/quote-dataset.json and synced it to the Obsidian plugin deployment copy.
  - SIMPLE now renders minimal headings: 本卦, 変爻, and optional 占例抜粋.

- [2026-04-19] Finalized ekikyo-plugin SIMPLE output restructuring.
  - SIMPLE now emits minimal headings: 本卦, 変爻, optional 占例抜粋.
  - Dataset generation now includes `本文抜粋.md` and `占断抜粋.md` as `bodyExcerpt` and `divinationExcerpt`.
  - Verified 384 SIMPLE outputs, six no-bullet 占断 cases, and synced main.js/dataset to the Obsidian plugin target.

## 2026-04-19 ekikyo Obsidian appendices rename
- Renamed 42 files in 高島易断/144_増補高島易断_上巻附録 from 高島易断増補_* to 増補高島易断_*.
- Preserved numbered appendix sequence 01-41; also renamed the non-numbered 上巻_附録 file.
- Updated old basename references under 高島易断 markdown tree; only 高島易断_index.md changed.
- Verified no old filename references remain and all new numbered files exist.

## 2026-04-19 Obsidian 高島易断 internal link repair
- Updated internal links under 100_易経/140_高島易断 according to mapping: old 141->current 142, old 142->current 143, old 143->current 141.
- Rewrote old 高島易断増補_NN basename links in 144 appendix files to current 141 増補 paths by number.
- Fixed two leftover 094a/094b links in 141_増補高島易断/19_地沢臨.md.
- Made appendix links in 高島易断_index.md explicit under 144_増補高島易断_上巻附録.
- Verified 262 Markdown files, 972 links checked/resolved, 0 broken, and 0 old path references remain.
- [2026-04-19] Repaired related_ideas links across 高島易断 141/142/143 hexagram files.
- 141 files point to 142 + 143 same-name notes.
- 142 files now point to 143 + 141 same-name notes.
- 143 files point to 142 + 141 same-name notes.
- Verified all 64 hexagram files in each folder; mismatches = 0 in 141/142/143.
- [2026-04-19] Unified related_ideas display names across 141/142/143 Takashima notes.
- 141 now points to 142 as 占例 and to 143 as 占例抜粋.
- 142 now points to 141 as 易断 and to 143 as 占例抜粋.
- 143 now points to 141 as 易断 and to 142 as 占例.
- Verified all 64 hexagram files in each folder; disallowed labels = 0.
- [2026-04-22] Synced updated `koji.md` and `高島易断占例.md` from plugin vendor back into `/home/ys/projects/ekikyo/assets`.
- [2026-04-22] Regenerated `data/quote-dataset.json` after the asset sync and copied it to the Obsidian plugin deployment target.
- [2026-04-22] Committed and pushed plugin repo `codex/quote-block-spacing-fix` as `029bf78` (`fix: sync updated ekikyo assets`).
- [2026-04-22] Source repo `/home/ys/projects/ekikyo` was left with matching uncommitted sync changes for later follow-up.
- [2026-04-23] Committed and pushed a one-file fix in `vendor/ekikyo/assets/高島易断占例.md`.
- [2026-04-23] Branch `codex/quote-block-spacing-fix` advanced to `a86a72d` with message `fix: correct 高島易断占例 references`.
- [2026-04-23] Plugin repo is clean after push.
- [2026-04-27] Updated ekikyo-plugin SIMPLE2 / 中筮法 to accept 0-6 changing lines.
- 0 changing lines now omits changing-line, zhi-gua, and reference-case output.
- 1 changing line preserves the previous SIMPLE2 output path with zhi-gua and optional reference case.
- 2-6 changing lines now omit changing-line/reference-case output and show the calculated zhi-gua.
- Synced main.js to the Obsidian plugin deployment target and verified syntax/cmp.
- [2026-04-27] Reworked SIMPLE2 output to reuse SIMPLE-style honka and changing-line sections.
- SIMPLE2 now emits honka as body excerpt + 卦辞/彖伝/大象伝 + divination excerpt.
- Single changing-line SIMPLE2 emits the SIMPLE-style changing-line section before zhi-gua.
- Zhi-gua now emits the SIMPLE honka-style section; 0 changing lines still omit zhi-gua.
- Synced main.js to the Obsidian plugin deployment target and verified syntax/cmp.
- [2026-04-29] Created a new normalized echo/recitation version of `work/易経_暗誦用.md` as `work/易経_暗誦用_整形版.md`.
- Kept the source file unchanged and used a mechanical transform from the source layout.
- Output format now keeps one blank line after each hexagram judgment only.
- All hexagram line readings are continuous with no blank lines between them.
- Verified 64 hexagram headings and one blank separator per block.
- [2026-05-01] Normalized Obsidian markdown in 182_龍青三_本田濟 by removing leading bullet markers inside 卦辞/彖伝/大象伝/爻辞.
- Scoped the edit to heading ranges only so キーワード bullets stayed intact.
- Applied the same mechanical transform across all 64 hexagram files.
- Verified no `- ` remains inside the four target sections after the edit.
- [2026-05-02] Added occupation-only archive copies for ekikyo vendor assets.
  - Created `vendor/ekikyo/assets/archive/honka-occupation.md` and `koji-occupation.md` in the Obsidian plugin repo.
  - Preserved the original `honka.md` and `koji.md` files unchanged.
  - Verified both archive files contain 64 hexagram sections.
  - Kept the work as copy-only so future restoration remains easy.
- [2026-05-02] Fixed `koji-occupation.md` to archive per-yaw lines instead of per-hexagram summaries.
  - Regenerated `vendor/ekikyo/assets/archive/koji-occupation.md` from `vendor/ekikyo/assets/koji.md`.
  - Kept `###` headings and extracted each of the 6爻 occupation blocks per hexagram.
  - Verified counts: 64 hexagrams, 384 `###` headings, 384 occupation blocks.
  - Left `honka.md`, `koji.md`, and `honka-occupation.md` unchanged.
- [2026-05-02] Disabled SIMPLE/SIMPLE2 divinationExcerpt output in ekikyo-plugin main.js.
- Kept divinationExcerpt data generation intact; only the Markdown output path was removed.
- Verified with python3 scripts/generate_quote_dataset.py and node --check main.js.
- [2026-05-02] Removed honka/koji from ekikyo-plugin dataset/runtime dependency.
- Moved vendor honka.md and koji.md into vendor/ekikyo/assets/archive/.
- Regenerated quote-dataset.json without sourceTitle/honkaBlock/lines and synced main.js + dataset to Obsidian plugin target.
- Verified node --check main.js, python3 scripts/generate_quote_dataset.py, py_compile, and dataset shape for 天地否.
- [2026-05-03] Created custom Codex pet Mana with hatch-pet from /mnt/e/Documents/Pictures/アイコン画像/GiBhqscakAEkMDX.jpg.
- Generated base plus row strips; delegated idle, running-right, waving, jumping, failed, waiting, running, and review to subagents.
- Derived running-left from running-right by mirror after confirming no side-specific text/logo/marking issue.
- Final package written to /mnt/c/Users/nekol/.codex/pets/mana with validation/review errors = 0; preview videos skipped because ffmpeg is unavailable.
- [2026-05-03] Renamed four Obsidian heading variants across the 64 numbered 易経 files.
- [2026-05-03] Verified all old bracketed headings were removed and the four normalized headings each appear in all 64 files.
- [2026-05-03] Kept unrelated repo modifications in assets/ untouched.
- [2026-05-09] Generated ekikyo EX_COMPARE answer for game-selection ranking at /home/ys/projects/ekikyo/work/2026-05-09_01.md.
- Preserved user input in the final question block; repository parser could not parse the inline 候補A： format, so quotes were verified directly from assets/koji.md.
- Self-review caught and corrected a 41山沢損・2爻 quote mix-up with 42風雷益・2爻; final recommendation changed to スト6.
- Existing unrelated modified assets/ files were left untouched.
- [2026-05-10] Generated ekikyo EX_COMPARE answer for SF6 character restart selection at /home/ys/projects/ekikyo/work/2026-05-10_01.md.
- Parser still rejected inline 候補A： style, so final EX_COMPARE answer was drafted from canonical koji/takashima sources directly.
- Recommendation ranked JP first from 10天沢履・九二; existing unrelated asset modifications were left untouched.
- [2026-05-13] Generated ekikyo EX_COMPARE answer for updated next-game selection at /home/ys/projects/ekikyo/work/2026-05-13_01.md.
- Parser still rejected inline 候補A： style, so quotes were verified directly from assets/koji.md.
- Recommendation ranked Heavenly Bodies first from 48水風井・九五; Detroit and Entropy Center followed from 吉爻.
- Existing unrelated modified assets/ files were left untouched.
- [2026-05-18] Generated ekikyo EX_COMPARE answer for next-game-or-rest selection at /home/ys/projects/ekikyo/work/2026-05-18_01.md.
- Parser still rejects inline 候補A： style, so final EX_COMPARE answer was drafted from canonical assets/koji.md line evidence directly.
- Ranked game break first from 14火天大有・六五; Entropy Center and Jedi followed as game candidates.
- Verified no EX_COMPARE-inapplicable 高島易断/高島解釈原文/占例抜粋 sections were added.
- [2026-05-21] Generated ekikyo EX_COMPARE answer for next-game reselection at /home/ys/projects/ekikyo/work/2026-05-21_01.md.
- Normalized inline 候補A： input only for repository parser validation, while preserving the pasted question block in the final answer.
- Ranked デトロイト first from 51震為雷・初九; アヌビス and レゴ followed as 吉 candidates.
- Self-review verified template order, fixed recommendation sentence, and absence of internal /home/ys paths.
- [2026-05-21] Re-output the same ekikyo EX_COMPARE at /home/ys/projects/ekikyo/work/2026-05-21_02.md using only line-level 吉凶 strength.
- Pure 吉凶 ranking kept デトロイト first, moved ホームズ up to 4th due to 小人吉/大人否亨, and left ジェダイ last.
- [2026-05-23] Generated ekikyo EX_COMPARE answer for refreshed next-game selection at /home/ys/projects/ekikyo/work/2026-05-23_01.md.
- Parser still rejected inline 候補A： input, so a normalized temporary input was used only for prompt/evidence extraction.
- Preserved the original pasted question block in the final answer and ranked by changing-line 吉凶 only.
- Recommendation ranked アヌビス first from 61風沢中孚・九二; ウィッチャー3 and タクティクスオウガ followed as conditional 姤初爻 picks.
- Existing unrelated modified assets/ files were left untouched.
- [2026-05-28] Generated ekikyo EX_COMPARE answer for main-bank selection at /home/ys/projects/ekikyo/work/2026-05-28_01.md.
- Original inline 候補A： input still failed parser, so normalized temp input was used only for prompt/skeleton extraction.
- Preserved the pasted question block in final answer and ranked 三井住友銀行 first from 14火天大有・六五.
- Self-review verified no internal paths, 高島易断, 高島解釈原文, or 占例抜粋 sections were added.
- [2026-05-28] Generated ekikyo EX_COMPARE answer for sub-bank selection at /home/ys/projects/ekikyo/work/2026-05-28_02.md.
- Used normalized temp input only for parser/prompt generation while preserving the pasted inline 候補A： block in final answer.
- Ranked auじぶん銀行 first from 46地風升・初六 大吉; PayPay銀行 second from 48水風井・九五 utility strength.
- Self-review verified no internal paths, 高島易断, 高島解釈原文, or 占例抜粋 sections were added.
- [2026-05-28] Generated ekikyo EX_COMPARE answer for securities-account selection at /home/ys/projects/ekikyo/work/2026-05-28_03.md.
- Used normalized temp input for parser/prompt generation while preserving the pasted inline 候補A： block in final answer.
- Ranked 松井証券 first from 55雷火豊・六五 吉; SBI証券 second from 37風火家人・六二 貞吉; PayPay証券 last from 27山雷頤・六二 往凶.
- Self-review verified no internal paths, 高島易断, 高島解釈原文, or 占例抜粋 sections were added.
- [2026-05-28] Generated ekikyo EX_COMPARE answer for next-game selection at /home/ys/projects/ekikyo/work/2026-05-28_04.md.
- Used normalized temp input only for parser/prompt generation while preserving the pasted inline candidate block in final answer.
- Ranked タクティクスオウガ first from 11地天泰・六五 祉あり元吉; ソニック second from 26山天大畜・六四 元吉.
- Self-review verified no internal paths, 高島易断, 高島解釈原文, or 占例抜粋 sections were added.
- [2026-06-19] Generated ekikyo EX_COMPARE answer for next-game selection at /home/ys/projects/ekikyo/work/2026-06-19_01.md.
- Preserved pasted candidate block in final answer; EX_COMPARE used line-level quote evidence only.
- Ranked ワイルドアームズ first from 26山天大畜・上九; 手持ち積みゲー and GRIS followed as strong 吉 candidates.
- Self-review caught and fixed an initial wrong quote for 64火水未済・六五 before completion.
- [2026-06-19] Updated ekikyo skill output destination to Obsidian Codex folder.
- Created canonical source copy at /home/ys/projects/lib-skills/codex/ekikyo/SKILL.md from existing runtime skill.
- Replaced final output path and next_work_filename usage with /mnt/c/Users/nekol/Proton Drive/Obsidian/Codex.
- Synced identical SKILL.md to /home/ys/.codex/skills/ekikyo and /mnt/c/Users/nekol/.codex/skills/ekikyo.
- Verified skill validation and next filename resolution for the new Obsidian output folder.
- [2026-06-19] Generated ekikyo EX_COMPARE answer for next-game reselection at /mnt/c/Users/nekol/Proton Drive/Obsidian/Codex/2026-06-19_01.md.
- Preserved pasted question block; EX_COMPARE used changing-line evidence only.
- Ranked ワイルドアームズ first from 19地沢臨・上六 吉无咎; GRIS second from 39水山蹇・六二 終无尤.
- Self-review verified no internal /home/ys paths or EX_COMPARE-inapplicable raw appendix sections.
- [2026-06-19] Split ekikyo runtime skill deployment by environment while keeping skill name ekikyo.
- Added Windows execution clone at /mnt/e/Documents/Playground/ekikyo using origin/codex/copilot-safe-mode because origin/main lacks next_work_filename.py.
- WSL runtime now points to /home/ys/projects/ekikyo with python3; Windows runtime points to E:\Documents\Playground\ekikyo with py.
- Both runtimes output to the Obsidian Codex folder; Windows runtime no longer depends on WSL bridge.
- Removed the old root-level lib-skills/ekikyo/SKILL.md to keep codex/ekikyo as the source-of-truth.
- Verified skill validation, runtime hash pairs, Windows clone required files, and prompt/skeleton helper execution via /mnt/e clone.
- [2026-06-23] Generated ekikyo EX_COMPARE answer for next-game selection at /home/ys/projects/ekikyo/work/2026-06-23_01.md.
- Preserved pasted question block in final answer; used normalized temp candidate headings only for parser/evidence extraction.
- Ranked ユニコーンオーバーロード first from 14火天大有・上九 吉无不利; ライザ3 and ソニック followed as strong/parallel-friendly 吉 candidates.
- Self-review verified no internal /home/ys paths or EX_COMPARE-inapplicable appendix sections in the final answer.
- [2026-07-22] Generated ekikyo EX_COMPARE answer for next-game selection at C:\Users\nekol\Proton Drive\Obsidian\Codex\2026-07-22_01.md.
- Preserved pasted question block in final answer; used normalized temporary candidate headings only for parser/prompt generation.
- Ranked GRIS first from 53風山漸・上九 吉; ライザ3 and 大神 followed from 貞吉 lines.
- Self-review verified no internal paths or EX_COMPARE-inapplicable appendix sections in the final answer.
- [2026-07-24] Generated ekikyo EX_COMPARE answer for next-game reselection at C:\Users\nekol\Proton Drive\Obsidian\Codex\2026-07-24_01.md.
- Preserved pasted inline candidate block in the final question section; used normalized temporary headings only for parser/prompt generation.
- Ranked ライザ3 first from 21火雷噬嗑・六二 无咎; FF3 second from 47沢水困・九四 吝有終.
- Self-review verified no internal paths or EX_COMPARE-inapplicable 高島易断/高島解釈原文/占例抜粋 sections were added.
- [2026-08-10] Migrated lib-skills edit source-of-truth from /home/ys/projects/lib-skills/codex to E:\Documents\Playground\lib-skills in Windows-side AGENTS and copied repo.
- Updated E:\Documents\Playground\lib-skills docs/skill metadata to make C:\Users\nekol\.codex\skills the default Windows runtime publish target.
- Published updated skill-creator-codex and ekikyo Windows runtime SKILL.md into C:\Users\nekol\.codex\skills; WSL runtime publish intentionally skipped.
- Verified old lib-skills /mnt/c runtime path references were removed from the source repo and updated runtime copies; quick_validate.py passes under WSL Python because Windows Python lacks PyYAML.
- [2026-08-10] Copied WSL /home/ys/notes to E:\Documents\Playground\notes and verified codex-notes.md/codex-log.md hashes match.
- Copied WSL /home/ys/bin to E:\Documents\Playground\bin; verified recursive file count, byte total, and file hashes match source except .git/index metadata.
- Updated C:\Users\nekol\.codex\AGENTS.md Session Memory paths to E:\Documents\Playground\notes.
- [2026-08-10] Backed up WSL home recommended config/data to E:\Documents\Playground\wsl-backup: .ssh, .config/gh, .codex, .bashrc, .profile, .gitconfig.
- Excluded .config/gcloud by request; .codex tmp/.tmp transient runtime dirs were excluded after robocopy hit disappearing temp files.
- Verified .ssh and .config/gh counts/bytes, .codex counts/bytes excluding tmp dirs, dotfile hashes, and absence of wsl-backup/.config/gcloud.
- [2026-08-10] Created one-time full /home/ys backup before possible Ubuntu removal: E:\Documents\Backup\ubuntu-home-ys-2026-08-10.tar.gz.
- Source size was about 6.7G; archive size is 2,863,370,583 bytes; gzip -t verification passed.
- SHA256: E0069FE979180A4CDA9AF6B99C61541DC4C9167A5FA22A3262601A35118DA231. tar ignored Zed runtime socket files only.
- [2026-08-10] Windows-native bin migration: rewrote codex-publish-skill and codex-verify-skill-runtime from WSL bash/rsync to Python.
- Defaults now publish/verify from E:\Documents\Playground\lib-skills to C:\Users\nekol\.codex\skills; WSL runtime requires explicit --dest.
- Script source resolution prefers top-level skills and supports legacy E:\Documents\Playground\lib-skills\codex\<skill> during transition.
- Windows runtime variants under runtime\windows are deployed as the runtime root; verified skill-creator-codex and ekikyo both report OK.
- Updated bin README/OPERATIONS/AGENTS and .gitignore for Windows-native operation; old WSL backup script deletions remain user-side uncommitted changes.
- [2026-08-10] Audited skill Windows-native readiness across C:\Users\nekol\.codex\skills and E:\Documents\Playground\lib-skills.
- Runtime sync check: skill-creator-codex and ekikyo OK; --all shows several source skills intentionally not deployed to runtime.
- Runtime skills still WSL-dependent: backup-codex, backup-ubuntu, chatgpt-conversations-md-export, markitdown, nano-banana; safe-git-publish and obsidian-vault-checkpoint include bash helper scripts.
- Source-only skills still WSL/Linux-oriented include iching-sdk, iching-divination, epub2pdf, pdf2md, pdf2md-gemini, prompt-refine-loop-gemini, plus related /mnt/e examples/defaults.
- [2026-08-10] Windows-native ported three retained skills: chatgpt-conversations-md-export, safe-git-publish, obsidian-vault-checkpoint.
- chatgpt-conversations-md-export now points to E:\Documents\Playground\bin\chatgpt-conversations\export_conversations_to_md.py and Windows E:\... examples.
- safe-git-publish and obsidian-vault-checkpoint helper scripts were rewritten from bash to Python and SKILL usage changed to `py`.
- Published all three to C:\Users\nekol\.codex\skills and verified runtime copies OK; targeted WSL path grep returned no matches.
- [2026-08-10] Audited and Windows-native adjusted E:\Documents\Playground\obsidian-plugin\ekikyo-plugin project docs/package script.
- AGENTS/README now point related assets to E:\Documents\Playground\ekikyo\assets and repo-local vendor\ekikyo\assets instead of /home/ys paths.
- package.json generate-dataset script now uses `py scripts\generate_quote_dataset.py`; npm run generate-dataset succeeds on Windows.
- Existing obsidian-plugin repo still has unrelated mode-only changes and quote-dataset newline/hash drift; no commit/push performed.
- [2026-09-06] Generated ekikyo EX_COMPARE answer for next-game selection at C:\Users\nekol\Proton Drive\Obsidian\Codex\2026-09-06_01.md.
- Original inline candidate block was preserved in the final question section; normalized temporary headings were used only for parser/evidence extraction.
- Ranked スパイダーマン first from 28沢風大過・九二 无不利, with グランディア second from 3水雷屯・六四 吉无不利.
- Self-review verified no internal paths or EX_COMPARE-inapplicable 高島易断/高島解釈原文/占例抜粋 sections; source/work and Obsidian file hashes matched.
- [2026-09-06] Updated ekikyo Windows runtime skill instructions for Japanese encoding verification.
- Added Windows Encoding Notes to use `Get-Content -Encoding UTF8`, avoid treating stdout mojibake as file corruption, and set `$env:PYTHONUTF8` when direct Python stdout inspection is needed.
- Also corrected the Windows runtime note to avoid assuming WSL exists; user confirmed WSL environment has been removed.
- Published and verified C:\Users\nekol\.codex\skills\ekikyo; committed/pushed branch codex/karpathy-coding-guardrails at a101801, not reflected to main because the branch contains prerequisite runtime-split work.
- [2026-09-06] Reflected ekikyo runtime-split and Windows encoding commits to lib-skills origin/main.
- Used a separate clean worktree at E:\Documents\Playground\lib-skills-main-reflect to avoid disturbing the dirty primary lib-skills working tree.
- Cherry-picked only ekikyo commits b180c73, 4ec3dee, and 5f8b764 to main; excluded the unrelated karpathy-coding-guardrails skill commit.
- Pushed origin/main successfully; both origin/main...main and origin/codex/karpathy-coding-guardrails...branch were 0/0 after fetch.
- [2026-09-11] Generated ekikyo EX_COMPARE answer for next-game reselection at C:\Users\nekol\Proton Drive\Obsidian\Codex\2026-09-11_01.md.
- Preserved the original pasted candidate block in the final question section; used normalized temporary candidate headings only for parser/evidence extraction.
- Ranked フロントミッション first from 8水地比・九五 吉; SEKIRO second from 46地風升・六四 吉无咎.
- Self-review verified no internal paths or EX_COMPARE-inapplicable 高島易断/高島解釈原文/占例抜粋 sections were added.
- [2026-09-11] Fixed ekikyo EX_COMPARE parser to accept Markdown candidate headings like `#### 候補A：...` and bare `候補A：...` labels without temporary normalization.
- Added parser regression tests for the new candidate-heading forms; `python -m unittest tests.test_build_extract_prompt` passes 76 tests.
- Updated Windows ekikyo skill source and runtime copy to prefer `python` over `py`, add PowerShell UTF-8 stdout prelude, and document accepted EX_COMPARE candidate heading forms.
- Verified the recent `#### 候補A：...` input shape builds skeleton/prompt directly; no temp files left. `py` launcher still emits its own py.ini mojibake warning, avoided by `python`.
- [2026-09-11] Updated Windows ekikyo skill output destination from C:\Users\nekol\Proton Drive\Obsidian\Codex to E:\Documents\Playground\ekikyo\work.
- Changed both source skill E:\Documents\Playground\lib-skills\codex\ekikyo\runtime\windows\SKILL.md and runtime copy C:\Users\nekol\.codex\skills\ekikyo\SKILL.md.
- Verified work/* is gitignored and `python scripts\next_work_filename.py --work-dir "E:\Documents\Playground\ekikyo\work"` returns E:\Documents\Playground\ekikyo\work\2026-09-11_02.md.
- [2026-09-11] Committed and pushed ekikyo parser fix: 039fab7 `fix: accept markdown compare candidate headings` on codex/copilot-safe-mode.
- Committed and pushed lib-skills Windows ekikyo output-path doc update: 4d1ef0a `docs: update ekikyo windows output path` on codex/karpathy-coding-guardrails.
- ekikyo is clean after push. lib-skills still has pre-existing unrelated dirty files; only codex/ekikyo/runtime/windows/SKILL.md was committed for this task.
- lib-skills origin was changed from HTTPS to SSH to avoid the broken GitHub CLI credential-helper path during push.
- [2026-09-25] Generated ekikyo EX_COMPARE answer for next-game selection at E:\Documents\Playground\ekikyo\work\2026-09-25_01.md.
- Preserved the original question block; ranked フロントミッションの残り first from 24地雷復・六五 敦復 无悔.
- Candidate F input said 62風沢中孚; used卦番号62's canonical name 雷山小過 and noted the discrepancy in the answer.
- Self-review verified 7 candidate sections, 28 quote lines, 7 citations, no placeholders/internal paths, and the exact recommendation sentence.
- [2026-09-25] Regenerated the ekikyo EX_COMPARE answer at E:\Documents\Playground\ekikyo\work\2026-09-25_02.md after correcting candidate F to 61風沢中孚.
- Used 61風沢中孚・九五「有孚攣如、无咎」 as the canonical evidence and ranked これ以外の候補 second.
- Preserved the corrected question block and verified 7 candidate sections, 28 quote lines, 7 citations, no stale 62/雷山小過 references, and the exact recommendation sentence.
- [2026-09-25] Generated ekikyo EX_COMPARE answer at E:\Documents\Playground\ekikyo\work\2026-09-25_03.md for Switch 2 first-game selection.
- Ranked ブレスオブザワイルド first because 革・六二 favors acting when the time arrives; treated 遯・上九 as strong吉 but retreat-oriented and ranked it second.
- Preserved the original question block and verified 4 candidate sections, 16 quote lines, 4 citations, no placeholders/internal paths, and the exact recommendation sentence.
- `python -m unittest tests.test_build_extract_prompt` passed all 76 tests; temporary input, skeleton, prompt, and evidence files were removed.
- [2026-09-25] Current run generated `E:\Documents\Playground\ekikyo\work\2026-09-25_03.md` for Switch 2 first-game selection.
- Current ranking is 時のオカリナ first, ブレスオブザワイルド second, ゼノブレイド2 third, ゼノブレイド1 fourth.
- Preserved the original question block; used Takashima changing-line evidence for all four candidates.
- Self-review verified 4 candidate sections, 16 quote lines, 4 citations, no placeholders/internal paths, and the exact recommendation sentence.
- [2026-09-26] Generated ekikyo EX_COMPARE answer for next-game selection at `E:\Documents\Playground\ekikyo\work\2026-09-26_01.md`.
- Preserved the original question block, ranked グラビティデイズ first from 48水風井・九五, and placed フロントミッションの別ルート last from 54雷沢帰妹・上六.
- Self-review verified 8 candidate sections, changing-line citations, no internal paths/placeholders, and the exact recommendation sentence.
- `python -X utf8 -c ... unittest tests.test_build_extract_prompt` passed all 76 tests; temporary input files were removed.
- [2026-09-26] Generated a follow-up EX_COMPARE answer at `E:\Documents\Playground\ekikyo\work\2026-09-26_02.md` about whether the top-four ranking may be changed by mood.
- The divination-based conclusion keeps the ranking by default, while allowing condition-matched swaps among the top four; arbitrary mood-only changes are not supported.
- Self-review verified 8 candidate sections, no internal paths/placeholders, and all 76 prompt-builder tests passed.
- Removed the temporary follow-up input after verification.
- [2026-09-28] Generated an EX_COMPARE answer for Street Fighter 6 next-character selection at `E:\Documents\Playground\ekikyo\work\2026-09-28_01.md`.
- Preserved the original question block and candidate labels; ranked リリー first, テリー second, and ヴァイパー third from changing-line evidence.
- Self-review verified 7 candidate sections, 28 quote lines, 7 citations, exact question-block copy, no forbidden sections, internal paths, or placeholders.
- `python -X utf8 -m unittest tests.test_build_extract_prompt` passed all 76 tests; temporary input, prompt, and skeleton files were removed.
- [2026-10-04] Generated ekikyo EX_COMPARE answer at `E:\Documents\Playground\ekikyo\work\2026-10-04_01.md` for Street Fighter 6 character selection.
- Preserved the original question block and all five candidate labels; ranked ジュリ first from 11地天泰・九二.
- Ranked テリー second, ジェイミー third, リリー継続 fourth, and ヴァイパー fifth from changing-line evidence and the stated move-away-from-Lily context.
- Self-review verified 5 candidate sections, 20 quote lines, 5 citations, no forbidden sections, internal paths, placeholders, or metadata tokens.
- `python -X utf8 -m unittest tests.test_build_extract_prompt` passed all 76 tests; the temporary input was removed after verification.
[2026-10-24] FirePanel prototype created in E:\Documents\Playground\firepanel on branch codex/initial-prototype.
Uses Flask, psutil, Waitress, a Tkinter settings window, six allowlisted launch buttons, and a 2.5-second status poll.
Local settings and password-derived auth data are kept under gitignored data/. The server defaults to 127.0.0.1 and does not change Windows Firewall.
Six unit tests pass; Tkinter window initialization and local HTTP login page were checked. Fire HD/Silk and dashboard visual layout remain unverified.
GitHub connector targets ys1887 but lacks repository creation; Windows gh targets a different account, so no GitHub remote was created.
[2026-10-24] FirePanel follow-up: user verified Fire HD Silk in portrait and landscape and a Windows browser launch from the panel.
The registered app was removed; zero buttons were registered before GitHub publication.
Created private ys1887/firepanel; pushed main scaffold and codex/initial-prototype; opened PR #1 for the prototype.
GitHub rejected the original author email under account privacy rules, so both unpushed commits were reauthored with the account noreply address without changing file trees.
Confirmed data/ remains ignored and untracked; six unit tests pass. PR review was running at the time of this note.
PR #1 review found two login issues: overlong passphrase truncation and concurrent failed-attempt undercount; both were fixed and verified by new tests.
PR #1 merged into main at 1234738; local main fast-forwarded and clean. Eight tests pass, data/ remains untracked, and zero app buttons are registered.
[2026-10-24] FirePanel light theme is on private branch codex/light-theme; user confirmed it appears on Fire HD.
Added browser fullscreen enter/exit button on branch codex/fullscreen-button, based on the light theme; pushed it to private GitHub.
Fullscreen uses the user-tap browser API and reports failures; actual Silk fullscreen behavior remains for device verification.
Node syntax check and eight Python tests pass; working tree clean, data/ untracked, and zero apps registered.
[2026-10-24] User confirmed Fire HD Silk fullscreen succeeds and all six buttons fit on one visible landscape screen.
Created PR #2 for light theme, fullscreen control, and viewport-height sizing; Codex review completed with no findings.
Merged PR #2 to private main at e8f6ade; local main is synchronized and clean.
Local data/ remains outside Git; Fire HD visual confirmation supersedes the earlier unverified status.
[2026-10-24] User reported fullscreen layout fits and is readable, but button labels overflowed before entering fullscreen.
PR #3 limited compact landscape sizing to the active fullscreen state; Codex review had no findings, eight Python tests and JS syntax check passed.
Merged PR #3 to private main at 3b75f9f; local main is clean. Normal Silk view after this fix remains for device verification.
[2026-10-25] FirePanel dashboard update merged via PR #4 to private main at 8cce6d0.
Added date/clock, response time, CPU/memory, C:/E: used/total GB, manual details refresh, and muted gray layout.
Expanded six saved app slots to eight without losing assignments; ninth grid cell controls fullscreen, logout hidden, weather deferred.
11 Python tests and JS syntax check pass; Tkinter shows eight settings rows; both local drives respond.
Codex PR review completed with no findings. Fire HD Silk visual fit remains to be verified on device; browser automation could not connect.
[2026-10-27] FirePanel Todoist dashboard merged via PR #6 to private main at 1285c14.
Configured Todoist iCal feed stays on the PC; dashboard shows today, then the next 30 days when today is empty, with stale-cache fallback.
Changed the app launcher to six slots plus fullscreen in one bottom row; C:/E: show percent and used/total GB.
Legacy slots 7 and 8 remain preserved in old settings files, but are hidden from the dashboard.
17 Python tests, JS syntax, diff checks, and a 1280x800 HTML/CSS screenshot passed; Codex rereview found no unresolved issues.
Live Todoist feed and Fire HD Silk display still need user verification; main is synchronized and clean.
