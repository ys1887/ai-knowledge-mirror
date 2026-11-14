from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


MODE_RULE_FILES = {
    "extract": "rules/extract.yaml",
    "general": "rules/general.yaml",
}
ANSWER_PROVIDER_NAMES = ("codex",)
CODEX_SANDBOX_VALUES = ("read-only", "workspace-write", "danger-full-access")
CODEX_APPROVAL_POLICY_VALUES = ("untrusted", "on-failure", "on-request", "never")


class IchingError(Exception):
    """Base SDK exception."""


class ConfigError(IchingError):
    """Raised when the local SDK configuration is invalid."""


class ValidationRuntimeError(IchingError):
    """Raised when validate cannot complete due to runtime errors."""


@dataclass(frozen=True)
class ModeConfig:
    mode: str
    sources_root: Path
    index_file: Path


@dataclass(frozen=True)
class ProviderRuntimeConfig:
    model: str | None = None
    sandbox: str | None = None
    approval_policy: str | None = None


@dataclass(frozen=True)
class RuntimeConfig:
    default_provider: str | None = None
    providers: dict[str, ProviderRuntimeConfig] | None = None

    @property
    def provider(self) -> str | None:
        return self.default_provider

    @property
    def codex_model(self) -> str | None:
        return self.provider_config("codex").model

    @property
    def codex_sandbox(self) -> str | None:
        return self.provider_config("codex").sandbox

    @property
    def codex_approval_policy(self) -> str | None:
        return self.provider_config("codex").approval_policy

    def provider_config(self, provider_name: str) -> ProviderRuntimeConfig:
        if self.providers is None:
            return ProviderRuntimeConfig()
        return self.providers.get(provider_name, ProviderRuntimeConfig())


@dataclass(frozen=True)
class ResolvedRuntimeConfig:
    provider: str | None
    codex_model: str | None
    codex_sandbox: str | None
    codex_approval_policy: str | None


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def runtime_config_path() -> Path:
    return repo_root() / "iching.toml"


def resolve_sources_root(override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / "sources"


def _validate_runtime_config_payload(payload: object, path: Path) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ConfigError(f"invalid runtime config: expected table in {path}")
    allowed_keys = {
        "provider",
        "default_provider",
        "codex_model",
        "codex_sandbox",
        "codex_approval_policy",
        "providers",
    }
    unknown_keys = sorted(set(payload) - allowed_keys)
    if unknown_keys:
        raise ConfigError(
            f"unknown runtime config keys in {path}: {', '.join(unknown_keys)}"
        )
    return payload


def _read_optional_string(
    payload: dict[str, object], key: str, path: Path
) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"invalid runtime config value for {key} in {path}: expected string")
    return value


def _validate_provider_name(provider: str | None, path: Path, key: str) -> None:
    if provider and provider not in ANSWER_PROVIDER_NAMES:
        providers = ", ".join(sorted(ANSWER_PROVIDER_NAMES))
        raise ConfigError(
            f"unknown runtime config provider in {path}: {provider} "
            f"(available providers: {providers})"
        )


def _read_provider_settings(
    payload: dict[str, object], provider_name: str, path: Path
) -> dict[str, str]:
    raw_providers = payload.get("providers")
    if raw_providers is None:
        return {}
    if not isinstance(raw_providers, dict):
        raise ConfigError(f"invalid runtime config value for providers in {path}: expected table")

    unknown_providers = sorted(set(raw_providers) - set(ANSWER_PROVIDER_NAMES))
    if unknown_providers:
        raise ConfigError(
            f"unknown runtime config providers in {path}: {', '.join(unknown_providers)}"
        )

    raw_provider_settings = raw_providers.get(provider_name)
    if raw_provider_settings is None:
        return {}
    if not isinstance(raw_provider_settings, dict):
        raise ConfigError(
            f"invalid runtime config value for providers.{provider_name} in {path}: expected table"
        )

    allowed_keys = {"model", "sandbox", "approval_policy"}
    unknown_keys = sorted(set(raw_provider_settings) - allowed_keys)
    if unknown_keys:
        raise ConfigError(
            "unknown runtime config keys in "
            f"{path} for providers.{provider_name}: {', '.join(unknown_keys)}"
        )

    settings: dict[str, str] = {}
    for key in allowed_keys:
        value = raw_provider_settings.get(key)
        if value is None:
            continue
        if not isinstance(value, str):
            raise ConfigError(
                "invalid runtime config value for "
                f"providers.{provider_name}.{key} in {path}: expected string"
            )
        settings[key] = value
    return settings


