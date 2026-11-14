from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Callable

from iching_sdk.answering import (
    CodexProviderOptions,
    answer_prompt,
    list_answer_presets,
    list_answer_providers,
)
from iching_sdk.config import (
    CODEX_APPROVAL_POLICY_VALUES,
    CODEX_SANDBOX_VALUES,
    ConfigError,
    MODE_RULE_FILES,
    RuntimeConfig,
    ResolvedRuntimeConfig,
    ValidationRuntimeError,
    load_mode_config,
    load_runtime_config,
    resolve_profile_config,
    resolve_sources_root,
    resolve_runtime_config,
)
from iching_sdk.prompting import build_prompt_text, load_prompt_input, resolve_prompt_mode
from iching_sdk.resolving import resolve_input_text, resolve_loaded_input
from iching_sdk.running import run_workflow
from iching_sdk.selecting import list_indexed_files, select_input_text, select_resolved_input
from iching_sdk.validation import (
    build_error_result,
    ensure_out_dir,
    load_validation_context,
    read_input_text,
    validate_citations,
    write_json,
)


@dataclass(frozen=True)
class ProviderCliSpec:
    provider: str
    option_arg_names: tuple[str, ...]
    build_provider_options: Callable[[ResolvedRuntimeConfig], CodexProviderOptions | None]
    invalid_option_message: str


def build_codex_provider_options(
    resolved_runtime: ResolvedRuntimeConfig,
) -> CodexProviderOptions:
    return CodexProviderOptions(
        path=resolved_runtime.codex_path,
        model=resolved_runtime.codex_model,
        sandbox=resolved_runtime.codex_sandbox,
        approval_policy=resolved_runtime.codex_approval_policy,
        preflight_probe=True,
    )


PROVIDER_CLI_SPECS = {
    "codex": ProviderCliSpec(
        provider="codex",
        option_arg_names=("codex_model", "codex_sandbox", "codex_approval_policy"),
        build_provider_options=build_codex_provider_options,
        invalid_option_message="--codex-model/--codex-sandbox/--codex-approval-policy require --provider codex",
    )
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="iching")
    subparsers = parser.add_subparsers(dest="command", required=True)
    answer_presets = list_answer_presets()
    answer_providers = list_answer_providers()

    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--mode", required=True, choices=sorted(MODE_RULE_FILES))
    index_parser.add_argument("--sources-root")
    add_profile_argument(index_parser)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--input", required=True)
    resolve_parser.add_argument("--mode", choices=sorted(MODE_RULE_FILES))
    add_profile_argument(resolve_parser)

    select_parser = subparsers.add_parser("select")
    select_parser.add_argument("--input", required=True)
    select_parser.add_argument("--mode", choices=sorted(MODE_RULE_FILES))
    select_parser.add_argument("--sources-root")
    add_profile_argument(select_parser)

    prompt_parser = subparsers.add_parser("build-prompt")
    prompt_parser.add_argument("--input", required=True)
    prompt_parser.add_argument("--mode", choices=sorted(MODE_RULE_FILES))
    prompt_parser.add_argument("--sources-root")
    add_profile_argument(prompt_parser)

    answer_parser = subparsers.add_parser(
        "answer",
        help="Run prompt -> answer using a provider, preset, or explicit answer command",
    )
    answer_parser.add_argument("--prompt", required=True)
    add_answer_runtime_arguments(answer_parser, answer_presets, answer_providers)

    run_parser = subparsers.add_parser(
        "run",
        help="Run resolve -> build-prompt -> answer -> validate",
    )
    run_parser.add_argument("--input", required=True)
    run_parser.add_argument("--mode", choices=sorted(MODE_RULE_FILES))
    run_parser.add_argument("--out-dir")
    add_profile_argument(run_parser)
    add_answer_runtime_arguments(run_parser, answer_presets, answer_providers)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--mode", required=True, choices=sorted(MODE_RULE_FILES))
    validate_parser.add_argument("--input", required=True)
    validate_parser.add_argument("--context")
    validate_parser.add_argument("--sources-root")
    validate_parser.add_argument("--out-dir")
    add_profile_argument(validate_parser)
    return parser


def add_profile_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        help="Select an extract profile (defaults to iching.toml default_profile)",
    )


def add_answer_runtime_arguments(
    parser: argparse.ArgumentParser,
    answer_presets: list[str],
    answer_providers: list[str],
) -> None:
    parser.add_argument(
        "--provider",
        choices=answer_providers,
        help="Use a built-in answer provider (recommended: codex)",
    )
    parser.add_argument(
        "--answer-preset",
        choices=answer_presets,
        help="Use a built-in answer preset for compatibility (recommended: codex-exec)",
    )
    parser.add_argument("--answer-cmd", nargs=argparse.REMAINDER)
    parser.add_argument("--codex-model")
    parser.add_argument(
        "--codex-sandbox",
        choices=sorted(CODEX_SANDBOX_VALUES),
    )
    parser.add_argument(
        "--codex-approval-policy",
        choices=sorted(CODEX_APPROVAL_POLICY_VALUES),
    )

def collect_provider_cli_option_values(args: argparse.Namespace) -> dict[str, tuple[object | None, ...]]:
    return {
        provider: tuple(getattr(args, option_name, None) for option_name in spec.option_arg_names)
        for provider, spec in PROVIDER_CLI_SPECS.items()
    }


def build_provider_options(
    resolved_runtime: ResolvedRuntimeConfig,
) -> CodexProviderOptions | None:
    if resolved_runtime.provider is None:
        return None
    spec = PROVIDER_CLI_SPECS.get(resolved_runtime.provider)
    if spec is None:
        return None
    return spec.build_provider_options(resolved_runtime)


