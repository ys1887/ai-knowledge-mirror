from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STRUCTURE_SOURCE = Path("/home/ys/projects/ekikyo/work/高島_本卦爻辞.md")
HONKA_SOURCE = Path("/home/ys/projects/ekikyo/work/高島_本卦彖伝大象伝.md")
TARGET_OUTPUT = Path("/home/ys/projects/ekikyo/work/高島_本卦爻辞_3行版.md")
FULL_WITH_RUBY = Path("/home/ys/projects/ekikyo/work/高島_全部.md")
HONDA_SOURCE_DIR = Path(
    "/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/180_易経_Clip編集/182_龍青三_本田濟"
)
CHIENOMORI_SOURCE_DIR = Path(
    "/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/180_易経_Clip編集/183_知恵の森"
)

KANJI_RE = re.compile(r"[一-龯々〆ヶ]")
PAREN_RUBY_RE = re.compile(r"([一-龯々〆ヶ]+)（([ぁ-んァ-ンゔゞ゛゜ー]+)）")
HONDA_RUBY_RE = re.compile(r"([一-龯々〆ヶ]+)\s+([ぁ-んァ-ンゔゞー]+)")
PAIR_LINE_RE = re.compile(r"^> ")


VARIANT_CHARS = {
    "德": "徳",
    "无": "無",
    "變": "変",
    "傳": "伝",
    "說": "説",
    "觀": "観",
    "國": "国",
    "對": "対",
    "晉": "晋",
    "晝": "昼",
    "爲": "為",
    "隨": "随",
    "從": "従",
    "號": "号",
    "戰": "戦",
    "數": "数",
    "處": "処",
    "顯": "顕",
    "豫": "予",
    "歸": "帰",
    "黃": "黄",
    "沒": "没",
    "擧": "挙",
    "應": "応",
    "與": "与",
}


PHRASE_OVERRIDES = {
    "君子": "くんし",
    "坤": "こん",
    "蒙": "もう",
    "蠱": "こ",
    "臨": "りん",
    "蹇": "けん",
    "解": "かい",
    "震": "しん",
    "西南": "せいなん",
    "東北": "とうほく",
    "甲": "こう",
    "再三": "さいさん",
    "三日": "みっか",
    "迷": "まよ",
    "驚": "おどろ",
    "百里": "ひゃくり",
    "悔い": "くい",
    "動は": "うごきは",
    "習わ": "ならわ",
    "在り": "あり",
    "有り": "あり",
    "有る": "ある",
    "德": "とく",
    "徳": "とく",
    "无": "な",
    "無": "な",
    "陽": "よう",
    "陰": "いん",
    "人": "ひと",
    "位": "くらい",
    "見": "み",
    "求": "もと",
    "厚": "あつ",
    "喜": "よろこ",
    "知": "ち",
    "始": "はじ",
    "至": "いた",
    "刑": "けい",
    "雨": "あめ",
    "思": "おも",
    "身": "み",
    "牛": "うし",
    "含": "ふく",
    "法": "のり",
    "必": "かなら",
    "門": "もん",
    "多": "おお",
    "死": "し",
    "教": "おし",
    "照": "てら",
    "立": "た",
    "制": "せい",
    "登": "のぼ",
    "待": "ま",
    "聞": "き",
    "鹿": "しか",
    "泉": "いずみ",
    "雲": "くも",
    "親": "した",
    "顕": "あら",
    "顯": "あら",
    "逆": "さか",
    "皆": "みな",
    "泰": "たい",
    "戰": "たたか",
    "戦": "たたか",
    "損": "そん",
    "反復": "はんぷく",
    "進": "すす",
    "直": "ちょく",
    "十年": "じゅうねん",
    "勿": "なか",
    "可": "べ",
    "處": "お",
    "処": "お",
    "建": "た",
    "引": "ひ",
    "足": "あし",
    "遠": "とお",
    "及": "およ",
    "同": "おな",
    "慶": "よろこ",
}


LONG_SURFACE_ALLOWLIST = {
    "其夷主",
    "其資斧",
    "凶如何",
    "初九虞",
    "剛柔接",
    "剛柔節",
    "剛柔際",
    "天地際",
    "六四元吉",
    "前言往行",
    "君子豹変",
    "大人虎変",
    "家人嗃嗃",
    "飲食宴楽",
    "飲食衎衎",
    "黄裳元吉",
}


