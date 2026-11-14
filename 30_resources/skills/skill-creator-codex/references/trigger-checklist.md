# Trigger Checklist

Use this after drafting or updating a skill.

## Positive Trigger Review

- Does the description say what the skill does?
- Does it say when to use it?
- Does it include phrases a user would plausibly say?
- Would it trigger for "create", "update", and "improve" variants when those are in scope?
- Does the wording mention Codex or the target environment when that distinction matters?

## Negative Trigger Review

- Could the description steal requests meant for `skill-installer`?
- Could it trigger on ordinary coding tasks that are not about skills?
- Could it trigger on generic Claude discussions with no Codex artifact to produce?
- Is the description using vague words like "help", "workflow", or "projects" without domain anchors?

## Manual Prompt Set

Review at least these cases:

- "Create a Codex skill for X."
- "Update this existing skill so Codex triggers it correctly."
- "Fix the frontmatter and metadata for this skill."
- "Prepare this skill for Codex runtime deployment."
- "List available skills I can install."
- "Install this skill from GitHub."
- "Implement this feature in the repo."
- "Explain how Claude skills work."

The first four should lean toward this skill. The latter four should not.
