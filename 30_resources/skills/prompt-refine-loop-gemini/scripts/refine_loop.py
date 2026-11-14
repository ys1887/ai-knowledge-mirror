#!/usr/bin/env python3
"""Run an automated prompt refinement loop using Gemini Developer API."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.5-pro"
DEFAULT_MAX_ITER = 5
DEFAULT_THRESHOLD = 0.15
DEFAULT_OUTPUT_ROOT = Path("/mnt/e/Documents/Workspace/prompt-loop")
MAX_RETRIES = 3

REWRITE_TEMPLATE = """You are an expert prompt engineer acting in a ChatGPT-style optimization role.

Task:
- Improve the prompt below for clarity, structure, constraints, and output quality.
- Keep the original intent.
- Remove ambiguity and contradiction.
- Return only the improved prompt text, no explanation.

Current prompt:
{current_prompt}
"""

REVIEW_TEMPLATE = """You are a strict Gemini reviewer.

Review this prompt and return practical improvement feedback.
Output format:
- 3 strengths
- 3 weaknesses
- 5 concrete improvement actions
- 2 potential failure modes

Prompt to review:
{draft_prompt}
"""

REVISION_TEMPLATE = """You are an expert prompt engineer.

Revise the draft prompt by applying the reviewer feedback.
Rules:
- Keep user intent unchanged.
- Make constraints explicit.
- Keep wording concise and testable.
- Return only the revised prompt text.

Draft prompt:
{draft_prompt}

Reviewer feedback:
{feedback}
"""

SCORING_TEMPLATE = """Evaluate how much additional improvement is still needed.
Compare previous prompt and revised prompt.

Return ONLY valid JSON:
{{"score": <float 0.0-1.0>, "reason": "<short reason>"}}

Interpretation:
- score near 0.0 = mostly converged, little left to improve
- score near 1.0 = major gaps remain

Previous prompt:
{previous_prompt}