LINE_OVERRIDES = {
    "象曰、抜茅、征吉、志在外也。": "ちがやをぬくゆきてきつとは、こころざしそとにあればなり。",
    "象曰、抜茅、貞吉、志在君也。": "ちがやをぬく、ていなればきつとは、こころざしきみにあるなり。",
    "象曰、雷出地奮豫。先王以作樂崇德、殷薦之上帝、以配祖考。": "かみなりのちをいでてふるうはよなり。せんのうもってがくをつくりとくをたっとび、これをじょうていにいんせんし、もってそこうをはいす。",
    "象曰、幹母之蠱、得中道也。": "ははのこにかんたりとは、ちゅうどうをうるなり。",
    "象曰、澤上有地臨。君子以教思无窮、容保民无疆。": "さわのうえにちあるはりんなり。くんしもっておしえおもうこときわまりなく、たみをいれやすんずることかぎりなし。",
    "象曰、噬膚滅鼻、乘剛也。": "ふをかみてはなをめっすとは、ごうにのずればなり。",
    "象曰、遇毒、位不當也。": "どくにあうとは、くらいあたらざればなり。",
    "象曰、舎車而徒、義弗乘也。": "くるまをすててとすとは、ぎとしてのらざるなり。",
    "象曰、白賁、无咎、上得志也。": "しろくかざる、とがなしとは、うえ、こころざしをうるなり。",
    "象曰、剝牀以膚、切近災也。": "しょうをはくするにはだえをもってすとは、せつにわざわいにちかきなり。",
    "象曰、迷復之凶、反君道也。": "かえるにまようのきょうは、くんどうにはんすればなり。",
    "象曰、天下雷行、物與无妄。先王以茂對時育萬物。": "てんのしたにかみなりゆき、ものみなむぼうなり。せんのうもってつとめてときにたいして、ばんぶつをやしなう。",
    "象曰、山下有雷頤。君子以愼言語、節飲食。": "やまのしたにかみなりあるはいなり。くんしもってげんごをつつしみ、いんしょくをせつす。",
    "象曰、澤滅木大過。君子以獨立不懼、世遯无悶。": "さわ、きをめっするは、たいかなり。くんしもってどくりつしておそれず、よをのがれてもだゆるなし。",
    "象曰、樽酒簋貳、剛柔際也。": "そんしゅきそふとは、ごうじゅうまじわるなり。",
    "象曰、恆浚之凶、始求深也。": "つねをふかくするのきょうは、はじめにもとむることふかければなり。",
    "象曰、婦人貞吉、從一而終也。夫子制義、從婦凶也。": "ふじんはていにしてきつとは、いちにしたがっておわればなり。ふうしはぎをせいす。ふにしたがうはきょうなるなり。",
    "象曰、雷在天上大壯。君子以非禮弗履。": "かみなり、てんのうえにあるはたいそうなり。くんしもってれいにあらざればふまず。",
    "象曰、南狩之志、乃得大也。": "みなみにかりすのこころざし、すなわちおおいにうるなり。",
    "象曰、王假有家、交相愛也。": "おう、ゆうかにいたるとは、こもごもあいあいするなり。",
    "象曰、澤上於地萃。君子以除戎器、戒不虞。": "さわ、ちにのぼるはすいなり。くんしもってじゅうきをおさめ、ふぐをいましむ。",
    "象曰、上火下澤睽。君子以同而異。": "うえはひ、したはさわなるはけいなり。くんしもっておなじくしてことなる。",
    "象曰、雷雨作解。君子以赦過宥罪。": "らいうおこるはかいなり。くんしもってあやまちをゆるしつみをなだむ。",
    "象曰、有孚惠心、勿問之矣。惠我德、大得志也。": "まことありけいしんあるは、これをとうなかれ。わがとくをめぐみとするは、おおいにこころざしをうるなり。",
    "象曰、據于蒺藜、乘剛也。入于其宮、不見其妻、不祥也。": "しつれいによるとは、ごうにのるなり。そのきゅうにはいり、そのつまをみずとは、ふしょうなるなり。",
    "象曰、震來虩虩、恐致福也。笑言啞啞、後有則也。": "しんきたるときげきげきたりとは、おそれてふくをいたすなり。しょうげんあくあくたりとは、のちにのりあるなり。",
    "象曰、山上有木漸。君子以居賢德善俗。": "やまのうえにきあるはぜんなり。くんしもってけんとくにおりぞくをよくす。",
    "象曰、其羽可用爲儀、吉、不可亂也。": "そのははもってぎとなすべし、きつとは、みだるべからざるなり。",
    "象曰、帝乙歸妹、不如其娣之袂良也。其位在中、以貴行也。": "ていおつ、いもうとをとつがす、そのていにたもとのよきにしかざるなり。そのくらい、ちゅうにあり、たっときをもってゆくなり。",
    "象曰、馬匹亡、絶類上也。": "ばひつほろぶとは、るいをたちてのぼるなり。",
    "象曰、水在火上、既濟。君子以思患而豫防之。": "みず、ひのうえにあるはきせいなり。くんしもってうれいをおもうてあらかじめこれをふせぐ。",
    "象曰、三年克之、憊也。": "みとせにしてこれにかつとは、つかるるなり。",
    "象曰、東鄰殺牛、不如西鄰之時也。實受其福、吉大來也。": "とうりんにうしをころすは、せいりんのときなるにしかざるなり。じつにそのさいわいをうくとは、きつおおいにきたるなり。",
    "象曰、飲酒濡首、亦不知節也。": "さけをのみこうべをぬらすは、また、せつをしらざるなり。",
}


