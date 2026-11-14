# AGENTS.md

Your operating manual for this workspace, written by you. Your main instructions cover how you work in general. This file is where you keep the specific, durable lessons and conventions you pick up as you work, the kind of thing you'd want a future session to know. It's not about the user (that goes in `USER.md` and your memory) or your personality (that's `SOUL.md`); it's about how you get work done here.

## Conventions
Add an entry whenever you work something out worth keeping, for example:
- a convention you've settled on ("keep data exports in `workspace/exports/` and clean them up monthly")
- a tool or site quirk worth remembering ("site X hides its form behind a cookie banner; dismiss it first")
- a workflow that worked, or a mistake not to repeat

It starts empty and is meant to grow slowly. Don't pad it; a short, accurate file beats a long, stale one.

- SOUL.md and MEMORY.md are kept in Japanese (user-facing). Living English mirrors live in `~/workspace/en-mirror/` (SOUL.md, MEMORY.md): whenever you edit either Japanese file, apply the same change to its English mirror in the same session. Pre-translation English snapshots from 2026-11-02 are in `~/workspace/backups/2026-11-02/` and are not mirrors.
- Document creation: follow the Digital Agency Design System-inspired structure recorded in MEMORY.md (key points first, numbered headings, period/scope/readers defined up front, chart axes from 0, derived metrics with calculation basis and caveats, issues paired 1:1 with proposals, decision items stated at the end).

## Proven patterns

- Reusable procedures and formats that demonstrably worked (stage reports, user-run procedure sheets, proof-of-read verification, controlled comparisons, research briefs, trial-then-schedule, multi-AI arbitration for Ekikyo, avatar image generation, the operations loop of section 9: generalisation gate, monthly permission inventory, scheduled-job guards) are collected in `~/workspace/playbook.md`. Consult it when a task matches one of those shapes, and add a pattern there when it proves itself in practice.

## Lessons from the 2026-11-04 review of past mistakes (all 12 chats read back)

- Never assert a negative ("does not exist", "cannot be fetched", "cannot be used") from one source or one route: enumerate the routes first (docs + connector catalog + official announcements; web + API + CLI; main path + plugins/alternatives) and check each before concluding. The OpenCode Go shared-pool error recurred in three chats because official doc wording was trusted without support answers / issue reports of actual behaviour.
- Cross-check stated specs against observed behaviour (support answers, issue reports, logs) before asserting them; treat on-screen fit/recommended badges as estimates, and say "decided" only after the real action (registration, execution) passes.
- Every completion report states what was verified and what remains unverified. Verify deliverables as the recipient receives them (attachment content, saved file at the specified path), not by the source file's existence; for external-service settings, confirm the effect, not just the save screen.
- Record numbers and conditions with their source (the user himself / a third party / my estimate / my derivation). A third party's terms quoted by the user are not the user's terms. Derived figures are labelled as derived, with the calculation. Deltas use only the user's latest measured values, never old snapshots.
- Check identity (images, posts, accounts) against the actual item, not against remembered context. When merging results from multiple routes, mechanically check for duplicated URLs/IDs. Keep secondary summaries labelled as leads; classify (in use / intention / under consideration) from the original wording.
- Troubleshooting: include my own side (connection method, tooling) as a suspect from the start; say "cause confirmed" only after a re-test passes. If a value does not change when acted on, question how the value is computed instead of repeating the same remedy. For UI problems, reset state (restart/reload) before declaring a route closed, and confirm a control is actually enabled before prescribing it.
- Config files handed over in full: proofread separators mechanically, and prefer separator-independent syntax (e.g. sshd_config `Key=Value`).
- Proofread Japanese output for stray foreign-script tokens before sending: on 2026-11-08 the Korean word “맡せる” slipped in where 「任せる」 belonged, and later the same day the Chinese word “清单” slipped in where 「一覧」 belonged (user caught both). Scan for Hangul and for Chinese-only forms/tokens mixed into Japanese text as a final check.
- Recommendations state their premises and the conditions that would flip the conclusion up front, instead of concluding from the user's current usage alone. When adopting a standard, present material by what the user treats as authoritative (e.g. reproducibility of the reference implementation), not by how many readers agree.
- Rules the user sets are applied by intent, not literal wording, and propagated to all chats (the あなた-only reference rule was first read as covering direct address only). Before proposing to do a check or a connection on the user's behalf, confirm whether they want to do it themselves.
- Research that feeds a decision carries a deadline; once the decision is made, stop pending research on it instead of delivering it late. Before reporting a topic in the main chat, check its dedicated side chat for what is already decided (already a standing rule since 2026-11-03; the failure was not following it).

## Rules adopted on 2026-11-06 from the technical overview "個人用AIエージェント運用環境の設計と実践"

- Transcribed material is never copied by hand: anything that must match a canonical source (code excerpts, quotations, figures, setting values) is cut mechanically from the canonical file itself. On acceptance, compare character by character; a structural match is not a substitute for exactness.
- Three-route exploration: when a core element cannot be used the usual way, explore at least three routes before judging — (1) an official alternative entrance, (2) fact extraction from primary sources, (3) redefinition by recombining the spec — instead of settling for a substitute workaround. This spells out the route enumeration already required before asserting a negative.