def validate_answer_runtime_args(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    runtime_config: RuntimeConfig,
) -> None:
    resolved_runtime = resolve_runtime_config(
        runtime_config,
        getattr(args, "provider", None),
        getattr(args, "codex_model", None),
        getattr(args, "codex_sandbox", None),
        getattr(args, "codex_approval_policy", None),
    )
    provider_option_values = collect_provider_cli_option_values(args)
    for provider, option_values in provider_option_values.items():
        if any(option is not None for option in option_values) and resolved_runtime.provider != provider:
            parser.error(PROVIDER_CLI_SPECS[provider].invalid_option_message)


def resolve_answer_runtime_from_args(
    args: argparse.Namespace, runtime_config: RuntimeConfig
) -> ResolvedRuntimeConfig:
    return resolve_runtime_config(
        runtime_config,
        getattr(args, "provider", None),
        getattr(args, "codex_model", None),
        getattr(args, "codex_sandbox", None),
        getattr(args, "codex_approval_policy", None),
    )


def run_index(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    profile = resolve_profile_config(runtime_config, getattr(args, "profile", None))
    config = load_mode_config(args.mode, args.sources_root, profile if args.mode == "extract" else None)
    payload = {
        "mode": config.mode,
        "profile": profile.name,
        "files": list_indexed_files(args.mode, profile, args.sources_root),
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def run_resolve(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    try:
        profile = resolve_profile_config(runtime_config, getattr(args, "profile", None))
        payload = resolve_input_text(args.input, args.mode, profile)
    except ValidationRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def run_build_prompt(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    try:
        profile = resolve_profile_config(runtime_config, getattr(args, "profile", None))
        input_label, input_text = load_prompt_input(args.input)
        mode = resolve_prompt_mode(input_text, args.mode)
        resolved = resolve_loaded_input(input_label, input_text, args.mode, profile)
        selection = select_resolved_input(
            resolved,
            sources_root_override=getattr(args, "sources_root", None),
            profile_name=profile.name,
            runtime_config=runtime_config,
        )
        prompt_text = build_prompt_text(input_text, mode, input_label, selection, profile)
    except ValidationRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    sys.stdout.write(prompt_text)
    if not prompt_text.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def run_select(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    try:
        payload = select_input_text(
            args.input,
            args.mode,
            args.sources_root,
            profile_name=getattr(args, "profile", None),
            runtime_config=runtime_config,
        )
    except ValidationRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def run_answer(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    resolved_runtime = resolve_answer_runtime_from_args(args, runtime_config)
    result = answer_prompt(
        args.prompt,
        args.answer_preset,
        args.answer_cmd,
        resolved_runtime.provider,
        build_provider_options(resolved_runtime),
    )
    if result.stdout_text:
        sys.stdout.write(result.stdout_text)
    if result.stderr_text:
        sys.stderr.write(result.stderr_text)
    return result.exit_code


def run_answer_workflow(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    resolved_runtime = resolve_answer_runtime_from_args(args, runtime_config)
    profile = resolve_profile_config(runtime_config, getattr(args, "profile", None))
    result = run_workflow(
        args.input,
        args.mode,
        args.out_dir,
        args.answer_preset,
        args.answer_cmd,
        resolved_runtime.provider,
        build_provider_options(resolved_runtime),
        runtime_config=runtime_config,
        profile_name=profile.name,
    )
    if result.stdout_text:
        sys.stdout.write(result.stdout_text)
    if result.stderr_text:
        sys.stderr.write(result.stderr_text)
    return result.exit_code


def run_validate(args: argparse.Namespace, runtime_config: RuntimeConfig) -> int:
    out_dir = ensure_out_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        profile = resolve_profile_config(runtime_config, getattr(args, "profile", None))
        config = load_mode_config(args.mode, args.sources_root, profile if args.mode == "extract" else None)
        indexed_files = list_indexed_files(args.mode, profile, args.sources_root)
        input_label, text = read_input_text(args.input)
        validation_context = None
        if args.context:
            validation_context = load_validation_context(args.context)
            if validation_context["mode"] != args.mode:
                raise ValidationRuntimeError(
                    f"context mode {validation_context['mode']} does not match --mode {args.mode}"
                )
        report, evidence, exit_code = validate_citations(
            config,
            indexed_files,
            input_label,
            text,
            validation_context,
            profile_name=profile.name,
        )
    except ValidationRuntimeError as exc:
        report, evidence, exit_code = build_error_result(
            args.mode,
            args.input,
            resolve_sources_root(args.sources_root) / args.mode,
            "runtime_error",
            "runtime_error",
            str(exc),
        )
    except ConfigError as exc:
        report, evidence, exit_code = build_error_result(
            args.mode,
            args.input,
            resolve_sources_root(args.sources_root) / args.mode,
            "config_error",
            "config_error",
            str(exc),
        )

    write_json(out_dir / "report.json", report)
    write_json(out_dir / "evidence.json", evidence)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        try:
            runtime_config = load_runtime_config()
        except ConfigError:
            if args.command in {"answer", "run"}:
                raise
            runtime_config = RuntimeConfig()
        if args.command == "index":
            return run_index(args, runtime_config)
        if args.command == "resolve":
            return run_resolve(args, runtime_config)
        if args.command == "select":
            return run_select(args, runtime_config)
        if args.command == "build-prompt":
            return run_build_prompt(args, runtime_config)
        if args.command == "answer":
            validate_answer_runtime_args(parser, args, runtime_config)
            return run_answer(args, runtime_config)
        if args.command == "run":
            validate_answer_runtime_args(parser, args, runtime_config)
            return run_answer_workflow(args, runtime_config)
        if args.command == "validate":
            return run_validate(args, runtime_config)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
