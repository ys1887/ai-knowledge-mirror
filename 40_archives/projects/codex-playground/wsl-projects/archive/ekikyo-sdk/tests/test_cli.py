from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from iching_sdk.running import run_workflow


REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = [sys.executable, str(REPO_ROOT / "iching")]
EXTRACT_SIMPLE_INPUT = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_1.md"
EXTRACT_COMPARE_INPUT = REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_4.md"
EXTRACT_COMPARE_CANONICAL = (
    REPO_ROOT / "tests" / "fixtures" / "extract_cases" / "test_4_answer_canonical.md"
)


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*CLI, *args],
        cwd=REPO_ROOT,
        input=input_text,
        check=False,
        capture_output=True,
        text=True,
    )


class IchingCliTests(unittest.TestCase):
    def test_build_prompt_extract_simple_uses_takashima_contract(self) -> None:
        result = run_cli("build-prompt", "--input", str(EXTRACT_SIMPLE_INPUT))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Extract contract: takashima", result.stdout)
        self.assertIn("## 高島解釈原文", result.stdout)
        self.assertIn("takashima_zouho/42_風雷益.md", result.stdout)

    def test_select_extract_simple_returns_takashima_sources(self) -> None:
        result = run_cli("select", "--input", str(EXTRACT_SIMPLE_INPUT))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "extract")
        self.assertEqual(payload["source_groups"][0], "extract_takashima")
        self.assertEqual(payload["selected_groups"][0]["group"], "extract_takashima")
        self.assertTrue(
            all(path.startswith("takashima_zouho/") for path in payload["selected_files"])
        )

    def test_run_extract_simple_appends_takashima_raw_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "run-artifacts"
            result = run_workflow(
                str(EXTRACT_SIMPLE_INPUT),
                None,
                str(out_dir),
                None,
                [
                    sys.executable,
                    "-c",
                    "\n".join(
                        [
                            "print('## 核心・結論')",
                            "print('Takashima EXTRACT simple.')",
                            "print('')",
                            "print('## 本卦')",
                            "print('42 風雷益')",
                            "print('')",
                            "print('## 変爻')",
                            "print('5爻')",
                            "print('')",
                            "print('## 総合解釈')",
                            "print('Takashima raw contract is appended by the SDK.')",
                        ]
                    ),
                ],
            )

            self.assertEqual(result.exit_code, 0, result.stderr_text)
            answer_text = (out_dir / "answer.md").read_text(encoding="utf-8")
            run_payload = json.loads((out_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_payload["final_status"], "success")
            self.assertIn("## 高島解釈原文", answer_text)
            self.assertIn("### 本卦", answer_text)
            self.assertIn("風雷益", answer_text)

    def test_validate_accepts_takashima_raw_simple_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            answer_path = Path(tmpdir) / "answer.md"
            out_dir = Path(tmpdir) / "validate-artifacts"
            answer_path.write_text(
                "\n".join(
                    [
                        "## 核心・結論",
                        "Takashima simple answer.",
                        "",
                        "## 本卦",
                        "42 風雷益",
                        "",
                        "## 変爻",
                        "5爻",
                        "",
                        "## 総合解釈",
                        "This answer matches the raw Takashima contract.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_cli(
                "validate",
                "--mode",
                "extract",
                "--input",
                str(answer_path),
                "--out-dir",
                str(out_dir),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence_status"], "sufficient")

    def test_build_prompt_compare_uses_takashima_sources(self) -> None:
        result = run_cli("build-prompt", "--input", str(EXTRACT_COMPARE_INPUT))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("takashima_zouho/24_地雷復.md", result.stdout)
        self.assertIn("takashima_zouho/42_風雷益.md", result.stdout)

    def test_compare_canonical_fixture_uses_takashima_references(self) -> None:
        text = EXTRACT_COMPARE_CANONICAL.read_text(encoding="utf-8")
        self.assertIn("takashima_zouho/24_地雷復.md", text)