@dataclass(frozen=True)
class QuotePair:
    original: str
    reading: str


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a 3-line Takashima honka/koji file with hiragana readings.")
    parser.add_argument("--input", type=Path, default=STRUCTURE_SOURCE, help="Structure markdown file.")
    parser.add_argument("--output", type=Path, default=TARGET_OUTPUT, help="Output markdown file.")
    parser.add_argument("--check-only", action="store_true", help="Validate conversion without writing the output file.")
    return parser.parse_args(argv)


def normalize_text(text: str) -> str:
    return "".join(VARIANT_CHARS.get(ch, ch) for ch in text)


def kata_to_hira(text: str) -> str:
    chars: list[str] = []
    for ch in text:
        if "ァ" <= ch <= "ヶ":
            chars.append(chr(ord(ch) - 0x60))
        else:
            chars.append(ch)
    return "".join(chars)


def remove_parenthetical_ruby(text: str) -> str:
    return re.sub(r"（[^）]*）", "", text)


def extract_quote_pairs(path: Path) -> list[QuotePair]:
    lines = path.read_text(encoding="utf-8").splitlines()
    pairs: list[QuotePair] = []
    for index, line in enumerate(lines[:-1]):
        if PAIR_LINE_RE.match(line) and PAIR_LINE_RE.match(lines[index + 1]):
            pairs.append(QuotePair(original=line[2:], reading=lines[index + 1][2:]))
    return pairs


def build_reference_map(path: Path) -> dict[str, QuotePair]:
    mapping: dict[str, QuotePair] = {}
    for pair in extract_quote_pairs(path):
        mapping[pair.original] = pair
    return mapping


def build_first_pair_by_heading(path: Path) -> dict[str, QuotePair]:
    lines = path.read_text(encoding="utf-8").splitlines()
    mapping: dict[str, QuotePair] = {}
    current_heading: str | None = None
    seen_pair = False
    for index, line in enumerate(lines):
        if line.startswith("## "):
            current_heading = line[3:]
            seen_pair = False
            continue
        if current_heading is None or seen_pair:
            continue
        if index + 1 >= len(lines):
            continue
        if line.startswith("> ") and lines[index + 1].startswith("> "):
            mapping[current_heading] = QuotePair(original=line[2:], reading=lines[index + 1][2:])
            seen_pair = True
    return mapping


def build_directory_reference_map(source_dir: Path) -> dict[str, QuotePair]:
    mapping: dict[str, QuotePair] = {}
    for path in sorted(source_dir.glob("*.md")):
        for pair in extract_quote_pairs(path):
            mapping.setdefault(pair.original, pair)
    return mapping


