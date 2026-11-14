#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from iching_sdk.provider_matrix import (
    DEFAULT_THEME,
    build_scenarios,
    run_cli_probe,
    write_app_manual_template,
    write_cli_markdown_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect a fixed Codex provider comparison matrix for CLI and Codex app runs."
    )
    parser.add_argument(
        "--workspace",
        default="/home/ys/projects/iching-sdk",
        help="Workspace path passed to Codex.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/comparisons/provider-matrix-2026-03-13",
        help="Output directory for prompts, logs, and reports.",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=2,
        help="Number of runs per scenario.",
    )
    parser.add_argument(
        "--theme",
        default=DEFAULT_THEME,
        help="Shared divination theme used across all scenarios.",
    )
    parser.add_argument(
        "--codex-command",
        default="codex",
        help="Codex executable to invoke for CLI scenarios.",
    )
    parser.add_argument(
        "--sandbox",
        default="workspace-write",
        help="Sandbox mode passed to `codex exec`.",
    )
    parser.add_argument(
        "--prepare-app-only",
        action="store_true",
        help="Only generate prompts and the Codex app manual record sheet.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scenarios = build_scenarios(str(workspace), theme=args.theme)
    prompts_dir = out_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for scenario in scenarios:
        (prompts_dir / f"{scenario.slug}.txt").write_text(scenario.prompt + "\n", encoding="utf-8")

    write_app_manual_template(scenarios, args.repetitions, out_dir / "app-manual.md")

    if args.prepare_app_only:
        return 0

    results = []
    for scenario in scenarios:
        for iteration in range(1, args.repetitions + 1):
            results.append(
                run_cli_probe(
                    scenario=scenario,
                    iteration=iteration,
                    workspace=workspace,
                    out_dir=out_dir,
                    codex_command=args.codex_command,
                    sandbox=args.sandbox,
                )
            )

    (out_dir / "cli-results.json").write_text(
        json.dumps([result.to_payload() for result in results], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_cli_markdown_report(results, scenarios, out_dir / "cli-results.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
