from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from iching_sdk.config import ConfigError


@dataclass(frozen=True)
class SplitHexagramSource:
    number: int
    name: str
    source_file: str
    folder_name: str
    sections: dict[str, str]


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid profile metadata JSON: {path}") from exc


def load_split_catalog(root: Path) -> dict[int, SplitHexagramSource]:
    index_path = root / "index.json"
    if not index_path.is_file():
        raise ConfigError(f"missing split source index: {index_path}")
    raw_index = _read_json(index_path)
    if not isinstance(raw_index, list):
        raise ConfigError(f"invalid split source index payload: {index_path}")

    catalog: dict[int, SplitHexagramSource] = {}
    for entry in raw_index:
        if not isinstance(entry, dict):
            raise ConfigError(f"invalid split source index entry in {index_path}")
        raw_number = entry.get("number")
        raw_name = entry.get("name")
        raw_folder_path = entry.get("folder_path")
        if not isinstance(raw_number, int) or not isinstance(raw_name, str):
            raise ConfigError(f"invalid split source index entry in {index_path}")
        if not isinstance(raw_folder_path, str) or not raw_folder_path:
            raise ConfigError(f"invalid split source folder_path in {index_path}")

        folder_name = Path(raw_folder_path).name
        manifest_path = root / folder_name / "manifest.json"
        if not manifest_path.is_file():
            raise ConfigError(f"missing split source manifest: {manifest_path}")
        raw_manifest = _read_json(manifest_path)
        if not isinstance(raw_manifest, dict):
            raise ConfigError(f"invalid split source manifest payload: {manifest_path}")

        source_file = raw_manifest.get("source_file")
        sections = raw_manifest.get("sections")
        if not isinstance(source_file, str) or not source_file:
            raise ConfigError(f"invalid source_file in split source manifest: {manifest_path}")
        if not isinstance(sections, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in sections.items()
        ):
            raise ConfigError(f"invalid sections in split source manifest: {manifest_path}")

        catalog[raw_number] = SplitHexagramSource(
            number=raw_number,
            name=raw_name,
            source_file=source_file,
            folder_name=folder_name,
            sections=dict(sections),
        )
    return catalog


def list_split_citation_files(root: Path) -> list[str]:
    catalog = load_split_catalog(root)
    return [catalog[number].source_file for number in sorted(catalog)]