def build_phrase_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for source in (STRUCTURE_SOURCE, HONKA_SOURCE, FULL_WITH_RUBY):
        text = source.read_text(encoding="utf-8")
        for match in PAREN_RUBY_RE.finditer(text):
            surface = match.group(1)
            if len(surface) > 2 and surface not in LONG_SURFACE_ALLOWLIST:
                continue
            reading = kata_to_hira(match.group(2))
            mapping[surface] = reading
            mapping[normalize_text(surface)] = reading

    for path in sorted(HONDA_SOURCE_DIR.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("> "):
                continue
            for match in HONDA_RUBY_RE.finditer(line[2:]):
                surface = match.group(1)
                if len(surface) > 2:
                    continue
                reading = kata_to_hira(match.group(2))
                mapping.setdefault(surface, reading)
                mapping.setdefault(normalize_text(surface), reading)

    for surface, reading in PHRASE_OVERRIDES.items():
        mapping.setdefault(surface, reading)
        mapping.setdefault(normalize_text(surface), reading)

    return mapping


def transliterate_line(text: str, phrase_map: dict[str, str]) -> str:
    def replace_explicit(match: re.Match[str]) -> str:
        surface = match.group(1)
        if len(surface) <= 2 or surface in LONG_SURFACE_ALLOWLIST:
            return kata_to_hira(match.group(2))
        return surface

    cleaned = PAREN_RUBY_RE.sub(replace_explicit, text)
    keys = sorted(phrase_map, key=len, reverse=True)
    output: list[str] = []
    index = 0
    while index < len(cleaned):
        matched = None
        for key in keys:
            candidate = cleaned[index : index + len(key)]
            if candidate == key or normalize_text(candidate) == normalize_text(key):
                matched = key
                break
        if matched is not None:
            output.append(phrase_map[matched])
            index += len(matched)
            continue
        ch = cleaned[index]
        if "ァ" <= ch <= "ヶ":
            output.append(chr(ord(ch) - 0x60))
        else:
            output.append(ch)
        index += 1
    return "".join(output)


def build_output_text(source_path: Path) -> str:
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    honka_reference = build_first_pair_by_heading(HONKA_SOURCE)
    chienomori_reference = build_directory_reference_map(CHIENOMORI_SOURCE_DIR)
    phrase_map = build_phrase_map()

    output_lines: list[str] = []
    unresolved: list[str] = []
    line_number = 0
    current_heading: str | None = None
    replace_next_pair = False
    while line_number < len(source_lines):
        line = source_lines[line_number]
        if line.startswith("## "):
            current_heading = line[3:]
            output_lines.append(line)
            line_number += 1
            continue
        if line.startswith("### 本卦"):
            output_lines.append(line)
            replace_next_pair = True
            line_number += 1
            continue
        if (
            line.startswith("> ")
            and line_number + 1 < len(source_lines)
            and source_lines[line_number + 1].startswith("> ")
        ):
            if replace_next_pair:
                if current_heading is None or current_heading not in honka_reference:
                    raise ValueError(f"missing honka reference for heading: {current_heading!r}")
                pair = honka_reference[current_heading]
                replace_next_pair = False
            else:
                pair = QuotePair(original=line[2:], reading=source_lines[line_number + 1][2:])
            clean_reading = remove_parenthetical_ruby(pair.reading)
            if pair.original in LINE_OVERRIDES:
                hiragana = LINE_OVERRIDES[pair.original]
            else:
                reference_pair = chienomori_reference.get(pair.original)
                reference_reading = reference_pair.reading if reference_pair is not None else pair.reading
                hiragana = transliterate_line(reference_reading, phrase_map)
            if KANJI_RE.search(hiragana):
                unresolved.append(f"{pair.original} -> {hiragana}")
            output_lines.append(f"> {pair.original}")
            output_lines.append(f"> {clean_reading}")
            output_lines.append(f"> {hiragana}")
            line_number += 2
            continue
        output_lines.append(line)
        line_number += 1

    if unresolved:
        unresolved_text = "\n".join(unresolved[:50])
        raise ValueError(f"unresolved kanji remain in generated hiragana lines:\n{unresolved_text}")
    return "\n".join(output_lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    output_text = build_output_text(args.input)
    if not args.check_only:
        args.output.write_text(output_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI guard
        print(str(exc), file=sys.stderr)
        raise
