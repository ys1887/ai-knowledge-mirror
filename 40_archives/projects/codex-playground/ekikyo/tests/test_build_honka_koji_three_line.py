from __future__ import annotations

import sys
import unittest
import tempfile
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPT_DIR))

import build_honka_koji_three_line as module  # noqa: E402

from build_honka_koji_three_line import (  # noqa: E402
    build_first_pair_by_heading,
    remove_parenthetical_ruby,
    transliterate_line,
)


class BuildHonkaKojiThreeLineTests(unittest.TestCase):
    def test_remove_parenthetical_ruby_keeps_base_text(self) -> None:
        self.assertEqual(
            remove_parenthetical_ruby("天行（てんこう）は健（けん）。君子以（もっ）て自強（じきょう）して息（や）まず。"),
            "天行は健。君子以て自強して息まず。",
        )

    def test_transliterate_line_uses_phrase_map(self) -> None:
        phrase_map = {
            "天行": "てんこう",
            "健": "けん",
            "以": "もっ",
            "自強": "じきょう",
            "息": "や",
            "君子": "くんし",
        }
        self.assertEqual(
            transliterate_line("天行（てんこう）は健（けん）。君子以（もっ）て自強（じきょう）して息（や）まず。", phrase_map),
            "てんこうはけん。くんしもってじきょうしてやまず。",
        )

    def test_transliterate_line_keeps_prefix_before_long_ruby_surface(self) -> None:
        phrase_map = {
            "君子": "くんし",
            "以": "もっ",
            "地勢": "ちせい",
            "坤": "こん",
            "德": "とく",
            "厚": "あつ",
            "載": "の",
            "物": "もの",
        }
        self.assertEqual(
            transliterate_line("地勢（ちせい）は坤（こん）なり。君子以（もっ）て德を厚くし物を載（の）す。", phrase_map),
            "ちせいはこんなり。くんしもってとくをあつくしものをのす。",
        )

    def test_build_first_pair_by_heading_uses_first_pair_after_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "honka.md"
            source_path.write_text(
                "\n".join(
                    [
                        "## 1 乾為天",
                        "",
                        "> 乾、元亨利貞。",
                        "> 乾（けん）は元（おお）いに亨（とお）りて、貞（ただ）しきに利（よろ）し。",
                        "",
                        "> 象曰、天行健。君子以自彊不息。",
                        "> 天行（てんこう）は健（けん）。君子以（もっ）て自強（じきょう）して息（や）まず。",
                        "",
                        "## 2 坤為地",
                        "",
                        "> 坤、元亨。",
                        "> 坤（こん）は元（おお）いに亨（とお）る。",
                    ]
                ),
                encoding="utf-8",
            )
            mapping = build_first_pair_by_heading(source_path)
            self.assertEqual(mapping["1 乾為天"].original, "乾、元亨利貞。")
            self.assertEqual(mapping["1 乾為天"].reading, "乾（けん）は元（おお）いに亨（とお）りて、貞（ただ）しきに利（よろ）し。")
            self.assertEqual(mapping["2 坤為地"].original, "坤、元亨。")

    def test_build_output_text_uses_honka_reference_for_boku(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            structure_path = tmpdir_path / "structure.md"
            honka_path = tmpdir_path / "honka.md"
            full_path = tmpdir_path / "full.md"
            empty_dir = tmpdir_path / "empty"
            empty_dir.mkdir()

            structure_path.write_text(
                "\n".join(
                    [
                        "## 1 乾為天",
                        "",
                        "### 本卦",
                        "",
                        "> 象曰、天行健。君子以自彊不息。",
                        "> 天行（てんこう）は健（けん）。君子以（もっ）て自強（じきょう）して息（や）まず。",
                        "",
                        "### 爻辞",
                        "",
                        "#### 初九",
                        "",
                        "> 潜龍勿用、陽在下也。",
                        "> 潜龍（せんりゅう）用うる勿れとは、陽にして下に在ればなり。",
                    ]
                ),
                encoding="utf-8",
            )
            honka_path.write_text(
                "\n".join(
                    [
                        "## 1 乾為天",
                        "",
                        "> 乾、元亨利貞。",
                        "> 乾（けん）は元（おお）いに亨（とお）りて、貞（ただ）しきに利（よろ）し。",
                    ]
                ),
                encoding="utf-8",
            )
            full_path.write_text("", encoding="utf-8")

            with mock.patch.object(module, "STRUCTURE_SOURCE", structure_path), mock.patch.object(
                module, "HONKA_SOURCE", honka_path
            ), mock.patch.object(module, "FULL_WITH_RUBY", full_path), mock.patch.object(
                module, "CHIENOMORI_SOURCE_DIR", empty_dir
            ):
                output = module.build_output_text(structure_path)

            self.assertIn("> 乾、元亨利貞。", output)
            self.assertIn("> 乾は元いに亨りて、貞しきに利し。", output)
            self.assertIn("> けんはおおいにとおりて、ただしきによろし。", output)
            self.assertIn("> 潜龍勿用、陽在下也。", output)


if __name__ == "__main__":
    unittest.main()