def load_runtime_config() -> RuntimeConfig:
    path = runtime_config_path()
    if not path.is_file():
        return RuntimeConfig()
    try:
        raw_payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid runtime config TOML: {path}: {exc}") from exc

    payload = _validate_runtime_config_payload(raw_payload, path)
    legacy_provider = _read_optional_string(payload, "provider", path)
    default_provider = _read_optional_string(payload, "default_provider", path)
    _validate_provider_name(legacy_provider, path, "provider")
    _validate_provider_name(default_provider, path, "default_provider")
    if legacy_provider and default_provider and legacy_provider != default_provider:
        raise ConfigError(
            "conflicting runtime config providers in "
            f"{path}: provider={legacy_provider}, default_provider={default_provider}"
        )

    codex_settings = _read_provider_settings(payload, "codex", path)

    codex_sandbox = _read_optional_string(payload, "codex_sandbox", path)
    if codex_sandbox and codex_sandbox not in CODEX_SANDBOX_VALUES:
        raise ConfigError(
            f"invalid runtime config value for codex_sandbox in {path}: {codex_sandbox}"
        )
    table_codex_sandbox = codex_settings.get("sandbox")
    if table_codex_sandbox and table_codex_sandbox not in CODEX_SANDBOX_VALUES:
        raise ConfigError(
            "invalid runtime config value for providers.codex.sandbox "
            f"in {path}: {table_codex_sandbox}"
        )

    codex_approval_policy = _read_optional_string(payload, "codex_approval_policy", path)
    if codex_approval_policy and codex_approval_policy not in CODEX_APPROVAL_POLICY_VALUES:
        raise ConfigError(
            "invalid runtime config value for codex_approval_policy "
            f"in {path}: {codex_approval_policy}"
        )
    table_codex_approval_policy = codex_settings.get("approval_policy")
    if (
        table_codex_approval_policy
        and table_codex_approval_policy not in CODEX_APPROVAL_POLICY_VALUES
    ):
        raise ConfigError(
            "invalid runtime config value for providers.codex.approval_policy "
            f"in {path}: {table_codex_approval_policy}"
        )

    return RuntimeConfig(
        default_provider=default_provider or legacy_provider,
        providers={
            "codex": ProviderRuntimeConfig(
                model=codex_settings.get("model")
                or _read_optional_string(payload, "codex_model", path),
                sandbox=table_codex_sandbox or codex_sandbox,
                approval_policy=table_codex_approval_policy or codex_approval_policy,
            )
        },
    )


def resolve_runtime_config(
    runtime_config: RuntimeConfig,
    provider_override: str | None,
    codex_model_override: str | None,
    codex_sandbox_override: str | None,
    codex_approval_policy_override: str | None,
) -> ResolvedRuntimeConfig:
    provider = provider_override if provider_override is not None else runtime_config.default_provider
    provider_config = runtime_config.provider_config(provider) if provider else ProviderRuntimeConfig()
    return ResolvedRuntimeConfig(
        provider=provider,
        codex_model=(
            codex_model_override
            if codex_model_override is not None
            else provider_config.model
        ),
        codex_sandbox=(
            codex_sandbox_override
            if codex_sandbox_override is not None
            else provider_config.sandbox
        ),
        codex_approval_policy=(
            codex_approval_policy_override
            if codex_approval_policy_override is not None
            else provider_config.approval_policy
        ),
    )


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    current_section: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        if line.endswith(":") and not line.startswith(" "):
            current_section = line[:-1].strip()
            continue
        if ":" not in line:
            continue
        key_part, value_part = line.split(":", 1)
        key = key_part.strip()
        value = value_part.strip()
        if current_section:
            values[f"{current_section}.{key}"] = value
        else:
            values[key] = value
    return values


def load_mode_config(mode: str, sources_root_override: str | None) -> ModeConfig:
    root = resolve_sources_root(sources_root_override)
    rule_file = repo_root() / MODE_RULE_FILES[mode]
    if not rule_file.is_file():
        raise ConfigError(f"missing rule file: {rule_file}")
    values = parse_simple_yaml(rule_file)
    configured_root = values.get("sources.root")
    configured_index = values.get("sources.index_md")
    if not configured_root or not configured_index:
        raise ConfigError(f"invalid rule file: {rule_file}")

    root_suffix = Path(configured_root).parts[-1]
    mode_root = (root / root_suffix).resolve()
    expected_root = (root / mode).resolve()
    if mode_root != expected_root:
        raise ConfigError(
            f"rule root mismatch for mode {mode}: expected {expected_root}, got {mode_root}"
        )

    index_file = (root.parent / configured_index).resolve()
    if not index_file.is_file():
        raise ConfigError(f"missing index file: {index_file}")
    if not mode_root.is_dir():
        raise ConfigError(f"missing sources directory: {mode_root}")
    return ModeConfig(mode=mode, sources_root=mode_root, index_file=index_file)
