from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "build_extract_prompt.py"
ASSEMBLE_SCRIPT = REPO_ROOT / "scripts" / "assemble_extract_answer.py"
APPEND_SCRIPT = REPO_ROOT / "scripts" / "append_takashima_raw.py"
NEXT_WORK_SCRIPT = REPO_ROOT / "scripts" / "next_work_filename.py"
SKELETON_SCRIPT = REPO_ROOT / "scripts" / "build_answer_skeleton.py"
FIXTURE_MANIFEST = REPO_ROOT / "fixtures" / "manifest.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from profiles import takashima_provider  # noqa: E402
from rendering import (  # noqa: E402
    build_ex_5_takashima_raw_text,
    build_ex_simple2_takashima_raw_text,
    build_ex_simple_takashima_raw_text,
    build_reference_case_excerpt_section,
    _extract_line_block,
    load_honka_quotes,
    load_takashima_honka_text,
    load_takashima_line_heading,
    load_takashima_line_text,
    load_line_quotes,
)
from resolving import extract_compare_candidates, parse_mode_marker, parse_template_marker, resolve_input  # noqa: E402
from selecting import select_sources  # noqa: E402
from workflow import build_answer_skeleton, line_labels_from_numbers, next_work_output_path  # noqa: E402
import append_takashima_raw as append_raw  # noqa: E402


def load_fixture_manifest() -> list[dict[str, object]]:
    payload = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    return payload["cases"]


def resolve_fixture_path(relpath: str) -> Path:
    return REPO_ROOT / relpath


def load_text(relpath: str) -> str:
    return resolve_fixture_path(relpath).read_text(encoding="utf-8")


