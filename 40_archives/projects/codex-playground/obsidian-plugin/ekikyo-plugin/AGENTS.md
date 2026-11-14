# Repo Working Rules

This repository manages the Obsidian plugin and the data bundle used by the plugin. Some source data is also maintained in the related ekikyo project, so data edits should keep both locations aligned.

## Data Locations

- Related project assets:
  - `E:\Documents\Playground\ekikyo\assets`
- Plugin repo generation input:
  - `E:\Documents\Playground\obsidian-plugin\ekikyo-plugin\vendor\ekikyo\assets`
- Obsidian plugin deployment target is:
  - `C:\Users\nekol\Proton Drive\Obsidian\.obsidian\plugins\ekikyo`

Treat `vendor/ekikyo/assets` as the plugin repo's generation input. The related project assets and this plugin repo should be compared before data edits so the current edited location is clear.

## Data Sync Rules

- For data changes, check both `E:\Documents\Playground\ekikyo\assets` and `vendor\ekikyo\assets` before editing or syncing.
- Prefer editing the location the user has already changed. If the user asks to edit in this repo, update `vendor\ekikyo\assets` and sync the corresponding change back to `E:\Documents\Playground\ekikyo\assets` when appropriate.
- If any of the following source files changed, sync the corresponding files between both asset locations before doing anything else:
  - `本文抜粋.md`
  - `占断抜粋.md`
  - `高島易断占例.md`
  - `takashima/`
- After syncing any of those files, regenerate:
  - `py scripts\generate_quote_dataset.py`
- After regeneration, sync the resulting `data/quote-dataset.json` to the Obsidian plugin deployment target as part of the normal workflow.

## Direct Edit Policy

- Safe to edit directly in this repo:
  - plugin implementation files such as `main.js`, `manifest.json`, `package.json`, `versions.json`
  - repo-local documentation such as `README.md` and `AGENTS.md`
- Avoid direct manual edits to:
  - `vendor/ekikyo/assets`
  - `data/quote-dataset.json`

If a user asks to update source data, the default workflow is:

1. confirm where the current source change exists
2. sync the change between `E:\Documents\Playground\ekikyo\assets` and `vendor\ekikyo\assets` as needed
3. regenerate `data/quote-dataset.json`
4. sync to the Obsidian plugin deployment target
5. commit and push only if the user asked for publish steps