Revised prompt:
{revised_prompt}
"""


@dataclass
class IterationRecord:
    iteration: int
    chatgpt_draft: str
    gemini_feedback: str
    revised_draft: str
    score: float
    stop_reason: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run prompt refinement loop with Gemini API")
    parser.add_argument("--input", help="Path to input markdown/text file")
    parser.add_argument("--input-text", help="Raw input prompt text")
    parser.add_argument("--max-iter", type=int, default=DEFAULT_MAX_ITER)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--temperature", type=float, default=0.2)
    return parser.parse_args()


def get_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set", file=sys.stderr)
        sys.exit(1)
    return api_key


def load_initial_prompt(path_arg: str | None, text_arg: str | None) -> str:
    if path_arg and text_arg:
        print("Error: use either --input or --input-text, not both", file=sys.stderr)
        sys.exit(1)

    if path_arg:
        source = Path(path_arg)
        if not source.exists() or not source.is_file():
            print(f"Error: input file not found: {source}", file=sys.stderr)
            sys.exit(1)
        value = source.read_text(encoding="utf-8").strip()
    elif text_arg:
        value = text_arg.strip()
    else:
        value = sys.stdin.read().strip()

    if not value:
        print("Error: initial prompt is empty", file=sys.stderr)
        sys.exit(1)

    return value


def ensure_run_dir(base_dir: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base_dir / f"run-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def call_gemini(api_key: str, model: str, prompt: str, temperature: float) -> str:
    endpoint = f"{API_BASE_URL}/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
            return extract_text(data)
        except urllib.error.HTTPError as error:
            status = error.code
            detail = ""
            if error.fp:
                detail = error.fp.read().decode("utf-8", errors="replace")
            retryable = status == 429 or 500 <= status <= 599
            if retryable and attempt < MAX_RETRIES:
                sleep_s = 2 ** (attempt - 1)
                print(f"Retryable API error HTTP {status}; retrying in {sleep_s}s", file=sys.stderr)
                time.sleep(sleep_s)
                continue
            print(f"Error: Gemini API request failed (HTTP {status})", file=sys.stderr)
            if detail:
                print(detail, file=sys.stderr)
            raise
        except urllib.error.URLError as error:
            if attempt < MAX_RETRIES:
                sleep_s = 2 ** (attempt - 1)
                print(f"Network error: {error.reason}; retrying in {sleep_s}s", file=sys.stderr)
                time.sleep(sleep_s)
                continue
            raise

    raise RuntimeError("Unexpected retry loop termination")


def extract_text(response: dict[str, Any]) -> str:
    candidates = response.get("candidates", [])
    if not candidates:
        raise ValueError("No candidates in Gemini response")

    parts = candidates[0].get("content", {}).get("parts", [])
    chunks: list[str] = []
    for part in parts:
        text = part.get("text")
        if text:
            chunks.append(text)

    merged = "\n".join(chunks).strip()
    if not merged:
        raise ValueError("No text content in Gemini response")
    return merged


def extract_score(scoring_text: str) -> tuple[float, str]:
    # Try strict JSON first.
    try:
        parsed = json.loads(scoring_text)
        score = float(parsed.get("score"))
        reason = str(parsed.get("reason", ""))
        return clamp_score(score), reason[:240]
    except Exception:
        pass

    # Then try JSON code blocks or embedded JSON objects.
    code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", scoring_text, flags=re.DOTALL)
    if code_block:
        try:
            parsed = json.loads(code_block.group(1))
            score = float(parsed.get("score"))
            reason = str(parsed.get("reason", ""))
            return clamp_score(score), reason[:240]
        except Exception:
            pass

    embedded = re.search(r"\{.*\"score\".*\}", scoring_text, flags=re.DOTALL)
    if embedded:
        try:
            parsed = json.loads(embedded.group(0))
            score = float(parsed.get("score"))
            reason = str(parsed.get("reason", ""))
            return clamp_score(score), reason[:240]
        except Exception:
            pass

    match = re.search(r"([01](?:\.\d+)?)", scoring_text)
    if not match:
        return 0.5, "Fallback score used because JSON parsing failed"
    return clamp_score(float(match.group(1))), "Fallback score parsed from free-text output"


def clamp_score(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def write_jsonl(path: Path, rows: list[IterationRecord]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")


def write_summary(path: Path, records: list[IterationRecord], threshold: float, max_iter: int) -> None:
    lines = [
        "# Prompt Refine Loop Summary",
        "",
        f"- total_iterations: {len(records)}",
        f"- threshold: {threshold}",
        f"- max_iter: {max_iter}",
        "",
        "## Iteration Scores",
    ]

    for row in records:
        reason = row.stop_reason or "continue"
        lines.append(f"- iter {row.iteration}: score={row.score:.3f} ({reason})")

    lines.append("")
    if records:
        final_reason = records[-1].stop_reason or "reached max iterations"
        lines.append(f"Final stop reason: {final_reason}")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    if args.max_iter < 1:
        print("Error: --max-iter must be >= 1", file=sys.stderr)
        sys.exit(1)
    if not (0.0 <= args.threshold <= 1.0):
        print("Error: --threshold must be in [0.0, 1.0]", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    current_prompt = load_initial_prompt(args.input, args.input_text)
    run_dir = ensure_run_dir(Path(args.out_dir))

    records: list[IterationRecord] = []

    print(f"Run directory: {run_dir}")
    print(f"Model: {args.model}")
    print(f"Max iterations: {args.max_iter}")
    print(f"Threshold: {args.threshold}")

    for idx in range(1, args.max_iter + 1):
        print(f"Iteration {idx}/{args.max_iter}...")

        chatgpt_draft = call_gemini(
            api_key,
            args.model,
            REWRITE_TEMPLATE.format(current_prompt=current_prompt),
            args.temperature,
        )
        gemini_feedback = call_gemini(
            api_key,
            args.model,
            REVIEW_TEMPLATE.format(draft_prompt=chatgpt_draft),
            args.temperature,
        )
        revised_draft = call_gemini(
            api_key,
            args.model,
            REVISION_TEMPLATE.format(draft_prompt=chatgpt_draft, feedback=gemini_feedback),
            args.temperature,
        )
        scoring_text = call_gemini(
            api_key,
            args.model,
            SCORING_TEMPLATE.format(previous_prompt=current_prompt, revised_prompt=revised_draft),
            0.0,
        )

        score, score_reason = extract_score(scoring_text)
        stop_reason = None
        if score < args.threshold:
            stop_reason = f"converged(score={score:.3f} < threshold={args.threshold:.3f}): {score_reason}"

        record = IterationRecord(
            iteration=idx,
            chatgpt_draft=chatgpt_draft,
            gemini_feedback=gemini_feedback,
            revised_draft=revised_draft,
            score=score,
            stop_reason=stop_reason,
        )
        records.append(record)
        current_prompt = revised_draft

        if stop_reason:
            print(f"Stopping early: {stop_reason}")
            break

    if records and records[-1].stop_reason is None and len(records) == args.max_iter:
        records[-1].stop_reason = f"max_iter_reached({args.max_iter})"

    final_prompt_path = run_dir / "final_prompt.md"
    summary_path = run_dir / "summary.md"
    jsonl_path = run_dir / "iterations.jsonl"

    final_prompt_path.write_text(current_prompt.rstrip() + "\n", encoding="utf-8")
    write_jsonl(jsonl_path, records)
    write_summary(summary_path, records, args.threshold, args.max_iter)

    print("Done")
    print(f"- {final_prompt_path}")
    print(f"- {jsonl_path}")
    print(f"- {summary_path}")


if __name__ == "__main__":
    main()