def build_prompt_for_case(input_relpath: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(resolve_fixture_path(input_relpath)),
                "--output-dir",
                tmpdir,
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AssertionError(f"evidence build failed for {input_relpath}: {result.stderr}")
        output_path = Path(result.stdout.strip())
        return output_path.read_text(encoding="utf-8")


def build_prompt_text_for_case(input_relpath: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(resolve_fixture_path(input_relpath)),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"prompt build failed for {input_relpath}: {result.stderr}")
    return result.stdout


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start_index = index + 1
            break
    if start_index is None:
        return ""
    end_index = len(lines)
    for index in range(start_index, len(lines)):
        if lines[index].startswith("## "):
            end_index = index
            break
    return "\n".join(lines[start_index:end_index]).strip()


def split_paragraphs(text: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n", text.strip()) if chunk.strip()]


def assert_section_contains_block(
    testcase: unittest.TestCase, text: str, heading: str, block_text: str, next_heading: str | None = None
) -> None:
    needle = f"{heading}\n\n{block_text}"
    testcase.assertIn(needle, text)
    if next_heading is not None:
        testcase.assertIn(f"{needle}\n\n{next_heading}", text)


def assert_question_section_contains_input(testcase: unittest.TestCase, text: str, input_text: str) -> None:
    needle = f"## 質問文\n\n```text\n{input_text.rstrip()}\n```"
    testcase.assertIn(needle, text)

class ParserTests(unittest.TestCase):
    def _resolve_simple_changing_lines(self, changing_line: str) -> list[int]:
        resolved = resolve_input(
            "[MODE:EXTRACT]\n"
            "[TEMPLATE:EX_SIMPLE]\n\n"
            "### 3. 占い結果入力\n"
            "本卦：42風雷益\n"
            f"変爻：{changing_line}\n"
        )
        return resolved["changing_lines"]

    def test_parse_valid_templates(self) -> None:
        self.assertEqual(parse_mode_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n"), "extract")
        self.assertEqual(parse_template_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n"), "EX_SIMPLE")
        self.assertEqual(parse_template_marker("[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE2]\n"), "EX_SIMPLE2")
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

    def test_standard_and_kanji_changing_line_inputs_are_accepted(self) -> None:
        cases = {
            "1": [1],
            "1爻": [1],
            "初爻": [1],
            "2": [2],
            "2爻": [2],
            "二爻": [2],
            "3": [3],
            "3爻": [3],
            "三爻": [3],
            "4": [4],
            "4爻": [4],
            "四爻": [4],
            "5": [5],
            "5爻": [5],
            "五爻": [5],
            "6": [6],
            "6爻": [6],
            "上爻": [6],
        }
        for changing_line, expected in cases.items():
            with self.subTest(changing_line=changing_line):
                self.assertEqual(self._resolve_simple_changing_lines(changing_line), expected)

    def test_invalid_changing_line_inputs_fail_fast(self) -> None:
        for changing_line in ("２", "２爻", "二", "六二", "九三"):
            with self.subTest(changing_line=changing_line):
                with self.assertRaisesRegex(Exception, "変爻を解釈できません"):
                    self._resolve_simple_changing_lines(changing_line)

    def test_compare_candidate_parsing(self) -> None:
        text = (REPO_ROOT / "fixtures" / "test_compare.md").read_text(encoding="utf-8")
        candidates = extract_compare_candidates(text)
        self.assertEqual(candidates[0]["label"], "ストリートファイター6")
        self.assertEqual(candidates[0]["hexagram_number"], 42)
        self.assertEqual(candidates[0]["changing_lines"], [4])
        self.assertEqual(candidates[-1]["label"], "ソニック")
        self.assertEqual(candidates[-1]["changing_lines"], [6])

    def test_compare_candidate_parsing_accepts_markdown_candidate_headings(self) -> None:
        text = (
            "[MODE:EXTRACT]\n"
            "[TEMPLATE:EX_COMPARE]\n\n"
            "### 3. 占い結果入力\n\n"
            "#### 候補A：スパイダーマン\n\n"
            "本卦：31沢山咸\n"
            "変爻：4爻\n\n"
            "#### 候補B：ライズオブローニン\n\n"
            "本卦：6天水訟\n"
            "変爻：初爻\n"
        )
        candidates = extract_compare_candidates(text)
        self.assertEqual(candidates[0]["label"], "候補A：スパイダーマン")
        self.assertEqual(candidates[0]["hexagram_number"], 31)
        self.assertEqual(candidates[0]["changing_lines"], [4])
        self.assertEqual(candidates[1]["label"], "候補B：ライズオブローニン")
        self.assertEqual(candidates[1]["hexagram_number"], 6)
        self.assertEqual(candidates[1]["changing_lines"], [1])

    def test_compare_candidate_parsing_accepts_candidate_prefix_without_trailing_colon(self) -> None:
        text = (
            "[MODE:EXTRACT]\n"
            "[TEMPLATE:EX_COMPARE]\n\n"
            "### 3. 占い結果入力\n\n"
            "候補A：スパイダーマン\n\n"
            "本卦：31沢山咸\n"
            "変爻：4爻\n\n"
            "候補B：ライズオブローニン\n\n"
            "本卦：6天水訟\n"
            "変爻：初爻\n"
        )
        candidates = extract_compare_candidates(text)
        self.assertEqual([candidate["label"] for candidate in candidates], ["候補A：スパイダーマン", "候補B：ライズオブローニン"])

    def test_ex_simple2_rejects_missing_changing_line(self) -> None:
        with self.assertRaisesRegex(Exception, "requires at least one changing line"):
            resolve_input(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE2]\n\n### 3. 占い結果入力\n本卦：5水天需\n変爻：なし\n之卦：6天水訟\n"
            )

    def test_ex_simple_rejects_missing_changing_line(self) -> None:
        with self.assertRaisesRegex(Exception, "EX_SIMPLE requires at least one changing line"):
            resolve_input(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n\n### 3. 占い結果入力\n本卦：5水天需\n変爻：なし\n"
            )

    def test_ex_simple_rejects_multiple_changing_lines(self) -> None:
        with self.assertRaisesRegex(Exception, "supports at most one changing line"):
            resolve_input(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n\n### 3. 占い結果入力\n本卦：34雷天大壮\n変爻：2爻 3爻\n"
            )

    def test_next_work_output_path_ignores_non_answer_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir)
            (work_dir / "2026-04-01_01.md").write_text("", encoding="utf-8")
            (work_dir / "2026-04-01_03.md").write_text("", encoding="utf-8")
            (work_dir / "2026-04-01_03_keika.md").write_text("", encoding="utf-8")
            (work_dir / "memo.md").write_text("", encoding="utf-8")
            next_path = next_work_output_path(work_dir, today=date(2026, 4, 1))
            self.assertEqual(next_path.name, "2026-04-01_04.md")

    def test_next_work_output_path_rejects_non_directory_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            work_file = Path(tmpdir) / "work.md"
            work_file.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(Exception, "work directory not found or not a directory"):
                next_work_output_path(work_file, today=date(2026, 4, 1))


class SelectionTests(unittest.TestCase):
    def test_takashima_provider_points_to_assets_root(self) -> None:
        provider = takashima_provider()
        self.assertEqual(provider.name, "takashima")
        self.assertEqual(provider.asset_root, REPO_ROOT / "assets" / "takashima")

    def test_ex_simple_uses_takashima_source_only(self) -> None:
        text = (REPO_ROOT / "fixtures" / "test_simple.md").read_text(encoding="utf-8")
        selection = select_sources(takashima_provider(), resolve_input(text))
        self.assertEqual({item["provider"] for item in selection["selected_items"]}, {"takashima"})
        self.assertEqual(selection["support_items"], [])
        self.assertEqual(len(selection["selected_items"]), 1)
        item = selection["selected_items"][0]
        self.assertEqual(item["section_names"], ["kaji", "tanden", "taisho", "yao_5"])
        self.assertEqual(item["section_paths"], [str(REPO_ROOT / "assets" / "takashima" / "42_風雷益.md")])
        self.assertEqual(selection["citation_files"], ["takashima/42_風雷益.md"])

    def test_ex_5_auxiliary_hexagrams_exclude_yao_sections(self) -> None:
        text = (REPO_ROOT / "fixtures" / "test_ex5_noline.md").read_text(encoding="utf-8")
        selection = select_sources(takashima_provider(), resolve_input(text))
        auxiliary_items = [item for item in selection["selected_items"] if item["role"] == "auxiliary_hexagram"]
        self.assertTrue(auxiliary_items)
        for item in auxiliary_items:
            self.assertFalse(any(name.startswith("yao_") for name in item["section_names"]))
        self.assertEqual(selection["support_items"], [])

    def test_ex_simple2_selects_main_and_zhigua_only(self) -> None:
        text = (REPO_ROOT / "fixtures" / "test_simple2.md").read_text(encoding="utf-8")
        selection = select_sources(takashima_provider(), resolve_input(text))
        self.assertEqual(len(selection["selected_items"]), 2)
        main_item, zhigua_item = selection["selected_items"]
        self.assertEqual(main_item["role"], "main_hexagram")
        self.assertEqual(main_item["section_names"], ["kaji", "tanden", "taisho", "yao_3"])
        self.assertEqual(zhigua_item["role"], "auxiliary_hexagram")
        self.assertEqual(zhigua_item["section_names"], ["kaji", "tanden", "taisho"])
        self.assertEqual(selection["citation_files"], ["takashima/40_雷水解.md", "takashima/32_雷風恒.md"])

    def test_ex_compare_uses_takashima_source_only(self) -> None:
        text = (REPO_ROOT / "fixtures" / "test_compare.md").read_text(encoding="utf-8")
        selection = select_sources(takashima_provider(), resolve_input(text))
        self.assertEqual({item["provider"] for item in selection["selected_items"]}, {"takashima"})
        self.assertEqual(selection["support_items"], [])
        self.assertGreaterEqual(len(selection["selected_items"]), 2)
        for item in selection["selected_items"]:
            self.assertTrue(all(name.startswith("yao_") for name in item["section_names"]))

    def test_honka_quotes_load_whole_block_without_legacy_subheadings(self) -> None:
        quotes = load_honka_quotes(42)
        self.assertEqual(quotes.title, "風雷益")
        self.assertIn("> 益、利有攸往。", quotes.raw_text)
        self.assertIn("（占）", quotes.raw_text)
        self.assertNotIn("#### 卦辞", quotes.raw_text)

    def test_line_quotes_load_whole_block_without_legacy_subheadings(self) -> None:
        quotes = load_line_quotes(42, "5爻")
        self.assertEqual(quotes.line_label, "5爻")
        self.assertIn("> 九五。有孚惠心。勿問元吉。", quotes.raw_text)
        self.assertIn("（占）", quotes.raw_text)
        self.assertNotIn("##### 爻辞", quotes.raw_text)

    def test_line_quotes_keep_shozoden_alignment_with_three_line_quotes(self) -> None:
        quotes = load_line_quotes(1, "初爻")
        self.assertEqual(quotes.koji.original, "初九。潜龍。勿用。")
        self.assertEqual(quotes.koji.reading, "初九（しょきゅう）。潜龍（せんりゅう）なり。用（もち）うる勿（なか）れ。")
        self.assertIsNotNone(quotes.shozoden)
        self.assertEqual(quotes.shozoden.original, "潜龍勿用、陽在下也。")
        self.assertEqual(quotes.shozoden.reading, "潜龍用うる勿れとは、陽にして下に在ればなり。")

    def test_extract_line_block_bridges_numeric_input_to_line_designations(self) -> None:
        block = """### 六三

> 六三。負且乘。致寇至。貞吝。
> 六三。負うて且つ乗る。寇の至るを致す。貞なれども吝。

（占）例。
"""
        extracted = _extract_line_block(block, "3爻")
        self.assertIn("> 六三。負且乘。致寇至。貞吝。", extracted)
        self.assertIn("（占）例。", extracted)

    def test_extract_line_block_bridges_kanji_input_to_line_designations(self) -> None:
        block = """### 六三

> 六三。負且乘。致寇至。貞吝。
> 六三。負うて且つ乗る。寇の至るを致す。貞なれども吝。

（占）例。
"""
        extracted = _extract_line_block(block, "三爻")
        self.assertIn("> 六三。負且乘。致寇至。貞吝。", extracted)
        self.assertIn("（占）例。", extracted)

    def test_extract_line_block_accepts_kanji_source_heading_aliases(self) -> None:
        block = """### 二爻

> 仮の爻辞。
> かりのこうじ。

（占）例。
"""
        extracted = _extract_line_block(block, "2爻")
        self.assertIn("> 仮の爻辞。", extracted)
        extracted_kanji = _extract_line_block(block, "二爻")
        self.assertIn("> 仮の爻辞。", extracted_kanji)

    def test_load_takashima_line_heading_resolves_actual_name_from_numeric_source_heading(self) -> None:
        path = REPO_ROOT / "assets" / "takashima" / "20_風地観.md"
        self.assertEqual(load_takashima_line_heading(path, "5爻"), "九五")

    def test_load_takashima_line_text_accepts_actual_name_source_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "99_仮.md"
            path.write_text(
                "---\n---\n\n### 変爻解釈\n\n#### 九二\n\n仮の本文。\n",
                encoding="utf-8",
            )
            self.assertEqual(load_takashima_line_text(path, "2爻"), "仮の本文。")


class PromptBuildTests(unittest.TestCase):
    def test_spec_defines_responsibility_boundary_and_acceptance_checklist(self) -> None:
        text = (REPO_ROOT / "spec" / "extract_contract.md").read_text(encoding="utf-8")
        self.assertIn("## responsibility boundary", text)
        self.assertIn("script が保証する範囲", text)
        self.assertIn("LLM が担当する範囲", text)
        self.assertIn("人間レビューが担当する範囲", text)
        self.assertIn("本卦ブロックと変爻ブロックの引用抽出", text)
        self.assertIn("classical block 機械差し込み", text)
        self.assertIn("各候補は変爻の引用ブロックを中心に据えます", text)
        self.assertIn("## stable acceptance checklist", text)
        self.assertIn("`EX_COMPARE` は `## 高島易断` と `## 占例抜粋` の対象外です。", text)

    def test_ex5_format_uses_block_based_quote_rules(self) -> None:
        text = (REPO_ROOT / "formats" / "ex_5_single.md").read_text(encoding="utf-8")
        self.assertIn("script-filled quote section", text)
        self.assertIn("supporting auxiliary hexagram", text)
        self.assertIn("Do not read or cite auxiliary changing lines", text)
        self.assertIn("omit both `## 変爻` and `## 之卦`", text)
        self.assertIn("Emit the `## 之卦` heading only", text)
        self.assertIn("After the fixed quote sections, emit exactly one `## 参照` section", text)

    def test_formats_state_quote_blocks_are_script_fixed(self) -> None:
        shared = (REPO_ROOT / "formats" / "shared.md").read_text(encoding="utf-8")
        ex_simple = (REPO_ROOT / "formats" / "ex_simple_single.md").read_text(encoding="utf-8")
        ex_simple2 = (REPO_ROOT / "formats" / "ex_simple2_single.md").read_text(encoding="utf-8")
        ex_5 = (REPO_ROOT / "formats" / "ex_5_single.md").read_text(encoding="utf-8")
        self.assertIn("fixed source blocks", shared)
        self.assertIn("script-filled quote section", ex_simple)
        self.assertIn("landing direction of the change", ex_simple2)
        self.assertIn("script-filled quote section", ex_5)
        self.assertNotIn("### 本卦解釈", ex_5)
        self.assertNotIn("### 変爻解釈", ex_5)

    def test_runtime_sources_define_block_only_contract_for_simple_templates(self) -> None:
        spec = (REPO_ROOT / "spec" / "extract_contract.md").read_text(encoding="utf-8")
        ex_simple = (REPO_ROOT / "formats" / "ex_simple_single.md").read_text(encoding="utf-8")
        ex_simple2 = (REPO_ROOT / "formats" / "ex_simple2_single.md").read_text(encoding="utf-8")
        ex_5 = (REPO_ROOT / "formats" / "ex_5_single.md").read_text(encoding="utf-8")
        self.assertIn("`EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` では、LLM は本文 section を書きません。", spec)
        self.assertIn("`EX_SIMPLE` / `EX_SIMPLE2` / `EX_5` の最終 md に、手書き prose section はありません。", spec)
        self.assertIn("script inserts the honka source block", ex_simple)
        self.assertIn("script-filled quote section for the landing direction", ex_simple2)
        self.assertIn("supporting auxiliary hexagram", ex_5)
        self.assertIn("`EX_5` の fixed quote sections では、問いの具体内容・選択肢・状況説明を再掲しません。", spec)
        self.assertIn("`EX_5` で変爻がない場合は、`## 変爻` と `## 之卦` を出さず、本卦と補助卦だけで直接適用します。", spec)
        self.assertIn("`EX_5` で変爻が1本のときは、その変爻を今回の主メッセージとして扱います。", spec)
        self.assertIn("`EX_5` で変爻が2本以上のときは、本卦の卦辞を今回の主メッセージとして扱い、各変爻は補助証拠として扱います。", spec)
        self.assertIn("The main hexagram and changing line are the primary evidence for the reading.", ex_5)
        self.assertIn("If multiple changing lines exist, emit one `## 変爻` section per line in input order.", ex_5)
        self.assertIn("`之卦` is supporting evidence for landing direction or after-state", ex_5)

    def test_evidence_contains_background_question_and_quotes(self) -> None:
        stdout = build_prompt_for_case("fixtures/test_simple.md")
        self.assertIn("# ekikyo Evidence Bundle", stdout)
        self.assertIn("## 背景", stdout)
        self.assertIn("## 易経への質問", stdout)
        self.assertIn("CodexはWindowsネイティブ側へ寄せたほうがいいだろうか？", stdout)
        self.assertIn("## 本卦（42 風雷益）", stdout)
        self.assertIn("## 変爻（5爻）", stdout)
        self.assertIn("> 益、利有攸往。", stdout)
        self.assertIn("利渉大川。", stdout)
        self.assertIn("> 九五。有孚惠心。勿問元吉。", stdout)
        self.assertIn("九五の王さまは剛健中正の徳を具えて君主の位に居る。", stdout)
        self.assertNotIn("> 原文", stdout)
        self.assertNotIn("## 核心・結論", stdout)

    def test_prompt_states_quote_blocks_are_script_fixed(self) -> None:
        stdout = build_prompt_for_case("fixtures/test_simple.md")
        prompt = build_prompt_text_for_case("fixtures/test_simple.md")
        self.assertIn("## 占例参考", stdout)
        self.assertIn("養子", stdout)
        self.assertIn("The final answer begins with a machine-copied `## 質問文` section built from the user input", prompt)
        self.assertIn("fixed source blocks", prompt)
        self.assertIn("## Source Evidence", prompt)
        self.assertIn("## 本卦（42 風雷益）", prompt)
        self.assertIn("## 変爻（5爻）", prompt)
        self.assertIn("## 占例参考", prompt)
        self.assertIn("養子", prompt)
        self.assertIn("> 益、利有攸往。", prompt)
        self.assertIn("> 九五。有孚惠心。勿問元吉。", prompt)
        self.assertIn("九五の王さまは剛健中正の徳を具えて君主の位に居る。", prompt)
        self.assertNotIn("\n## 高島易断\n", prompt)

    def test_ex_simple2_prompt_and_evidence_include_zhigua_only(self) -> None:
        stdout = build_prompt_for_case("fixtures/test_simple2.md")
        prompt = build_prompt_text_for_case("fixtures/test_simple2.md")
        for text in (stdout, prompt):
            self.assertIn("## 本卦（40 雷水解）", text)
            self.assertIn("## 変爻（3爻）", text)
            self.assertIn("## 占例参考", text)
            self.assertIn("## 之卦（32 雷風恒）", text)
            self.assertNotIn("## 互卦（", text)
            self.assertNotIn("## 錯卦（", text)
            self.assertNotIn("## 綜卦（", text)

    def test_compare_evidence_is_line_only(self) -> None:
        stdout = build_prompt_for_case("fixtures/test_compare.md")
        self.assertIn("## 比較候補", stdout)
        self.assertIn("## 候補1：ストリートファイター6（42 風雷益）", stdout)
        self.assertIn("### 爻辞", stdout)
        self.assertNotIn("### 高島解釈", stdout)
        self.assertNotIn("### 卦辞", stdout)

    def test_build_answer_skeleton_for_ex_simple2_has_required_headings(self) -> None:
        skeleton = build_answer_skeleton(resolve_input(load_text("fixtures/test_simple2.md")))
        self.assertIn("## 質問文", skeleton)
        self.assertIn("## 本卦", skeleton)
        self.assertIn("## 変爻", skeleton)
        self.assertNotIn("### 本卦解釈", skeleton)
        self.assertNotIn("### 変爻解釈", skeleton)
        self.assertIn("## 之卦", skeleton)
        self.assertNotIn("### 之卦解釈", skeleton)
        self.assertTrue(skeleton.rstrip().endswith("## 参照"))

    def test_build_answer_skeleton_for_ex5_without_line_omits_line_and_zhigua(self) -> None:
        skeleton = build_answer_skeleton(resolve_input(load_text("fixtures/test_ex5_noline.md")))
        self.assertNotIn("## 変爻", skeleton)
        self.assertNotIn("## 之卦", skeleton)
        self.assertIn("## 互卦", skeleton)
        self.assertIn("## 錯卦", skeleton)
        self.assertIn("## 綜卦", skeleton)

    def test_build_answer_skeleton_for_ex_compare_has_question_heading(self) -> None:
        skeleton = build_answer_skeleton(resolve_input(load_text("fixtures/test_compare.md")))
        self.assertTrue(skeleton.startswith("## 質問文"))
        self.assertIn("**核心・結論**", skeleton)
        self.assertIn("**まとめ**", skeleton)

    def test_next_work_filename_script_prints_next_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir)
            (work_dir / "2026-04-01_02.md").write_text("", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(NEXT_WORK_SCRIPT),
                    "--work-dir",
                    str(work_dir),
                    "--date",
                    "2026-04-01",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), str(work_dir / "2026-04-01_03.md"))

    def test_build_answer_skeleton_script_outputs_ex_simple_skeleton(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SKELETON_SCRIPT),
                "--input",
                str(REPO_ROOT / "fixtures" / "test_simple.md"),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## 質問文", result.stdout)
        self.assertIn("## 本卦", result.stdout)
        self.assertIn("## 変爻", result.stdout)
        self.assertNotIn("### 本卦解釈", result.stdout)
        self.assertNotIn("### 変爻解釈", result.stdout)
        self.assertNotIn("## 総合解釈", result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith("## 参照"))
        self.assertNotIn("### 彖伝", result.stdout)
        self.assertNotIn("### 大象伝", result.stdout)

    def test_compare_prompt_keeps_lightweight_prompt_shape(self) -> None:
        prompt = build_prompt_text_for_case("fixtures/test_compare.md")
        self.assertNotIn("## Source Evidence", prompt)
        self.assertNotIn("## 比較候補", prompt)

    def test_ex5_evidence_omits_line_and_zhigua_when_no_changing_line(self) -> None:
        stdout = build_prompt_for_case("fixtures/test_ex5_noline.md")
        self.assertIn("## 本卦（5 水天需）", stdout)
        self.assertIn("> 需、有孚。光亨。貞吉。利渉大川。", stdout)
        self.assertIn("九五の陽爻が陰爻の中に陥り、下卦の三陽が進むのを待っている。", stdout)
        self.assertNotIn("## 之卦（", stdout)
        self.assertNotIn("## 変爻（", stdout)
        self.assertIn("## 互卦（38 火沢睽）", stdout)
        self.assertIn("## 錯卦（35 火地晋）", stdout)
        self.assertIn("## 綜卦（6 天水訟）", stdout)

    def test_ex5_prompt_embeds_auxiliary_evidence_without_auxiliary_line_text(self) -> None:
        prompt = build_prompt_text_for_case("fixtures/test_ex5_noline.md")
        self.assertIn("## Source Evidence", prompt)
        self.assertIn("## 本卦（5 水天需）", prompt)
        self.assertNotIn("## 之卦（", prompt)
        self.assertNotIn("## 変爻（", extract_section(prompt, "## Source Evidence"))
        self.assertIn("## 互卦（38 火沢睽）", prompt)
        self.assertIn("## 錯卦（35 火地晋）", prompt)
        self.assertIn("## 綜卦（6 天水訟）", prompt)
        self.assertNotIn("\n## 高島易断\n", prompt)

    def test_ex5_evidence_includes_multiple_line_sections_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_5]\n\n### 1. 占いに至った背景・状況\n状況。\n\n### 2. 易経への質問\nどうすべきか。\n\n### 3. 占い結果入力\n本卦：34雷天大壮\n変爻：2爻 3爻\n之卦：54雷沢帰妹\n互卦：43沢天夬\n錯卦：20風地観\n綜卦：33天山遯\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = result.stdout
            self.assertIn("## 変爻（2爻）", prompt)
            self.assertIn("## 変爻（3爻）", prompt)

    def test_fixture_smoke_runs_all_fixtures(self) -> None:
        for input_path in sorted((REPO_ROOT / "fixtures").glob("*.md")):
            if input_path.name.endswith("_answer_canonical.md"):
                continue
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--input",
                        str(input_path),
                        "--output-dir",
                        tmpdir,
                    ],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, f"{input_path.name}: {result.stderr}")
                output_path = Path(result.stdout.strip())
                self.assertTrue(output_path.is_file())
                content = output_path.read_text(encoding="utf-8")
                self.assertIn("# ekikyo Evidence Bundle", content)
                self.assertNotIn("> 原文", content)
                self.assertNotIn("## 核心・結論", content)

    def test_manifest_cases_lock_expected_mode_and_template(self) -> None:
        for case in load_fixture_manifest():
            prompt = build_prompt_for_case(case["input"])
            self.assertIn(f"- template: {case['template']}", prompt)
            if case["template"] == "EX_SIMPLE":
                self.assertIn("## 変爻（", prompt)
            elif case["template"] == "EX_SIMPLE2":
                self.assertIn("## 之卦（", prompt)
                self.assertNotIn("## 互卦（", prompt)
            elif case["template"] == "EX_5":
                self.assertIn("## 互卦（", prompt)
            elif case["template"] == "EX_COMPARE":
                self.assertIn("## 比較候補", prompt)
                self.assertIn("## 候補1：", prompt)

    def test_standard_canonical_answers_keep_block_only_shape(self) -> None:
        for relpath in (
            "fixtures/test_simple_answer_canonical.md",
            "fixtures/test_simple2_answer_canonical.md",
        ):
            text = load_text(relpath)
            self.assertNotIn("### 本卦解釈", text)
            self.assertNotIn("### 変爻解釈", text)
            self.assertNotIn("### 之卦解釈", text)
            self.assertNotIn("## 総合解釈", text, relpath)
            self.assertIn("## 参照", text)
            self.assertNotIn("（参照：", text)
            self.assertRegex(text, r"- takashima/.+.md | .+")
            self.assertIn("## 高島易断", text)
            self.assertIn("## 占例抜粋", text)
            self.assertRegex(text, r"## 参照\n(?:- .+\n)+\n\n## 高島易断")
            self.assertLess(text.index("## 参照"), text.index("## 高島易断"))
            self.assertLess(text.index("## 高島易断"), text.index("## 占例抜粋"))
            self.assertNotRegex(text, r"/home/ys/projects/ekikyo|run\.json")

    def test_ex5_canonical_answers_keep_block_only_shape(self) -> None:
        for relpath in (
            "fixtures/test_ex5_noline_answer_canonical.md",
            "fixtures/test_ex5_answer_canonical.md",
        ):
            text = load_text(relpath)
            self.assertNotIn("## 総合解釈", text, relpath)
            self.assertIn("## 参照", text, relpath)
            self.assertIn("## 高島易断", text, relpath)
            self.assertNotIn("### 之卦解釈", text, relpath)
            self.assertNotIn("### 互卦解釈", text, relpath)
            self.assertNotIn("### 錯卦解釈", text, relpath)
            self.assertNotIn("### 綜卦解釈", text, relpath)
            self.assertNotIn("**高島解釈**", text, relpath)
            self.assertNotIn("**本田解釈**", text, relpath)
            self.assertNotRegex(text, r"/home/ys/projects/ekikyo|run\.json", relpath)

    def test_compare_canonical_answer_keeps_ranked_skeleton(self) -> None:
        text = load_text("fixtures/test_compare_answer_canonical.md")
        ranked_sections = re.findall(r"^### \d+位 ", text, flags=re.MULTILINE)
        self.assertIn("**核心・結論**", text)
        self.assertIn("**吉凶順位（1位 = 最吉）**", text)
        self.assertGreaterEqual(len(ranked_sections), 2)
        self.assertNotIn("## 高島易断", text)
        self.assertNotIn("honda_wataru/", text)
        self.assertIn("（参照：takashima/24_地雷復.md|地雷復）", text)
        self.assertIn("今回のおすすめは、エントロピーセンターです。", text)
        self.assertNotRegex(text, r"/home/ys/projects/ekikyo|run\.json")


