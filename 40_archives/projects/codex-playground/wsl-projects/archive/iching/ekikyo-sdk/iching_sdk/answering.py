from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Callable

from iching_sdk.config import ValidationRuntimeError
from iching_sdk.validation import read_input_text

ANSWER_PRESETS = {
    "codex-exec": {"provider": "codex"},
}
ANSWER_PROVIDERS = ("codex",)
PROVIDER_MISSING = "provider_missing"
PROVIDER_AUTH = "provider_auth"
PROVIDER_CLI_COMPAT = "provider_cli_compat"
PROVIDER_SANDBOX_OR_FS = "provider_sandbox_or_fs"
PROVIDER_CONNECTION = "provider_connection"
PROVIDER_EXECUTION_FAILED = "provider_execution_failed"
CODEX_AUTH_PATTERNS = (
    "codex login",
    "login required",
    "not authenticated",
    "authentication required",
    "unauthenticated",
    "please authenticate",
)
CODEX_CLI_COMPAT_PATTERNS = (
    "unexpected argument",
    "unknown option",
    "unrecognized option",
    "unexpected option",
    "for more information, try '--help'",
)
CODEX_SANDBOX_OR_FS_PATTERNS = (
    "permission denied",
    "readonly database",
    "read-only file system",
    "failed to open state db",
    "failed to initialize state runtime",
    "state db discrepancy",
    "shell snapshot",
    "migration 1 was previously applied but has been modified",
)
CODEX_CONNECTION_PATTERNS = (
    "websocket",
    "https",
    "stream disconnected",
    "upstream timeout",
    "connection reset",
    "connection refused",
    "tls",
    "timed out",
)
CODEX_PREFLIGHT_PROMPT = "Reply with exactly OK.\n"
CODEX_READONLY_PATTERNS = (
    "readonly database",
    "read-only file system",
    "permission denied",
)
CODEX_STATE_DB_PATTERNS = (
    "failed to open state db",
    "failed to initialize state runtime",
    "unable to open database file",
    "state db discrepancy",
    "migration 1 was previously applied but has been modified",
)
CODEX_SHELL_SNAPSHOT_PATTERNS = (
    "shell snapshot",
    "failed to create shell snapshot",
)
CODEX_STREAM_DISCONNECTED_PATTERNS = ("stream disconnected",)
CODEX_CLI_ARGUMENT_PATTERNS = (
    "unexpected argument",
    "unknown option",
    "unrecognized option",
    "unexpected option",
)


@dataclass(frozen=True)
class CodexProviderOptions:
    path: str | None = None
    model: str | None = None
    sandbox: str | None = None
    approval_policy: str | None = None
    preflight_probe: bool = True

    def to_payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        if self.model:
            payload["model"] = self.model
        if self.sandbox:
            payload["sandbox"] = self.sandbox
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
    resolved_codex_path: str | None = None
    resolved_codex_version: str | None = None
    preflight_probe: bool = False


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
    resolved_codex_path: str | None
    resolved_codex_version: str | None
    error_type: str | None
    error_summary: str | None
    raw_stderr: str | None
    preflight_ran: bool
    preflight_exit_code: int | None
    preflight_stderr: str | None
    runtime_diagnostics: dict[str, Any] | None


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


def matches_any_pattern(stderr_text: str, patterns: tuple[str, ...]) -> bool:
    lowered = stderr_text.lower()
    return any(pattern in lowered for pattern in patterns)


def format_categorized_failure(
    category: str,
    returncode: int | None,
    stderr_text: str,
    detail: str | None = None,
) -> str:
    first_line = first_stderr_line(stderr_text)
    category_text = category if detail is None else f"{category} ({detail})"
    if first_line:
        return f"{category_text} (exit code {returncode}): {first_line}"
    return f"{category_text} (exit code {returncode})"


