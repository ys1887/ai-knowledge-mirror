from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable

from iching_sdk.config import ValidationRuntimeError
from iching_sdk.validation import read_input_text

ANSWER_PRESETS = {
    "codex-exec": {"provider": "codex"},
}
ANSWER_PROVIDERS = ("codex",)
PROVIDER_MISSING = "provider_missing"
PROVIDER_AUTH = "provider_auth"
PROVIDER_EXECUTION_FAILED = "provider_execution_failed"
CODEX_AUTH_PATTERNS = (
    "codex login",
    "login required",
    "not authenticated",
    "authentication required",
    "unauthenticated",
    "please authenticate",
)


@dataclass(frozen=True)
class CodexProviderOptions:
    model: str | None = None
    sandbox: str | None = None
    approval_policy: str | None = None

    def to_payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        if self.model:
            payload["model"] = self.model
        if self.sandbox:
            payload["sandbox"] = self.sandbox
        if self.approval_policy:
            payload["approval_policy"] = self.approval_policy
        return payload


@dataclass(frozen=True)
class ProviderDefinition:
    name: str
    build_command: Callable[[CodexProviderOptions | None], list[str]]
    build_options_payload: Callable[[CodexProviderOptions | None], dict[str, str] | None]
    classify_failure: Callable[[int | None, str], tuple[str | None, str]]
    missing_executable: str | None = None
    missing_summary: str | None = None


@dataclass(frozen=True)
class AnswerExecution:
    command: list[str]
    provider: str | None
    provider_options: dict[str, str] | None


@dataclass(frozen=True)
class AnswerResult:
    stdout_text: str
    stderr_text: str
    exit_code: int
    answer_text: str | None
    answer_exit_code: int | None
    resolved_command: list[str] | None
    provider: str | None
    provider_options: dict[str, str] | None
    error_type: str | None
    error_summary: str | None
    raw_stderr: str | None


def format_answer_failure(summary: str) -> str:
    return f"{summary}\n"


def first_stderr_line(stderr_text: str) -> str | None:
    for line in stderr_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def is_codex_auth_failure(stderr_text: str) -> bool:
    if not stderr_text.strip():
        return False
    lowered = stderr_text.lower()
    return any(pattern in lowered for pattern in CODEX_AUTH_PATTERNS)


def classify_codex_failure(
    returncode: int | None,
    stderr_text: str,
) -> tuple[str | None, str]:
    if is_codex_auth_failure(stderr_text):
        return PROVIDER_AUTH, "codex authentication required"
    first_line = first_stderr_line(stderr_text)
    if first_line:
        return (
            PROVIDER_EXECUTION_FAILED,
            f"codex provider failed with exit code {returncode}: {first_line}",
        )
    return (
        PROVIDER_EXECUTION_FAILED,
        f"codex provider failed with exit code {returncode}",
    )


def classify_provider_failure(
    provider: str | None,
    returncode: int | None,
    stderr_text: str,
) -> tuple[str | None, str]:
    definition = PROVIDER_DEFINITIONS.get(provider or "")
    if definition is not None:
        return definition.classify_failure(returncode, stderr_text)
    return None, f"answer command failed with exit code {returncode}"


def list_answer_presets() -> list[str]:
    return sorted(ANSWER_PRESETS)


def build_codex_command(options: CodexProviderOptions) -> list[str]:
    command = ["codex", "exec"]
    if options.model:
        command.extend(["--model", options.model])
    if options.sandbox:
        command.extend(["--sandbox", options.sandbox])
    if options.approval_policy:
        command.extend(["--ask-for-approval", options.approval_policy])
    return command


def build_codex_options_payload(
    options: CodexProviderOptions | None,
) -> dict[str, str] | None:
    resolved_options = options or CodexProviderOptions()
    return resolved_options.to_payload() or None


PROVIDER_DEFINITIONS = {
    "codex": ProviderDefinition(
        name="codex",
        build_command=lambda options: build_codex_command(options or CodexProviderOptions()),
        build_options_payload=build_codex_options_payload,
        classify_failure=classify_codex_failure,
        missing_executable="codex",
        missing_summary="codex executable not found",
    ),
}


def list_answer_providers() -> list[str]:
    return sorted(PROVIDER_DEFINITIONS)


def format_available_answer_methods() -> str:
    providers = ", ".join(list_answer_providers())
    presets = ", ".join(list_answer_presets())
    return f"available providers: {providers}; available presets: {presets}"


