from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class IchingDivError(Exception):
    """Base exception for Takashima-source prompt building."""


class ValidationError(IchingDivError):
    """Raised when user input or local metadata is invalid."""


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    asset_root: Path
    citation_prefix: str
    interpretation_label: str


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def formats_root() -> Path:
    return repo_root() / "formats"


def canonical_quotes_root() -> Path:
    return repo_root() / "assets" / "quotes"


def _provider(name: str) -> ProviderConfig:
    root = repo_root() / "assets" / name
    return ProviderConfig(
        name=name,
        asset_root=root,
        citation_prefix="takashima",
        interpretation_label="高島解釈",
    )


def takashima_provider() -> ProviderConfig:
    return _provider("takashima")


def load_format(name: str) -> str:
    path = formats_root() / name
    if not path.is_file():
        raise ValidationError(f"format fragment not found: {path}")
    return path.read_text(encoding="utf-8").strip()
