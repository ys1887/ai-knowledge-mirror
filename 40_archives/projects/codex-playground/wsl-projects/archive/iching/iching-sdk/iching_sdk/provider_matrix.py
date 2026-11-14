from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_THEME = "今後の占い運用はCodexCLI中心に寄せるべきか、それともCodexアプリ中心を維持するべきか"

HONDA_PROMPT_TEMPLATE = (
    "{workspace} を対象に、本田プロファイルで占ってください。"
    'テーマは「{theme}」です。'
    "計画ではなく最終的な占い回答だけを出してください。"
)

PLAIN_PROMPT_TEMPLATE = (
    "{workspace} を対象に、占いの最終回答だけを出してください。"
    'テーマは「{theme}」です。'
    "計画や仕様整理は不要です。"
)

FILE_ACTION_PREFIXES = ("Read ", "Search ", "List ", "Ran ")
RUN_PATH_PATTERN = re.compile(r"(?<![\w/.-])(?:\./)?iching run(?![\w/.-])")
PROVIDER_FAILURE_PATTERNS = (
    "failed to connect to websocket",
    "stream disconnected",
    "codex connection issue",
    "preflight failed",
    "provider failed",
)


@dataclass(frozen=True)
class Scenario:
    slug: str
    label: str
    prompt: str


@dataclass(frozen=True)
class ProbeResult:
    scenario: str
    iteration: int
    success: bool
    returncode: int
    elapsed_seconds: float
    provider_failure_logged: bool
    used_run_path: bool
    observed_files: list[str]
    final_message_path: str
    raw_log_path: str

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


def build_prompt(workspace: str, use_honda: bool, theme: str = DEFAULT_THEME) -> str:
    template = HONDA_PROMPT_TEMPLATE if use_honda else PLAIN_PROMPT_TEMPLATE
    return template.format(workspace=workspace, theme=theme)


def build_scenarios(workspace: str, theme: str = DEFAULT_THEME) -> list[Scenario]:
    return [
        Scenario(
            slug="cli-honda",
            label="CodexCLI / 本田指定あり",
            prompt=build_prompt(workspace, use_honda=True, theme=theme),
        ),
        Scenario(
            slug="cli-plain",
            label="CodexCLI / 本田指定なし",
            prompt=build_prompt(workspace, use_honda=False, theme=theme),
        ),
    ]


def parse_observed_files(log_text: str) -> list[str]:
    observed: list[str] = []
    seen: set[str] = set()
    for raw_line in log_text.splitlines():
        line = raw_line.strip(" •│└")
        if not line.startswith(FILE_ACTION_PREFIXES):
            continue
        if line.startswith("Read "):
            tail = line.removeprefix("Read ")
            candidates = [item.strip() for item in tail.split(",")]
        elif line.startswith("Search ") and " in " in line:
            candidates = [line.rsplit(" in ", 1)[1].strip()]
        elif line.startswith("List "):
            candidates = [line.removeprefix("List ").strip()]
        elif line.startswith("Ran "):
            candidates = []
            if RUN_PATH_PATTERN.search(line):
                candidates.append("./iching run")
        else:
            candidates = []
        for candidate in candidates:
            if not candidate:
                continue
            if candidate not in seen:
                seen.add(candidate)
                observed.append(candidate)
    return observed


def parse_probe_output(log_text: str) -> tuple[bool, bool, list[str]]:
    lowered = log_text.lower()
    provider_failure = any(pattern in lowered for pattern in PROVIDER_FAILURE_PATTERNS)
    used_run_path = bool(RUN_PATH_PATTERN.search(log_text))
    observed_files = parse_observed_files(log_text)
    return provider_failure, used_run_path, observed_files


def run_cli_probe(
    scenario: Scenario,
    iteration: int,
    workspace: Path,
    out_dir: Path,
    codex_command: str = "codex",
    sandbox: str = "workspace-write",
) -> ProbeResult:
    run_dir = out_dir / scenario.slug / f"run-{iteration:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = run_dir / "prompt.txt"
    prompt_path.write_text(scenario.prompt + "\n", encoding="utf-8")
    final_message_path = run_dir / "final.md"
    raw_log_path = run_dir / "raw.log"

    command = [
        codex_command,
        "exec",
        "--json",
        "-C",
        str(workspace),
        "--skip-git-repo-check",
        "--sandbox",
        sandbox,
        "-o",
        str(final_message_path),
        scenario.prompt,
    ]
    started_at = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=workspace,
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed_seconds = time.monotonic() - started_at

    combined_log = completed.stdout
    if completed.stderr:
        if combined_log and not combined_log.endswith("\n"):
            combined_log += "\n"
        combined_log += completed.stderr
    raw_log_path.write_text(combined_log, encoding="utf-8")

    provider_failure, used_run_path, observed_files = parse_probe_output(combined_log)
    success = completed.returncode == 0 and final_message_path.exists() and final_message_path.read_text(
        encoding="utf-8"
    ).strip() != ""

    result = ProbeResult(
        scenario=scenario.slug,
        iteration=iteration,
        success=success,
        returncode=completed.returncode,
        elapsed_seconds=round(elapsed_seconds, 2),
        provider_failure_logged=provider_failure,
        used_run_path=used_run_path,
        observed_files=observed_files,
        final_message_path=str(final_message_path),
        raw_log_path=str(raw_log_path),
    )
    (run_dir / "summary.json").write_text(
        json.dumps(result.to_payload(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def write_cli_markdown_report(
    results: Iterable[ProbeResult],
    scenarios: Iterable[Scenario],
    out_path: Path,
) -> None:
    scenario_map = {scenario.slug: scenario for scenario in scenarios}
    lines = [
        "# Codex Provider Matrix",
        "",
        "| scenario | iteration | success | returncode | provider failure | run path | elapsed(s) | observed files |",
        "|---|---:|---|---:|---|---|---:|---|",
    ]
    for result in results:
        files = ", ".join(result.observed_files[:6]) if result.observed_files else "-"
        label = scenario_map[result.scenario].label
        lines.append(
            f"| {label} | {result.iteration} | "
            f"{'yes' if result.success else 'no'} | {result.returncode} | "
            f"{'yes' if result.provider_failure_logged else 'no'} | "
            f"{'yes' if result.used_run_path else 'no'} | "
            f"{result.elapsed_seconds:.2f} | {files} |"
        )
    lines.extend(
        [
            "",
            "## Paths",
            "",
        ]
    )
    for result in results:
        label = scenario_map[result.scenario].label
        lines.append(
            f"- {label} run {result.iteration}: raw={result.raw_log_path} final={result.final_message_path}"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_app_manual_template(
    scenarios: Iterable[Scenario],
    repetitions: int,
    out_path: Path,
) -> None:
    lines = [
        "# Codex App Provider Matrix",
        "",
        "Codex アプリ側は手動記録する。各 run は必ず新規セッションで実施する。",
        "",
        "## Fixed Prompts",
        "",
    ]
    for scenario in scenarios:
        app_label = scenario.label.replace("CodexCLI", "Codexアプリ")
        lines.append(f"### {app_label}")
        lines.append("")
        lines.append("```text")
        lines.append(scenario.prompt)
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Runs",
            "",
            "| scenario | iteration | final answer | provider failure log | `./iching run` path | major files read | notes |",
            "|---|---:|---|---|---|---|---|",
        ]
    )
    for scenario in scenarios:
        app_label = scenario.label.replace("CodexCLI", "Codexアプリ")
        for iteration in range(1, repetitions + 1):
            lines.append(f"| {app_label} | {iteration} |  |  |  |  |  |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