class AssemblyTests(unittest.TestCase):
    def test_assemble_script_rejects_missing_answer_file_with_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "missing.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(f"answer file not found: {output_path}", result.stderr)

    def test_assemble_script_rejects_draft_missing_question_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 本卦

## 変爻

""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("required section heading not found: ## 質問文", result.stderr)

    def test_assemble_script_supports_multiple_changing_lines_for_ex5(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_5]\n\n### 1. 占いに至った背景・状況\n状況。\n\n### 2. 易経への質問\nどうすべきか。\n\n### 3. 占い結果入力\n本卦：34雷天大壮\n変爻：2爻 3爻\n之卦：54雷沢帰妹\n互卦：43沢天夬\n錯卦：20風地観\n綜卦：33天山遯\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

## 本卦

## 変爻

## 之卦

## 変爻

## 互卦

## 錯卦

## 綜卦

## 参照
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertEqual(content.count("## 九二"), 1)
            self.assertEqual(content.count("## 九三"), 1)
            self.assertIn(load_line_quotes(34, "2爻").raw_text, content)
            self.assertIn(load_line_quotes(34, "3爻").raw_text, content)
            self.assertIn("## 之卦：雷沢帰妹", content)

    def test_assemble_script_injects_ex_simple_blocks_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

**本卦（42 風雷益）**

