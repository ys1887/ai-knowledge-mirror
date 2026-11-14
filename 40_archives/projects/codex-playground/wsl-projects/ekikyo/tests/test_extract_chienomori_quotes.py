from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "extract_chienomori_quotes.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from extract_chienomori_quotes import build_combined_output, build_honka_output, build_koji_output, load_documents  # noqa: E402


def _write_source(path: Path, title: str, body: str) -> None:
    normalized_body = textwrap.dedent(body).strip()
    text = "\n".join(
        [
            "---",
            f"title: {title}",
            "number: 1",
            "tags:",
            "  - 易経",
            f"  - {title}",
            "---",
            normalized_body,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


class ExtractChienomoriQuotesTests(unittest.TestCase):
    def test_build_outputs_keep_only_quote_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir)
            _write_source(
                source_dir / "01.乾為天.md",
                "乾為天",
                """

                ## キーワード
                - 偉大なる天

                ## 序卦伝
                > 不要1
                > 不要2

                ## 卦辞
                > 乾。元亨。利貞。
                > 乾は、元いに亨る。貞しきに利ろし。
                - 解説

                ## 彖伝
                > 彖曰、大哉乾元。
                > 彖に曰く、大なるかな乾元。
                - 解説

                ## 大象伝
                > 象曰、天行健。
                > 象に曰く、天行は健なり。
                - 解説

                ## 爻辞
                ### 初九
                > 初九。潜龍。勿用。
                > 初九。潜龍。用うる勿れ。
                - 解説

                #### 小象伝
                > 潜龍勿用、陽在下也。
                > 潜龍用うる勿れとは、陽にして下に在ればなり。
                - 解説

                ### 用九
                > 用九。見羣龍无首。吉。
                > 用九。群龍首无きを見る。吉。
                - 解説

                #### 小象伝
                > 用九、天徳不可爲首也。
                > 用九は、天徳は首たるべからざるなり。
                - 解説

                ## 文言伝
                > 不要3
                > 不要4
                """,
            )
            for number in range(2, 65):
                _write_source(
                    source_dir / f"{number:02d}.仮卦{number}.md",
                    f"仮卦{number}",
                    """

                    ## 卦辞
                    > 卦辞原文
                    > 卦辞読み

                    ## 彖伝
                    > 彖伝原文
                    > 彖伝読み

                    ## 大象伝
                    > 大象原文
                    > 大象読み

                    ## 爻辞
                    ### 初九
                    > 爻辞原文
                    > 爻辞読み

                    #### 小象伝
                    > 小象原文
                    > 小象読み
                    """,
                )

            documents = load_documents(source_dir)
            honka = build_honka_output(documents)
            koji = build_koji_output(documents)
            combined = build_combined_output(documents)

        self.assertIn("## 1 乾為天\n\n### 卦辞\n\n> 乾。元亨。利貞。\n> 乾は、元いに亨る。貞しきに利ろし。", honka)
        self.assertNotIn("## 序卦伝", honka)
        self.assertNotIn("## 文言伝", honka)
        self.assertNotIn("- 解説", honka)

        self.assertIn("### 初九\n\n> 初九。潜龍。勿用。\n> 初九。潜龍。用うる勿れ。", koji)
        self.assertIn("### 用九\n\n> 用九。見羣龍无首。吉。\n> 用九。群龍首无きを見る。吉。", koji)
        self.assertIn("#### 小象伝\n\n> 用九、天徳不可爲首也。\n> 用九は、天徳は首たるべからざるなり。", koji)
        self.assertNotIn("文言伝", koji)
        self.assertNotIn("- 解説", koji)

        self.assertIn("## 1 乾為天\n\n### 本卦\n\n#### 卦辞", combined)
        self.assertIn("#### 大象伝\n\n> 象曰、天行健。", combined)
        self.assertIn("### 爻辞\n\n#### 初九", combined)
        self.assertIn("##### 小象伝\n\n> 潜龍勿用、陽在下也。", combined)
        self.assertNotIn("序卦伝", combined)
        self.assertNotIn("文言伝", combined)

    def test_cli_writes_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            source_dir.mkdir()
            for number in range(1, 65):
                _write_source(
                    source_dir / f"{number:02d}.仮卦{number}.md",
                    f"仮卦{number}",
                    """

                    ## 卦辞
                    > 卦辞原文
                    > 卦辞読み

                    ## 彖伝
                    > 彖伝原文
                    > 彖伝読み

                    ## 大象伝
                    > 大象原文
                    > 大象読み

                    ## 爻辞
                    ### 初九
                    > 爻辞原文
                    > 爻辞読み

                    #### 小象伝
                    > 小象原文
                    > 小象読み
                    """,
                )
            honka_output = Path(tmpdir) / "honka.md"
            koji_output = Path(tmpdir) / "koji.md"
            combined_output = Path(tmpdir) / "combined.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source-dir",
                    str(source_dir),
                    "--honka-output",
                    str(honka_output),
                    "--koji-output",
                    str(koji_output),
                    "--combined-output",
                    str(combined_output),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            honka_text = honka_output.read_text(encoding="utf-8") if honka_output.exists() else ""
            koji_text = koji_output.read_text(encoding="utf-8") if koji_output.exists() else ""
            combined_text = combined_output.read_text(encoding="utf-8") if combined_output.exists() else ""

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(honka_output.exists())
            self.assertTrue(koji_output.exists())
            self.assertTrue(combined_output.exists())
            self.assertIn("## 1 仮卦1", honka_text)
            self.assertIn("### 初九", koji_text)
            self.assertIn("### 本卦", combined_text)
            self.assertIn("### 爻辞", combined_text)
