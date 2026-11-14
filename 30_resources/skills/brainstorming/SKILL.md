---
name: brainstorming
description: 曖昧なアイデアを実装しやすい設計案に整理するskill。
---

# Brainstorming (Codex)

## Purpose
Turn rough ideas into implementation-ready designs before coding. Clarify intent, constraints, and success criteria, then produce a practical design artifact the team can execute.

## When to Use
- Before starting a new feature, UI flow, or behavior change.
- When requirements are ambiguous or conflicting.
- When multiple implementation directions are possible.
- When you need to reduce rework by validating design early.

## Conversation Protocol
- Start by checking project context (relevant files, docs, and current behavior).
- Ask one question per turn.
- Prefer multiple-choice questions when possible; use open-ended only when needed.
- Prioritize clarifying: goal, constraints, non-goals, and definition of success.

## Option Exploration
- Propose 2-3 viable approaches.
- Lead with the recommended option first.
- For each option, include: complexity, risks, scalability, and implementation cost.
- Remove unnecessary scope aggressively (YAGNI).

## Design Output
Present the design in small validated sections and confirm alignment after each section.

Include at minimum:
- Architecture and boundaries
- Components/modules and responsibilities
- Data flow and state transitions
- Error handling and fallback behavior
- Testing strategy (unit/integration/e2e where relevant)
- Rollout or migration considerations (if behavior changes in production)

## Deliverable
- Produce a design document suitable for:
  `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Keep the document concise, actionable, and implementation-ready.
- If implementation continues, convert the design into an ordered task list.

## Principles
- One question at a time
- Prefer explicit trade-offs over vague preferences
- Recommend, then explain why
- Validate incrementally
- Keep scope minimal and practical