> 壊れた引用

### 本卦解釈

ここに本卦解釈。

（参照：takashima_zouho/42_風雷益.md|42 風雷益）

**変爻（5爻）**

> 壊れた変爻引用

### 変爻解釈

ここに変爻解釈。

（参照：takashima_zouho/42_風雷益.md|42 風雷益）

## 参照
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("## 質問文\n\n```text\n"))
            self.assertIn(load_text("fixtures/test_simple.md").rstrip(), content)
            assert_section_contains_block(self, content, "## 風雷益", load_honka_quotes(42).raw_text, "## 九五")
            assert_section_contains_block(self, content, "## 九五", load_line_quotes(42, "5爻").raw_text, "## 参照")
            self.assertNotIn("（参照：", content)
            self.assertIn("## 参照\n- takashima/42_風雷益.md | 風雷益", content)

    def test_assemble_script_replaces_existing_references_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

**本卦（40 雷水解）**

仮置き。

**変爻（3爻）**

仮置き。

**之卦（32 雷風恒）**

仮置き。

## 参照
- old/path.md | 古い参照
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple2.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertEqual(content.count("## 参照"), 1)
            self.assertNotIn("old/path.md", content)
            self.assertIn("- takashima/40_雷水解.md | 雷水解", content)
            self.assertIn("- takashima/32_雷風恒.md | 雷風恒", content)

    def test_assemble_script_removes_normalized_references_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