def detect_codex_failure_detail(stderr_text: str) -> str | None:
    if not stderr_text.strip():
        return None
    if matches_any_pattern(stderr_text, CODEX_READONLY_PATTERNS):
        return "readonly filesystem"
    if matches_any_pattern(stderr_text, CODEX_STATE_DB_PATTERNS):
        return "state db open failure"
    if matches_any_pattern(stderr_text, CODEX_SHELL_SNAPSHOT_PATTERNS):
        return "shell snapshot failure"
    if matches_any_pattern(stderr_text, CODEX_STREAM_DISCONNECTED_PATTERNS):
        return "stream disconnected"
    if matches_any_pattern(stderr_text, CODEX_CLI_ARGUMENT_PATTERNS):
        return "cli argument error"
    return None


def classify_codex_failure(
    returncode: int | None,
    stderr_text: str,
) -> tuple[str | None, str]:
    detail = detect_codex_failure_detail(stderr_text)
    if is_codex_auth_failure(stderr_text):
        return PROVIDER_AUTH, "codex authentication required"
    if matches_any_pattern(stderr_text, CODEX_CLI_COMPAT_PATTERNS):
        return (
            PROVIDER_CLI_COMPAT,
            format_categorized_failure(
                "codex CLI compatibility issue",
                returncode,
                stderr_text,
                detail,
            ),
        )
    if matches_any_pattern(stderr_text, CODEX_SANDBOX_OR_FS_PATTERNS):
        return (
            PROVIDER_SANDBOX_OR_FS,
            format_categorized_failure(
                "codex sandbox or filesystem issue",
                returncode,
                stderr_text,
                detail,
            ),
        )
    if matches_any_pattern(stderr_text, CODEX_CONNECTION_PATTERNS):
        return (
            PROVIDER_CONNECTION,
            format_categorized_failure(
                "codex connection issue",
                returncode,
                stderr_text,
                detail,
            ),
        )
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


def resolve_codex_executable(options: CodexProviderOptions) -> str:
    if options.path:
        return str(Path(options.path).expanduser())
    return shutil.which("codex") or "codex"


def resolve_codex_version(executable: str) -> str | None:
    if executable == "codex":
        return None
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    for candidate in (result.stdout, result.stderr):
        first_line = first_stderr_line(candidate)
        if first_line:
            return first_line
    return None


def build_codex_command(
    options: CodexProviderOptions,
    executable: str | None = None,
) -> list[str]:
    command = [executable or resolve_codex_executable(options), "exec"]
    if options.model:
        command.extend(["--model", options.model])
    if options.sandbox:
        command.extend(["--sandbox", options.sandbox])
    return command


def build_runtime_diagnostics(
    prompt_text: str,
    resolved_codex_path: str | None,
    resolved_codex_version: str | None,
    preflight_ran: bool,
) -> dict[str, Any]:
    return {
        "cwd": str(Path.cwd()),
        "resolved_codex_path": resolved_codex_path,
        "resolved_codex_version": resolved_codex_version,
        "home": os.environ.get("HOME"),
        "codex_home": os.environ.get("CODEX_HOME"),
        "path": os.environ.get("PATH"),
        "prompt_chars": len(prompt_text),
        "preflight_ran": preflight_ran,
    }


