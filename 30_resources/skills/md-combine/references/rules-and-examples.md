# Rules and Examples

## Ordering
- Input files are read from `--in-dir` (direct children only).
- Only `.md` files are processed.
- Files are sorted by natural key: first numeric token, then lowercase name.

## Group Selection
- `--group-size N`: split sorted files into fixed-size chunks.
- `--groups "a-b,c-d"`: select explicit 1-based index ranges from the sorted list.
- Range bounds are inclusive.

## Heading Transformation
- Each output starts with `# <prefix>_<suffix>`.
- Body headings are demoted one level outside code fences:
  - `# A` -> `## A`
  - `## B` -> `### B`
- Inside fenced blocks (``` or ~~~), heading markers are preserved.

## Suffix Inference
- `auto-range` mode (default):
  - Use first numeric token from first file and last numeric token from last file.
  - Example: `2.md..5.md` -> suffix `2-5`
  - Example: `繋辞上伝_1-4.md..繋辞上伝_9-12.md` -> suffix `1-12`
- If numeric inference fails, fallback suffix is ordinal (`1`, `2`, ...).

## Safety
- Source files are never edited.
- `--dry-run` prints planned outputs without writing files.
- Duplicate output names are blocked with an error.