**本卦（40 雷水解）**

仮置き。

### 本卦解釈

ここに本卦解釈。

**変爻（3爻）**

仮置き。

### 変爻解釈

ここに変爻解釈。

**之卦（32 雷風恒）**

仮置き。

**参照**
- old/path.md | 古い参照
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple2.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertEqual(content.count("## 参照"), 1)
            self.assertNotIn("old/path.md", content)
            self.assertNotIn("**参照**", content)

    def test_assemble_script_injects_ex_simple2_blocks_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

**本卦（40 雷水解）**

仮置き。

### 本卦解釈

ここに本卦解釈。

**変爻（3爻）**

仮置き。

### 変爻解釈

ここに変爻解釈。

**之卦（32 雷風恒）**

仮置き。

## 参照
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple2.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("## 質問文\n\n```text\n"))
            self.assertIn(load_text("fixtures/test_simple2.md").rstrip(), content)
            assert_section_contains_block(self, content, "## 雷水解", load_honka_quotes(40).raw_text, "## 六三")
            assert_section_contains_block(self, content, "## 六三", load_line_quotes(40, "3爻").raw_text, "## 之卦：雷風恒")
            assert_section_contains_block(self, content, "## 之卦：雷風恒", load_honka_quotes(32).raw_text, "## 参照")
            self.assertIn("## 参照", content)
            self.assertIn("- takashima/40_雷水解.md | 雷水解", content)
            self.assertIn("- takashima/32_雷風恒.md | 雷風恒", content)

    def test_assemble_script_injects_ex5_auxiliary_blocks_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

