---
name: obsidian-vault-checkpoint
description: Create a protective local Git checkpoint commit before AI edits Markdown inside an Obsidian vault. Use when the user asks to run an Obsidian checkpoint, protect a vault before editing, or make a pre-edit commit from anywhere inside the vault.
metadata:
  short-description: Protect an Obsidian vault before AI edits
---

# Obsidian Vault Checkpoint

## Purpose
- Create a local checkpoint commit before AI edits Markdown in an Obsidian vault.
- Work from the current directory or any subfolder inside the vault.

## Use This Skill When
- The user asks for a checkpoint before editing Obsidian notes.
- The user says `/obsidian-vault-checkpoint` or names this skill explicitly.
- The request involves editing Markdown inside an Obsidian vault protected by local Git.

## Workflow
1. Run `py scripts\obsidian_vault_checkpoint`.
2. If the script reports `No commit needed`, continue with the requested work.
3. If the script creates a commit, continue with the requested work after reporting the checkpoint.
4. If the script reports that the current directory is not inside an Obsidian vault Git repo, stop and report the reason.

## Script
- `scripts/obsidian_vault_checkpoint`

## Notes
- The script looks up the Git root from the current directory.
- The Git root must contain `.obsidian/` to qualify as an Obsidian vault.
- The script stages all non-ignored changes and creates a local commit with the fixed message `checkpoint: before AI markdown edit`.
- The helper is Windows-native Python and should be run with `py` in Codex desktop sessions.