def run_codex_preflight_probe(
    resolved_command: list[str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        resolved_command,
        input=CODEX_PREFLIGHT_PROMPT,
        capture_output=True,
        text=True,
        check=False,
    )


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
        if definition.name == "codex":
            resolved_options = codex_options or CodexProviderOptions()
            executable = resolve_codex_executable(resolved_options)
            return AnswerExecution(
                command=build_codex_command(resolved_options, executable=executable),
                provider=definition.name,
                provider_options=definition.build_options_payload(resolved_options),
                resolved_codex_path=executable,
                resolved_codex_version=resolve_codex_version(executable),
                preflight_probe=resolved_options.preflight_probe,
            )
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
    resolved_codex_path = execution.resolved_codex_path
    resolved_codex_version = execution.resolved_codex_version
    preflight_ran = False
    preflight_exit_code: int | None = None
    preflight_stderr: str | None = None
    runtime_diagnostics = build_runtime_diagnostics(
        prompt_text,
        resolved_codex_path,
        resolved_codex_version,
        preflight_ran,
    )

    if provider == "codex" and execution.preflight_probe:
        preflight_ran = True
        runtime_diagnostics = build_runtime_diagnostics(
            prompt_text,
            resolved_codex_path,
            resolved_codex_version,
            preflight_ran,
        )
        try:
            probe_result = run_codex_preflight_probe(resolved_command)
        except OSError as exc:
            summary = str(exc)
            error_type = None
            definition = PROVIDER_DEFINITIONS.get(provider or "")
            if (
                definition is not None
                and (
                    (
                        definition.missing_executable is not None
                        and exc.filename == definition.missing_executable
                    )
                    or exc.filename == resolved_command[0]
                )
            ):
                summary = definition.missing_summary or summary
                error_type = PROVIDER_MISSING
            elif matches_any_pattern(summary, CODEX_SANDBOX_OR_FS_PATTERNS):
                error_type = PROVIDER_SANDBOX_OR_FS
                summary = format_categorized_failure(
                    "codex sandbox or filesystem issue",
                    None,
                    summary,
                    detect_codex_failure_detail(summary),
                )
            return AnswerResult(
                "",
                format_answer_failure(f"preflight failed: {summary}"),
                2,
                None,
                None,
                resolved_command,
                provider,
                provider_options,
                resolved_codex_path,
                resolved_codex_version,
                error_type,
                f"preflight failed: {summary}",
                None,
                preflight_ran,
                None,
                None,
                runtime_diagnostics,
            )

        preflight_exit_code = probe_result.returncode
        preflight_stderr = probe_result.stderr
        if probe_result.returncode != 0:
            error_type, summary = classify_provider_failure(
                provider,
                probe_result.returncode,
                probe_result.stderr,
            )
            summary = f"preflight failed: {summary}"
            return AnswerResult(
                "",
                format_answer_failure(summary),
                2,
                None,
                probe_result.returncode,
                resolved_command,
                provider,
                provider_options,
                resolved_codex_path,
                resolved_codex_version,
                error_type,
                summary,
                probe_result.stderr,
                preflight_ran,
                preflight_exit_code,
                preflight_stderr,
                runtime_diagnostics,
            )

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
            and (
                (
                    definition.missing_executable is not None
                    and exc.filename == definition.missing_executable
                )
                or exc.filename == resolved_command[0]
            )
        ):
            summary = definition.missing_summary or summary
            error_type = PROVIDER_MISSING
        elif provider == "codex" and matches_any_pattern(summary, CODEX_SANDBOX_OR_FS_PATTERNS):
            error_type = PROVIDER_SANDBOX_OR_FS
            summary = format_categorized_failure(
                "codex sandbox or filesystem issue",
                None,
                summary,
            )
        return AnswerResult(
            "",
            format_answer_failure(summary),
            2,
            None,
            None,
            resolved_command,
            provider,
            provider_options,
            resolved_codex_path,
            resolved_codex_version,
            error_type,
            summary,
            None,
            preflight_ran,
            preflight_exit_code,
            preflight_stderr,
            runtime_diagnostics,
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
            resolved_codex_path,
            resolved_codex_version,
            error_type,
            summary,
            result.stderr,
            preflight_ran,
            preflight_exit_code,
            preflight_stderr,
            runtime_diagnostics,
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
        resolved_codex_path,
        resolved_codex_version,
        None,
        None,
        result.stderr,
        preflight_ran,
        preflight_exit_code,
        preflight_stderr,
        runtime_diagnostics,
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
            None,
            None,
            str(exc),
            None,
            False,
            None,
            None,
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
            None,
            None,
            str(exc),
            None,
            False,
            None,
            None,
            None,
        )
    return run_answer_command(
        prompt_text, answer_preset, answer_command, provider, codex_options
    )
