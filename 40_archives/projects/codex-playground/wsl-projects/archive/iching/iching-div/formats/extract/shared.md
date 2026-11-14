# EXTRACT shared rules (split-source v1)

- v1 implements only `EXTRACT`.
- If the input says `[MODE:GENERAL]`, stop with the unimplemented error from the preprocessing layer.
- If `MODE` is missing, stop with an error.
- If `EXTRACT` has no `TEMPLATE`, stop with an error.
- Use only the provided citation paths and internal section paths.
- Final answer reference lines must use citation paths only.
- Internal section paths must never appear in the final answer.
- Treat the final answer as a user-facing deliverable, not as a debug dump of the preprocessing result.
- Do not include execution metadata such as `skill used: ...`, profile banners, tool banners, or similar run annotations in the final answer.
- Never echo `provider=...`, `role=...`, `visibility=...`, or raw section names in the final answer.
- Always start with `**核心・結論**` and then follow the required section order for the active template.
- Keep the final answer fully in Japanese.
- If evidence is missing, stop with a short insufficiency report instead of filling gaps from general knowledge.
- Do not guess when source evidence is missing.
- Canonical answers in `examples/extract/` are structural references only, not text to copy.
- Use the canonical answers only to understand section order, label shape, and answer density.
