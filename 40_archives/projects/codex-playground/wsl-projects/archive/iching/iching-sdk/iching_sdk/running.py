from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from iching_sdk.answering import (
    CodexProviderOptions,
    execute_answer_command,
    resolve_answer_execution,
)
from iching_sdk.config import (
    ConfigError,
    RuntimeConfig,
    ValidationRuntimeError,
    load_mode_config,
    load_runtime_config,
    resolve_profile_config,
    repo_root,
)
from iching_sdk.prompting import build_prompt_text, resolve_prompt_mode
from iching_sdk.resolving import resolve_loaded_input
from iching_sdk.selecting import list_indexed_files, select_resolved_input
from iching_sdk.validation import (
    ensure_out_dir,
    read_input_text,
    validate_citations,
    write_json,
)


@dataclass(frozen=True)
class RunArtifacts:
    artifacts_dir: Path
    resolve_path: Path
    select_path: Path
    prompt_path: Path
    answer_path: Path
    report_path: Path
    evidence_path: Path
    run_path: Path


@dataclass(frozen=True)
class RunResult:
    stdout_text: str
    stderr_text: str
    exit_code: int


def write_text_file(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def default_run_out_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return (repo_root() / "out" / "run" / stamp).resolve()


def ensure_run_artifacts(path_arg: str | None) -> RunArtifacts:
    artifacts_dir = default_run_out_dir() if path_arg is None else ensure_out_dir(path_arg)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return RunArtifacts(
        artifacts_dir=artifacts_dir,
        resolve_path=artifacts_dir / "resolve.json",
        select_path=artifacts_dir / "select.json",
        prompt_path=artifacts_dir / "prompt.txt",
        answer_path=artifacts_dir / "answer.md",
        report_path=artifacts_dir / "report.json",
        evidence_path=artifacts_dir / "evidence.json",
        run_path=artifacts_dir / "run.json",
    )


def write_run_payload(path: Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def build_run_payload(
    resolved: dict[str, Any] | None,
    selection: dict[str, Any] | None,
    input_label: str,
    artifacts: RunArtifacts,
    answer_command: list[str],
    provider: str | None,
    provider_options: dict[str, str] | None,
    resolved_codex_path: str | None,
    resolved_codex_version: str | None,
    answer_exit_code: int | None,
    validate_exit_code: int | None,
    final_status: str,
    validation_summary: dict[str, Any] | None = None,
    error: str | None = None,
    error_type: str | None = None,
    error_summary: str | None = None,
    error_source: str | None = None,
    error_stderr: str | None = None,
    preflight_ran: bool = False,
    preflight_exit_code: int | None = None,
    preflight_stderr: str | None = None,
    runtime_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "input": input_label,
        "artifacts_dir": str(artifacts.artifacts_dir),
        "answer_command": answer_command,
        "provider": provider,
        "provider_options": provider_options,
        "resolved_codex_path": resolved_codex_path,
        "resolved_codex_version": resolved_codex_version,
        "answer_exit_code": answer_exit_code,
        "validate_exit_code": validate_exit_code,
        "final_status": final_status,
        "validation": validation_summary,
        "error_type": error_type,
        "error_summary": error_summary,
        "error_source": error_source,
        "error_stderr": error_stderr,
        "preflight_ran": preflight_ran,
        "preflight_exit_code": preflight_exit_code,
        "preflight_stderr": preflight_stderr,
        "runtime_diagnostics": runtime_diagnostics,
    }
    if resolved is not None:
        payload["mode"] = resolved["mode"]
        payload["profile"] = resolved.get("profile")
        payload["input_kind"] = resolved["input_kind"]
        payload["hints"] = resolved.get("hints", [])
    if selection is not None:
        payload["selected_groups"] = [
            {
                "group": group["group"],
                "file_count": len(group["files"]),
            }
            for group in selection.get("selected_groups", [])
        ]
        payload["selected_file_count"] = selection.get("selected_file_count", 0)
        payload["selected_files_preview"] = selection.get("selected_files", [])[:5]
        payload["selected_section_count"] = selection.get("selected_section_count", 0)
        payload["selected_section_files_preview"] = selection.get("selected_section_files", [])[:5]
    if error:
        payload["error"] = error
    return payload


def format_failure_stderr(summary: str, artifacts_dir: Path) -> str:
    return f"{summary}\nartifacts: {artifacts_dir}\n"


def summarize_validation_failure(report: dict[str, Any]) -> str:
    finding_codes = [
        finding.get("code", "unknown")
        for finding in report.get("findings", [])
        if finding.get("severity") == "error"
    ]
    if not finding_codes:
        finding_codes = [
            finding.get("code", "unknown") for finding in report.get("findings", [])[:3]
        ]
    if not finding_codes:
        return "validation failed"
    return f"validation failed ({', '.join(finding_codes[:3])})"


def build_validation_summary(
    report: dict[str, Any] | None,
    validate_exit_code: int | None,
) -> dict[str, Any] | None:
    if report is None and validate_exit_code is None:
        return None
    if report is None:
        return {
            "validate_exit_code": validate_exit_code,
            "evidence_status": None,
            "errors": None,
            "warnings": None,
            "finding_codes": [],
        }
    summary = report.get("summary", {})
    return {
        "validate_exit_code": validate_exit_code,
        "evidence_status": report.get("evidence_status"),
        "errors": summary.get("errors"),
        "warnings": summary.get("warnings"),
        "finding_codes": [finding.get("code", "unknown") for finding in report.get("findings", [])],
    }


def run_workflow(
    input_arg: str,
    override_mode: str | None,
    out_dir: str | None,
    answer_preset: str | None,
    answer_command: list[str] | None,
    provider: str | None = None,
    codex_options: CodexProviderOptions | None = None,
    runtime_config: RuntimeConfig | None = None,
    profile_name: str | None = None,
) -> RunResult:
    try:
        artifacts = ensure_run_artifacts(out_dir)
    except OSError as exc:
        return RunResult("", f"{exc}\n", 2)

    try:
        answer_execution = resolve_answer_execution(
            answer_preset, answer_command, provider, codex_options
        )
    except ValidationRuntimeError as exc:
        payload = build_run_payload(
            None,
            None,
            input_arg,
            artifacts,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            "runtime_error",
            error=str(exc),
            error_summary=str(exc),
            error_source="runtime",
        )
        write_run_payload(artifacts.run_path, payload)
        return RunResult("", format_failure_stderr(str(exc), artifacts.artifacts_dir), 2)

    try:
        active_runtime_config = load_runtime_config() if runtime_config is None else runtime_config
        profile = resolve_profile_config(active_runtime_config, profile_name)
        input_label, input_text = read_input_text(input_arg)
        resolved = resolve_loaded_input(input_label, input_text, override_mode, profile)
        mode = resolve_prompt_mode(input_text, override_mode)
        selection = select_resolved_input(
            resolved,
            profile_name=profile.name,
            runtime_config=active_runtime_config,
        )
        prompt_text = build_prompt_text(input_text, mode, input_label, selection, profile)
        config = load_mode_config(mode, None, profile if mode == "extract" else None)
        indexed_files = list_indexed_files(mode, profile, None)
    except ValidationRuntimeError as exc:
        payload = build_run_payload(
            None,
            None,
            input_arg,
            artifacts,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            "runtime_error",
            error=str(exc),
            error_summary=str(exc),
            error_source="runtime",
        )
        write_run_payload(artifacts.run_path, payload)
        return RunResult("", format_failure_stderr(str(exc), artifacts.artifacts_dir), 2)
    except ConfigError as exc:
        payload = build_run_payload(
            None,
            None,
            input_arg,
            artifacts,
            [],
            None,
            None,
            None,
            None,
            None,
            None,
            "config_error",
            error=str(exc),
            error_summary=str(exc),
            error_source="config",
        )
        write_run_payload(artifacts.run_path, payload)
        return RunResult("", format_failure_stderr(str(exc), artifacts.artifacts_dir), 2)

    write_json(artifacts.resolve_path, resolved)
    write_json(artifacts.select_path, selection)
    write_text_file(artifacts.prompt_path, prompt_text)

    answer_result = execute_answer_command(prompt_text, answer_execution)
    if answer_result.exit_code != 0:
        summary = answer_result.error_summary or answer_result.stderr_text.strip() or "answer command failed"
        payload = build_run_payload(
            resolved,
            selection,
            input_label,
            artifacts,
            answer_result.resolved_command or answer_execution.command,
            answer_result.provider,
            answer_result.provider_options,
            answer_result.resolved_codex_path,
            answer_result.resolved_codex_version,
            answer_result.answer_exit_code,
            None,
            "runtime_error",
            validation_summary=build_validation_summary(None, None),
            error=summary,
            error_type=answer_result.error_type,
            error_summary=summary,
            error_source="provider" if answer_result.provider else "answer_command",
            error_stderr=answer_result.raw_stderr,
            preflight_ran=answer_result.preflight_ran,
            preflight_exit_code=answer_result.preflight_exit_code,
            preflight_stderr=answer_result.preflight_stderr,
            runtime_diagnostics=answer_result.runtime_diagnostics,
        )
        write_run_payload(artifacts.run_path, payload)
        return RunResult("", format_failure_stderr(summary, artifacts.artifacts_dir), 2)

    answer_text = answer_result.answer_text or ""
    write_text_file(artifacts.answer_path, answer_text)

    report, evidence, validate_exit_code = validate_citations(
        config, indexed_files, input_label, answer_text, resolved, profile_name=profile.name
    )
    write_json(artifacts.report_path, report)
    write_json(artifacts.evidence_path, evidence)

    final_status = "success" if validate_exit_code == 0 else "validation_failed"
    run_payload = build_run_payload(
        resolved,
        selection,
        input_label,
        artifacts,
        answer_result.resolved_command or answer_execution.command,
        answer_result.provider,
        answer_result.provider_options,
        answer_result.resolved_codex_path,
        answer_result.resolved_codex_version,
        answer_result.answer_exit_code,
        validate_exit_code,
        final_status,
        validation_summary=build_validation_summary(report, validate_exit_code),
        preflight_ran=answer_result.preflight_ran,
        preflight_exit_code=answer_result.preflight_exit_code,
        preflight_stderr=answer_result.preflight_stderr,
        runtime_diagnostics=answer_result.runtime_diagnostics,
    )
    write_run_payload(artifacts.run_path, run_payload)

    stdout_text = answer_result.stdout_text

    stderr_text = ""
    if validate_exit_code != 0:
        stderr_text = format_failure_stderr(
            summarize_validation_failure(report), artifacts.artifacts_dir
        )

    return RunResult(stdout_text, stderr_text, validate_exit_code)