**本卦（5 水天需）**

仮置き。

（参照：takashima_zouho/5_水天需.md|5 水天需）

**互卦（38 火沢睽）**

仮置き。

（参照：takashima_zouho/38_火沢睽.md|38 火沢睽）

**錯卦（35 火地晋）**

仮置き。

（参照：takashima_zouho/35_火地晋.md|35 火地晋）

**綜卦（6 天水訟）**

仮置き。

（参照：takashima_zouho/6_天水訟.md|6 天水訟）

## 参照
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_ex5_noline.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("## 質問文\n\n```text\n"))
            self.assertIn(load_text("fixtures/test_ex5_noline.md").rstrip(), content)
            assert_section_contains_block(self, content, "## 水天需", load_honka_quotes(5).raw_text, "## 互卦：火沢睽")
            self.assertNotIn("## 変爻", content)
            self.assertNotIn("## 之卦", content)
            assert_section_contains_block(self, content, "## 互卦：火沢睽", load_honka_quotes(38).raw_text, "## 錯卦：火地晋")
            assert_section_contains_block(self, content, "## 錯卦：火地晋", load_honka_quotes(35).raw_text, "## 綜卦：天水訟")
            assert_section_contains_block(self, content, "## 綜卦：天水訟", load_honka_quotes(6).raw_text, "## 参照")
            self.assertNotIn("（参照：", content)
            self.assertIn("## 参照", content)
            self.assertIn("- takashima/05_水天需.md | 水天需", content)
            self.assertIn("- takashima/38_火沢睽.md | 火沢睽", content)
            self.assertIn("- takashima/35_火地晋.md | 火地晋", content)
            self.assertIn("- takashima/06_天水訟.md | 天水訟", content)


    def test_assemble_script_injects_question_section_for_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_COMPARE]\n\n### 1. 候補A\n本卦：42風雷益\n変爻：4爻\n\n### 2. 候補B\n本卦：24地雷復\n変爻：初爻\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                """## 質問文

