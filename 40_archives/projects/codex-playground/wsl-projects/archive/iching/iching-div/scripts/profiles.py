from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class IchingDivError(Exception):
    """Base exception for split-source prompt building."""


class ValidationError(IchingDivError):
    """Raised when user input or local metadata is invalid."""


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    asset_root: Path
    interpretation_root: Path
    citation_prefix: str
    interpretation_label: str


@dataclass(frozen=True)
class ProfileConfig:
    name: str
    providers: tuple[ProviderConfig, ...]
    final_sections: tuple[str, ...]
    compare_takashima_support_only: bool = False


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def formats_root() -> Path:
    return repo_root() / "formats" / "extract"


def canonical_quotes_root() -> Path:
    return repo_root() / "assets" / "canonical" / "quotes"


def _provider(name: str) -> ProviderConfig:
    root = repo_root() / "assets" / "split" / name
    interpretation_root = repo_root() / "assets" / "canonical" / "interp" / name
    citation_prefix = "honda_wataru" if name == "honda" else "takashima_zouho"
    interpretation_label = "本田解釈" if name == "honda" else "高島解釈"
    return ProviderConfig(
        name=name,
        asset_root=root,
        interpretation_root=interpretation_root,
        citation_prefix=citation_prefix,
        interpretation_label=interpretation_label,
    )


PROFILES = {
    "legacy": ProfileConfig(
        name="legacy",
        providers=(_provider("honda"), _provider("takashima")),
        final_sections=("本田解釈", "高島解釈"),
        compare_takashima_support_only=True,
    ),
    "honda": ProfileConfig(
        name="honda",
        providers=(_provider("honda"),),
        final_sections=("本田解釈",),
    ),
    "takashima": ProfileConfig(
        name="takashima",
        providers=(_provider("takashima"),),
        final_sections=("高島解釈",),
    ),
}


def resolve_profile(profile_name: str) -> ProfileConfig:
    profile = PROFILES.get(profile_name)
    if profile is None:
        available = ", ".join(sorted(PROFILES))
        raise ValidationError(f"unknown profile: {profile_name} (available: {available})")
    return profile


def load_format(name: str) -> str:
    path = formats_root() / name
    if not path.is_file():
        raise ValidationError(f"format fragment not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def load_template_format(profile_name: str, template: str) -> str:
    variant = "legacy" if profile_name == "legacy" else "single"
    filename = f"{template.lower()}_{variant}.md"
    return load_format(filename)
