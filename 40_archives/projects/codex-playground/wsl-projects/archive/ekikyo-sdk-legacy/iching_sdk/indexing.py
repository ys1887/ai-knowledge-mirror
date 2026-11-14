from __future__ import annotations

from pathlib import Path

from iching_sdk.config import ConfigError, MODE_RULE_FILES, ModeConfig


SECTION_HEADERS = {f"### {mode}" for mode in MODE_RULE_FILES}


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def parse_index(config: ModeConfig) -> list[str]:
    section_files: list[str] = []
    seen_modes: set[str] = set()
    current_mode: str | None = None

    for line_number, raw_line in enumerate(
        config.index_file.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        if line in SECTION_HEADERS:
            current_mode = line.removeprefix("### ").strip()
            if current_mode in seen_modes:
                raise ConfigError(
                    f"duplicate index section '{current_mode}' at line {line_number}"
                )
            seen_modes.add(current_mode)
            continue
        if line.startswith("### "):
            raise ConfigError(f"unsupported section header at line {line_number}: {line}")
        if current_mode is None:
            raise ConfigError(f"content before first section at line {line_number}")
        if not line.startswith("- "):
            raise ConfigError(f"invalid index entry at line {line_number}: {line}")

        rel_path = line[2:].strip()
        if not rel_path.endswith(".md"):
            raise ConfigError(f"non-markdown index entry at line {line_number}: {rel_path}")
        if Path(rel_path).is_absolute():
            raise ConfigError(f"absolute path not allowed at line {line_number}: {rel_path}")

        if current_mode == config.mode:
            section_files.append(rel_path)

    missing_sections = {mode for mode in MODE_RULE_FILES if mode not in seen_modes}
    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise ConfigError(f"missing index section(s): {missing}")

    seen_files: set[str] = set()
    for rel_path in section_files:
        if rel_path in seen_files:
            raise ConfigError(f"duplicate index entry for mode {config.mode}: {rel_path}")
        seen_files.add(rel_path)

        target = (config.sources_root / rel_path).resolve()
        if not is_relative_to(target, config.sources_root):
            raise ConfigError(f"index entry escapes source root: {rel_path}")
        if not target.is_file():
            raise ConfigError(f"indexed file does not exist: {rel_path}")

    return section_files