**核心・結論**

仮置き。

**吉凶順位（1位 = 最吉）**

1. 
2. 

### 1位 候補A（42風雷益・4爻）

仮置き。

### 2位 候補B（24地雷復・初爻）

仮置き。

**まとめ**

| 順位 | 候補 | 根拠 |
| --- | --- | --- |

今回のおすすめは、候補Aです。
""" ,
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ASSEMBLE_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("## 質問文\n\n```text\n"))
            self.assertIn(input_path.read_text(encoding="utf-8").rstrip(), content)
            self.assertNotIn("## 参照", content)
            self.assertIn("**核心・結論**", content)

class RawAppendTests(unittest.TestCase):
    def test_build_reference_case_excerpt_section_extracts_matching_line_only(self) -> None:
        excerpt_text = build_reference_case_excerpt_section(40, "3爻")
        self.assertIn("## 占例抜粋", excerpt_text)
        self.assertIn("区長", excerpt_text)
        self.assertNotIn("清国公使館内通事件", excerpt_text)
        self.assertNotIn("商人Ａ", excerpt_text)
        self.assertNotIn("# 41_山沢損 占例抜粋", excerpt_text)

    def test_append_reference_case_excerpt_skips_when_empty(self) -> None:
        with patch.object(append_raw, "build_reference_case_excerpt_section", return_value=""):
            original = "## 高島易断\n\n本文。\n"
            self.assertEqual(append_raw._append_reference_case_excerpt(original, 1, "1爻"), original)

    def test_append_script_appends_reference_case_excerpt_for_ex_simple(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n\n### 3. 占い結果入力\n本卦：1乾為天\n変爻：1爻\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/01_乾為天.md | 乾為天\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 高島易断", content)
            self.assertIn("## 占例抜粋", content)
            self.assertNotIn("### 初九", content)
            self.assertIn("ある貴人の運氣", content)
            self.assertNotIn("養子", content)
            self.assertLess(content.index("## 高島易断"), content.index("## 占例抜粋"))

    def test_append_script_appends_reference_case_excerpt_for_ex_simple2_current_line_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/40_雷水解.md | 雷水解\n- takashima/32_雷風恒.md | 雷風恒\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple2.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 占例抜粋", content)
            self.assertIn("区長", content)
            self.assertNotIn("清国公使館内通事件", content)
            self.assertNotIn("商人Ａ", content)

    def test_append_script_rejects_missing_answer_file_with_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "missing.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(f"answer file not found: {output_path}", result.stderr)

    def test_build_ex_simple_raw_text_contains_honka_and_line(self) -> None:
        path = REPO_ROOT / "assets" / "takashima" / "20_風地観.md"
        raw_text = build_ex_simple_takashima_raw_text(path, "5爻")
        self.assertIn("## 高島易断", raw_text)
        self.assertIn("### 風地観", raw_text)
        self.assertIn("#### 卦辞", raw_text)
        self.assertIn("#### 彖伝", raw_text)
        self.assertIn("#### 大象伝", raw_text)
        self.assertIn("### 爻辞と小象伝（九五）", raw_text)
        self.assertIn("風は目視できないが、草木が撓(たわ)むのを見て風があることを知る。", raw_text)
        self.assertIn("九五は尊位に居るから天下の人物を総括するのは、自分一身に在る。", raw_text)
        self.assertNotIn('title: "高島易断 解釈 20 風地観"', raw_text)
        self.assertNotIn("includes:", raw_text)
        self.assertNotIn("hexagram_title:", raw_text)
        self.assertNotIn("#### 初爻", raw_text)
        self.assertNotIn("#### 2爻", raw_text)
        self.assertNotIn("#### 3爻", raw_text)
        self.assertNotIn("#### 4爻", raw_text)
        self.assertNotIn("#### 上爻", raw_text)

    def test_all_takashima_assets_remain_extractable(self) -> None:
        assets_dir = REPO_ROOT / "assets" / "takashima"
        for path in sorted(assets_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertIn("### 本卦解釈", text, path.name)
            self.assertIn("### 変爻解釈", text, path.name)
            honka = load_takashima_honka_text(path)
            self.assertTrue(honka["kaji"].strip(), path.name)
            self.assertTrue(honka["tanden"].strip(), path.name)
            self.assertTrue(honka["taisho"].strip(), path.name)

            line_section = text.split("### 変爻解釈", 1)[1]
            self.assertEqual(len(re.findall(r"(?m)^####\s+(?!用[九六])", line_section)), 6, path.name)
            for line_label in line_labels_from_numbers([1, 2, 3, 4, 5, 6]):
                line_text = load_takashima_line_text(path, line_label)
                self.assertTrue(line_text.strip(), f"{path.name} line {line_label}")

            post_honka = text.split("### 本卦解釈", 1)[1]
            self.assertNotIn("\nnumber:", post_honka, path.name)
            self.assertNotIn("\ntitle:", post_honka, path.name)
            self.assertNotIn("\nyomi:", post_honka, path.name)

    def test_append_script_appends_raw_section_for_ex_simple(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/42_風雷益.md | 風雷益\n", encoding="utf-8")
            result = subprocess.run(
                    [
                        sys.executable,
                        str(APPEND_SCRIPT),
                        "--input",
                        str(REPO_ROOT / "fixtures" / "test_simple.md"),
                        "--output",
                        str(output_path),
                    ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 参照\n- takashima/42_風雷益.md | 風雷益", content)
            self.assertIn("## 高島易断", content)
            self.assertIn("### 風雷益", content)
            self.assertIn("### 爻辞と小象伝（九五）", content)

    def test_append_script_leaves_two_blank_lines_before_takashima_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n\n### 3. 占い結果入力\n本卦：14火天大有\n変爻：2爻\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text(
                "## 参照\n- takashima/14_火天大有.md | 火天大有\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 参照\n- takashima/14_火天大有.md | 火天大有\n\n\n## 高島易断", content)
            self.assertIn("### 爻辞と小象伝（九二）", content)

    def test_append_script_rejects_ex_simple_without_changing_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_SIMPLE]\n\n### 3. 占い結果入力\n本卦：5水天需\n変爻：なし\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/05_水天需.md | 水天需\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                    text=True,
                )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("EX_SIMPLE requires at least one changing line", result.stderr)

    def test_build_ex5_raw_text_contains_all_sections(self) -> None:
        raw_text = build_ex_5_takashima_raw_text(
            main_path=REPO_ROOT / "assets" / "takashima" / "34_雷天大壮.md",
            main_heading_suffix="（34 雷天大壮）",
            line_labels=["3爻"],
            zhigua_path=REPO_ROOT / "assets" / "takashima" / "54_雷沢帰妹.md",
            zhigua_heading_suffix="（54 雷沢帰妹）",
            auxiliary_items=[
                ("互卦", REPO_ROOT / "assets" / "takashima" / "43_沢天夬.md", "（43 沢天夬）"),
                ("錯卦", REPO_ROOT / "assets" / "takashima" / "20_風地観.md", "（20 風地観）"),
                ("綜卦", REPO_ROOT / "assets" / "takashima" / "33_天山遯.md", "（33 天山遯）"),
            ],
        )
        self.assertIn("## 高島易断", raw_text)
        self.assertIn("### 雷天大壮", raw_text)
        self.assertIn("### 爻辞と小象伝（九三）", raw_text)
        self.assertIn("### 之卦（54 雷沢帰妹）", raw_text)
        self.assertIn("### 互卦（43 沢天夬）", raw_text)
        self.assertIn("### 錯卦（20 風地観）", raw_text)
        self.assertIn("### 綜卦（33 天山遯）", raw_text)

    def test_build_ex5_raw_text_contains_multiple_line_sections(self) -> None:
        raw_text = build_ex_5_takashima_raw_text(
            main_path=REPO_ROOT / "assets" / "takashima" / "34_雷天大壮.md",
            main_heading_suffix="（34 雷天大壮）",
            line_labels=["2爻", "3爻"],
            zhigua_path=REPO_ROOT / "assets" / "takashima" / "54_雷沢帰妹.md",
            zhigua_heading_suffix="（54 雷沢帰妹）",
            auxiliary_items=[],
        )
        self.assertIn("### 爻辞と小象伝（九二）", raw_text)
        self.assertIn("### 爻辞と小象伝（九三）", raw_text)

    def test_append_script_omits_reference_case_excerpt_for_multiple_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            input_path.write_text(
                "[MODE:EXTRACT]\n[TEMPLATE:EX_5]\n\n### 1. 占いに至った背景・状況\n状況。\n\n### 2. 易経への質問\nどうすべきか。\n\n### 3. 占い結果入力\n本卦：34雷天大壮\n変爻：2爻 3爻\n之卦：54雷沢帰妹\n互卦：43沢天夬\n錯卦：20風地観\n綜卦：33天山遯\n",
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/34_雷天大壮.md | 雷天大壮\n- takashima/54_雷沢帰妹.md | 雷沢帰妹\n- takashima/43_沢天夬.md | 沢天夬\n- takashima/20_風地観.md | 風地観\n- takashima/33_天山遯.md | 天山遯\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("### 爻辞と小象伝（九二）", content)
            self.assertIn("### 爻辞と小象伝（九三）", content)
            self.assertNotIn("## 占例抜粋", content)

    def test_build_ex_simple2_raw_text_contains_honka_line_and_zhigua(self) -> None:
        raw_text = build_ex_simple2_takashima_raw_text(
            main_path=REPO_ROOT / "assets" / "takashima" / "40_雷水解.md",
            line_label="3爻",
            zhigua_path=REPO_ROOT / "assets" / "takashima" / "32_雷風恒.md",
            zhigua_heading_suffix="（32 雷風恒）",
        )
        self.assertIn("## 高島易断", raw_text)
        self.assertIn("### 雷水解", raw_text)
        self.assertIn("### 爻辞と小象伝（六三）", raw_text)
        self.assertIn("### 之卦（32 雷風恒）", raw_text)
        self.assertNotIn("### 互卦（", raw_text)

    def test_append_script_appends_raw_section_for_ex5(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/40_雷水解.md | 雷水解\n- takashima/32_雷風恒.md | 雷風恒\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_ex5.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 高島易断", content)
            self.assertIn("### 雷天大壮", content)
            self.assertIn("### 爻辞と小象伝（九三）", content)
            self.assertIn("### 之卦（54 雷沢帰妹）", content)
            self.assertIn("### 互卦（43 沢天夬）", content)
            self.assertIn("### 錯卦（20 風地観）", content)
            self.assertIn("### 綜卦（33 天山遯）", content)

    def test_append_script_appends_raw_section_for_ex_simple2(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/05_水天需.md | 水天需\n- takashima/38_火沢睽.md | 火沢睽\n- takashima/35_火地晋.md | 火地晋\n- takashima/06_天水訟.md | 天水訟\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_simple2.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 高島易断", content)
            self.assertIn("### 雷水解", content)
            self.assertIn("### 爻辞と小象伝（六三）", content)
            self.assertIn("### 之卦（32 雷風恒）", content)
            self.assertNotIn("### 互卦（", content)
            self.assertNotIn("### 錯卦（", content)
            self.assertNotIn("### 綜卦（", content)

    def test_append_script_appends_raw_section_for_ex5_without_line_and_zhigua(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## 参照\n- takashima/05_水天需.md | 水天需\n- takashima/38_火沢睽.md | 火沢睽\n- takashima/35_火地晋.md | 火地晋\n- takashima/06_天水訟.md | 天水訟\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_ex5_noline.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("## 高島易断", content)
            self.assertIn("### 水天需", content)
            self.assertIn("### 互卦（38 火沢睽）", content)
            self.assertIn("### 錯卦（35 火地晋）", content)
            self.assertIn("### 綜卦（6 天水訟）", content)
            self.assertNotIn("### 爻辞と小象伝（", content)
            self.assertNotIn("### 之卦（", content)

    def test_append_script_rejects_ex_compare(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "answer.md"
            output_path.write_text("## まとめ\n\nここに回答。\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPEND_SCRIPT),
                    "--input",
                    str(REPO_ROOT / "fixtures" / "test_compare.md"),
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("not supported for EX_COMPARE", result.stderr)


if __name__ == "__main__":
    unittest.main()
