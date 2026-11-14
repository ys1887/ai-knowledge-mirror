from __future__ import annotations

import subprocess
import sys
import unittest
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "build_extract_prompt.py"
FIXTURE_MANIFEST = REPO_ROOT / "examples" / "extract" / "manifest.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import resolve_profile  # noqa: E402
from resolving import extract_compare_candidates, parse_mode_marker, parse_template_marker, resolve_input  # noqa: E402
from selecting import select_sources  # noqa: E402


def load_fixture_manifest() -> list[dict[str, object]]:
    payload = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    return payload["cases"]


def normalize_fixture_relpath(relpath: str) -> str:
    if (REPO_ROOT / relpath).exists():
        return relpath
    return relpath.replace("tests/fixtures/extract_cases/", "examples/extract/")


def resolve_fixture_path(relpath: str) -> Path:
    return REPO_ROOT / normalize_fixture_relpath(relpath)


def build_prompt_for_case(input_relpath: str, profile: str = "legacy") -> str:
    normalized = normalize_fixture_relpath(input_relpath)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / normalized), "--profile", profile],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"prompt build failed for {normalized}: {result.stderr}")
    return result.stdout


def extract_canonical_skeleton(text: str) -> set[str]:
    skeleton: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("**") and line.endswith("**"):
            label = line.strip("*")
            if label.startswith("核心・結論"):
                skeleton.add("核心・結論")
            elif label.startswith("本卦"):
                skeleton.add("本卦")
            elif label.startswith("変爻"):
                skeleton.add("変爻")
            elif label.startswith(("之卦", "互卦", "錯卦", "綜卦")):
                skeleton.add(label.split("（", 1)[0])
            elif label in {"本田解釈", "高島解釈", "吉凶順位（1位 = 最吉）", "まとめ"}:
                skeleton.add(label)
        elif re.match(r"^### \d+位 ", line):
            skeleton.add("候補別詳細")
        elif line.startswith("| 順位 |"):
            skeleton.add("まとめ表")
        elif re.match(r"^今回のおすすめは、.+です。$", line):
            skeleton.add("おすすめ")
    return skeleton


def extract_input_auxiliary_labels(text: str) -> set[str]:
    labels: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        for label in ("之卦", "互卦", "錯卦", "綜卦"):
            if stripped.startswith(f"{label}：") and not stripped.endswith("なし"):
                labels.add(label)
    return labels


def count_quote_blocks(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith(">"))


def count_citation_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith("（参照："))


def count_reading_lines(text: str) -> int:
    return sum(
        1
        for line in text.splitlines()
        if line.strip().startswith("> ") and re.search(r"[ぁ-ん]", line)
    )


def extract_interpretation_labels(text: str) -> set[str]:
    labels: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line in {"**本田解釈**", "**高島解釈**"}:
            labels.add(line.strip("*"))
    return labels


def extract_section_block(text: str, heading: str) -> str:
    lines = text.splitlines()
    target = f"**{heading}**"
    top_level_prefixes = ("核心・結論", "本卦", "変爻", "之卦", "互卦", "錯卦", "綜卦", "本田解釈", "高島解釈", "吉凶順位", "まとめ")
    start_index: int | None = None
    for index, raw_line in enumerate(lines):
        if raw_line.strip() == target:
            start_index = index
            break
    if start_index is None:
        return ""

    collected: list[str] = []
    for raw_line in lines[start_index + 1 :]:
        stripped = raw_line.strip()
        if stripped.startswith("**") and stripped.endswith("**"):
            label = stripped.strip("*")
            if label.startswith(top_level_prefixes):
                break
        collected.append(raw_line)
    return "\n".join(collected)


def expected_interpretation_labels_for_profile(canonical_text: str, profile: str) -> set[str]:
    labels = extract_interpretation_labels(canonical_text)
    if profile == "legacy":
        return labels
    if not labels:
        return set()
    profile_label = {"honda": "本田解釈", "takashima": "高島解釈"}[profile]
    return {profile_label}


