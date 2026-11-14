## Purpose

This directory contains lookup/reference material used by the quote dataset generation workflow.

- `base_hexagrams.json`
  - Runtime input for `scripts/generate_quote_dataset.py`.
  - Do not remove unless the generator is changed accordingly.
- `duanyi.py`
  - Preserved as reference material from the original calculator source.
  - Not loaded by the current plugin runtime or dataset generator.

Keep this directory focused on source-reference files for the generator workflow.
