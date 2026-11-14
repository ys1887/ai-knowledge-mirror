from __future__ import annotations

import json
from pathlib import Path

from iching_sdk.config import ConfigError, ModeConfig


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def parse_index(config: ModeConfig) -> list[str]:
    try:
        payload = json.loads(config.index_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid index JSON: {config.index_file}") from exc
    if not isinstance(payload, list):
        raise ConfigError(f"index JSON must be an array: {config.index_file}")

    section_files: list[str] = []
    seen_files: set[str] = set()
    for entry in payload:
        if not isinstance(entry, dict):
            raise ConfigError(f"invalid index entry in {config.index_file}: expected object")
        folder_path = entry.get("folder_path")
        if not isinstance(folder_path, str) or not folder_path:
            raise ConfigError(f"invalid index entry in {config.index_file}: missing folder_path")
        if Path(folder_path).is_absolute():
            raise ConfigError(f"absolute path not allowed in index: {folder_path}")
        target = (config.sources_root / folder_path).resolve()
        if not is_relative_to(target, config.sources_root):
            raise ConfigError(f"index entry escapes source root: {folder_path}")
        if not target.is_dir():
            raise ConfigError(f"indexed folder does not exist: {folder_path}")
        if folder_path in seen_files:
            raise ConfigError(f"duplicate index entry: {folder_path}")
        seen_files.add(folder_path)
        section_files.append(folder_path)
    return section_files
