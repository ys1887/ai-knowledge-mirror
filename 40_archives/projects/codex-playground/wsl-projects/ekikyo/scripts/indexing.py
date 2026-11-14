from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from profiles import ProviderConfig, ValidationError


SOURCE_FILE_RE = re.compile(r"^(?P<number>0?[1-9][0-9]?)_(?P<name>.+)\.md$")


@dataclass(frozen=True)
class TakashimaSource:
    number: int
    name: str
    source: str
    source_file: str
    file_path: Path


def load_takashima_catalog(provider: ProviderConfig) -> dict[int, TakashimaSource]:
    if not provider.asset_root.is_dir():
        raise ValidationError(f"missing source directory: {provider.asset_root}")

    catalog: dict[int, TakashimaSource] = {}
    for path in sorted(provider.asset_root.glob("*.md")):
        match = SOURCE_FILE_RE.match(path.name)
        if match is None:
            raise ValidationError(f"invalid source filename: {path}")
        number = int(match.group("number"))
        name = match.group("name")
        source_file = f"{provider.citation_prefix}/{path.name}"
        catalog[number] = TakashimaSource(
            number=number,
            name=name,
            source=provider.citation_prefix,
            source_file=source_file,
            file_path=path,
        )

    if not catalog:
        raise ValidationError(f"no Takashima source files found in {provider.asset_root}")
    return catalog
