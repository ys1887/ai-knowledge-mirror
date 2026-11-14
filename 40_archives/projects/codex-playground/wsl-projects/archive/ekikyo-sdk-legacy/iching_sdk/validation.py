from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from iching_sdk.config import ModeConfig, ValidationRuntimeError, repo_root
from iching_sdk.indexing import is_relative_to


CITATION_LINE_RE = re.compile(r"^（参照：(?P<body>.+)）$")
POTENTIAL_CITATION_RE = re.compile(r"[（(]\s*参照\s*[:：]|^参照\s*[:：]")
RANKING_OUTPUT_RE = re.compile(r"(^|\s)(?:1\.|第?1位|順位|ランキング|おすすめ|オススメ)")
COMPARE_SECTION_RE = re.compile(
    r"^(?:(?:#+\s*)|\*\*)?(?:🥇\s*)?\d+位\s+.+[（(][^)）]+・[^)）]+[）)](?:\*\*)?\s*$"
)


def has_compare_summary_table(text: str) -> bool:
    table_lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    return len(table_lines) >= 3


def extract_filename(citation_body: str) -> str | None:
    filename = citation_body.split("|", 1)[0].strip()
    if not filename or not filename.endswith(".md"):
        return None
    return filename


def read_input_text(input_arg: str) -> tuple[str, str]:
    if input_arg == "-":
        return ("stdin", sys.stdin.read())
    path = Path(input_arg).expanduser().resolve()
    if not path.is_file():
        raise ValidationRuntimeError(f"input file not found: {path}")
    return (str(path), path.read_text(encoding="utf-8"))


