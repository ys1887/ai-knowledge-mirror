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
CODEX_PATH = "/home/ys/.nvm/versions/node/v22.21.1/bin/codex"
CODEX_VERSION = "codex-cli 0.114.0"


def write_split_fixture(root: Path, source_name: str) -> None:
    if source_name == "honda_wataru":
        root_name = "extract_honda_split"
        names = {
            5: "水天需",
            6: "天水訟",
            24: "地雷復",
            35: "火地晋",
            38: "火澤睽",
            42: "風雷益",
        }
    elif source_name == "takashima_zouho":
        root_name = "extract_takashima_split"
        names = {
            5: "水天需",
            6: "天水訟",
            24: "地雷復",
            35: "火地晋",
            38: "火沢睽",
            42: "風雷益",
        }
    else:
        raise ValueError(f"unsupported split fixture source: {source_name}")
    entries = [
        (5, names[5], f"{source_name}/05_{names[5]}.md", ["kaji", "tanden", "taisho", "yao_2"]),
        (6, names[6], f"{source_name}/06_{names[6]}.md", ["kaji", "tanden", "taisho"]),
        (24, names[24], f"{source_name}/24_{names[24]}.md", ["kaji", "taisho", "yao_1"]),
        (35, names[35], f"{source_name}/35_{names[35]}.md", ["kaji", "tanden", "taisho"]),
        (38, names[38], f"{source_name}/38_{names[38]}.md", ["kaji", "tanden", "taisho"]),
        (42, names[42], f"{source_name}/42_{names[42]}.md", ["kaji", "tanden", "taisho", "yao_4", "yao_5", "yao_6"]),
    ]
    index_payload = []
    for number, name, source_file, section_names in entries:
        folder_name = f"{number:02d}_{name}"
        folder = root / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        sections = {section_name: f"{section_name}.md" for section_name in section_names}
        manifest = {
            "number": number,
            "name": name,
            "source": source_name,
            "source_file": source_file,
            "sections": sections,
        }
        (folder / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        for section_name, filename in sections.items():
            heading = section_name
            (folder / filename).write_text(
                f"---\nnumber: {number}\nname: \"{name}\"\nsection: \"{heading}\"\nsource_file: \"{source_file}\"\n---\n\n### {heading}\n\n本文\n",
                encoding="utf-8",
            )
        index_payload.append(
            {
                "number": number,
                "name": name,
                "folder_path": f"sources/{root_name}/{folder_name}",
                "sections": section_names,
                "special_sections": {
                    "bungen": False,
                    "yongjiu": False,
                    "yongliu": False,
                },
                "has_exceptions": False,
            }
        )
    (root / "index.json").write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "exceptions.json").write_text("[]\n", encoding="utf-8")


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
        with patch("iching_sdk.answering.shutil.which", return_value=CODEX_PATH), patch(
            "iching_sdk.answering.resolve_codex_version", return_value=CODEX_VERSION
        ):
            self.assertEqual(
                resolve_answer_command("codex-exec", None),
                [CODEX_PATH, "exec"],
            )
        self.assertEqual(list_answer_presets(), ["codex-exec"])
        self.assertEqual(list_answer_providers(), ["codex"])

    def test_build_codex_command_applies_requested_options(self) -> None:
        command = build_codex_command(
            CodexProviderOptions(
                path=CODEX_PATH,
                model="gpt-5",
                sandbox="workspace-write",
                approval_policy="never",
            )
        )
        self.assertEqual(
            command,
            [
                CODEX_PATH,
                "exec",
                "--model",
                "gpt-5",
                "--sandbox",
                "workspace-write",
            ],
        )

    def test_build_codex_command_falls_back_to_which_when_path_is_unset(self) -> None:
        with patch("iching_sdk.answering.shutil.which", return_value=CODEX_PATH):
            command = build_codex_command(CodexProviderOptions(model="gpt-5"))
        self.assertEqual(command, [CODEX_PATH, "exec", "--model", "gpt-5"])

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
            with patch("iching_sdk.answering.resolve_codex_version", return_value=CODEX_VERSION), patch(
                "iching_sdk.answering.subprocess.run"
            ) as run_mock:
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
                    CodexProviderOptions(path=CODEX_PATH, model="gpt-5"),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(
                run_mock.call_args.args[0],
                [CODEX_PATH, "exec", "--model", "gpt-5"],
            )
            self.assertEqual(result.provider, "codex")
            self.assertTrue(result.preflight_ran)
            self.assertEqual(result.preflight_exit_code, 0)

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
                codex_path=CODEX_PATH,
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            )
        )
        self.assertEqual(
            provider_options,
            CodexProviderOptions(
                path=CODEX_PATH,
                model="gpt-5",
                sandbox="workspace-write",
                approval_policy="never",
            ),
        )

    def test_build_provider_options_returns_none_without_provider(self) -> None:
        provider_options = cli_module.build_provider_options(
            ResolvedRuntimeConfig(
                provider=None,
                codex_path=CODEX_PATH,
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
            f'path = "{CODEX_PATH}"\n'
            'model = "gpt-5"\n'
            'sandbox = "workspace-write"\n'
            'approval_policy = "never"\n'
        ):
            runtime_config = load_runtime_config()
        self.assertEqual(runtime_config.default_provider, "codex")
        self.assertEqual(
            runtime_config.provider_config("codex"),
            ProviderRuntimeConfig(
                path=CODEX_PATH,
                model="gpt-5",
                sandbox="workspace-write",
                approval_policy="never",
            ),
        )
        self.assertEqual(runtime_config.provider, "codex")
        self.assertEqual(runtime_config.codex_model, "gpt-5")

    def test_load_runtime_config_defaults_profile_to_legacy_and_merges_builtin_profiles(self) -> None:
        with self.runtime_config_file('default_provider = "codex"\n'):
            runtime_config = load_runtime_config()
        self.assertEqual(runtime_config.default_profile, "legacy")
        self.assertEqual(runtime_config.profile_config("legacy").name, "legacy")
        self.assertEqual(runtime_config.profile_config("honda").extract_source_kind, "split")
        self.assertEqual(runtime_config.profile_config("takashima").extract_source_kind, "split")

    def test_resolve_runtime_config_reads_provider_structured_config(self) -> None:
        resolved = resolve_runtime_config(
            RuntimeConfig(
                default_provider="codex",
                providers={
                    "codex": ProviderRuntimeConfig(
                        path=CODEX_PATH,
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
                codex_path=CODEX_PATH,
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            ),
        )

    def test_resolve_runtime_config_cli_overrides_structured_provider_defaults(self) -> None:
        resolved = resolve_runtime_config(
            RuntimeConfig(
                default_provider="codex",
                providers={"codex": ProviderRuntimeConfig(path=CODEX_PATH, model="gpt-5-mini")},
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
                codex_path=CODEX_PATH,
                codex_model="gpt-5",
                codex_sandbox="workspace-write",
                codex_approval_policy="never",
            ),
        )

    def test_answer_cli_allows_codex_options_when_runtime_config_sets_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(f'provider = "codex"\n[providers.codex]\npath = "{CODEX_PATH}"\n'):
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
                [CODEX_PATH, "exec", "--model", "gpt-5"],
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
                f'[providers.codex]\npath = "{CODEX_PATH}"\n'
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
                    CODEX_PATH,
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                ],
            )

    def test_answer_cli_uses_provider_table_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with self.runtime_config_file(
                'default_provider = "codex"\n'
                "[providers.codex]\n"
                f'path = "{CODEX_PATH}"\n'
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
                    CODEX_PATH,
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
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
                f'path = "{CODEX_PATH}"\n'
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
                    CODEX_PATH,
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
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
                f'[providers.codex]\npath = "{CODEX_PATH}"\n'
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
                    CODEX_PATH,
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                ],
            )

    def test_answer_cli_runs_codex_provider_with_requested_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.resolve_codex_version", return_value=CODEX_VERSION), patch(
                "iching_sdk.answering.subprocess.run"
            ) as run_mock:
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
                        path=CODEX_PATH,
                        model="gpt-5",
                        sandbox="workspace-write",
                        approval_policy="never",
                    ),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    CODEX_PATH,
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                ],
            )
            self.assertEqual(result.provider, "codex")
            self.assertEqual(
                result.provider_options,
                {
                    "model": "gpt-5",
                    "sandbox": "workspace-write",
                },
            )
            self.assertEqual(result.resolved_codex_path, CODEX_PATH)

    def test_answer_returns_runtime_error_when_codex_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch(
                "iching_sdk.answering.subprocess.run",
                side_effect=FileNotFoundError(2, "No such file or directory", CODEX_PATH),
            ):
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertIn("codex executable not found", result.stderr_text)
            self.assertEqual(result.error_type, "provider_missing")
            self.assertEqual(result.error_summary, "preflight failed: codex executable not found")
            self.assertIsNone(result.raw_stderr)
            self.assertEqual(result.resolved_codex_path, CODEX_PATH)

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
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_auth")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex authentication required",
            )
            self.assertEqual(
                result.stderr_text,
                "preflight failed: codex authentication required\n",
            )
            self.assertEqual(
                result.raw_stderr,
                "Authentication required. Please run codex login.\n",
            )
            self.assertTrue(result.preflight_ran)
            self.assertEqual(result.preflight_exit_code, 1)
            self.assertEqual(
                result.preflight_stderr,
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
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_auth")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex authentication required",
            )

    def test_answer_classifies_codex_connection_failure(self) -> None:
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
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_connection")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex connection issue (exit code 17): upstream timeout",
            )
            self.assertEqual(
                result.stderr_text,
                "preflight failed: codex connection issue (exit code 17): upstream timeout\n",
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
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_execution_failed")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex provider failed with exit code 23: login shell failed to start",
            )

    def test_answer_classifies_codex_cli_compat_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=2,
                    stdout="",
                    stderr="error: unexpected argument '--ask-for-approval' found\n",
                )
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_cli_compat")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex CLI compatibility issue (cli argument error) (exit code 2): error: unexpected argument '--ask-for-approval' found",
            )

    def test_answer_classifies_codex_sandbox_or_fs_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="attempt to write a readonly database\n",
                )
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(result.error_type, "provider_sandbox_or_fs")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex sandbox or filesystem issue (readonly filesystem) (exit code 1): attempt to write a readonly database",
            )

    def test_answer_classifies_codex_state_db_failure_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="failed to open state db at /tmp/state.sqlite\n",
                )
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.error_type, "provider_sandbox_or_fs")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex sandbox or filesystem issue (state db open failure) (exit code 1): failed to open state db at /tmp/state.sqlite",
            )

    def test_answer_classifies_codex_shell_snapshot_failure_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="Failed to create shell snapshot\n",
                )
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.error_type, "provider_sandbox_or_fs")
            self.assertEqual(
                result.error_summary,
                "preflight failed: codex sandbox or filesystem issue (shell snapshot failure) (exit code 1): Failed to create shell snapshot",
            )

    def test_answer_preflight_success_runs_full_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.resolve_codex_version", return_value=CODEX_VERSION), patch(
                "iching_sdk.answering.subprocess.run"
            ) as run_mock:
                run_mock.side_effect = [
                    subprocess.CompletedProcess(args=["codex", "exec"], returncode=0, stdout="OK\n", stderr=""),
                    subprocess.CompletedProcess(args=["codex", "exec"], returncode=0, stdout="provider answer\n", stderr=""),
                ]
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.stdout_text, "provider answer\n")
            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(run_mock.call_args_list[0].kwargs["input"], "Reply with exactly OK.\n")
            self.assertEqual(run_mock.call_args_list[1].kwargs["input"], "prompt body\n")
            self.assertTrue(result.preflight_ran)
            self.assertEqual(result.preflight_exit_code, 0)

    def test_answer_explicit_command_does_not_run_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_path = Path(tmpdir) / "prompt.txt"
            prompt_path.write_text("prompt body\n", encoding="utf-8")
            with patch("iching_sdk.answering.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess(
                    args=[sys.executable, "-c", "print('explicit')"],
                    returncode=0,
                    stdout="explicit\n",
                    stderr="",
                )
                result = answer_prompt(
                    str(prompt_path),
                    None,
                    [sys.executable, "-c", "print('explicit')"],
                )
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(result.preflight_ran)
            self.assertIsNone(result.preflight_exit_code)
            self.assertEqual(run_mock.call_count, 1)

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
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")

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
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")
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
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")
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
            input_path.write_text("[MODE:GENERAL]\n質問です。\n", encoding="utf-8")
            result = run_workflow(str(input_path), None, str(out_dir), None, None)
            self.assertEqual(result.exit_code, 2)
            self.assertIn("one of answer provider, preset, or command is required", result.stderr_text)

    def test_run_missing_answer_execution_fails_before_reading_stdin(self) -> None:
        class ExplodingStdin:
            def read(self) -> str:
                raise AssertionError("stdin should not be read")

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "run-artifacts"
            with patch("sys.stdin", new=ExplodingStdin()):
                result = run_workflow("-", None, str(out_dir), None, None)

            self.assertEqual(result.exit_code, 2)
            self.assertIn("one of answer provider, preset, or command is required", result.stderr_text)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_source"], "runtime")
            self.assertEqual(run_payload["input"], "-")
            self.assertFalse((out_dir / "resolve.json").exists())
            self.assertFalse((out_dir / "prompt.txt").exists())

    def test_run_extract_missing_mode_marker_fails_before_answer_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[TEMPLATE:EX_COMPARE]\n候補A：\n本卦：42風雷益\n変爻：4爻\n", encoding="utf-8")

            with patch("iching_sdk.running.execute_answer_command") as answer_mock:
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    [sys.executable, "-c", "print('unused')"],
                )

            self.assertEqual(result.exit_code, 2)
            self.assertIn("MODE marker must be the first non-empty line", result.stderr_text)
            answer_mock.assert_not_called()
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_source"], "runtime")
            self.assertIn("MODE marker must be the first non-empty line", run_payload["error_summary"])
            self.assertFalse((out_dir / "resolve.json").exists())
            self.assertFalse((out_dir / "prompt.txt").exists())

    def test_run_extract_missing_template_marker_fails_before_answer_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:EXTRACT]\n候補A：\n本卦：42風雷益\n変爻：4爻\n", encoding="utf-8")

            with patch("iching_sdk.running.execute_answer_command") as answer_mock:
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    [sys.executable, "-c", "print('unused')"],
                )

            self.assertEqual(result.exit_code, 2)
            self.assertIn("EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT].", result.stderr_text)
            answer_mock.assert_not_called()
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_source"], "runtime")
            self.assertIn("EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT].", run_payload["error_summary"])
            self.assertFalse((out_dir / "resolve.json").exists())
            self.assertFalse((out_dir / "prompt.txt").exists())

    def test_run_extract_compare_with_fewer_than_two_candidates_fails_before_answer_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n候補A：\n本卦：42風雷益\n変爻：4爻\n",
                encoding="utf-8",
            )

            with patch("iching_sdk.running.execute_answer_command") as answer_mock:
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    [sys.executable, "-c", "print('unused')"],
                )

            self.assertEqual(result.exit_code, 2)
            self.assertIn("EX_COMPARE requires at least two candidates in the result input block.", result.stderr_text)
            answer_mock.assert_not_called()
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_source"], "runtime")
            self.assertIn(
                "EX_COMPARE requires at least two candidates in the result input block.",
                run_payload["error_summary"],
            )
            self.assertFalse((out_dir / "resolve.json").exists())
            self.assertFalse((out_dir / "prompt.txt").exists())

    def test_run_extract_compare_validates_headers_before_answer_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text(
                (
                    "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n"
                    "候補A：\n本卦：24地雷復\n変爻：初爻\n\n"
                    "候補B：\n本卦：42風雷益\n変爻：4爻\n"
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
                    (
                        "print('**核心・結論**');"
                        "print('候補Aを推します。');"
                        "print('');"
                        "print('**吉凶順位（1位 = 最吉）**');"
                        "print('1. 候補A（24地雷復・初爻）');"
                        "print('2. 候補B（42風雷益・4爻）');"
                        "print('');"
                        "print('### 1位 候補A（24地雷復・初爻）');"
                        "print('候補Aの比較解釈です。');"
                        "print('（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）');"
                        "print('');"
                        "print('### 2位 候補B（42風雷益・4爻）');"
                        "print('候補Bの比較解釈です。');"
                        "print('（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）');"
                        "print('');"
                        "print('**まとめ**');"
                        "print('| 順位 | タイトル | 卦・爻 | 断辞/要点 |');"
                        "print('|---|---|---|---|');"
                        "print('| 1 | 候補A | 24地雷復・初爻 | 元吉 |');"
                        "print('| 2 | 候補B | 42風雷益・4爻 | 中行 |');"
                        "print('');"
                        "print('今回の推薦候補は、1位の候補Aです。')"
                    ),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            resolve_payload = json.loads((out_dir / "resolve.json").read_text(encoding="utf-8"))
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(resolve_payload["mode"], "extract")
            self.assertEqual(resolve_payload["input_kind"], "extract_comparison")
            self.assertEqual(resolve_payload["template"], "EX_COMPARE")
            self.assertEqual(resolve_payload["compare_candidate_count"], 2)
            self.assertEqual(run_payload["final_status"], "success")

    def test_run_records_provider_metadata_when_using_codex_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")
            with patch("iching_sdk.answering.resolve_codex_version", return_value=CODEX_VERSION), patch(
                "iching_sdk.answering.subprocess.run"
            ) as run_mock:
                run_mock.side_effect = [
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="OK\n",
                        stderr="",
                    ),
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout="provider answer\n（参照：honda_wataru_eki_jobun.md|序文）\n",
                        stderr="",
                    ),
                ]
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(
                        path=CODEX_PATH,
                        model="gpt-5",
                        sandbox="workspace-write",
                        approval_policy="never",
                    ),
                )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                run_mock.call_args.args[0],
                [
                    CODEX_PATH,
                    "exec",
                    "--model",
                    "gpt-5",
                    "--sandbox",
                    "workspace-write",
                ],
            )
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["provider"], "codex")
            self.assertEqual(
                run_payload["provider_options"],
                {
                    "model": "gpt-5",
                    "sandbox": "workspace-write",
                },
            )
            self.assertEqual(run_payload["resolved_codex_path"], CODEX_PATH)
            self.assertEqual(run_payload["resolved_codex_version"], CODEX_VERSION)
            self.assertTrue(run_payload["preflight_ran"])
            self.assertEqual(run_payload["preflight_exit_code"], 0)
            self.assertEqual(run_payload["preflight_stderr"], "")
            self.assertEqual(run_payload["runtime_diagnostics"]["resolved_codex_path"], CODEX_PATH)
            self.assertEqual(run_payload["selected_file_count"], 7)
            self.assertEqual(
                run_payload["selected_groups"],
                [
                    {"group": "general_core", "file_count": 7},
                ],
            )

    def test_run_prefers_explicit_command_over_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")
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
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")
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
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")
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
                        "print('**核心・結論**');"
                        "print('抽出回答です。');"
                        "print('');"
                        "print('**本卦（乾為天）**');"
                        "print('本卦の解釈です。');"
                        "print('（参照：honda_wataru/01_乾為天.md|乾為天 - 卦辞）');"
                        "print('');"
                        "print('**変爻**');"
                        "print('変爻の解釈です。');"
                        "print('（参照：honda_wataru/01_乾為天.md|乾為天 - 卦辞）')"
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
                input="[MODE:GENERAL]\nstdin経由の質問です。\n",
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
            input_path.write_text("[MODE:GENERAL]\n参照のない回答を試す。\n", encoding="utf-8")

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
            input_path.write_text("[MODE:GENERAL]\n失敗させる質問です。\n", encoding="utf-8")

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
            self.assertFalse(run_payload["preflight_ran"])
            self.assertIsNone(run_payload["preflight_exit_code"])
            self.assertIsNone(run_payload["validation"])
            self.assertFalse((out_dir / "answer.md").exists())

    def test_run_records_codex_missing_failure_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:GENERAL]\nprovider failure を試す。\n", encoding="utf-8")

            with patch(
                "iching_sdk.answering.subprocess.run",
                side_effect=FileNotFoundError(2, "No such file or directory", CODEX_PATH),
            ):
                result = run_workflow(
                    str(input_path),
                    None,
                    str(out_dir),
                    None,
                    None,
                    "codex",
                    CodexProviderOptions(path=CODEX_PATH),
                )

            self.assertEqual(result.exit_code, 2)
            self.assertIn("codex executable not found", result.stderr_text)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_type"], "provider_missing")
            self.assertEqual(run_payload["error_summary"], "preflight failed: codex executable not found")
            self.assertEqual(run_payload["error"], "preflight failed: codex executable not found")
            self.assertEqual(run_payload["error_source"], "provider")
            self.assertIsNone(run_payload["error_stderr"])
            self.assertTrue(run_payload["preflight_ran"])
            self.assertIsNone(run_payload["preflight_exit_code"])
            self.assertEqual(run_payload["resolved_codex_path"], CODEX_PATH)
            self.assertEqual(run_payload["runtime_diagnostics"]["resolved_codex_path"], CODEX_PATH)

    def test_run_records_codex_auth_failure_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:GENERAL]\nprovider auth failure を試す。\n", encoding="utf-8")

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
                    CodexProviderOptions(path=CODEX_PATH, model="gpt-5"),
                )

            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.stderr_text,
                f"preflight failed: codex authentication required\nartifacts: {out_dir}\n",
            )
            self.assertEqual(
                run_mock.call_args.args[0],
                [CODEX_PATH, "exec", "--model", "gpt-5"],
            )
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "runtime_error")
            self.assertEqual(run_payload["error_type"], "provider_auth")
            self.assertEqual(run_payload["error_summary"], "preflight failed: codex authentication required")
            self.assertEqual(run_payload["error"], "preflight failed: codex authentication required")
            self.assertEqual(run_payload["error_source"], "provider")
            self.assertEqual(
                run_payload["error_stderr"],
                "Not authenticated. Please run codex login.\n",
            )
            self.assertTrue(run_payload["preflight_ran"])
            self.assertEqual(run_payload["preflight_exit_code"], 1)
            self.assertEqual(
                run_payload["preflight_stderr"],
                "Not authenticated. Please run codex login.\n",
            )
            self.assertEqual(run_payload["resolved_codex_path"], CODEX_PATH)
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
            input_path.write_text("[MODE:GENERAL]\n設定失敗を試す。\n", encoding="utf-8")

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
                "honda_wataru/01_乾為天.md",
                "honda_wataru/02_坤為地.md",
                "honda_wataru/03_水雷屯.md",
            ],
        )
        self.assertEqual(payload["files"][-1], "takashima_zouho/64_火水未済.md")

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
                        "（参照：honda_wataru/01_乾為天.md|乾為天 - 卦辞）",
                        "（参照：takashima_zouho/01_乾為天.md|乾為天）",
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
                    {"file": "honda_wataru/01_乾為天.md", "cited_lines": [2]},
                    {"file": "takashima_zouho/01_乾為天.md", "cited_lines": [3]},
                ],
            )

    def test_validate_honda_profile_accepts_logical_citations_against_split_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_honda_split"
            write_split_fixture(split_root, "honda_wataru")
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text(
                "\n".join(
                    [
                        "本文です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 卦辞）",
                    ]
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--profile",
                    "honda",
                    "--mode",
                    "extract",
                    "--sources-root",
                    str(split_root),
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
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(report["profile"], "honda")
            self.assertEqual(report["evidence_status"], "sufficient")
            self.assertEqual(
                evidence["matched_evidence"],
                [{"file": "honda_wataru/42_風雷益.md", "cited_lines": [2]}],
            )

    def test_validate_honda_profile_rejects_split_section_path_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_honda_split"
            write_split_fixture(split_root, "honda_wataru")
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text(
                "\n".join(
                    [
                        "本文です。",
                        "（参照：42_風雷益/kaji.md|風雷益 - 卦辞）",
                    ]
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--profile",
                    "honda",
                    "--mode",
                    "extract",
                    "--sources-root",
                    str(split_root),
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

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            finding_codes = [finding["code"] for finding in report["findings"]]
            self.assertIn("reference_not_indexed", finding_codes)

    def test_validate_takashima_profile_accepts_logical_citations_against_split_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_takashima_split"
            write_split_fixture(split_root, "takashima_zouho")
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text(
                "\n".join(
                    [
                        "本文です。",
                        "（参照：takashima_zouho/42_風雷益.md|風雷益 - 卦辞）",
                    ]
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--profile",
                    "takashima",
                    "--mode",
                    "extract",
                    "--sources-root",
                    str(split_root),
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
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(report["profile"], "takashima")
            self.assertEqual(report["evidence_status"], "sufficient")
            self.assertEqual(
                evidence["matched_evidence"],
                [{"file": "takashima_zouho/42_風雷益.md", "cited_lines": [2]}],
            )

    def test_validate_takashima_profile_rejects_split_section_path_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_takashima_split"
            write_split_fixture(split_root, "takashima_zouho")
            input_path = Path(tmpdir) / "answer.md"
            input_path.write_text(
                "\n".join(
                    [
                        "本文です。",
                        "（参照：42_風雷益/kaji.md|風雷益 - 卦辞）",
                    ]
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmpdir) / "out"

            result = subprocess.run(
                [
                    *CLI,
                    "validate",
                    "--profile",
                    "takashima",
                    "--mode",
                    "extract",
                    "--sources-root",
                    str(split_root),
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

            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            finding_codes = [finding["code"] for finding in report["findings"]]
            self.assertIn("reference_not_indexed", finding_codes)

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

    def test_run_allows_general_freeform_text_with_comparison_words(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:GENERAL]",
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

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("総評だけです。", result.stdout)
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "success")
            self.assertEqual(run_payload["input_kind"], "general_question")

    def test_resolve_rejects_missing_mode_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "missing-mode.md"
            input_path.write_text("易の考え方について教えてください。\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "MODE marker must be the first non-empty line. Use [MODE:EXTRACT], [MODE:GENERAL].",
                result.stderr,
            )

    def test_resolve_rejects_extract_without_template_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract-missing-template.md"
            input_path.write_text("[MODE:EXTRACT]\n本卦：42風雷益\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT].",
                result.stderr,
            )

    def test_build_prompt_rejects_unknown_mode_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "unknown-mode.md"
            input_path.write_text("[MODE:LEGACY]\n質問です。\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "build-prompt", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "Unknown MODE marker. Allowed values: [MODE:EXTRACT], [MODE:GENERAL].",
                result.stderr,
            )

    def test_run_rejects_unknown_extract_template_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "unknown-template.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_LEGACY]\n本卦：42風雷益\n",
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
                    "print('unused')",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "Unknown TEMPLATE marker for EXTRACT. Allowed values: [TEMPLATE:EX_SIMPLE], [TEMPLATE:EX_5], [TEMPLATE:EX_COMPARE].",
                result.stderr,
            )

    def test_resolve_rejects_compare_input_with_fewer_than_two_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "compare-one-candidate.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_COMPARE]",
                        "",
                        "### 3. 占い結果入力",
                        "### 候補A",
                        "- 本卦：42風雷益",
                        "- 変爻：4爻",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "EX_COMPARE requires at least two candidates in the result input block.",
                result.stderr,
            )

    def test_resolve_rejects_compare_input_when_memo_heading_sees_next_candidate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "compare-memo-heading.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_COMPARE]",
                        "",
                        "### 3. 占い結果入力",
                        "### 候補A",
                        "- 本卦：42風雷益",
                        "- 変爻：4爻",
                        "",
                        "### メモ",
                        "ここから下は候補ではない補足です。",
                        "本卦：24地雷復",
                        "変爻：初爻",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "EX_COMPARE requires at least two candidates in the result input block.",
                result.stderr,
            )

    def test_resolve_rejects_compare_input_when_memo_colon_heading_sees_candidate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "compare-memo-colon-heading.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_COMPARE]",
                        "",
                        "### 3. 占い結果入力",
                        "候補A：",
                        "本卦：42風雷益",
                        "変爻：4爻",
                        "",
                        "補足メモ：",
                        "ここから下は候補ではない補足です。",
                        "本卦：24地雷復",
                        "変爻：初爻",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "EX_COMPARE requires at least two candidates in the result input block.",
                result.stderr,
            )

    def test_resolve_rejects_mode_marker_after_body_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "late-mode.md"
            input_path.write_text("前置きです。\n[MODE:GENERAL]\n質問本文\n", encoding="utf-8")

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "MODE marker must appear only at the top of the input before the body starts.",
                result.stderr,
            )

    def test_resolve_rejects_extract_template_after_body_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "late-template.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n本文です。\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "TEMPLATE marker must appear only in the EXTRACT header block before the body starts.",
                result.stderr,
            )

    def test_build_prompt_general_allows_body_line_that_quotes_mode_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "quoted-marker.md"
            input_path.write_text(
                "[MODE:GENERAL]\n仕様説明として [MODE:EXTRACT] の意味も書いてください。\n",
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
            self.assertIn("[MODE:EXTRACT] の意味も書いてください。", result.stdout)

    def test_build_prompt_general_ignores_standalone_mode_marker_inside_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "body-marker-line.md"
            input_path.write_text(
                "[MODE:GENERAL]\nこのあとに marker 文字列を引用します。\n[MODE:EXTRACT]\n引用終わり。\n",
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
            self.assertIn("[MODE:EXTRACT]\n引用終わり。", result.stdout)

    def test_resolve_rejects_multiple_extract_template_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "multiple-templates.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n[TEMPLATE:EX_COMPARE]\n本卦：42風雷益\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "Multiple TEMPLATE markers found for EXTRACT. Use exactly one of: [TEMPLATE:EX_SIMPLE], [TEMPLATE:EX_5], [TEMPLATE:EX_COMPARE].",
                result.stderr,
            )

    def test_build_prompt_extract_ignores_template_marker_inside_body_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "quoted-template.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n質問文で [TEMPLATE:EX_COMPARE] という表記にも触れたい。\n本卦：42風雷益\n",
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
            self.assertIn("[TEMPLATE:EX_COMPARE] という表記", result.stdout)

    def test_resolve_rejects_blank_line_before_extract_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "blank-before-template.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [*CLI, "resolve", "--input", str(input_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "TEMPLATE marker must appear only in the EXTRACT header block before the body starts.",
                result.stderr,
            )

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
            (sources_root / "extract" / "honda_wataru" / "01_乾為天.md").write_text(
                "dummy\n",
                encoding="utf-8",
            )
            (sources_root / "index.md").write_text(
                "### extract\n- honda_wataru/01_乾為天.md\n",
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
            self.assertIn("  - honda_wataru/01_乾為天.md", result.stdout)
            self.assertIn("## Prompt Instructions", result.stdout)
            self.assertIn("## EXTRACT simple structure", result.stdout)
            self.assertIn("**本田解釈**", result.stdout)
            self.assertIn("**高島解釈**", result.stdout)
            self.assertIn("`統合解釈` や一本化した総合解釈は使わない", result.stdout)
            self.assertIn("支えを受けて整う構図", result.stdout)
            self.assertIn("2〜3 文を基本とする", result.stdout)
            self.assertIn("本田解釈は本田系ソースで完結", result.stdout)
            self.assertIn("高島解釈は高島系ソースで完結", result.stdout)
            self.assertNotIn("之卦・互卦・錯卦・綜卦を可能な限り全部束ねて扱う", result.stdout)

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
            self.assertIn("## EXTRACT 5-hexagram structure", result.stdout)
            self.assertIn("変爻なしの回答形式と、変爻ありの回答形式の両方に対応する", result.stdout)
            self.assertIn("全変爻を順番に出す", result.stdout)
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
            self.assertIn("**吉凶順位（1位 = 最吉）**", result.stdout)
            self.assertIn("`1. 候補名` または `1. 候補名（<卦名>・<変爻>）`", result.stdout)
            self.assertIn("`### 1位 候補名（<卦名>・<変爻>）`", result.stdout)
            self.assertIn("卦名・変爻付きの順位行が望ましいが、候補名だけでもよい", result.stdout)
            self.assertIn("順位 | タイトル | 卦・爻 | 断辞/要点", result.stdout)
            self.assertIn("今回の推薦候補は、1位の候補Aです。", result.stdout)
            self.assertIn("Markdown リンクや絶対パス参照は禁止", result.stdout)
            self.assertIn("プレフィックス付きパスや、バッククォート付き citation は禁止", result.stdout)
            self.assertIn("`（参照：honda_wataru/46_地風升.md|地風升 - 5爻）` を正解形として固定", result.stdout)
            self.assertIn("`|` の前後へ空白を入れない", result.stdout)
            self.assertIn("禁止:\n（参照：`sources/extract/honda_wataru/46_地風升.md` | 地風升 - 5爻）", result.stdout)
            self.assertIn("正解:\n今回の推薦候補は、1位のヴァルキリープロファイルです。", result.stdout)
            self.assertNotIn("## GENERAL mode instructions", result.stdout)

    def test_build_prompt_allows_general_freeform_comparison_words(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:GENERAL]",
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
            self.assertIn("次にやるゲームを比較したい。", result.stdout)

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
            [case["template"] for case in cases[:3]],
            ["EX_SIMPLE", "EX_5", "EX_5"],
        )
        self.assertEqual(
            [case.get("has_auxiliary_hexagrams") for case in cases[:3]],
            [None, True, True],
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
        self.assertIn("## EXTRACT simple structure", result.stdout)
        self.assertNotIn("## EXTRACT 5-hexagram structure", result.stdout)
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
        self.assertIn("## EXTRACT 5-hexagram structure", result.stdout)
        self.assertIn("互卦：38火澤睽", result.stdout)
        self.assertIn("**之卦（<卦名>）**", result.stdout)
        self.assertIn("**彖伝**", result.stdout)
        self.assertIn("**大象伝**", result.stdout)
        self.assertIn("変爻がある場合のみ出す", result.stdout)
        self.assertIn("入力に卦名があるものだけ出す", result.stdout)

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
        self.assertIn("## EXTRACT 5-hexagram structure", result.stdout)
        self.assertIn("之卦：54.雷沢帰妹", result.stdout)
        self.assertIn("互卦：43.沢天夬", result.stdout)
        self.assertIn("錯卦：20.風地観", result.stdout)
        self.assertIn("綜卦：33.天山遯", result.stdout)

    def test_build_prompt_includes_ex5_structure_without_auxiliary_hexagram_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5_minimal.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_5]",
                        "",
                        "本卦：5水天需",
                        "変爻：なし",
                        "之卦：",
                        "互卦：",
                        "錯卦：",
                        "綜卦：",
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
            self.assertIn("## EXTRACT 5-hexagram structure", result.stdout)
            self.assertIn("変爻なしの回答形式と、変爻ありの回答形式の両方に対応する", result.stdout)
            self.assertIn("`変爻：なし` の場合でも `**変爻**` 節は必ず出す", result.stdout)
            self.assertIn("今回は変爻がないため、本卦全体の意味を主として読みます。", result.stdout)
            self.assertIn("之卦は変爻がある場合のみ出し", result.stdout)

    def test_build_prompt_includes_multi_change_guidance_for_ex5(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5_multi_change.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_5]",
                        "",
                        "本卦：49沢火革",
                        "変爻：2爻、5爻",
                        "之卦：55雷火豊",
                        "互卦：43沢天夬",
                        "錯卦：50火風鼎",
                        "綜卦：50火風鼎",
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
            self.assertIn("## EXTRACT 5-hexagram structure", result.stdout)
            self.assertIn("変爻が複数ある場合は、全変爻を順番に出す", result.stdout)
            self.assertIn("之卦は変爻がある場合のみ出し、変爻が複数でも 1 つだけ扱う", result.stdout)

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

    def test_validate_accepts_standard_and_complex_canonical_answers_with_context(self) -> None:
        payload = json.loads(EXTRACT_CASES_MANIFEST.read_text(encoding="utf-8"))
        adopted_cases = payload["cases"][:3]

        for case in adopted_cases:
            with self.subTest(case=case["id"]):
                input_path = REPO_ROOT / case["input"]
                answer_path = REPO_ROOT / case["expected_answer"]
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

    def test_validate_extract_template_reports_missing_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "簡単な感想だけです。\n（参照：honda_wataru/01_乾為天.md|乾為天 - 卦辞）\n",
                encoding="utf-8",
            )
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_template",
                        "template": "EX_SIMPLE",
                        "hints": ["requires_strict_citation", "template_marker_present"],
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
            self.assertIn("extract_missing_core_conclusion", codes)
            self.assertIn("extract_missing_primary_hexagram_section", codes)
            self.assertIn("extract_missing_changing_line_section", codes)

    def test_validate_extract_ex5_requires_auxiliary_section_when_input_has_auxiliary_hexagrams(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "\n".join(
                    [
                        "**核心・結論**",
                        "全体方針です。",
                        "",
                        "**本卦（水天需）**",
                        "本卦の解釈です。",
                        "（参照：honda_wataru/05_水天需.md|水天需 - 卦辞）",
                        "",
                        "**変爻**",
                        "今回は変爻がないため、本卦全体の意味を主として読みます。",
                        "（参照：honda_wataru/05_水天需.md|水天需 - 卦辞）",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_template",
                        "template": "EX_5",
                        "hints": [
                            "requires_strict_citation",
                            "template_marker_present",
                            "auxiliary_hexagrams_present",
                        ],
                        "has_auxiliary_hexagrams": True,
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
            self.assertIn("extract_missing_auxiliary_hexagram_section", codes)

    def test_validate_extract_ex5_allows_no_auxiliary_section_without_auxiliary_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "\n".join(
                    [
                        "**核心・結論**",
                        "待って整えるのがよいです。",
                        "",
                        "**本卦（水天需）**",
                        "本卦の解釈です。",
                        "（参照：honda_wataru/05_水天需.md|水天需 - 卦辞）",
                        "",
                        "**変爻**",
                        "今回は変爻がないため、本卦全体の意味を主として読みます。",
                        "（参照：honda_wataru/05_水天需.md|水天需 - 卦辞）",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            context_path.write_text(
                json.dumps(
                    {
                        "mode": "extract",
                        "input_kind": "extract_template",
                        "template": "EX_5",
                        "hints": ["requires_strict_citation", "template_marker_present"],
                        "has_auxiliary_hexagrams": False,
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
            self.assertNotIn("extract_missing_auxiliary_hexagram_section", codes)

    def test_run_writes_select_artifact_and_prompt_includes_selected_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "general.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text("[MODE:GENERAL]\n易の考え方を教えてください。\n", encoding="utf-8")

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

    def test_build_prompt_extract_includes_exact_citation_filenames(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n変爻：5爻\n",
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
            self.assertIn("## Citation Filenames", result.stdout)
            self.assertIn("`honda_wataru/42_風雷益.md`", result.stdout)
            self.assertIn("`takashima_zouho/42_風雷益.md`", result.stdout)
            self.assertIn("basename だけの表記は禁止", result.stdout)

    def test_build_prompt_honda_profile_uses_logical_citations_and_selected_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_honda_split"
            write_split_fixture(split_root, "honda_wataru")
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n変爻：5爻\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "build-prompt",
                    "--profile",
                    "honda",
                    "--sources-root",
                    str(split_root),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Citation Filenames", result.stdout)
            self.assertIn("`honda_wataru/42_風雷益.md`", result.stdout)
            self.assertNotIn("`takashima_zouho/42_風雷益.md`", result.stdout)
            self.assertIn("## Selected Section Sources", result.stdout)
            self.assertIn("42_風雷益/tanden.md", result.stdout)
            self.assertIn("42_風雷益/yao_5.md", result.stdout)
            self.assertIn("split section path", result.stdout)
            self.assertIn("**解釈**", result.stdout)
            self.assertNotIn("**高島解釈**", result.stdout)
            self.assertNotIn("本田解釈", result.stdout)
            self.assertNotIn("高島解釈", result.stdout)

    def test_build_prompt_takashima_profile_uses_logical_citations_and_selected_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_takashima_split"
            write_split_fixture(split_root, "takashima_zouho")
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n変爻：5爻\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "build-prompt",
                    "--profile",
                    "takashima",
                    "--sources-root",
                    str(split_root),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Citation Filenames", result.stdout)
            self.assertIn("`takashima_zouho/42_風雷益.md`", result.stdout)
            self.assertNotIn("`honda_wataru/42_風雷益.md`", result.stdout)
            self.assertIn("## Selected Section Sources", result.stdout)
            self.assertIn("42_風雷益/tanden.md", result.stdout)
            self.assertIn("42_風雷益/yao_5.md", result.stdout)
            self.assertIn("**解釈**", result.stdout)
            self.assertNotIn("本田解釈", result.stdout)
            self.assertNotIn("高島解釈", result.stdout)

    def test_run_honda_profile_accepts_profile_flag_and_writes_split_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_honda_split"
            write_split_fixture(split_root, "honda_wataru")
            input_path = Path(tmpdir) / "extract.md"
            out_dir = Path(tmpdir) / "run-artifacts"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n変爻：5爻\n",
                encoding="utf-8",
            )
            runtime_config_text = "\n".join(
                [
                    'default_profile = "legacy"',
                    "",
                    "[profiles.legacy]",
                    'extract_source_kind = "legacy"',
                    'extract_groups = ["extract_honda", "extract_takashima"]',
                    'extract_prompt_fragment = "extract_shared.md"',
                    "",
                    "[profiles.honda]",
                    'extract_source_kind = "split"',
                    'extract_groups = ["extract_honda"]',
                    f'extract_root = "{split_root.as_posix()}"',
                    'extract_prompt_fragment = "extract_shared_split.md"',
                    "",
                    "[profiles.takashima]",
                    'extract_source_kind = "split"',
                    'extract_groups = ["extract_takashima"]',
                    'extract_root = "sources/extract_takashima_split"',
                    'extract_prompt_fragment = "extract_shared_split.md"',
                    "",
                ]
            )

            with self.runtime_config_file(runtime_config_text):
                result = subprocess.run(
                    [
                        *CLI,
                        "run",
                        "--profile",
                        "honda",
                        "--input",
                        str(input_path),
                        "--out-dir",
                        str(out_dir),
                        "--answer-cmd",
                        sys.executable,
                        "-c",
                        (
                            "print('**核心・結論**');"
                            "print('今回は絞って整理する流れです。');"
                            "print();"
                            "print('**本卦（風雷益）**');"
                            "print('本卦の要点です。');"
                            "print('（参照：honda_wataru/42_風雷益.md|風雷益 - 卦辞）');"
                            "print();"
                            "print('**変爻（5爻）**');"
                            "print('変爻の要点です。');"
                            "print('（参照：honda_wataru/42_風雷益.md|風雷益 - 5爻）');"
                            "print();"
                            "print('**解釈**');"
                            "print('Honda source だけでまとめます。');"
                            "print('（参照：honda_wataru/42_風雷益.md|風雷益）')"
                        ),
                    ],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("**解釈**", result.stdout)
            select_payload = json.loads((out_dir / "select.json").read_text(encoding="utf-8"))
            prompt_text = (out_dir / "prompt.txt").read_text(encoding="utf-8")
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(select_payload["profile"], "honda")
            self.assertEqual(run_payload["profile"], "honda")
            self.assertEqual(run_payload["final_status"], "success")
            self.assertEqual(run_payload["selected_section_count"], 4)
            self.assertIn("- Resolved profile: honda", prompt_text)
            self.assertIn("**解釈**", prompt_text)
            self.assertNotIn("高島解釈", prompt_text)
            self.assertEqual(report["evidence_status"], "sufficient")

    def test_build_prompt_extract_requires_formatted_core_conclusion_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_5]\n本卦：5水天需\n変爻：2爻\n互卦：38火澤睽\n",
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
            self.assertIn("必ず `**核心・結論**` または Markdown 見出し", result.stdout)
            self.assertIn("plain text の `核心・結論` だけを単独行で置く形は禁止", result.stdout)

    def test_build_prompt_ex5_requires_multi_line_summary_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5_no_change.md"
            input_path.write_text(
                (
                    "[MODE:EXTRACT]\n[TEMPLATE:EX_5]\n"
                    "本卦：5水天需\n変爻：なし\n之卦：なし\n"
                    "互卦：38火澤睽\n錯卦：35火地晋\n綜卦：6天水訟\n"
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
            self.assertIn("系統ごとに `1 卦 1 行` で列挙する", result.stdout)
            self.assertIn("変爻なしでも、本卦と存在する補助卦の参照を省略しない", result.stdout)
            self.assertIn("解釈全体を 1 件だけの代表参照に縮めない", result.stdout)
            self.assertNotIn("各解釈の末尾参照は 1 回だけ", result.stdout)

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
            input="[MODE:GENERAL]\n一般的な易の質問です。\n",
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
                ["extract_honda", "extract_takashima"],
            )
            self.assertEqual(payload["selected_groups"][0]["files"], ["honda_wataru/42_風雷益.md"])
            self.assertEqual(payload["selected_groups"][1]["files"], ["takashima_zouho/42_風雷益.md"])
            self.assertEqual(payload["selected_file_count"], 2)

    def test_select_extract_template_with_honda_profile_returns_split_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_honda_split"
            write_split_fixture(split_root, "honda_wataru")
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n変爻：5爻\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "select",
                    "--profile",
                    "honda",
                    "--sources-root",
                    str(split_root),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["profile"], "honda")
            self.assertEqual([group["group"] for group in payload["selected_groups"]], ["extract_honda"])
            self.assertEqual(payload["selected_groups"][0]["files"], ["honda_wataru/42_風雷益.md"])
            self.assertEqual(
                payload["selected_sections"],
                [
                    {
                        "hexagram_number": 42,
                        "citation_file": "honda_wataru/42_風雷益.md",
                        "sections": ["kaji", "tanden", "taisho", "yao_5"],
                        "section_files": [
                            "42_風雷益/kaji.md",
                            "42_風雷益/tanden.md",
                            "42_風雷益/taisho.md",
                            "42_風雷益/yao_5.md",
                        ],
                    }
                ],
            )
            self.assertEqual(payload["selected_file_count"], 1)
            self.assertEqual(payload["selected_section_count"], 4)

    def test_select_extract_comparison_returns_extract_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare.md"
            input_path.write_text(
                (
                    "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n"
                    "候補A：\n本卦：42風雷益\n変爻：4爻\n\n"
                    "候補B：\n本卦：24地雷復\n変爻：初爻\n"
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
            self.assertEqual(payload["mode"], "extract")
            self.assertEqual(payload["input_kind"], "extract_comparison")
            self.assertEqual(payload["template"], "EX_COMPARE")
            self.assertEqual(payload["compare_candidate_count"], 2)
            self.assertEqual(
                [group["group"] for group in payload["selected_groups"]],
                ["extract_honda", "extract_takashima"],
            )
            self.assertEqual(
                payload["selected_groups"][0]["files"],
                ["honda_wataru/42_風雷益.md", "honda_wataru/24_地雷復.md"],
            )
            self.assertEqual(
                payload["selected_groups"][1]["files"],
                ["takashima_zouho/42_風雷益.md", "takashima_zouho/24_地雷復.md"],
            )
            self.assertEqual(payload["selected_file_count"], 4)

    def test_select_extract_compare_with_honda_profile_omits_tanden(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_honda_split"
            write_split_fixture(split_root, "honda_wataru")
            input_path = Path(tmpdir) / "extract_compare.md"
            input_path.write_text(
                (
                    "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n"
                    "候補A：\n本卦：42風雷益\n変爻：4爻\n\n"
                    "候補B：\n本卦：24地雷復\n変爻：初爻\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "select",
                    "--profile",
                    "honda",
                    "--sources-root",
                    str(split_root),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["selected_file_count"], 2)
            self.assertEqual(
                payload["selected_sections"][0]["sections"],
                ["kaji", "taisho", "yao_4"],
            )
            self.assertEqual(
                payload["selected_sections"][1]["sections"],
                ["kaji", "taisho", "yao_1"],
            )
            self.assertNotIn("tanden", payload["selected_sections"][0]["sections"])
            self.assertNotIn("tanden", payload["selected_sections"][1]["sections"])

    def test_select_extract_template_with_takashima_profile_returns_split_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_takashima_split"
            write_split_fixture(split_root, "takashima_zouho")
            input_path = Path(tmpdir) / "extract.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n本卦：42風雷益\n変爻：5爻\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "select",
                    "--profile",
                    "takashima",
                    "--sources-root",
                    str(split_root),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["profile"], "takashima")
            self.assertEqual([group["group"] for group in payload["selected_groups"]], ["extract_takashima"])
            self.assertEqual(payload["selected_groups"][0]["files"], ["takashima_zouho/42_風雷益.md"])
            self.assertEqual(
                payload["selected_sections"],
                [
                    {
                        "hexagram_number": 42,
                        "citation_file": "takashima_zouho/42_風雷益.md",
                        "sections": ["kaji", "tanden", "taisho", "yao_5"],
                        "section_files": [
                            "42_風雷益/kaji.md",
                            "42_風雷益/tanden.md",
                            "42_風雷益/taisho.md",
                            "42_風雷益/yao_5.md",
                        ],
                    }
                ],
            )
            self.assertEqual(payload["selected_file_count"], 1)
            self.assertEqual(payload["selected_section_count"], 4)

    def test_select_extract_compare_with_takashima_profile_omits_tanden(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            split_root = Path(tmpdir) / "extract_takashima_split"
            write_split_fixture(split_root, "takashima_zouho")
            input_path = Path(tmpdir) / "extract_compare.md"
            input_path.write_text(
                (
                    "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n"
                    "候補A：\n本卦：42風雷益\n変爻：4爻\n\n"
                    "候補B：\n本卦：24地雷復\n変爻：初爻\n"
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    *CLI,
                    "select",
                    "--profile",
                    "takashima",
                    "--sources-root",
                    str(split_root),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["selected_file_count"], 2)
            self.assertEqual(
                payload["selected_sections"][0]["sections"],
                ["kaji", "taisho", "yao_4"],
            )
            self.assertEqual(
                payload["selected_sections"][1]["sections"],
                ["kaji", "taisho", "yao_1"],
            )
            self.assertNotIn("tanden", payload["selected_sections"][0]["sections"])
            self.assertNotIn("tanden", payload["selected_sections"][1]["sections"])

    def test_select_general_allows_freeform_comparison_words(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:GENERAL]",
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
            self.assertEqual(payload["input_kind"], "general_question")
            self.assertEqual(payload["selected_groups"][0]["group"], "general_core")

    def test_select_general_question_skips_extract_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "question.md"
            input_path.write_text("[MODE:GENERAL]\n易の考え方について教えてください。\n", encoding="utf-8")

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
            self.assertEqual(payload["selected_file_count"], 7)

    def test_select_general_override_allows_freeform_comparison_words(self) -> None:
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
            self.assertEqual(payload["input_kind"], "general_question")

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
                ["extract_honda", "extract_takashima"],
            )
            self.assertIn("requires_strict_citation", payload["hints"])
            self.assertIn("template_marker_present", payload["hints"])

    def test_resolve_general_allows_freeform_comparison_words(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "comparison.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:GENERAL]",
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
            self.assertEqual(payload["input_kind"], "general_question")

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
                        "",
                        "候補B：",
                        "本卦：24地雷復",
                        "変爻：初爻",
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
            self.assertEqual(payload["template"], "EX_COMPARE")
            self.assertEqual(payload["compare_candidate_count"], 2)
            self.assertIn("comparison_requested", payload["hints"])
            self.assertIn("ranking_requested", payload["hints"])

    def test_resolve_extract_comparison_accepts_verbose_candidate_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_compare_verbose.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_COMPARE]",
                        "",
                        "### 1. 占いに至った背景・状況",
                        "候補を比較したいです。",
                        "",
                        "### 3. 占い結果入力",
                        "### 候補A",
                        "最初の候補についての補足です。",
                        "",
                        "判断メモを挟みます。",
                        "",
                        "- 本卦：42風雷益",
                        "",
                        "別の補足を入れます。",
                        "- 変爻：4爻",
                        "",
                        "候補B：",
                        "ここでも補足を先に書きます。",
                        "",
                        "本卦：24地雷復",
                        "",
                        "さらに空行を入れます。",
                        "",
                        "変爻：初爻",
                    ]
                )
                + "\n",
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
            self.assertEqual(payload["input_kind"], "extract_comparison")
            self.assertEqual(payload["compare_candidate_count"], 2)

    def test_resolve_ex5_detects_auxiliary_hexagram_presence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_5]",
                        "本卦：5水天需",
                        "変爻：なし",
                        "之卦：なし",
                        "互卦：38火澤睽",
                        "錯卦：35火地晋",
                        "綜卦：6天水訟",
                    ]
                )
                + "\n",
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
            self.assertEqual(payload["template"], "EX_5")
            self.assertTrue(payload["has_auxiliary_hexagrams"])
            self.assertIn("auxiliary_hexagrams_present", payload["hints"])
            self.assertEqual(payload["hexagram_numbers"], [5, 38, 35, 6])

    def test_select_extract_ex5_returns_primary_and_auxiliary_hexagrams(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "extract_ex5.md"
            input_path.write_text(
                "\n".join(
                    [
                        "[MODE:EXTRACT]",
                        "[TEMPLATE:EX_5]",
                        "本卦：5水天需",
                        "変爻：なし",
                        "之卦：なし",
                        "互卦：38火澤睽",
                        "錯卦：35火地晋",
                        "綜卦：6天水訟",
                    ]
                )
                + "\n",
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
            self.assertEqual(
                payload["selected_groups"][0]["files"],
                [
                    "honda_wataru/05_水天需.md",
                    "honda_wataru/38_火澤睽.md",
                    "honda_wataru/35_火地晋.md",
                    "honda_wataru/06_天水訟.md",
                ],
            )
            self.assertEqual(
                payload["selected_groups"][1]["files"],
                [
                    "takashima_zouho/05_水天需.md",
                    "takashima_zouho/38_火沢睽.md",
                    "takashima_zouho/35_火地晋.md",
                    "takashima_zouho/06_天水訟.md",
                ],
            )
            self.assertEqual(payload["selected_file_count"], 8)

    def test_resolve_general_question_detects_plain_question(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "question.md"
            input_path.write_text("[MODE:GENERAL]\n易の考え方について教えてください。\n", encoding="utf-8")

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

    def test_resolve_general_override_allows_freeform_comparison_words(self) -> None:
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
            self.assertEqual(payload["input_kind"], "general_question")

    def test_validate_extract_compare_reports_missing_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "総評だけです。\n（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）\n",
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
            self.assertIn("compare_missing_ranked_list", codes)
            self.assertIn("compare_missing_candidate_sections", codes)
            self.assertIn("compare_missing_summary_table", codes)
            self.assertIn("compare_missing_recommendation", codes)
            self.assertIn("ranking_not_explicit", codes)

    def test_validate_extract_compare_accepts_canonical_structure(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertNotIn("compare_missing_ranked_list", codes)
            self.assertNotIn("compare_missing_candidate_sections", codes)
            self.assertNotIn("compare_missing_recommendation", codes)
            self.assertNotIn("compare_recommendation_mismatch", codes)

    def test_validate_extract_compare_rejects_ranking_list_without_detail_sections(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "候補Aは最有力です。",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "候補Bは次点です。",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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

    def test_validate_extract_compare_requires_recommendation_line(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
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
            self.assertIn("compare_missing_recommendation", codes)

    def test_validate_extract_compare_requires_recommendation_to_match_rank_1(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Bです。",
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
            self.assertIn("compare_recommendation_mismatch", codes)
            self.assertNotIn("compare_missing_recommendation", codes)

    def test_validate_extract_compare_ignores_numbered_list_in_core_conclusion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "\n".join(
                    [
                        "**核心・結論**",
                        "最上位候補の整理です。",
                        "1. 候補Bは雰囲気が合う",
                        "2. 候補Aは堅実に強い",
                        "",
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertNotIn("compare_missing_ranked_list", codes)
            self.assertNotIn("compare_recommendation_mismatch", codes)

    def test_validate_extract_compare_requires_ranked_list_inside_ranking_section(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "順位の説明だけを書きます。",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "1. 候補Aは立て直しに向く",
                        "2. 候補Bは追い風がある",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertIn("compare_missing_ranked_list", codes)
            self.assertNotIn("compare_recommendation_mismatch", codes)

    def test_validate_extract_compare_uses_rank_1_from_ranking_section_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            context_path = Path(tmpdir) / "context.json"
            out_dir = Path(tmpdir) / "validate-out"
            answer_path.write_text(
                "\n".join(
                    [
                        "**核心・結論**",
                        "優先候補の補足です。",
                        "",
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "1. 候補Bの雰囲気も魅力",
                        "2. 候補Aは安定感がある",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertNotIn("compare_missing_ranked_list", codes)
            self.assertNotIn("compare_recommendation_mismatch", codes)

    def test_validate_extract_compare_rejects_markdown_link_citations(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "参照: [24_地雷復.md](/home/ys/projects/iching-sdk/sources/extract/honda_wataru/24_地雷復.md)",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "参照: [42_風雷益.md](/home/ys/projects/iching-sdk/sources/extract/honda_wataru/42_風雷益.md)",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertIn("malformed_citation", codes)
            self.assertIn("insufficient_evidence", codes)

    def test_validate_extract_compare_accepts_ranked_list_without_hexagram_info(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A",
                        "2. 候補B",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertNotIn("compare_missing_ranked_list", codes)

    def test_validate_extract_compare_rejects_missing_numbered_ranking_lines(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "候補A",
                        "候補B",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertIn("compare_missing_ranked_list", codes)

    def test_validate_extract_compare_rejects_sources_extract_prefixed_citations(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：`sources/extract/honda_wataru/24_地雷復.md` | 地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：`sources/extract/honda_wataru/42_風雷益.md` | 風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の推薦候補は、1位の候補Aです。",
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
            self.assertIn("invalid_citation_target", codes)
            self.assertIn("insufficient_evidence", codes)

    def test_validate_extract_compare_rejects_alternate_recommendation_phrase(self) -> None:
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
                        "**吉凶順位（1位 = 最吉）**",
                        "1. 候補A（24地雷復・初爻）",
                        "2. 候補B（42風雷益・4爻）",
                        "",
                        "### 1位 候補A（24地雷復・初爻）",
                        "候補Aの解釈です。",
                        "（参照：honda_wataru/24_地雷復.md|地雷復 - 初爻）",
                        "",
                        "### 2位 候補B（42風雷益・4爻）",
                        "候補Bの解釈です。",
                        "（参照：honda_wataru/42_風雷益.md|風雷益 - 4爻）",
                        "",
                        "**まとめ**",
                        "| 順位 | タイトル | 卦・爻 | 断辞/要点 |",
                        "|---|---|---|---|",
                        "| 1 | 候補A | 24地雷復・初爻 | 元吉 |",
                        "| 2 | 候補B | 42風雷益・4爻 | 中行 |",
                        "",
                        "今回の第一推薦は 候補A です。",
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
            self.assertIn("compare_missing_recommendation", codes)

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
