from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iching_sdk.answering import (
    CodexProviderOptions,
    answer_prompt,
    build_codex_command,
    list_answer_presets,
    list_answer_providers,
    resolve_answer_command,
)
from iching_sdk import cli as cli_module
from iching_sdk.config import (
    ProviderRuntimeConfig,
    ResolvedRuntimeConfig,
    RuntimeConfig,
    load_runtime_config,
    resolve_runtime_config,
)
from iching_sdk.running import run_workflow


REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = [sys.executable, str(REPO_ROOT / "iching")]
RUNTIME_CONFIG = REPO_ROOT / "iching.toml"
CODEX_SMOKE_ENV = "ICHING_RUN_CODEX_SMOKE"
CODEX_SMOKE_SKIP_PATTERNS = (
    "codex executable not found",
    "codex authentication required",
    "failed to clean up stale arg0 temp dirs",
    "permission denied",
)
EXTRACT_CASES_MANIFEST = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "manifest.json"


class IchingCliTests(unittest.TestCase):
    @contextmanager
    def runtime_config_file(self, text: str):
        original_exists = RUNTIME_CONFIG.exists()
        original_text = RUNTIME_CONFIG.read_text(encoding="utf-8") if original_exists else None
        try:
            RUNTIME_CONFIG.write_text(text, encoding="utf-8")
            yield RUNTIME_CONFIG
        finally:
            if original_exists and original_text is not None:
                RUNTIME_CONFIG.write_text(original_text, encoding="utf-8")
            elif RUNTIME_CONFIG.exists():
                RUNTIME_CONFIG.unlink()

    def test_answer_reads_prompt_file_and_returns_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "answer",
                    "--prompt",
                    str(prompt_path),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('answer body')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "answer body\n")
            self.assertEqual(result.stderr, "")

    def test_answer_with_preset_resolves_codex_exec(self) -> None:
        self.assertEqual(
            resolve_answer_command("codex-exec", None),
            ["codex", "exec"],
        )
        self.assertEqual(list_answer_presets(), ["codex-exec"])
        self.assertEqual(list_answer_providers(), ["codex"])

    def test_build_codex_command_applies_requested_options(self) -> None:
        command = build_codex_command(
            CodexProviderOptions(
                model="gpt-5",
                sandbox="workspace-write",
                approval_policy="never",
            )
        )
        self.assertEqual(
            command,
            [
                "codex",
                "exec",
                "--model",
                "gpt-5",
                "--sandbox",
                "workspace-write",
                "--ask-for-approval",
                "never",
            ],
        )

    def test_answer_prompt_runs_resolved_preset_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch.dict(
                "iching_sdk.answering.ANSWER_PRESETS",
                {"codex-exec": [sys.executable, "-c", "print('preset answer')"]},
                clear=False,
            ):
                result = answer_prompt(str(prompt_path), "codex-exec", None)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.stdout_text, "preset answer\n")

    def test_answer_accepts_stdin_and_passes_prompt_to_child(self) -> None:
        result = subprocess.run(
            [
                *CLI,
                "answer",
                "--prompt",
                "-",
                "--answer-cmd",
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "prompt = sys.stdin.read(); "
                    "print('PROMPT_OK' if prompt == 'prompt from stdin\\n' else 'PROMPT_BAD')"
                ),
            ],
            cwd=REPO_ROOT,
            input="prompt from stdin\n",
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "PROMPT_OK\n")

    def test_answer_returns_runtime_error_for_missing_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.txt"
            result = subprocess.run(
                [
                    *CLI,
                    "answer",
                    "--prompt",
                    str(missing),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('unused')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("input file not found", result.stderr)

    def test_answer_returns_runtime_error_when_answer_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "answer",
                    "--prompt",
                    str(prompt_path),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "raise SystemExit(9)",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("answer command failed with exit code 9", result.stderr)

    def test_answer_prompt_returns_runtime_error_when_command_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            result = answer_prompt(str(prompt_path), None, [])
            self.assertEqual(result.exit_code, 2)
            self.assertIn("one of answer provider, preset, or command is required", result.stderr_text)

    def test_answer_prefers_explicit_command_over_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            result = answer_prompt(
                str(prompt_path),
                "codex-exec",
                [sys.executable, "-c", "print('explicit command')"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.stdout_text, "explicit command\n")

    def test_answer_prefers_explicit_command_over_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            result = answer_prompt(
                str(prompt_path),
                None,
                [sys.executable, "-c", "print('explicit command')"],
                "codex",
                CodexProviderOptions(model="gpt-5"),
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.stdout_text, "explicit command\n")
            self.assertIsNone(result.provider)

    def test_answer_prefers_provider_over_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=0,
                    stdout="provider answer\n",
                    stderr="",
                )
                result = answer_prompt(
                    str(prompt_path),
                    "codex-exec",
                    None,
                    "codex",
                    CodexProviderOptions(model="gpt-5"),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                ["codex", "exec", "--model", "gpt-5"],
            )
            self.assertEqual(result.provider, "codex")

    def test_answer_cli_fails_when_no_preset_or_command_is_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            result = subprocess.run(
                [*CLI, "answer", "--prompt", str(prompt_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("one of answer provider, preset, or command is required", result.stderr)
            self.assertIn("codex", result.stderr)
            self.assertIn("codex-exec", result.stderr)

    def test_answer_cli_help_mentions_provider_flag(self) -> None:
        result = subprocess.run(
            [*CLI, "answer", "--help"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--provider", result.stdout)
        self.assertIn("--codex-model", result.stdout)
        self.assertIn("codex-exec", result.stdout)

    def test_answer_cli_reports_available_presets_for_unknown_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            result = subprocess.run(
                [*CLI, "answer", "--prompt", str(prompt_path), "--answer-preset", "missing"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid choice", result.stderr)
            self.assertIn("codex-exec", result.stderr)

    def test_answer_cli_rejects_codex_options_without_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            result = subprocess.run(
                [
                    *CLI,
                    "answer",
                    "--prompt",
                    str(prompt_path),
                    "--codex-model",
                    "gpt-5",
                    "--answer-preset",
                    "codex-exec",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("require --provider codex", result.stderr)

    def test_build_provider_options_returns_codex_options_for_codex_runtime(self) -> None:
        provider_options = cli_module.build_provider_options(
            ResolvedRuntimeConfig(
                provider="codex",
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            )
        )
        self.assertEqual(
            provider_options,
            CodexProviderOptions(
                model="gpt-5",
                sandbox="workspace-write",
                approval_policy="never",
            ),
        )

    def test_build_provider_options_returns_none_without_provider(self) -> None:
        provider_options = cli_module.build_provider_options(
            ResolvedRuntimeConfig(
                provider=None,
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            )
        )
        self.assertIsNone(provider_options)

    def test_load_runtime_config_returns_provider_structured_config(self) -> None:
        with self.runtime_config_file(
            'default_provider = "codex"\n'
            "[providers.codex]\n"
            'model = "gpt-5"\n'
            'sandbox = "workspace-write"\n'
            'approval_policy = "never"\n'
        ):
            runtime_config = load_runtime_config()
        self.assertEqual(runtime_config.default_provider, "codex")
        self.assertEqual(
            runtime_config.provider_config("codex"),
            ProviderRuntimeConfig(
                model="gpt-5",
                sandbox="workspace-write",
                approval_policy="never",
            ),
        )
        self.assertEqual(runtime_config.provider, "codex")
        self.assertEqual(runtime_config.codex_model, "gpt-5")

    def test_resolve_runtime_config_reads_provider_structured_config(self) -> None:
        resolved = resolve_runtime_config(
            RuntimeConfig(
                default_provider="codex",
                providers={
                    "codex": ProviderRuntimeConfig(
                        model="gpt-5",
                        sandbox="workspace-write",
                        approval_policy="never",
                    )
                },
            ),
            None,
            None,
            None,
            None,
        )
        self.assertEqual(
            resolved,
            ResolvedRuntimeConfig(
                provider="codex",
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            ),
        )

    def test_resolve_runtime_config_cli_overrides_structured_provider_defaults(self) -> None:
        resolved = resolve_runtime_config(
            RuntimeConfig(
                default_provider="codex",
                providers={"codex": ProviderRuntimeConfig(model="gpt-5-mini")},
            ),
            "codex",
            "gpt-5",
            "workspace-write",
            "never",
        )
        self.assertEqual(
            resolved,
            ResolvedRuntimeConfig(
                provider="codex",
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            ),
        )

    def test_answer_cli_allows_codex_options_when_runtime_config_sets_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file('provider = "codex"\n'):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(
                            [
                                "answer",
                                "--prompt",
                                str(prompt_path),
                                "--codex-model",
                                "gpt-5",
                            ]
                        )
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                ["codex", "exec", "--model", "gpt-5"],
            )

    def test_answer_cli_uses_runtime_config_provider_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'provider = "codex"\n'
                'codex_model = "gpt-5"\n'
                'codex_sandbox = "workspace-write"\n'
                'codex_approval_policy = "never"\n'
            ):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(["answer", "--prompt", str(prompt_path)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                ],
            )

    def test_answer_cli_uses_provider_table_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'default_provider = "codex"\n'
                "[providers.codex]\n"
                'model = "gpt-5"\n'
                'sandbox = "workspace-write"\n'
                'approval_policy = "never"\n'
            ):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(["answer", "--prompt", str(prompt_path)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                ],
            )

    def test_answer_cli_prefers_provider_table_over_legacy_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'provider = "codex"\n'
                'codex_model = "gpt-5-mini"\n'
                'codex_sandbox = "read-only"\n'
                'codex_approval_policy = "on-request"\n'
                'default_provider = "codex"\n'
                "[providers.codex]\n"
                'model = "gpt-5"\n'
                'sandbox = "workspace-write"\n'
                'approval_policy = "never"\n'
            ):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(["answer", "--prompt", str(prompt_path)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                ],
            )

    def test_answer_cli_cli_options_override_runtime_config_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'provider = "codex"\n'
                'codex_model = "gpt-5-mini"\n'
                'codex_sandbox = "read-only"\n'
                'codex_approval_policy = "on-request"\n'
            ):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(
                            [
                                "answer",
                                "--prompt",
                                str(prompt_path),
                                "--provider",
                                "codex",
                                "--codex-model",
                                "gpt-5",
                                "--codex-sandbox",
                                "workspace-write",
                                "--codex-approval-policy",
                                "never",
                            ]
                        )
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                ],
            )

    def test_answer_cli_runs_codex_provider_with_requested_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="provider answer\n",
                    stderr="",
                )
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(
                        model="gpt-5",
                        sandbox="workspace-write",
                        approval_policy="never",
                    ),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                ],
            )
            self.assertEqual(result.provider, "codex")
            self.assertEqual(
                result.provider_options,
                {
                    "model": "gpt-5",
                    "sandbox": "workspace-write",
                    "approval_policy": "never",
                },
            )

    def test_answer_returns_runtime_error_when_codex_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch(
                "iching_sdk.answering.subprocess.run",
                side_effect=FileNotFoundError(2, "No such file or directory", "codex"),
            ):
                result = answer_prompt(str(prompt_path), None, None, "codex")
            self.assertEqual(result.exit_code, 2)
            self.assertIn("codex executable not found", result.stderr_text)
            self.assertEqual(result.error_type, "provider_missing")
            self.assertEqual(result.error_summary, "codex executable not found")
            self.assertIsNone(result.raw_stderr)

    def test_answer_classifies_codex_auth_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="Authentication required. Please run codex login.\n",
                )
                result = answer_prompt(str(prompt_path), None, None, "codex")
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_auth")
            self.assertEqual(result.error_summary, "codex authentication required")
            self.assertEqual(
                result.stderr_text,
                "codex authentication required\n",
            )
            self.assertEqual(
                result.raw_stderr,
                "Authentication required. Please run codex login.\n",
            )

    def test_answer_classifies_additional_codex_auth_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="Unauthenticated session. Please authenticate first.\n",
                )
                result = answer_prompt(str(prompt_path), None, None, "codex")
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_auth")
            self.assertEqual(result.error_summary, "codex authentication required")

    def test_answer_classifies_non_auth_codex_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=17,
                    stdout="",
                    stderr="upstream timeout\nretry later\n",
                )
                result = answer_prompt(str(prompt_path), None, None, "codex")
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_execution_failed")
            self.assertEqual(
                result.error_summary,
                "codex provider failed with exit code 17: upstream timeout",
            )
            self.assertEqual(
                result.stderr_text,
                "codex provider failed with exit code 17: upstream timeout\n",
            )
            self.assertEqual(result.raw_stderr, "upstream timeout\nretry later\n")

    def test_answer_does_not_treat_plain_login_word_as_auth_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=23,
                    stdout="",
                    stderr="login shell failed to start\n",
                )
                result = answer_prompt(str(prompt_path), None, None, "codex")
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_execution_failed")
            self.assertEqual(
                result.error_summary,
                "codex provider failed with exit code 23: login shell failed to start",
            )

    def test_answer_codex_smoke_opt_in(self) -> None:
        if os.environ.get(CODEX_SMOKE_ENV) != "1":
            self.skipTest(f"set {CODEX_SMOKE_ENV}=1 to run codex CLI smoke test")

        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("Reply with exactly SMOKE_OK.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "answer",
                    "--prompt",
                    str(prompt_path),
                    "--provider",
                    "codex",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                stderr_lower = result.stderr.lower()
                if any(pattern in stderr_lower for pattern in CODEX_SMOKE_SKIP_PATTERNS):
                    self.skipTest(result.stderr.strip() or "codex smoke blocked by local environment")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SMOKE_OK", result.stdout)

    def test_run_general_auto_detects_mode_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    (
                        "print('一般回答です。');"
                        "print('（参照：honda_wataru_eki_jobun.md|序文）')"
                    ),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("一般回答です。", result.stdout)
            resolve_payload = json.loads((out_dir / "resolve.json").read_text(encoding="utf-8"))
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(resolve_payload["mode"], "general")
            self.assertEqual(run_payload["final_status"], "success")
            self.assertEqual(run_payload["answer_exit_code"], 0)
            self.assertEqual(run_payload["validate_exit_code"], 0)
            self.assertEqual(run_payload["selected_file_count"], 7)
            self.assertEqual(run_payload["validation"]["evidence_status"], "sufficient")
            self.assertEqual(run_payload["validation"]["errors"], 0)
            self.assertEqual(report["evidence_status"], "sufficient")
            self.assertEqual(evidence["matched_evidence"][0]["file"], "honda_wataru_eki_jobun.md")

    def test_run_prefers_explicit_command_over_preset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")
            result = run_workflow(
                str(input_path),
                None,
                str(out_dir),
                "codex-exec",
                [sys.executable, "-c", "print('explicit answer')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')"],
            )
            self.assertEqual(result.exit_code, 0)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["answer_command"], [sys.executable, "-c", "print('explicit answer')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')"])

    def test_run_uses_preset_when_command_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")
            with patch.dict(
                "iching_sdk.answering.ANSWER_PRESETS",
                {
                    "codex-exec": [
                        sys.executable,
                        "-c",
                        "print('preset answer')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')",
                    ]
                },
                clear=False,
            ):
                result = run_workflow(str(input_path), None, str(out_dir), "codex-exec", None)
            self.assertEqual(result.exit_code, 0)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(
                run_payload["answer_command"],
                [
                    sys.executable,
                    "-c",
                    "print('preset answer')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')",
                ],
            )

    def test_run_fails_when_no_preset_or_command_is_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("質問です。\n", encoding="utf-8")
            result = run_workflow(str(input_path), None, str(out_dir), None, None)
            self.assertEqual(result.exit_code, 2)
            self.assertIn("one of answer provider, preset, or command is required", result.stderr_text)

    def test_run_records_provider_metadata_when_using_codex_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="provider answer\n（参照：honda_wataru_eki_jobun.md|序文）\n",
                    stderr="",
                )
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(
                        model="gpt-5",
                        sandbox="workspace-write",
                        approval_policy="never",
                    ),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    "codex",
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                    "--ask-for-approval",
                    "never",
                ],
            )
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["provider"], "codex")
            self.assertEqual(
                run_payload["provider_options"],
                {
                    "model": "gpt-5",
                    "sandbox": "workspace-write",
                    "approval_policy": "never",
                },
            )
            self.assertEqual(run_payload["selected_file_count"], 7)
            self.assertEqual(
                run_payload["selected_groups"],
                [
                    {"group": "general_core", "file_count": 7},
                    {"group": "extract_support", "file_count": 0},
                ],
            )

    def test_run_prefers_explicit_command_over_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")
            result = run_workflow(
                str(input_path),
                None,
                str(out_dir),
                None,
                [sys.executable, "-c", "print('explicit answer')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')"],
                "codex",
                CodexProviderOptions(model="gpt-5"),
            )
            self.assertEqual(result.exit_code, 0)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertIsNone(run_payload["provider"])
            self.assertEqual(
                run_payload["answer_command"],
                [
                    sys.executable,
                    "-c",
                    "print('explicit answer')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')",
                ],
            )

    def test_run_cli_uses_runtime_config_defaults_and_records_provider_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")
            with self.runtime_config_file(
                'provider = "codex"\n'
                'codex_model = "gpt-5"\n'
                'codex_sandbox = "workspace-write"\n'
            ):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n（参照：honda_wataru_eki_jobun.md|序文）\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(
                            [
                                "run",
                                "--input",
                                str(input_path),
                                "--out-dir",
                                str(out_dir),
                            ]
                        )
            self.assertEqual(exit_code, 0)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["provider"], "codex")
            self.assertEqual(
                run_payload["provider_options"],
                {"model": "gpt-5", "sandbox": "workspace-write"},
            )
            self.assertEqual(run_payload["selected_file_count"], 7)

    def test_run_cli_uses_provider_table_runtime_config_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")
            with self.runtime_config_file(
                'default_provider = "codex"\n'
                "[providers.codex]\n"
                'model = "gpt-5"\n'
                'sandbox = "workspace-write"\n'
            ):
                with patch("iching_sdk.answering.subprocess.run") as run_mock:
                    run_mock.return_value = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n（参照：honda_wataru_eki_jobun.md|序文）\n",
                        stderr="",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        exit_code = cli_module.main(
                            [
                                "run",
                                "--input",
                                str(input_path),
                                "--out-dir",
                                str(out_dir),
                            ]
                        )
            self.assertEqual(exit_code, 0)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["provider"], "codex")
            self.assertEqual(
                run_payload["provider_options"],
                {"model": "gpt-5", "sandbox": "workspace-write"},
            )

    def test_run_extract_auto_detects_mode_and_returns_answer_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：1乾為天\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    (
                        "print('抽出回答です。');"
                        "print('（参照：honda_wataru/honda_wataru_1-8.md|乾為天 - 卦辞）')"
                    ),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("抽出回答です。", result.stdout)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["mode"], "extract")
            self.assertEqual(run_payload["final_status"], "success")

    def test_run_mode_override_beats_detected_extract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "override.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:EXTRACT]\n一般質問として扱いたい。\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--mode",
                    "general",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    (
                        "print('override answer');"
                        "print('（参照：honda_wataru_eki_jobun.md|序文）')"
                    ),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            resolve_payload = json.loads((out_dir / "resolve.json").read_text(encoding="utf-8"))
            self.assertEqual(resolve_payload["mode"], "general")
            self.assertEqual(resolve_payload["input_kind"], "general_question")

    def test_run_accepts_stdin_and_passes_prompt_to_answer_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "run-artifacts"
            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    "-",
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    (
                        "import sys; "
                        "prompt = sys.stdin.read(); "
                        "label = 'PROMPT_OK' if 'Input source: stdin' in prompt and 'stdin経由の質問です。' in prompt else 'PROMPT_BAD'; "
                        "print(label); "
                        "print('（参照：honda_wataru_eki_jobun.md|序文）')"
                    ),
                ],
                cwd=REPO_ROOT,
                input="stdin経由の質問です。\n",
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PROMPT_OK", result.stdout)
            prompt_text = (out_dir / "prompt.txt").read_text(encoding="utf-8")
            self.assertIn("- Input source: stdin", prompt_text)
            self.assertTrue((out_dir / "select.json").is_file())

    def test_run_returns_validation_failure_but_keeps_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("参照のない回答を試す。\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('参照なし回答です。')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("参照なし回答です。", result.stdout)
            self.assertIn("validation failed (insufficient_evidence)", result.stderr)
            self.assertTrue((out_dir / "answer.md").is_file())
            self.assertTrue((out_dir / "report.json").is_file())
            self.assertTrue((out_dir / "evidence.json").is_file())
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "validation_failed")
            self.assertEqual(run_payload["validation"]["evidence_status"], "insufficient")
            self.assertIn("insufficient_evidence", run_payload["validation"]["finding_codes"])

    def test_run_returns_runtime_error_when_answer_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("失敗させる質問です。\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "import sys; sys.stderr.write('boom\\n'); raise SystemExit(7)",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("answer command failed with exit code 7", result.stderr)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["answer_exit_code"], 7)
            self.assertIsNone(run_payload["error_type"])
            self.assertEqual(run_payload["error_summary"], "answer command failed with exit code 7")
            self.assertEqual(run_payload["error_source"], "answer_command")
            self.assertEqual(run_payload["error_stderr"], "boom\n")
            self.assertIsNone(run_payload["validation"])
            self.assertFalse((out_dir / "answer.md").exists())

    def test_run_records_codex_missing_failure_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("provider failure を試す。\n", encoding="utf-8")

            with patch(
                "iching_sdk.answering.subprocess.run",
                side_effect=FileNotFoundError(2, "No such file or directory", "codex"),
            ):
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(),
                )

            self.assertEqual(result.exit_code, 2)
            self.assertIn("codex executable not found", result.stderr_text)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_type"], "provider_missing")
            self.assertEqual(run_payload["error_summary"], "codex executable not found")
            self.assertEqual(run_payload["error"], "codex executable not found")
            self.assertEqual(run_payload["error_source"], "provider")
            self.assertIsNone(run_payload["error_stderr"])

    def test_run_records_codex_auth_failure_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("provider auth failure を試す。\n", encoding="utf-8")

            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="Not authenticated. Please run codex login.\n",
                )
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(model="gpt-5"),
                )

            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.stderr_text,
                f"codex authentication required\nartifacts: {out_dir}\n",
            )
            self.assertEqual(
                run_mock.call_args.args[0],
                ["codex", "exec", "--model", "gpt-5"],
            )
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_type"], "provider_auth")
            self.assertEqual(run_payload["error_summary"], "codex authentication required")
            self.assertEqual(run_payload["error"], "codex authentication required")
            self.assertEqual(run_payload["error_source"], "provider")
            self.assertEqual(
                run_payload["error_stderr"],
                "Not authenticated. Please run codex login.\n",
            )
            self.assertIsNone(run_payload["validation"])

    def test_run_missing_input_returns_runtime_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "run-artifacts"
            missing = Path(tmpdir) / "missing.md"
            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(missing),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('unused')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("input file not found", result.stderr)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertIsNone(run_payload["validation"])

    def test_run_workflow_returns_config_error_when_mode_config_fails(self) -> None:
        from unittest.mock import patch
        from iching_sdk.config import ConfigError

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("設定失敗を試す。\n", encoding="utf-8")

            with patch("iching_sdk.running.load_mode_config", side_effect=ConfigError("bad config")):
                result = run_workflow(str(input_path), None, str(out_dir), None, [sys.executable, "-c", "print('unused')"])

            self.assertEqual(result.exit_code, 2)
            self.assertIn("bad config", result.stderr_text)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "config_error")
            self.assertIsNone(run_payload["validation"])

    def test_index_extract_returns_expected_files_in_order(self) -> None:
        result = subprocess.run(
            [*CLI, "index", "--mode", "extract"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "extract")
        self.assertEqual(
            payload["files"][:3],
            [
                "honda_wataru/honda_wataru_1-8.md",
                "honda_wataru/honda_wataru_9-16.md",
                "honda_wataru/honda_wataru_17-24.md",
            ],
        )
        self.assertEqual(payload["files"][-1], "takashima_zouho/takashima_zouho_57-64.md")

    def test_index_general_returns_expected_files_in_order(self) -> None:
        result = subprocess.run(
            [*CLI, "index", "--mode", "general"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["files"],
            [
                "honda_wataru_eki_jobun.md",
                "honda_wataru_eki_sanden.md",
                "keiji_jouden_1-12.md",
                "keiji_kaden_1-12.md",
                "takashima_sendanjizai.md",
                "yasuoka_eki_to_jinseitetsugaku.md",
                "yasuoka_ekigaku_nyumon.md",
            ],
        )

    def test_validate_sufficient_input_writes_json_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text(
                "\n".join(
                    [
                        "本文です。",
                        "（参照：honda_wataru/honda_wataru_1-8.md|乾為天 - 卦辞）",
                        "（参照：takashima_zouho/takashima_zouho_1-8.md|乾為天）",
                    ]
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [*CLI, "validate", "--mode", "extract", "--input", str(input_path), "--out-dir", str(out_dir)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence_status"], "sufficient")
            self.assertEqual(report["summary"]["valid_evidence_files"], 2)
            self.assertEqual(
                evidence["matched_evidence"],
                [
                    {"file": "honda_wataru/honda_wataru_1-8.md", "cited_lines": [2]},
                    {"file": "takashima_zouho/takashima_zouho_1-8.md", "cited_lines": [3]},
                ],
            )

    def test_validate_insufficient_when_no_valid_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text("参照なしです。\n", encoding="utf-8")
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [*CLI, "validate", "--mode", "general", "--input", str(input_path), "--out-dir", str(out_dir)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence_status"], "insufficient")
            self.assertEqual(report["findings"][0]["code"], "insufficient_evidence")

    def test_run_comparison_reports_missing_ranking_and_interpretations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text(
                "\n".join(
                    [
                        "どれがいいか比較して、順位も付けてほしい。",
                        "## 候補A",
                        "- 本卦：42風雷益",
                        "## 候補B",
                        "- 本卦：1乾為天",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('総評だけです。')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("comparison_missing_interpretations", result.stderr)
            self.assertIn("ranking_not_explicit", result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("comparison_missing_interpretations", codes)
            self.assertIn("ranking_not_explicit", codes)

    def test_validate_with_resolve_context_reuses_comparison_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            answer_path = Path(tmpdir) / "answer.md"
            resolve_path = Path(tmpdir) / "resolve.json"
            out_dir = Path(tmpdir) / "validate-out"
            input_path.write_text(
                "\n".join(
                    [
                        "どれがいいか比較して、順位も付けてほしい。",
                        "## 候補A",
                        "- 本卦：42風雷益",
                        "## 候補B",
                        "- 本卦：1乾為天",
                    ]
                ),
                encoding="utf-8",
            )
            answer_path.write_text(
                "総評だけです。\n（参照：honda_wataru_eki_jobun.md|序文）\n",
                encoding="utf-8",
            )

            resolve_result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(resolve_result.returncode, 0, resolve_result.stderr)
            resolve_path.write_text(resolve_result.stdout, encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "general",
                    "--input",
                    str(answer_path),
                    "--context",
                    str(resolve_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("comparison_missing_interpretations", codes)
            self.assertIn("ranking_not_explicit", codes)

    def test_validate_with_run_context_reuses_comparison_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            revalidate_out_dir = Path(tmpdir) / "validate-out"
            input_path.write_text(
                "\n".join(
                    [
                        "どれがいいか比較して、順位も付けてほしい。",
                        "## 候補A",
                        "- 本卦：42風雷益",
                        "## 候補B",
                        "- 本卦：1乾為天",
                    ]
                ),
                encoding="utf-8",
            )

            run_result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('総評だけです。')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(run_result.returncode, 1, run_result.stderr)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertIn("comparison_requested", run_payload["hints"])

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "general",
                    "--input",
                    str(out_dir / "answer.md"),
                    "--context",
                    str(out_dir / "run.json"),
                    "--out-dir",
                    str(revalidate_out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((revalidate_out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("comparison_missing_interpretations", codes)
            self.assertIn("ranking_not_explicit", codes)

    def test_validate_rejects_context_mode_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "resolve.json"
            out_dir = Path(tmpdir) / "validate-out"
            input_path.write_text("本文です。\n（参照：honda_wataru_eki_jobun.md|序文）\n", encoding="utf-8")
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_template",
                        "hints": ["requires_strict_citation"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "general",
                    "--input",
                    str(input_path),
                    "--context",
                    str(context_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence_status"], "runtime_error")
            self.assertIn("does not match --mode general", report["findings"][0]["message"])

    def test_validate_rejects_invalid_context_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "bad-context.json"
            out_dir = Path(tmpdir) / "validate-out"
            input_path.write_text("本文です。\n（参照：honda_wataru_eki_jobun.md|序文）\n", encoding="utf-8")
            context_path.write_text(json.dumps({"mode": "general"}, ensure_ascii=False), encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "general",
                    "--input",
                    str(input_path),
                    "--context",
                    str(context_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence_status"], "runtime_error")
            self.assertIn("validation context missing input_kind", report["findings"][0]["message"])

    def test_validate_reports_missing_answer_body_when_only_citations_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text("（参照：honda_wataru_eki_jobun.md|序文）\n", encoding="utf-8")
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [*CLI, "validate", "--mode", "general", "--input", str(input_path), "--out-dir", str(out_dir)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("missing_answer_body", codes)
            self.assertEqual(report["summary"]["errors"], 1)

    def test_validate_reports_malformed_and_unindexed_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text(
                "\n".join(
                    [
                        "本文です。",
                        "(参照:honda_wataru_eki_jobun.md)",
                        "（参照：not_listed.md|説明）",
                    ]
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [*CLI, "validate", "--mode", "general", "--input", str(input_path), "--out-dir", str(out_dir)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertEqual(codes, {"malformed_citation", "reference_not_indexed", "insufficient_evidence"})

    def test_validate_accepts_stdin(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "out"
            result = subprocess.run(
                [*CLI, "validate", "--mode", "general", "--input", "-", "--out-dir", str(out_dir)],
                cwd=REPO_ROOT,
                input="本文です。\n（参照：honda_wataru_eki_jobun.md|序文）\n",
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["input"], "stdin")

    def test_index_fails_for_missing_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sources_root = Path(tmpdir) / "sources"
            (sources_root / "extract" / "honda_wataru").mkdir(parents=True)
            (sources_root / "general").mkdir(parents=True)
            (sources_root / "extract" / "honda_wataru" / "honda_wataru_1-8.md").write_text(
                "dummy\n",
                encoding="utf-8",
            )
            (sources_root / "index.md").write_text(
                "### extract\n- honda_wataru/honda_wataru_1-8.md\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "index", "--mode", "extract", "--sources-root", str(sources_root)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("missing index section", result.stderr)

    def test_validate_returns_runtime_error_for_missing_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "out"
            result = subprocess.run(
                [*CLI, "validate", "--mode", "general", "--input", str(Path(tmpdir) / "missing.md"), "--out-dir", str(out_dir)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence_status"], "runtime_error")

    def test_build_prompt_auto_detects_extract_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_SIMPLE]",
                        "",
                        "### 1. 占いに至った背景・状況",
                        "状況メモです。",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "build-prompt", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Mode Override\n[MODE:EXTRACT]", result.stdout)
            self.assertIn("[TEMPLATE:EX_SIMPLE]", result.stdout)
            self.assertIn("## Selected Sources", result.stdout)
            self.assertIn("- extract_honda:", result.stdout)
            self.assertIn("  - honda_wataru/honda_wataru_1-8.md", result.stdout)
            self.assertIn("## Prompt Instructions", result.stdout)
            self.assertIn("## EXTRACT standard structure", result.stdout)
            self.assertIn("**本田解釈**", result.stdout)
            self.assertIn("**高島解釈**", result.stdout)
            self.assertIn("`統合解釈` や一本化した総合解釈は使わない", result.stdout)
            self.assertIn("支えを受けて整う構図", result.stdout)
            self.assertIn("2〜3 文を基本とする", result.stdout)
            self.assertIn("本田解釈は本田系ソースで完結", result.stdout)
            self.assertIn("高島解釈は高島系ソースで完結", result.stdout)
            self.assertIn("之卦・互卦・錯卦・綜卦を可能な限り全部束ねて扱う", result.stdout)

    def test_build_prompt_preserves_ex5_raw_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_5]",
                        "",
                        "本卦：5水天需",
                        "互卦：38火澤睽",
                        "錯卦：35火地晋",
                        "綜卦：6天水訟",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "build-prompt", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[TEMPLATE:EX_5]", result.stdout)
            self.assertIn("互卦：38火澤睽", result.stdout)
            self.assertIn("綜卦：6天水訟", result.stdout)
            self.assertIn("## EXTRACT auxiliary hexagrams", result.stdout)
            self.assertIn("本卦 -> 変爻 -> 之卦 -> 互卦 -> 錯卦 -> 綜卦 -> 本田解釈 -> 高島解釈", result.stdout)
            self.assertIn("補助卦ありでも末尾は `総合解釈` に一本化せず", result.stdout)
            self.assertIn("本田解釈の中で高島ソースを使ったり", result.stdout)
            self.assertIn("補助卦全体の働きを本卦に接続して述べる", result.stdout)

    def test_build_prompt_includes_compare_section_for_extract_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_COMPARE]",
                        "",
                        "### 1. 占いに至った背景・状況",
                        "次にやるゲームで迷っている。",
                        "",
                        "### 2. 易経への質問",
                        "どれがよいか、順位付きで知りたい。",
                        "",
                        "### 3. 占い結果入力",
                        "候補A：",
                        "本卦：42風雷益",
                        "変爻：4爻",
                        "",
                        "候補B：",
                        "本卦：24地雷復",
                        "変爻：初爻",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "build-prompt", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Mode Override\n[MODE:EXTRACT]", result.stdout)
            self.assertIn("## EXTRACT comparison structure", result.stdout)
            self.assertIn("吉凶順位", result.stdout)
            self.assertIn("順位 | タイトル | 卦・爻 | 断辞/要点", result.stdout)
            self.assertNotIn("## GENERAL mode instructions", result.stdout)

    def test_build_prompt_defaults_to_general_and_adds_comparison_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            input_path.write_text(
                "\n".join(
                    [
                        "次にやるゲームを比較したい。",
                        "## 候補A",
                        "- 本卦：42風雷益",
                        "- 変爻：4爻",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "build-prompt", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Mode Override\n[MODE:GENERAL]", result.stdout)
            self.assertIn("## Selected Sources", result.stdout)
            self.assertIn("- general_core:", result.stdout)
            self.assertIn("- extract_support:", result.stdout)
            self.assertIn("比較占いでは候補ごとに短い解釈を付ける", result.stdout)
            self.assertIn("（参照：filename.md|section）", result.stdout)
            self.assertIn("Markdown link", result.stdout)
            self.assertIn("## 候補A", result.stdout)

    def test_extract_case_manifest_prioritizes_adopted_cases_and_supports_expected_answers(self) -> None:
        payload = json.loads(EXTRACT_CASES_MANIFEST.read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(
            [case["id"] for case in cases[:3]],
            [
                "extract-standard-test-1",
                "extract-complex-test-2",
                "extract-complex-test-3",
            ],
        )
        self.assertEqual(
            [case["kind"] for case in cases[:3]],
            ["standard", "complex", "complex"],
        )
        self.assertEqual(
            [case["expected_mode"] for case in cases],
            ["extract"] * len(cases),
        )
        self.assertEqual(
            [case["required_sections"] for case in cases[:3]],
            [
                ["核心・結論", "本卦", "変爻"],
                ["核心・結論", "本卦", "変爻", "補助卦"],
                ["核心・結論", "本卦", "変爻", "補助卦"],
            ],
        )
        self.assertEqual(
            [case["expected_answer"] for case in cases[:3]],
            [
                "tests/fixtures/extract_cases/test_1_answer_canonical.md",
                "tests/fixtures/extract_cases/test_2_answer_canonical.md",
                "tests/fixtures/extract_cases/test_3_answer_canonical.md",
            ],
        )

    def test_build_prompt_excludes_auxiliary_section_for_standard_extract_case(self) -> None:
        input_path = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_1.md"

        result = subprocess.run(
            [*CLI, "build-prompt", "--input", str(input_path)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## EXTRACT standard structure", result.stdout)
        self.assertNotIn("## EXTRACT auxiliary hexagrams", result.stdout)
        self.assertIn("**本田解釈**", result.stdout)
        self.assertIn("**高島解釈**", result.stdout)
        self.assertIn("2 段落以上", result.stdout)
        self.assertIn("流れが自然に収束する文章", result.stdout)
        self.assertIn("本卦：42風雷益", result.stdout)

    def test_build_prompt_includes_auxiliary_section_for_complex_extract_case(self) -> None:
        input_path = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_2.md"

        result = subprocess.run(
            [*CLI, "build-prompt", "--input", str(input_path)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## EXTRACT standard structure", result.stdout)
        self.assertIn("## EXTRACT auxiliary hexagrams", result.stdout)
        self.assertIn("互卦：38火澤睽", result.stdout)
        self.assertIn("**之卦（<卦名>）**", result.stdout)
        self.assertIn("**彖伝**", result.stdout)
        self.assertIn("**大象伝**", result.stdout)

    def test_build_prompt_handles_full_auxiliary_extract_case(self) -> None:
        input_path = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_3.md"

        result = subprocess.run(
            [*CLI, "build-prompt", "--input", str(input_path)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## EXTRACT auxiliary hexagrams", result.stdout)
        self.assertIn("之卦：54.雷沢帰妹", result.stdout)
        self.assertIn("互卦：43.沢天夬", result.stdout)
        self.assertIn("錯卦：20.風地観", result.stdout)
        self.assertIn("綜卦：33.天山遯", result.stdout)

    def test_validate_accepts_canonical_extract_answers_from_manifest(self) -> None:
        payload = json.loads(EXTRACT_CASES_MANIFEST.read_text(encoding="utf-8"))
        adopted_cases = payload["cases"][:3]

        for case in adopted_cases:
            with self.subTest(case=case["id"]):
                answer_path = REPO_ROOT / case["expected_answer"]
                with tempfile.TemporaryDirectory() as tmpdir:
                    out_dir = Path(tmpdir) / "validate-out"
                    result = subprocess.run(
                        [
                            *CLI,
                            "validate",
                            "--mode",
                            "extract",
                            "--input",
                            str(answer_path),
                            "--out-dir",
                            str(out_dir),
                        ],
                        cwd=REPO_ROOT,
                        check=False,
                            capture_output=True,
                            text=True,
                        )
                    report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(report["summary"]["errors"], 0)
                self.assertFalse(
                    any(finding["code"] == "reference_not_indexed" for finding in report["findings"])
                )

    def test_validate_accepts_compare_canonical_answer_with_context(self) -> None:
        input_path = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_4.md"
        answer_path = (
            REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_4_answer_canonical.md"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            resolve_path = Path(tmpdir) / "resolve.json"
            out_dir = Path(tmpdir) / "validate-out"
            resolve_result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(resolve_result.returncode, 0, resolve_result.stderr)
            resolve_path.write_text(resolve_result.stdout, encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "extract",
                    "--input",
                    str(answer_path),
                    "--context",
                    str(resolve_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(report["summary"]["errors"], 0)

    def test_canonical_extract_answers_start_with_core_conclusion_and_drop_history_labels(self) -> None:
        payload = json.loads(EXTRACT_CASES_MANIFEST.read_text(encoding="utf-8"))

        for case in payload["cases"][:3]:
            with self.subTest(case=case["id"]):
                answer_text = (REPO_ROOT / case["expected_answer"]).read_text(encoding="utf-8")
                self.assertTrue(answer_text.startswith("**核心・結論**"))
                self.assertNotIn("ChatGPT", answer_text)
                self.assertNotIn("iching-sdkの回答", answer_text)
                self.assertNotIn("ekikyo-sdkの回答", answer_text)

    def test_canonical_extract_answers_keep_required_case_specific_sections(self) -> None:
        answer_2 = (
            REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_2_answer_canonical.md"
        ).read_text(encoding="utf-8")
        answer_3 = (
            REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_3_answer_canonical.md"
        ).read_text(encoding="utf-8")

        self.assertIn("**変爻**", answer_2)
        self.assertIn("今回は変爻がないため", answer_2)
        self.assertIn("**互卦（火澤睽）**", answer_2)
        self.assertIn("**錯卦（火地晋）**", answer_2)
        self.assertIn("**綜卦（天水訟）**", answer_2)

        self.assertIn("**之卦（雷澤帰妹）**", answer_3)
        self.assertIn("**互卦（沢天夬）**", answer_3)
        self.assertIn("**錯卦（風地観）**", answer_3)
        self.assertIn("**綜卦（天山遯）**", answer_3)

    def test_compare_canonical_answer_keeps_ranked_sections_and_summary_table(self) -> None:
        answer_4 = (
            REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_4_answer_canonical.md"
        ).read_text(encoding="utf-8")

        self.assertIn("**吉凶順位（1位 = 最吉）**", answer_4)
        self.assertIn("### 1位 エントロピーセンター（24地雷復・初爻）", answer_4)
        self.assertIn("### 8位 ソニック（42風雷益・上爻）", answer_4)
        self.assertIn("| 順位 | タイトル | 卦・爻 | 断辞/要点 |", answer_4)

    def test_run_writes_select_artifact_and_prompt_includes_selected_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("易の考え方を教えてください。\n", encoding="utf-8")

            result = subprocess.run(
                [
                    *CLI,
                    "run",
                    "--input",
                    str(input_path),
                    "--out-dir",
                    str(out_dir),
                    "--answer-cmd",
                    sys.executable,
                    "-c",
                    "print('一般回答です。')\nprint('（参照：honda_wataru_eki_jobun.md|序文）')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            select_payload = json.loads((out_dir / "select.json").read_text(encoding="utf-8"))
            self.assertEqual(select_payload["selected_file_count"], 7)
            prompt_text = (out_dir / "prompt.txt").read_text(encoding="utf-8")
            self.assertIn("## Selected Sources", prompt_text)
            self.assertIn("- general_core:", prompt_text)

    def test_build_prompt_general_override_beats_extract_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "override.md"
            input_path.write_text("[MODE:EXTRACT]\n質問本文\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "build-prompt", "--mode", "general", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Mode Override\n[MODE:GENERAL]", result.stdout)

    def test_build_prompt_accepts_stdin(self) -> None:
        result = subprocess.run(
            [*CLI, "build-prompt", "--input", "-"],
            cwd=REPO_ROOT,
            input="一般的な易の質問です。\n",
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("- Input source: stdin", result.stdout)
        self.assertIn("一般的な易の質問です。", result.stdout)

    def test_build_prompt_missing_input_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.md"
            result = subprocess.run(
                [*CLI, "build-prompt", "--input", str(missing)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("input file not found", result.stderr)

    def test_select_extract_template_returns_grouped_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "select", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "extract")
            self.assertEqual(
                [group["group"] for group in payload["selected_groups"]],
                ["extract_honda", "extract_takashima", "general_support"],
            )
            self.assertEqual(len(payload["selected_groups"][0]["files"]), 8)
            self.assertEqual(len(payload["selected_groups"][1]["files"]), 8)
            self.assertEqual(len(payload["selected_groups"][2]["files"]), 7)
            self.assertEqual(payload["selected_file_count"], 23)

    def test_select_extract_comparison_returns_extract_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n候補A：\n本卦：42風雷益\n変爻：4爻\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "select", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "extract")
            self.assertEqual(payload["input_kind"], "extract_comparison")
            self.assertEqual(
                [group["group"] for group in payload["selected_groups"]],
                ["extract_honda", "extract_takashima", "general_support"],
            )

    def test_select_general_comparison_includes_extract_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            input_path.write_text(
                "\n".join(
                    [
                        "どれがいいか、オススメしてほしい。",
                        "吉である順番にも並べてほしい。",
                        "## 候補A",
                        "- 本卦：42風雷益",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "select", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "general")
            self.assertEqual(payload["input_kind"], "general_comparison")
            self.assertEqual(
                [group["group"] for group in payload["selected_groups"]],
                ["general_core", "extract_support"],
            )
            self.assertEqual(len(payload["selected_groups"][0]["files"]), 7)
            self.assertEqual(len(payload["selected_groups"][1]["files"]), 16)
            self.assertEqual(payload["selected_file_count"], 23)

    def test_select_general_question_skips_extract_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "question.md"
            input_path.write_text("易の考え方について教えてください。\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "select", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "general")
            self.assertEqual(payload["input_kind"], "general_question")
            self.assertEqual(payload["selected_groups"][0]["group"], "general_core")
            self.assertEqual(payload["selected_groups"][1]["group"], "extract_support")
            self.assertEqual(payload["selected_groups"][1]["files"], [])
            self.assertEqual(payload["selected_file_count"], 7)

    def test_select_mode_override_beats_detected_extract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "override.md"
            input_path.write_text("[MODE:EXTRACT]\n比較したいです。\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "select", "--mode", "general", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "general")
            self.assertEqual(payload["input_kind"], "general_comparison")

    def test_answer_cli_reports_invalid_runtime_config_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file('provider = "codex"\ninvalid = [\n'):
                result = subprocess.run(
                    [*CLI, "answer", "--prompt", str(prompt_path)],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid runtime config TOML", result.stderr)

    def test_answer_cli_reports_unknown_runtime_config_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file('provider = "codex"\nextra = "nope"\n'):
                result = subprocess.run(
                    [*CLI, "answer", "--prompt", str(prompt_path)],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(result.returncode, 2)
            self.assertIn("unknown runtime config keys", result.stderr)

    def test_answer_cli_reports_unknown_runtime_config_provider_table_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file('[providers.openai]\nmodel = "gpt-5"\n'):
                result = subprocess.run(
                    [*CLI, "answer", "--prompt", str(prompt_path)],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(result.returncode, 2)
            self.assertIn("unknown runtime config providers", result.stderr)

    def test_answer_cli_reports_invalid_provider_table_value_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'default_provider = "codex"\n'
                "[providers.codex]\n"
                "model = 123\n"
            ):
                result = subprocess.run(
                    [*CLI, "answer", "--prompt", str(prompt_path)],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(result.returncode, 2)
            self.assertIn("providers.codex.model", result.stderr)

    def test_answer_cli_reports_unknown_default_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'default_provider = "openai"\n'
            ):
                result = subprocess.run(
                    [*CLI, "answer", "--prompt", str(prompt_path)],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(result.returncode, 2)
            self.assertIn("unknown runtime config provider", result.stderr)

    def test_validate_cli_ignores_broken_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "answer.md"
            out_dir = Path(tmpdir) / "validate-out"
            input_path.write_text("回答です。\n（参照：honda_wataru_eki_jobun.md|序文）\n", encoding="utf-8")
            with self.runtime_config_file('provider = "codex"\ninvalid = [\n'):
                result = subprocess.run(
                    [
                        *CLI,
                        "validate",
                        "--mode",
                        "general",
                        "--input",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                    ],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_resolve_extract_template_returns_expected_groups_and_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "extract")
            self.assertEqual(payload["input_kind"], "extract_template")
            self.assertEqual(
                payload["source_groups"],
                ["extract_honda", "extract_takashima", "general_support"],
            )
            self.assertIn("requires_strict_citation", payload["hints"])
            self.assertIn("template_marker_present", payload["hints"])

    def test_resolve_general_comparison_detects_ranking_hint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            input_path.write_text(
                "\n".join(
                    [
                        "どれがいいか、オススメしてほしい。",
                        "吉である順番にも並べてほしい。",
                        "## 候補A",
                        "- 本卦：42風雷益",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "general")
            self.assertEqual(payload["input_kind"], "general_comparison")
            self.assertEqual(payload["source_groups"], ["general_core", "extract_support"])
            self.assertIn("comparison_requested", payload["hints"])
            self.assertIn("ranking_requested", payload["hints"])

    def test_resolve_extract_comparison_detects_ranking_hint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_COMPARE]",
                        "順位を付けておすすめしてほしい。",
                        "候補A：",
                        "本卦：42風雷益",
                        "変爻：4爻",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "extract")
            self.assertEqual(payload["input_kind"], "extract_comparison")
            self.assertIn("comparison_requested", payload["hints"])
            self.assertIn("ranking_requested", payload["hints"])

    def test_resolve_general_question_detects_plain_question(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "question.md"
            input_path.write_text("易の考え方について教えてください。\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "general")
            self.assertEqual(payload["input_kind"], "general_question")
            self.assertEqual(payload["hints"], [])

    def test_resolve_mode_override_beats_detected_extract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "override.md"
            input_path.write_text("[MODE:EXTRACT]\n比較したいです。\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "resolve", "--mode", "general", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "general")
            self.assertEqual(payload["input_kind"], "general_comparison")

    def test_validate_extract_compare_reports_missing_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "総評だけです。\n（参照：honda_wataru/honda_wataru_17-24.md|地雷復 - 初爻）\n",
                encoding="utf-8",
            )
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_comparison",
                        "hints": [
                            "requires_strict_citation",
                            "comparison_requested",
                            "ranking_requested",
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "extract",
                    "--input",
                    str(answer_path),
                    "--context",
                    str(context_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("compare_missing_core_conclusion", codes)
            self.assertIn("compare_missing_ranking_section", codes)
            self.assertIn("compare_missing_candidate_sections", codes)
            self.assertIn("compare_missing_summary_table", codes)
            self.assertIn("ranking_not_explicit", codes)

    def test_validate_extract_compare_accepts_plain_ranked_candidate_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "\n".join(
                    [
                        "**核心・結論**",
                        "比較結果です。",
                        "",
                        "**吉凶順位**",
                        "1位 候補A（24地雷復・初爻）",
                        "2位 候補B（42風雷益・4爻）",
                        "",
                        "1位 候補A(24地雷復・初爻)",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/honda_wataru_17-24.md|地雷復 - 初爻）",
                        "",
                        "2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/honda_wataru_41-48.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_comparison",
                        "hints": [
                            "requires_strict_citation",
                            "comparison_requested",
                            "ranking_requested",
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "extract",
                    "--input",
                    str(answer_path),
                    "--context",
                    str(context_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("compare_missing_candidate_sections", codes)

    def test_validate_extract_compare_rejects_ranked_lines_without_hexagram_info(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "\n".join(
                    [
                        "**核心・結論**",
                        "比較結果です。",
                        "",
                        "**吉凶順位**",
                        "1位 候補A",
                        "2位 候補B",
                        "",
                        "1位 候補A",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/honda_wataru_17-24.md|地雷復 - 初爻）",
                        "",
                        "2位 候補B",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/honda_wataru_41-48.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_comparison",
                        "hints": [
                            "requires_strict_citation",
                            "comparison_requested",
                            "ranking_requested",
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--mode",
                    "extract",
                    "--input",
                    str(answer_path),
                    "--context",
                    str(context_path),
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            codes = {finding["code"] for finding in report["findings"]}
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("compare_missing_candidate_sections", codes)

    def test_resolve_missing_input_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.md"
            result = subprocess.run(
                [*CLI, "resolve", "--input", str(missing)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("input file not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