def ensure_out_dir(path_arg: str | None) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return (repo_root() / "out").resolve()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_validation_context(path_arg: str) -> dict[str, Any]:
    path = Path(path_arg).expanduser().resolve()
    if not path.is_file():
        raise ValidationRuntimeError(f"context file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationRuntimeError(f"invalid validation context JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValidationRuntimeError(f"validation context must be a JSON object: {path}")

    mode = payload.get("mode")
    input_kind = payload.get("input_kind")

    if not isinstance(mode, str) or not mode:
        raise ValidationRuntimeError(f"validation context missing mode: {path}")
    if not isinstance(input_kind, str) or not input_kind:
        raise ValidationRuntimeError(f"validation context missing input_kind: {path}")
    if "hints" not in payload:
        raise ValidationRuntimeError(f"validation context missing hints: {path}")
    hints = payload["hints"]
    if not isinstance(hints, list) or not all(isinstance(hint, str) for hint in hints):
        raise ValidationRuntimeError(f"validation context hints must be a list of strings: {path}")

    return {
        "mode": mode,
        "input_kind": input_kind,
        "hints": hints,
    }


def build_error_result(
    mode: str,
    input_value: str,
    sources_root: Path,
    evidence_status: str,
    code: str,
    message: str,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    report = {
        "mode": mode,
        "input": input_value,
        "sources_root": str(sources_root),
        "index_file": str(sources_root.parent / "index.md"),
        "evidence_status": evidence_status,
        "summary": {"citation_lines_seen": 0, "valid_evidence_files": 0, "findings": 1},
        "findings": [{"code": code, "severity": "error", "message": message}],
    }
    evidence = {"mode": mode, "indexed_files": [], "matched_evidence": []}
    return report, evidence, 2


def extract_non_citation_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if CITATION_LINE_RE.fullmatch(line):
            continue
        if POTENTIAL_CITATION_RE.search(line):
            continue
        lines.append((line_number, raw_line))
    return lines


def build_structure_findings(
    config: ModeConfig,
    text: str,
    validation_context: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    non_citation_lines = extract_non_citation_lines(text)
    if not non_citation_lines:
        findings.append(
            {
                "code": "missing_answer_body",
                "severity": "error",
                "message": "Answer body is missing; only citations or empty lines were found.",
            }
        )
        return findings

    if not validation_context:
        return findings

    input_kind = validation_context.get("input_kind")
    hints = set(validation_context.get("hints", []))
    if config.mode == "general" and input_kind == "general_comparison":
        if len(non_citation_lines) < 2:
            findings.append(
                {
                    "code": "comparison_missing_interpretations",
                    "severity": "error",
                    "message": "Comparison answer should include separate interpretation lines for the candidates.",
                }
            )
        if "ranking_requested" in hints and not any(
            RANKING_OUTPUT_RE.search(line) for _, line in non_citation_lines
        ):
            findings.append(
                {
                    "code": "ranking_not_explicit",
                    "severity": "error",
                    "message": "Ranking was requested but the answer does not state a ranking explicitly.",
                }
            )
    if config.mode == "extract" and input_kind == "extract_comparison":
        if "核心・結論" not in text:
            findings.append(
                {
                    "code": "compare_missing_core_conclusion",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a 核心・結論 section.",
                }
            )
        if "吉凶順位" not in text:
            findings.append(
                {
                    "code": "compare_missing_ranking_section",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a 吉凶順位 section.",
                }
            )
        candidate_sections = sum(
            1 for _, raw_line in non_citation_lines if COMPARE_SECTION_RE.match(raw_line.strip())
        )
        if candidate_sections < 2:
            findings.append(
                {
                    "code": "compare_missing_candidate_sections",
                    "severity": "error",
                    "message": "EX_COMPARE answer should include separate ranked sections for at least two candidates.",
                }
            )
        if not has_compare_summary_table(text):
            findings.append(
                {
                    "code": "compare_missing_summary_table",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a summary table.",
                }
            )
        if "ranking_requested" in hints and not any(
            RANKING_OUTPUT_RE.search(line) for _, line in non_citation_lines
        ):
            findings.append(
                {
                    "code": "ranking_not_explicit",
                    "severity": "error",
                    "message": "Ranking was requested but the answer does not state a ranking explicitly.",
                }
            )
    return findings


def validate_citations(
    config: ModeConfig,
    indexed_files: list[str],
    input_label: str,
    text: str,
    validation_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    allowed_files = set(indexed_files)
    findings = build_structure_findings(config, text, validation_context)
    evidence_map: dict[str, list[int]] = {}
    citation_count = 0

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not POTENTIAL_CITATION_RE.search(line):
            continue
        citation_count += 1
        match = CITATION_LINE_RE.fullmatch(line)
        if not match:
            findings.append(
                {
                    "code": "malformed_citation",
                    "severity": "warning",
                    "message": "Malformed citation line.",
                    "line": line_number,
                    "text": raw_line,
                }
            )
            continue

        citation_body = match.group("body").strip()
        filename = extract_filename(citation_body)
        if not filename:
            findings.append(
                {
                    "code": "invalid_citation_target",
                    "severity": "warning",
                    "message": "Citation does not start with a markdown filename.",
                    "line": line_number,
                    "text": raw_line,
                }
            )
            continue

        target = (config.sources_root / filename).resolve()
        if not is_relative_to(target, config.sources_root):
            findings.append(
                {
                    "code": "reference_outside_root",
                    "severity": "error",
                    "message": f"Referenced file escapes mode root: {filename}",
                    "line": line_number,
                    "text": raw_line,
                }
            )
            continue

        if filename not in allowed_files:
            findings.append(
                {
                    "code": "reference_not_indexed",
                    "severity": "error",
                    "message": f"Referenced file is not indexed for mode {config.mode}: {filename}",
                    "line": line_number,
                    "text": raw_line,
                }
            )
            continue

        evidence_map.setdefault(filename, []).append(line_number)

    valid_evidence_count = len(evidence_map)
    evidence_status = "sufficient" if valid_evidence_count > 0 else "insufficient"
    if valid_evidence_count == 0:
        findings.append(
            {
                "code": "insufficient_evidence",
                "severity": "error",
                "message": "No valid citation lines were found.",
            }
        )

    report = {
        "mode": config.mode,
        "input": input_label,
        "sources_root": str(config.sources_root),
        "index_file": str(config.index_file),
        "evidence_status": evidence_status,
        "summary": {
            "citation_lines_seen": citation_count,
            "valid_evidence_files": valid_evidence_count,
            "errors": sum(1 for finding in findings if finding["severity"] == "error"),
            "warnings": sum(1 for finding in findings if finding["severity"] == "warning"),
            "findings": len(findings),
        },
        "findings": findings,
    }
    evidence = {
        "mode": config.mode,
        "indexed_files": indexed_files,
        "matched_evidence": [
            {"file": file_name, "cited_lines": line_numbers}
            for file_name, line_numbers in evidence_map.items()
        ],
    }
    exit_code = 0 if evidence_status == "sufficient" and not findings else 1
    return report, evidence, exit_code