class ParserTests(unittest.TestCase):
    def test_parse_valid_templates(self) -> None:
        self.assertEqual(parse_mode_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n"), "extract")
        self.assertEqual(parse_template_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n"), "EX_SIMPLE")
        self.assertEqual(parse_template_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_5]\n"), "EX_5")
        self.assertEqual(parse_template_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n"), "EX_COMPARE")

    def test_missing_mode_fails(self) -> None:
        with self.assertRaisesRegex(Exception, "MODE marker must be the first non-empty line"):
            parse_mode_marker("質問だけ\n")

    def test_general_is_explicitly_unimplemented(self) -> None:
        with self.assertRaisesRegex(Exception, "not implemented"):
            resolve_input("[MODE:GENERAL]\n本文\n")

    def test_extract_without_template_fails(self) -> None:
        with self.assertRaisesRegex(Exception, "TEMPLATE marker"):
            parse_template_marker("[MODE:EXTRACT]\n本文\n")

    def test_compare_candidate_parsing(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "test_4.md").read_text(encoding="utf-8")
        candidates = extract_compare_candidates(text)
        self.assertEqual(candidates[0]["label"], "ストリートファイター6")
        self.assertEqual(candidates[0]["hexagram_number"], 42)
        self.assertEqual(candidates[0]["changing_lines"], [4])
        self.assertEqual(candidates[-1]["label"], "ソニック")
        self.assertEqual(candidates[-1]["changing_lines"], [6])


class SelectionTests(unittest.TestCase):
    def test_profile_source_roots_match_new_layout(self) -> None:
        legacy = resolve_profile("legacy")
        self.assertEqual(len(legacy.providers), 2)
        self.assertEqual(
            {provider.interpretation_root for provider in legacy.providers},
            {
                REPO_ROOT / "assets" / "canonical" / "interp" / "honda",
                REPO_ROOT / "assets" / "canonical" / "interp" / "takashima",
            },
        )

    def test_legacy_ex_simple_uses_both_source_families(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "test_1.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("legacy"), resolve_input(text))
        providers = {item["provider"] for item in selection["selected_items"]}
        self.assertEqual(providers, {"honda", "takashima"})
        for item in selection["selected_items"]:
            self.assertIn("kaji", item["section_names"])
            self.assertIn("tanden", item["section_names"])
            self.assertIn("taisho", item["section_names"])
            if item["role"] == "main_hexagram":
                self.assertIn("yao_5", item["section_names"])

    def test_honda_profile_uses_only_honda_sections(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "test_1.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("honda"), resolve_input(text))
        self.assertEqual({item["provider"] for item in selection["selected_items"]}, {"honda"})
        self.assertEqual(selection["final_sections"], ["本田解釈"])
        self.assertEqual(selection["support_items"], [])

    def test_takashima_profile_uses_only_takashima_sections(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "test_1.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("takashima"), resolve_input(text))
        self.assertEqual({item["provider"] for item in selection["selected_items"]}, {"takashima"})
        self.assertEqual(selection["final_sections"], ["高島解釈"])
        self.assertEqual(selection["support_items"], [])

    def test_ex5_auxiliary_hexagrams_exclude_yao_sections(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "test_2.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("legacy"), resolve_input(text))
        auxiliary_items = [item for item in selection["selected_items"] if item["role"] == "auxiliary_hexagram"]
        self.assertTrue(auxiliary_items)
        for item in auxiliary_items:
            self.assertFalse(any(name.startswith("yao_") for name in item["section_names"]))

    def test_legacy_compare_marks_takashima_as_support_only(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "test_4.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("legacy"), resolve_input(text))
        takashima_items = [item for item in selection["selected_items"] if item["provider"] == "takashima"]
        self.assertTrue(takashima_items)
        self.assertTrue(all(item["output_visibility"] == "support_only" for item in takashima_items))
        self.assertEqual(selection["support_items"], [])

    def test_honda_ex_simple_collects_bungen_support_only_for_qian_or_kun(self) -> None:
        text = (REPO_ROOT / "examples" / "extract" / "standard_1.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("honda"), resolve_input(text))
        self.assertEqual(len(selection["support_items"]), 1)
        support_item = selection["support_items"][0]
        self.assertEqual(support_item["hexagram_number"], 1)
        self.assertEqual(support_item["support_section_names"], ["bungen"])
        self.assertNotIn("bungen", selection["selected_items"][0]["section_names"])
        self.assertNotIn("jokaden", selection["selected_items"][0]["section_names"])

    def test_honda_ex_compare_collects_no_support_sections(self) -> None:
        text = (REPO_ROOT / "tests" / "test_4.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("honda"), resolve_input(text))
        self.assertEqual(selection["support_items"], [])
        self.assertEqual(selection["support_section_paths"], [])

    def test_honda_ex5_collects_jokaden_support_for_main_and_auxiliary_hexagrams(self) -> None:
        text = (REPO_ROOT / "tests" / "test_3.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("honda"), resolve_input(text))
        support_items = selection["support_items"]
        self.assertEqual(len(support_items), 5)
        self.assertTrue(all("jokaden" in item["support_section_names"] for item in support_items))
        for item in selection["selected_items"]:
            self.assertNotIn("jokaden", item["section_names"])

    def test_honda_ex5_collects_bungen_support_only_for_involved_qian_or_kun(self) -> None:
        text = """[MODE:EXTRACT]
[TEMPLATE:EX_5]

### 1. 占いに至った背景・状況
流れをまとめて見たい。

### 2. 易経への質問
この構図をどう読むべきか。

### 3. 占い結果入力
本卦：2坤為地
変爻：5爻
之卦：1乾為天
互卦：24地雷復
錯卦：1乾為天
綜卦：2坤為地
"""
        selection = select_sources(resolve_profile("honda"), resolve_input(text))
        support_by_number = {item["hexagram_number"]: item["support_section_names"] for item in selection["support_items"]}
        self.assertEqual(set(support_by_number), {1, 2, 24})
        self.assertEqual(support_by_number[24], ["jokaden"])
        self.assertEqual(support_by_number[1], ["jokaden", "bungen"])
        self.assertEqual(support_by_number[2], ["jokaden", "bungen"])


class PromptBuildTests(unittest.TestCase):
    def test_prompt_stdout_contains_citation_and_section_paths(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_1.md"), "--profile", "legacy"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("## Canonical Source Roots", stdout)
        self.assertIn(str(REPO_ROOT / "assets" / "canonical" / "quotes"), stdout)
        self.assertIn(str(REPO_ROOT / "assets" / "canonical" / "interp" / "honda"), stdout)
        self.assertIn(str(REPO_ROOT / "assets" / "canonical" / "interp" / "takashima"), stdout)
        self.assertIn("## Citation Paths", stdout)
        self.assertIn("`honda_wataru/42_風雷益.md`", stdout)
        self.assertIn("`takashima_zouho/42_風雷益.md`", stdout)
        self.assertIn("## Section Paths (Internal Only)", stdout)
        self.assertIn(str(REPO_ROOT / "assets" / "split" / "honda" / "42_風雷益" / "kaji.md"), stdout)
        self.assertIn("must never appear in the final answer", stdout)

    def test_profile_and_template_fragments_are_composed(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_4.md"), "--profile", "legacy"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("Profile: legacy", stdout)
        self.assertIn("# Profile: legacy", stdout)
        self.assertIn("# EX_COMPARE output skeleton (legacy)", stdout)
        self.assertIn("## Output Quality Bar", stdout)
        self.assertIn("Honda leads the narrated candidate detail", stdout)

    def test_prompt_spells_out_template_section_order(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_2.md"), "--profile", "legacy"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("Order: `**核心・結論**` -> `**本卦（<卦名>）**` -> `**変爻**`", stdout)
        self.assertIn("Within `**本卦（<卦名>）**`, keep the order `序卦伝` -> `卦辞` -> `彖伝` -> `大象伝`", stdout)
        self.assertIn("For each auxiliary hexagram, keep the order `卦辞` -> `彖伝` -> `大象伝`.", stdout)

    def test_ex_simple_prompt_states_main_and_changing_line_roles(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_1.md"), "--profile", "legacy"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("overall situation, phase, or governing tendency", stdout)
        self.assertIn("strongest evidence for the specific condition", stdout)
        self.assertIn("supporting evidence for the overall reading", stdout)
        self.assertIn("emit explicit subsection headings as `### 序卦伝`", stdout)
        self.assertIn("quote the original text first, then include its reading", stdout)
        self.assertIn("do not emit `### 爻辞` or `### 小象伝` headings", stdout)
        self.assertIn("do not restate the user's concrete question", stdout)
        self.assertIn("Only the interpretation sections may reconnect", stdout)
        self.assertIn("Do not append profile notes", stdout)

    def test_ex5_prompt_states_auxiliary_hexagrams_are_support_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_2.md"), "--profile", "legacy"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("main hexagram remains the governing frame", stdout)
        self.assertIn("Auxiliary hexagrams are supporting structure only", stdout)
        self.assertIn("For each auxiliary hexagram, emit explicit subsection headings as `### 卦辞`", stdout)
        self.assertIn("do not emit `### 爻辞` or `### 小象伝` headings", stdout)
        self.assertIn("Outside `**核心・結論**` and the final interpretation sections, do not restate the user's concrete question", stdout)
        self.assertIn("Only the interpretation sections may reconnect", stdout)
        self.assertIn("Do not append profile notes", stdout)
        self.assertIn("Interpretation citation lines must use the form `（参照：<citation path>|<卦名>）`", stdout)
        self.assertIn("Do not replace per-section citation lines with `引用:` blocks", stdout)

    def test_ex_compare_prompt_states_primary_vs_supporting_evidence(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_4.md"), "--profile", "legacy"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("treat `爻辞` or `卦辞` as the primary evidence", stdout)
        self.assertIn("`彖伝` or `大象伝` only as supporting reinforcement", stdout)
        self.assertIn("include it in the same unified quote block", stdout)
        self.assertIn("do not expand into extra practical advice", stdout)

    def test_single_source_profile_does_not_leak_other_source(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(REPO_ROOT / "examples" / "extract" / "test_1.md"), "--profile", "honda"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = result.stdout
        self.assertIn("do not leak the other source family", stdout)
        self.assertIn("Do not rely on Takashima material", stdout)
        self.assertIn("Do not include execution metadata such as `skill used: ...`", stdout)
        self.assertIn("Treat `序卦伝` and `文言伝` as support-only layers", stdout)
        self.assertIn(str(REPO_ROOT / "assets" / "canonical" / "interp" / "honda"), stdout)

    def test_fixture_smoke_runs_all_examples(self) -> None:
        for input_path in sorted((REPO_ROOT / "examples" / "extract").glob("*.md")):
            if input_path.name.endswith("_answer_canonical.md"):
                continue
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(input_path), "--profile", "legacy"],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{input_path.name}: {result.stderr}")
            self.assertIn("## User Input", result.stdout)
            self.assertIn("structural references only", result.stdout)

    def test_manifest_cases_lock_expected_mode_and_template(self) -> None:
        for case in load_fixture_manifest():
            prompt = build_prompt_for_case(case["input"])
            self.assertIn("Mode: extract", prompt)
            self.assertIn(f"Template: {case['template']}", prompt)

    def test_added_test_fixtures_are_official_manifest_cases(self) -> None:
        ids = {
            "extract-standard-test-1": ("tests/test_1.md", "tests/test_1_answer_canonical.md"),
            "extract-complex-test-2": ("tests/test_2.md", "tests/test_2_answer_canonical.md"),
            "extract-complex-test-3": ("tests/test_3.md", "tests/test_3_answer_canonical.md"),
            "extract-compare-test-4": ("tests/test_4.md", "tests/test_4_answer_canonical.md"),
        }
        manifest_by_id = {case["id"]: case for case in load_fixture_manifest()}
        for case_id, (input_path, answer_path) in ids.items():
            self.assertIn(case_id, manifest_by_id)
            case = manifest_by_id[case_id]
            self.assertEqual(case["input"], input_path)
            self.assertEqual(case["expected_answer"], answer_path)
            self.assertTrue(resolve_fixture_path(input_path).exists())
            self.assertTrue(resolve_fixture_path(answer_path).exists())

    def test_manifest_required_sections_are_reflected_in_prompt_contract(self) -> None:
        mapping = {
            "核心・結論": "Order: `**核心・結論**`",
            "本卦": "`**本卦（<卦名>）**`",
            "変爻": "`**変爻",
            "補助卦": "auxiliary hexagrams",
            "吉凶順位": "`**吉凶順位（1位 = 最吉）**`",
            "まとめ": "`**まとめ**`",
        }
        for case in load_fixture_manifest():
            prompt = build_prompt_for_case(case["input"])
            for required in case.get("required_sections", []):
                self.assertIn(mapping[required], prompt, f"{case['id']} missing contract for {required}")

    def test_canonical_skeleton_sections_match_prompt_contract(self) -> None:
        for case in load_fixture_manifest():
            expected_answer = case.get("expected_answer")
            if not expected_answer:
                continue
            canonical_text = resolve_fixture_path(expected_answer).read_text(encoding="utf-8")
            skeleton = extract_canonical_skeleton(canonical_text)
            prompt = build_prompt_for_case(case["input"])
            if "核心・結論" in skeleton:
                self.assertIn("**核心・結論**", prompt, case["id"])
            if "本卦" in skeleton:
                self.assertIn("**本卦（<卦名>）**", prompt, case["id"])
            if "変爻" in skeleton:
                self.assertIn("**変爻", prompt, case["id"])
            if "本田解釈" in skeleton:
                self.assertIn("`**本田解釈**`", prompt, case["id"])
            if "高島解釈" in skeleton:
                self.assertIn("`**高島解釈**`", prompt, case["id"])
            if "吉凶順位（1位 = 最吉）" in skeleton:
                self.assertIn("`**吉凶順位（1位 = 最吉）**`", prompt, case["id"])
            if "候補別詳細" in skeleton:
                self.assertIn("Candidate detail headings must use", prompt, case["id"])
            if "まとめ" in skeleton:
                self.assertIn("`**まとめ**`", prompt, case["id"])
            if "まとめ表" in skeleton:
                self.assertIn("Markdown table under `**まとめ**`", prompt, case["id"])
            if "おすすめ" in skeleton:
                self.assertIn("explicitly names the recommended first-place candidate", prompt, case["id"])

    def test_official_canonical_files_have_structural_markers(self) -> None:
        for case in load_fixture_manifest():
            expected_answer = case.get("expected_answer")
            if not expected_answer:
                continue
            if not Path(expected_answer).name.startswith("test_"):
                continue
            canonical_text = resolve_fixture_path(expected_answer).read_text(encoding="utf-8")
            self.assertIn("**核心・結論**", canonical_text, case["id"])
            self.assertGreaterEqual(count_quote_blocks(canonical_text), 1, case["id"])
            self.assertGreaterEqual(count_citation_lines(canonical_text), 1, case["id"])
            self.assertGreaterEqual(count_reading_lines(canonical_text), 1, case["id"])
            self.assertNotIn("補足として", canonical_text, case["id"])
            self.assertNotIn("今回は honda profile", canonical_text, case["id"])
            self.assertNotIn("未検証の点", canonical_text, case["id"])
            if case["template"] == "EX_COMPARE":
                self.assertIn("**吉凶順位（1位 = 最吉）**", canonical_text, case["id"])
                self.assertTrue(
                    any(re.match(r"^### \d+位 .+$", line) for line in canonical_text.splitlines()),
                    case["id"],
                )
                self.assertIn("**まとめ**", canonical_text, case["id"])
            else:
                self.assertIn("**本卦", canonical_text, case["id"])
                self.assertIn("**変爻", canonical_text, case["id"])
                self.assertNotIn("### 爻辞", canonical_text, case["id"])
                self.assertNotIn("### 小象伝", canonical_text, case["id"])
                self.assertTrue(extract_interpretation_labels(canonical_text), case["id"])

    def test_legacy_canonical_interpretation_labels_can_be_reduced_for_single_source_profiles(self) -> None:
        for case in load_fixture_manifest():
            expected_answer = case.get("expected_answer")
            if not expected_answer or case["template"] == "EX_COMPARE":
                continue
            canonical_text = resolve_fixture_path(expected_answer).read_text(encoding="utf-8")
            if extract_interpretation_labels(canonical_text) != {"本田解釈", "高島解釈"}:
                continue
            self.assertEqual(expected_interpretation_labels_for_profile(canonical_text, "honda"), {"本田解釈"})
            self.assertEqual(expected_interpretation_labels_for_profile(canonical_text, "takashima"), {"高島解釈"})
            honda_prompt = build_prompt_for_case(case["input"], profile="honda")
            takashima_prompt = build_prompt_for_case(case["input"], profile="takashima")
            self.assertIn("output exactly one interpretation section with the profile label only", honda_prompt, case["id"])
            self.assertIn("output exactly one interpretation section with the profile label only", takashima_prompt, case["id"])

    def test_ex5_prompt_mentions_only_present_auxiliary_labels(self) -> None:
        for case in load_fixture_manifest():
            if case["template"] != "EX_5":
                continue
            input_text = resolve_fixture_path(case["input"]).read_text(encoding="utf-8")
            prompt = build_prompt_for_case(case["input"])
            present_labels = extract_input_auxiliary_labels(input_text)
            for label in present_labels:
                self.assertIn(label, prompt, f"{case['id']} should mention present {label}")
            if "之卦" not in present_labels:
                self.assertIn("If `之卦：なし`, do not fabricate a `之卦` section.", prompt, case["id"])

    def test_ex5_honda_prompt_forbids_metadata_and_locks_single_source_acceptance(self) -> None:
        prompt = build_prompt_for_case("tests/test_3.md", profile="honda")
        self.assertIn("Do not include execution metadata such as `skill used: ...`", prompt)
        self.assertIn("Do not prepend any execution metadata line before `**核心・結論**`.", prompt)
        self.assertIn("the answer must contain only that profile's interpretation label and citation family", prompt)
        self.assertIn("do not output any other profile-labeled interpretation section", prompt)
        self.assertIn("Final interpretation section: `本田解釈` only.", prompt)
        self.assertIn("Do not rely on Takashima material", prompt)
        self.assertIn("`序卦伝` may be used only inside `**本田解釈**`", prompt)
        self.assertIn("never emit standalone `### 序卦伝` or `### 文言伝`", prompt)

    def test_ex5_honda_prompt_requires_per_section_citations_for_no_changing_line_case(self) -> None:
        prompt = build_prompt_for_case("tests/test_2.md", profile="honda")
        self.assertIn("Within `**本卦（<卦名>）**`, keep the order `卦辞` -> `彖伝` -> `大象伝`.", prompt)
        self.assertIn("Each quoted main-hexagram subsection must end with exactly one citation line", prompt)
        self.assertIn("Each quoted auxiliary-hexagram subsection must end with exactly one citation line", prompt)
        self.assertIn("Interpretation citation lines must use the form `（参照：<citation path>|<卦名>）`", prompt)
        self.assertIn("Do not replace per-section citation lines with `引用:` blocks, bullet lists, or backticked path lists.", prompt)
        self.assertIn("They must never produce standalone `### 序卦伝` or `### 文言伝` headings.", prompt)

    def test_ex5_honda_acceptance_shape_matches_minimal_review_bar(self) -> None:
        input_text = (REPO_ROOT / "tests" / "test_3.md").read_text(encoding="utf-8")
        selection = select_sources(resolve_profile("honda"), resolve_input(input_text))
        self.assertEqual(selection["final_sections"], ["本田解釈"])
        self.assertEqual({item["provider"] for item in selection["selected_items"]}, {"honda"})
        self.assertFalse(any("takashima_zouho/" in path for path in selection["citation_files"]))
        auxiliary_items = [item for item in selection["selected_items"] if item["role"] == "auxiliary_hexagram"]
        self.assertTrue(auxiliary_items)
        self.assertTrue(all(not any(name.startswith("yao_") for name in item["section_names"]) for item in auxiliary_items))
        self.assertTrue(all("jokaden" not in item["section_names"] for item in selection["selected_items"]))
        self.assertEqual(len(selection["support_items"]), 5)
        main_items = [item for item in selection["selected_items"] if item["role"] == "main_hexagram"]
        self.assertEqual(len(main_items), 1)
        self.assertIn("yao_3", main_items[0]["section_names"])

        honda_prompt = build_prompt_for_case("tests/test_3.md", profile="honda")
        self.assertIn("Within `**本卦（<卦名>）**`, emit explicit subsection headings as `### 卦辞`, `### 彖伝`, and `### 大象伝`.", honda_prompt)
        self.assertIn("never emit standalone `### 序卦伝` or `### 文言伝`", honda_prompt)
        self.assertIn("## Honda Interpretation Support Paths (Internal Only)", honda_prompt)

        canonical_text = (REPO_ROOT / "tests" / "test_3_answer_canonical.md").read_text(encoding="utf-8")
        self.assertFalse(canonical_text.startswith("skill used:"))
        for label in ("之卦（雷澤帰妹）", "互卦（沢天夬）", "錯卦（風地観）", "綜卦（天山遯）"):
            block = extract_section_block(canonical_text, label)
            self.assertTrue(block)
            self.assertIn("### 卦辞", block.replace("**卦辞**", "### 卦辞"))
            self.assertIn("### 彖伝", block.replace("**彖伝**", "### 彖伝"))
            self.assertIn("### 大象伝", block.replace("**大象伝**", "### 大象伝"))
            self.assertNotIn("爻", block.replace("大象伝", "").replace("卦辞", "").replace("彖伝", ""))
        self.assertEqual(canonical_text.count("**変爻（3爻）**"), 1)

    def test_ex_simple_honda_prompt_suppresses_standalone_jokaden_and_allows_bungen_only_in_interpretation(self) -> None:
        prompt = build_prompt_for_case("examples/extract/standard_1.md", profile="honda")
        self.assertIn("Within `**本卦（<卦名>）**`, emit explicit subsection headings as `### 卦辞`, `### 彖伝`, and `### 大象伝`.", prompt)
        self.assertIn("do not use `序卦伝` for EX_SIMPLE", prompt)
        self.assertIn("never emit standalone `### 文言伝`", prompt)
        self.assertIn("`文言伝` may be used only as optional support inside `**本田解釈**`", prompt)
        self.assertIn("## Honda Interpretation Support Paths (Internal Only)", prompt)
        self.assertIn("bungen.md", prompt)

    def test_compare_prompt_forbids_standalone_takashima_section_in_legacy(self) -> None:
        for case in load_fixture_manifest():
            if case["template"] != "EX_COMPARE":
                continue
            prompt = build_prompt_for_case(case["input"], profile="legacy")
            self.assertIn("Takashima remains support-only", prompt, case["id"])
            self.assertIn("do not output any standalone Takashima-labeled section", prompt, case["id"])

    def test_compare_prompt_requires_exact_recommendation_sentence(self) -> None:
        for case in load_fixture_manifest():
            if case["template"] != "EX_COMPARE":
                continue
            prompt = build_prompt_for_case(case["input"], profile="legacy")
            self.assertIn("The final recommendation sentence must be exactly", prompt, case["id"])
            self.assertIn("`今回のおすすめは、<候補名>です。`", prompt, case["id"])


if __name__ == "__main__":
    unittest.main()
