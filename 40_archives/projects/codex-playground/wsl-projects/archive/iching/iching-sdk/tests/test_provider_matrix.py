from __future__ import annotations

import unittest

from iching_sdk.provider_matrix import (
    DEFAULT_THEME,
    build_prompt,
    build_scenarios,
    parse_probe_output,
)


class ProviderMatrixTests(unittest.TestCase):
    def test_build_prompt_includes_honda_profile_when_requested(self) -> None:
        prompt = build_prompt("/home/ys/projects/iching-sdk", use_honda=True, theme=DEFAULT_THEME)

        self.assertIn("本田プロファイルで占ってください", prompt)
        self.assertIn(DEFAULT_THEME, prompt)
        self.assertIn("最終的な占い回答だけ", prompt)

    def test_build_prompt_avoids_honda_when_plain(self) -> None:
        prompt = build_prompt("/home/ys/projects/iching-sdk", use_honda=False, theme=DEFAULT_THEME)

        self.assertNotIn("本田プロファイル", prompt)
        self.assertIn("計画や仕様整理は不要", prompt)

    def test_build_scenarios_returns_two_fixed_cli_cases(self) -> None:
        scenarios = build_scenarios("/home/ys/projects/iching-sdk")

        self.assertEqual([scenario.slug for scenario in scenarios], ["cli-honda", "cli-plain"])

    def test_parse_probe_output_detects_provider_failure_run_path_and_files(self) -> None:
        log_text = """
• Explored
  └ Read README.md, test_cli.py
  └ Search 本田|Honda in README.md
• Ran bash -lc './iching run --input /tmp/question.md --provider codex'
2026-03-13T14:14:09Z ERROR codex_api::endpoint::responses_websocket: failed to connect to websocket
""".strip()

        provider_failure, used_run_path, observed_files = parse_probe_output(log_text)

        self.assertTrue(provider_failure)
        self.assertTrue(used_run_path)
        self.assertEqual(
            observed_files,
            ["README.md", "test_cli.py", "./iching run"],
        )

    def test_parse_probe_output_handles_clean_logs(self) -> None:
        provider_failure, used_run_path, observed_files = parse_probe_output("• Explored\n  └ Read SKILL.md\n")

        self.assertFalse(provider_failure)
        self.assertFalse(used_run_path)
        self.assertEqual(observed_files, ["SKILL.md"])


if __name__ == "__main__":
    unittest.main()
