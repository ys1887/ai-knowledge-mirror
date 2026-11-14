from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from profiles import ProviderConfig, ValidationError


@dataclass(frozen=True)
class SplitSource:
    number: int
    name: str
    source: str
    source_file: str
    folder_name: str
    sections: dict[str, str]
    special_sections: dict[str, bool]


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing metadata file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON metadata: {path}") from exc


def load_split_catalog(provider: ProviderConfig) -> dict[int, SplitSource]:
    index_path = provider.asset_root / "index.json"
    raw_index = _read_json(index_path)
    if not isinstance(raw_index, list):
        raise ValidationError(f"invalid split index payload: {index_path}")

    catalog: dict[int, SplitSource] = {}
    for entry in raw_index:
        if not isinstance(entry, dict):
            raise ValidationError(f"invalid split index entry in {index_path}")
        number = entry.get("number")
        name = entry.get("name")
        folder_path = entry.get("folder_path")
        special_sections = entry.get("special_sections", {})
        if not isinstance(number, int) or not isinstance(name, str) or not isinstance(folder_path, str):
            raise ValidationError(f"invalid split index entry in {index_path}")
        if not isinstance(special_sections, dict) or not all(
            isinstance(key, str) and isinstance(value, bool)
            for key, value in special_sections.items()
        ):
            raise ValidationError(f"invalid special_sections in {index_path}")

        folder_name = Path(folder_path).name
        manifest_path = provider.asset_root / folder_name / "manifest.json"
        raw_manifest = _read_json(manifest_path)
        if not isinstance(raw_manifest, dict):
            raise ValidationError(f"invalid split manifest payload: {manifest_path}")

        source = raw_manifest.get("source")
        source_file = raw_manifest.get("source_file")
        sections = raw_manifest.get("sections")
        if not isinstance(source, str) or not isinstance(source_file, str):
            raise ValidationError(f"invalid manifest header: {manifest_path}")
        if not isinstance(sections, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in sections.items()
        ):
            raise ValidationError(f"invalid manifest sections: {manifest_path}")

        catalog[number] = SplitSource(
            number=number,
            name=name,
            source=source,
            source_file=source_file,
            folder_name=folder_name,
            sections=dict(sections),
            special_sections=dict(special_sections),
        )
    return catalog