def resolve_provider_execution(
    provider: str, codex_options: CodexProviderOptions | None
) -> AnswerExecution:
    definition = PROVIDER_DEFINITIONS.get(provider)
    if definition is not None:
        return AnswerExecution(
            command=definition.build_command(codex_options),
            provider=definition.name,
            provider_options=definition.build_options_payload(codex_options),
        )
    providers = ", ".join(list_answer_providers())
    raise ValidationRuntimeError(
        f"unknown answer provider: {provider} (available providers: {providers})"
    )


def resolve_answer_execution(
    answer_preset: str | None,
    answer_command: list[str] | None,
    provider: str | None,
    codex_options: CodexProviderOptions | None,
) -> AnswerExecution:
    if answer_command:
        return AnswerExecution(answer_command, None, None)
    if provider:
        return resolve_provider_execution(provider, codex_options)
    if answer_preset:
        try:
            preset_value = ANSWER_PRESETS[answer_preset]
        except KeyError as exc:
            raise ValidationRuntimeError(
                f"unknown answer preset: {answer_preset} ({format_available_answer_methods()})"
            ) from exc

        if isinstance(preset_value, dict):
            preset_provider = preset_value.get("provider")
            if preset_provider is None:
                raise ValidationRuntimeError(f"invalid answer preset: {answer_preset}")
            return resolve_provider_execution(preset_provider, codex_options)
        return AnswerExecution(list(preset_value), None, None)

    raise ValidationRuntimeError(
        "one of answer provider, preset, or command is required "
        f"({format_available_answer_methods()})"
    )


def resolve_answer_command(
    answer_preset: str | None,
    answer_command: list[str] | None,
    provider: str | None = None,
    codex_options: CodexProviderOptions | None = None,
) -> list[str]:
    return resolve_answer_execution(
        answer_preset, answer_command, provider, codex_options
    ).command


def execute_answer_command(prompt_text: str, execution: AnswerExecution) -> AnswerResult:
    resolved_command = execution.command
    provider = execution.provider
    provider_options = execution.provider_options

    try:
        result = subprocess.run(
            resolved_command,
            input=prompt_text,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        summary = str(exc)
        error_type = None
        definition = PROVIDER_DEFINITIONS.get(provider or "")
        if (
            definition is not None
            and definition.missing_executable is not None
            and exc.filename == definition.missing_executable
        ):
            summary = definition.missing_summary or summary
            error_type = PROVIDER_MISSING
        return AnswerResult(
            "",
            format_answer_failure(summary),
            2,
            None,
            None,
            resolved_command,
            provider,
            provider_options,
            error_type,
            summary,
            None,
        )

    if result.returncode != 0:
        error_type, summary = classify_provider_failure(
            provider,
            result.returncode,
            result.stderr,
        )
        return AnswerResult(
            "",
            format_answer_failure(summary),
            2,
            None,
            result.returncode,
            resolved_command,
            provider,
            provider_options,
            error_type,
            summary,
            result.stderr,
        )

    stdout_text = result.stdout
    if stdout_text and not stdout_text.endswith("\n"):
        stdout_text += "\n"
    return AnswerResult(
        stdout_text,
        "",
        0,
        result.stdout,
        result.returncode,
        resolved_command,
        provider,
        provider_options,
        None,
        None,
        result.stderr,
    )


def run_answer_command(
    prompt_text: str,
    answer_preset: str | None,
    answer_command: list[str] | None,
    provider: str | None = None,
    codex_options: CodexProviderOptions | None = None,
) -> AnswerResult:
    try:
        execution = resolve_answer_execution(
            answer_preset, answer_command, provider, codex_options
        )
    except ValidationRuntimeError as exc:
        return AnswerResult(
            "",
            format_answer_failure(str(exc)),
            2,
            None,
            None,
            None,
            None,
            None,
            None,
            str(exc),
            None,
        )
    return execute_answer_command(prompt_text, execution)


def answer_prompt(
    prompt_arg: str,
    answer_preset: str | None,
    answer_command: list[str] | None,
    provider: str | None = None,
    codex_options: CodexProviderOptions | None = None,
) -> AnswerResult:
    try:
        _, prompt_text = read_input_text(prompt_arg)
    except ValidationRuntimeError as exc:
        return AnswerResult(
            "",
            format_answer_failure(str(exc)),
            2,
            None,
            None,
            None,
            None,
            None,
            None,
            str(exc),
            None,
        )
    return run_answer_command(
        prompt_text, answer_preset, answer_command, provider, codex_options
    )
