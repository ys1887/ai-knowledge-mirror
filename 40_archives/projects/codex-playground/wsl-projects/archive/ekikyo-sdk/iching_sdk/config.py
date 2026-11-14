from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


MODE_NAME = "extract"
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
    path: str | None = None
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
    def codex_path(self) -> str | None:
        return self.provider_config("codex").path

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
    codex_path: str | None
    codex_model: str | None
    codex_sandbox: str | None
    codex_approval_policy: str | None


TAKASHIMA_EXTRACT_ROOT = "assets/extract_takashima_split"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def runtime_config_path() -> Path:
    return repo_root() / "iching.toml"


def resolve_sources_root(override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / "assets"


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

    allowed_keys = {"path", "model", "sandbox", "approval_policy"}
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
                path=codex_settings.get("path"),
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
        codex_path=provider_config.path,
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


def load_mode_config(
    mode: str,
    sources_root_override: str | None,
) -> ModeConfig:
    if mode != MODE_NAME:
        raise ConfigError(f"unsupported mode: {mode}")
    if sources_root_override:
        mode_root = Path(sources_root_override).expanduser().resolve()
    else:
        mode_root = (repo_root() / TAKASHIMA_EXTRACT_ROOT).resolve()
    index_file = (mode_root / "index.json").resolve()
    if not mode_root.is_dir():
        raise ConfigError(f"missing sources directory: {mode_root}")
    if not index_file.is_file():
        raise ConfigError(f"missing index file: {index_file}")
    return ModeConfig(mode=mode, sources_root=mode_root, index_file=index_file)
