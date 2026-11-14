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
COMPARE_RANKING_LINE_RE = re.compile(r"^(?P<rank>\d+)\.\s+(?P<candidate>.+)$")
COMPARE_DETAIL_HEADING_RE = re.compile(
    r"^###\s*(?:🥇\s*)?\d+位\s+.+[（(][^)）]+・[^)）]+[）)]\s*$"
)
COMPARE_RECOMMENDATION_RE = re.compile(r"^今回の推薦候補は、1位の(?P<candidate>.+)です。$")
COMPARE_RANKING_CANDIDATE_SUFFIX_RE = re.compile(r"^(?P<name>.+?)(?:\s*[（(][^)）]+[）)])?$")
SECTION_HEADING_RE = re.compile(r"^(?:(?:#+\s*)|\*\*)(?P<label>[^（(＊*#\n]+)")


def normalize_heading_label(label: str) -> str:
    return label.strip().strip("*").strip()


def has_named_section(text: str, labels: set[str]) -> bool:
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        match = SECTION_HEADING_RE.match(stripped)
        if not match:
            continue
        label = normalize_heading_label(match.group("label"))
        if label in labels:
            return True
    return False


def has_compare_summary_table(text: str) -> bool:
    table_lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    return len(table_lines) >= 3


def count_compare_ranking_lines(lines: list[tuple[int, str]]) -> int:
    return sum(1 for _, raw_line in lines if COMPARE_RANKING_LINE_RE.match(raw_line.strip()))


def count_compare_detail_headings(lines: list[tuple[int, str]]) -> int:
    return sum(1 for _, raw_line in lines if COMPARE_DETAIL_HEADING_RE.match(raw_line.strip()))


def has_compare_recommendation(text: str) -> bool:
    return any(COMPARE_RECOMMENDATION_RE.match(raw_line.strip()) for raw_line in text.splitlines())


def extract_compare_ranking_section_lines(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    in_section = False
    ranking_lines: list[tuple[int, str]] = []
    for line_number, raw_line in lines:
        stripped = raw_line.strip()
        match = SECTION_HEADING_RE.match(stripped) if stripped else None
        if match:
            label = normalize_heading_label(match.group("label"))
            if not in_section:
                if label == "吉凶順位":
                    in_section = True
                continue
            break
        if in_section:
            ranking_lines.append((line_number, raw_line))
    return ranking_lines


def extract_compare_rank_1_candidate(lines: list[tuple[int, str]]) -> str | None:
    for _, raw_line in lines:
        match = COMPARE_RANKING_LINE_RE.match(raw_line.strip())
        if not match or match.group("rank") != "1":
            continue
        candidate = match.group("candidate").strip()
        suffix_match = COMPARE_RANKING_CANDIDATE_SUFFIX_RE.match(candidate)
        if suffix_match:
            candidate = suffix_match.group("name").strip()
        return candidate or None
    return None


def extract_compare_recommendation_candidate(text: str) -> str | None:
    for raw_line in text.splitlines():
        match = COMPARE_RECOMMENDATION_RE.match(raw_line.strip())
        if match:
            candidate = match.group("candidate").strip()
            return candidate or None
    return None


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

    result = {
        "mode": mode,
        "input_kind": input_kind,
        "hints": hints,
    }
    template_name = payload.get("template")
    if template_name is not None:
        if not isinstance(template_name, str) or not template_name:
            raise ValidationRuntimeError(f"validation context template must be a string: {path}")
        result["template"] = template_name
    has_auxiliary_hexagrams = payload.get("has_auxiliary_hexagrams")
    if has_auxiliary_hexagrams is not None:
        if not isinstance(has_auxiliary_hexagrams, bool):
            raise ValidationRuntimeError(
                f"validation context has_auxiliary_hexagrams must be a boolean: {path}"
            )
        result["has_auxiliary_hexagrams"] = has_auxiliary_hexagrams
    return result


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
        "index_file": str(sources_root / "index.json"),
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
    template_name = validation_context.get("template")
    hints = set(validation_context.get("hints", []))
    if config.mode == "extract" and input_kind == "extract_template":
        if not has_named_section(text, {"核心・結論"}):
            findings.append(
                {
                    "code": "extract_missing_core_conclusion",
                    "severity": "error",
                    "message": "EXTRACT answer must include a 核心・結論 section.",
                }
            )
        if not has_named_section(text, {"本卦"}):
            findings.append(
                {
                    "code": "extract_missing_primary_hexagram_section",
                    "severity": "error",
                    "message": "EXTRACT answer must include a 本卦 section.",
                }
            )
        if not has_named_section(text, {"変爻"}):
            findings.append(
                {
                    "code": "extract_missing_changing_line_section",
                    "severity": "error",
                    "message": "EXTRACT answer must include a 変爻 section.",
                }
            )
        if template_name == "EX_5" and "auxiliary_hexagrams_present" in hints:
            if not has_named_section(text, {"補助卦", "之卦", "互卦", "錯卦", "綜卦"}):
                findings.append(
                    {
                        "code": "extract_missing_auxiliary_hexagram_section",
                        "severity": "error",
                        "message": "EX_5 answer must include a 補助卦 section or one of 之卦/互卦/錯卦/綜卦 when auxiliary hexagrams are provided.",
                    }
                )
    if config.mode == "extract" and input_kind == "extract_comparison":
        if not has_named_section(text, {"核心・結論"}):
            findings.append(
                {
                    "code": "compare_missing_core_conclusion",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a 核心・結論 section.",
                }
            )
        if not has_named_section(text, {"吉凶順位"}):
            findings.append(
                {
                    "code": "compare_missing_ranking_section",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a 吉凶順位 section.",
                }
            )
        ranking_section_lines = extract_compare_ranking_section_lines(non_citation_lines)
        ranking_lines = count_compare_ranking_lines(ranking_section_lines)
        if ranking_lines < 2:
            findings.append(
                {
                    "code": "compare_missing_ranked_list",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a numbered ranking list with candidate names.",
                }
            )
        candidate_sections = count_compare_detail_headings(non_citation_lines)
        if candidate_sections < 2:
            findings.append(
                {
                    "code": "compare_missing_candidate_sections",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include separate ranked Markdown heading sections for candidates.",
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
        recommendation_candidate = extract_compare_recommendation_candidate(text)
        if recommendation_candidate is None:
            findings.append(
                {
                    "code": "compare_missing_recommendation",
                    "severity": "error",
                    "message": "EX_COMPARE answer must include a final recommendation sentence that matches rank 1.",
                }
            )
        else:
            rank_1_candidate = extract_compare_rank_1_candidate(ranking_section_lines)
            if rank_1_candidate is not None and recommendation_candidate != rank_1_candidate:
                findings.append(
                    {
                        "code": "compare_recommendation_mismatch",
                        "severity": "error",
                        "message": "EX_COMPARE final recommendation must match the rank 1 candidate.",
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


def build_takashima_raw_findings(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not has_named_section(text, {"核心・結論"}):
        findings.append(
            {
                "code": "extract_missing_core_conclusion",
                "severity": "error",
                "message": "Takashima EXTRACT answer must include a 核心・結論 section.",
            }
        )
    if not has_named_section(text, {"本卦"}):
        findings.append(
            {
                "code": "extract_missing_primary_hexagram_section",
                "severity": "error",
                "message": "Takashima EXTRACT answer must include a 本卦 section.",
            }
        )
    if not has_named_section(text, {"変爻"}):
        findings.append(
            {
                "code": "extract_missing_changing_line_section",
                "severity": "error",
                "message": "Takashima EXTRACT answer must include a 変爻 section.",
            }
        )
    if not has_named_section(text, {"総合解釈"}):
        findings.append(
            {
                "code": "extract_missing_summary_section",
                "severity": "error",
                "message": "Takashima EXTRACT answer must include a 総合解釈 section.",
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
    is_extract_compare = (
        config.mode == "extract"
        and validation_context is not None
        and validation_context.get("input_kind") == "extract_comparison"
    )
    raw_takashima_contract = (
        config.mode == "extract"
        and (
            validation_context is None
            or (
                validation_context.get("input_kind") == "extract_template"
                and validation_context.get("template") in {"EX_SIMPLE", "EX_5"}
            )
        )
    )

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

        if filename not in allowed_files and not is_extract_compare:
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
    has_error_findings = any(finding["severity"] == "error" for finding in findings)
    if raw_takashima_contract and valid_evidence_count == 0:
        findings.extend(build_takashima_raw_findings(text))
        has_error_findings = any(finding["severity"] == "error" for finding in findings)
    evidence_status = "sufficient" if valid_evidence_count > 0 else "insufficient"
    if valid_evidence_count == 0 and raw_takashima_contract and not has_error_findings:
        evidence_status = "sufficient"
    if valid_evidence_count == 0 and evidence_status != "sufficient" and not raw_takashima_contract:
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
