#!/usr/bin/env python3
"""
Book OCR + linebreak restoration + furigana normalization to one Markdown file.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Sequence


API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_PAGE_SEPARATOR = "---"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_MODEL_MAP = {
    "flash": "gemini-3-flash-preview",
    "thinking": "gemini-3-flash-preview",
    "pro": "gemini-3-pro-preview",
}
MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".pdf": "application/pdf",
}
JP_END_PUNCT = set("。！？")
ANNOTATION_PREFIXES = ("〇", "○", "●", "※")
KANJI_RE = r"[一-龯々〆ヶ]"
HIRAGANA_RE = r"[ぁ-ゖー]"


def natural_key(path: Path) -> List[object]:
    parts = re.split(r"(\d+)", path.name)
    key: List[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def ensure_text_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def get_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return api_key


def resolve_model_id(profile: str) -> str:
    env_key = {
        "flash": "PDF2MD_MODEL_FLASH",
        "thinking": "PDF2MD_MODEL_THINKING",
        "pro": "PDF2MD_MODEL_PRO",
    }[profile]
    return os.environ.get(env_key, DEFAULT_MODEL_MAP[profile])


def list_input_files(path: Path) -> List[Path]:
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported input extension: {path.suffix}")
        return [path]
    if not path.is_dir():
        raise ValueError(f"Input path does not exist: {path}")

    files = [p for p in path.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    files.sort(key=natural_key)
    return files


def build_book_prompt(writing_mode: str, page_separator: str, furigana_mode: str) -> str:
    furigana_rule = (
        "6) ふりがなが本文に混入する場合、可能であれば 漢字（かな） 形式で表す。\n"
        if furigana_mode != "none"
        else "6) ふりがなを推測補完しない。本文にない読みを挿入しない。原文にない括弧補足を挿入しない。\n"
    )
    return (
        "あなたは日本語書籍OCR専用アシスタントです。入力文書を本文テキストとして抽出してください。\n"
        "要件:\n"
        "1) 日本語文書として扱う。\n"
        f"2) 文字方向は {writing_mode} として解釈する。\n"
        "3) 見出し・段落・注記・独立行など原文で意図された改行はできるだけ維持する。\n"
        "4) 行幅都合の折返し改行は入れない（文の続きは同じ行にする）。\n"
        "5) 推測補完しない。読めない箇所は [判読不能] と記す。\n"
        f"{furigana_rule}"
        f"7) 複数ページの場合はページ境界に必ず {page_separator} を1行で挿入する。\n"
        "8) 出力は本文テキストのみ。説明文やコードブロックを付けない。"
    )


def make_api_request(api_key: str, model_id: str, prompt: str, file_path: Path) -> dict:
    endpoint = f"{API_BASE_URL}/{model_id}:generateContent"
    url = f"{endpoint}?key={api_key}"
    suffix = file_path.suffix.lower()
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": MIME_MAP[suffix],
                            "data": base64.b64encode(file_path.read_bytes()).decode("utf-8"),
                        }
                    },
                ],
            }
        ],
        "generationConfig": {"temperature": 0},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as response:
        return json.loads(response.read().decode("utf-8"))


def make_api_request_with_retry(
    api_key: str,
    model_id: str,
    prompt: str,
    file_path: Path,
    retries: int,
) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return make_api_request(api_key, model_id, prompt, file_path)
        except urllib.error.HTTPError as error:
            last_error = error
            detail = ""
            if error.fp:
                try:
                    detail = error.fp.read().decode("utf-8")
                except Exception:
                    detail = ""
            if attempt >= retries:
                if detail:
                    print(detail, file=sys.stderr)
                raise
        except Exception as error:
            last_error = error
            if attempt >= retries:
                raise
        time.sleep(2 * (attempt + 1))
    assert last_error is not None
    raise last_error


def extract_text(response: dict) -> str:
    candidates = response.get("candidates", [])
    if not candidates:
        raise ValueError("No candidates found in Gemini response")
    parts = candidates[0].get("content", {}).get("parts", [])
    chunks: List[str] = []
    for part in parts:
        text = part.get("text")
        if text:
            chunks.append(text)
    result = "\n".join(chunks).strip()
    if not result:
        raise ValueError("No text extracted from Gemini response")
    return result


def split_pages(text: str, page_separator: str) -> List[str]:
    if not text:
        return [""]
    pattern = rf"\n{re.escape(page_separator)}\n"
    return [part.strip("\n") for part in re.split(pattern, text.strip())]


def join_pages(pages: Sequence[str], page_separator: str) -> str:
    return (f"\n{page_separator}\n").join(p.strip("\n") for p in pages).strip()


def is_heading_like(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if len(s) > 12:
        return False
    if any(ch in s for ch in "。！？、，．.,:：;；()（）[]【】<>「」『』"):
        return False
    return True


def line_length_threshold(lines: Sequence[str]) -> int:
    lengths = [len(ln.strip()) for ln in lines if ln.strip()]
    if not lengths:
        return 9999
    max_len = max(lengths)
    return max(20, int(max_len * 0.8))


def is_annotation_start(line: str) -> bool:
    return bool(line.strip()) and line.strip().startswith(ANNOTATION_PREFIXES)


def looks_classical_or_quote_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # Classical quoted lines often start with dense kanji and particles like 之/於/也.
    if re.search(r"[之於而也矣焉乎]", s):
        return True
    if len(s) >= 10 and sum(1 for ch in s[:8] if re.match(KANJI_RE, ch)) >= 4:
        return True
    return False


def insert_inferred_blank_lines(lines: Sequence[str]) -> List[str]:
    if not lines:
        return []
    out: List[str] = []
    for idx, line in enumerate(lines):
        cur = line.strip()
        if out and cur:
            prev = out[-1].strip()
            if prev:
                need_blank = False
                if is_annotation_start(cur) and not is_annotation_start(prev):
                    need_blank = True
                elif looks_classical_or_quote_line(cur) and not looks_classical_or_quote_line(prev):
                    if prev.endswith(("。", "）", ")", "』", "」")):
                        need_blank = True
                if need_blank and out[-1] != "":
                    out.append("")
        out.append(line)
    # Collapse repeated blanks
    normalized: List[str] = []
    for line in out:
        if line == "" and (not normalized or normalized[-1] == ""):
            continue
        normalized.append(line)
    return normalized


def should_join(current: str, nxt: str, threshold: int) -> bool:
    cur = current.strip()
    ns = nxt.strip()
    if not cur or not ns:
        return False
    # Preserve clear intentional breaks before considering wrap joining.
    if cur[-1] in JP_END_PUNCT:
        return False
    if ns.startswith(ANNOTATION_PREFIXES):
        return False
    if is_heading_like(cur):
        return False
    # Strong wrap signal: line is near the dominant width for this page.
    if len(cur) >= threshold:
        return True
    # Medium signal used only when the line is close to the page width.
    near_threshold = len(cur) >= max(12, int(threshold * 0.7))
    if cur.endswith(("、", "，", ",", "・", "（", "(", "「", "『")):
        return True
    if near_threshold and len(ns) >= 1 and re.match(r"[ぁ-ゖァ-ヶ一-龯々「『（(]", ns[0]):
        return True
    return False


def normalize_linebreaks_page(text: str, mode: str) -> str:
    if mode == "none":
        return text.strip("\n")

    lines = [ln.rstrip() for ln in text.splitlines()]
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""

    heading = None
    body_start = 0
    if is_heading_like(lines[0]):
        heading = lines[0].strip()
        body_start = 1

    body_lines = lines[body_start:]
    threshold = line_length_threshold(body_lines)
    if mode == "strict":
        threshold = max(14, threshold - 6)

    out: List[str] = []
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        if not line.strip():
            out.append("")
            i += 1
            continue
        cur = line.strip()
        while i + 1 < len(body_lines):
            nxt = body_lines[i + 1]
            if not nxt.strip():
                break
            if not should_join(cur, nxt, threshold):
                break
            cur += nxt.strip()
            i += 1
        out.append(cur)
        i += 1

    normalized: List[str] = []
    if heading:
        normalized.append(heading)
        normalized.append("")
    for line in out:
        if line == "" and (not normalized or normalized[-1] == ""):
            continue
        normalized.append(line)

    if mode in {"heuristic", "strict"}:
        normalized = insert_inferred_blank_lines(normalized)
    return "\n".join(normalized).strip()


FURIGANA_PATTERN = re.compile(
    rf"(?<![（(])(?P<kanji>{KANJI_RE}{{2,4}})(?P<kana>{HIRAGANA_RE}{{2,8}})"
    rf"(?=(?:[\s、。，．,.:：;；!?！？（）()【】「」『』<>\[\]＜＞]|$|{KANJI_RE}))"
)
FURIGANA_KANA_STOPWORDS = {
    "という",
    "をいう",
    "のごとし",
    "ことし",
    "もの",
    "ために",
}
FURIGANA_KANA_START_BLOCK = set("をにはへとでもの")


def normalize_furigana_paren(text: str) -> str:
    if not text:
        return text

    def repl(match: re.Match[str]) -> str:
        kanji = match.group("kanji")
        kana = match.group("kana")

        # Skip common okurigana-like endings.
        if kana in {"する", "した", "して", "され", "れる", "られ"}:
            return match.group(0)
        if kana in FURIGANA_KANA_STOPWORDS:
            return match.group(0)
        if kana and kana[0] in FURIGANA_KANA_START_BLOCK:
            return match.group(0)
        if len(kanji) <= 2 and len(kana) <= 2:
            return match.group(0)
        if len(kanji) >= 4 and len(kana) >= 6:
            return match.group(0)
        return f"{kanji}（{kana}）"

    prev = None
    cur = text
    # A few passes handle adjacent candidates without risking infinite loops.
    for _ in range(3):
        if cur == prev:
            break
        prev = cur
        cur = FURIGANA_PATTERN.sub(repl, cur)
    return cur


def normalize_furigana(text: str, mode: str) -> str:
    if mode == "none":
        return text
    if mode in {"paren", "heuristic"}:
        return normalize_furigana_paren(text)
    raise ValueError(f"Unsupported furigana mode: {mode}")


PAREN_CONTENT_RE = re.compile(r"（([^）]{1,80})）")
RUBY_LIKE_PAREN_RE = re.compile(r"^[ぁ-ゖァ-ヶー・･ゝゞヽヾ\s]+$")
PAREN_PRESERVE_KEYWORDS = (
    "『",
    "」",
    "』",
    "正義",
    "折中",
    "本義",
    "語類",
    "について",
    "意味",
    "章",
    "第",
)


def should_preserve_paren(content: str) -> bool:
    s = content.strip()
    if not s:
        return True
    if any(key in s for key in PAREN_PRESERVE_KEYWORDS):
        return True
    if re.search(r"[一-龯々A-Za-z0-9]", s):
        return True
    return False


def looks_ruby_paren(content: str) -> bool:
    s = re.sub(r"\s+", "", content)
    if not s:
        return False
    if len(s) > 12:
        return False
    return bool(RUBY_LIKE_PAREN_RE.fullmatch(s))


def normalize_parenthetical_noise(text: str, policy: str) -> str:
    if policy == "preserve":
        return text

    def repl(match: re.Match[str]) -> str:
        content = match.group(1)
        if should_preserve_paren(content):
            return match.group(0)
        if policy == "none":
            return ""
        if policy == "no-ruby" and looks_ruby_paren(content):
            return ""
        return match.group(0)

    if policy not in {"preserve", "no-ruby", "none"}:
        raise ValueError(f"Unsupported paren policy: {policy}")
    return PAREN_CONTENT_RE.sub(repl, text)


def default_output_path(input_path: Path) -> Path:
    if input_path.is_dir():
        return Path.cwd() / f"{input_path.name}_ocr.md"
    return Path.cwd() / f"{input_path.stem}_ocr.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OCR book images/PDF and merge to one Markdown with linebreak restoration"
    )
    parser.add_argument(
        "--in",
        dest="input_path",
        required=True,
        help="Image directory or file (.jpg/.png/.webp/.heic/.heif/.pdf)",
    )
    parser.add_argument("--writing-mode", required=True, choices=["vertical", "horizontal"])
    parser.add_argument("--model", required=True, choices=["flash", "thinking", "pro"])
    parser.add_argument("--out", help="Output Markdown file path")
    parser.add_argument("--linebreak-mode", default="heuristic", choices=["none", "heuristic", "strict"])
    parser.add_argument("--furigana-mode", default="none", choices=["none", "paren", "heuristic"])
    parser.add_argument("--paren-policy", default="no-ruby", choices=["preserve", "no-ruby", "none"])
    parser.add_argument("--page-separator", default=DEFAULT_PAGE_SEPARATOR)
    parser.add_argument("--keep-raw", action="store_true", help="Save combined raw OCR text next to output")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it exists")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first page/file failure")
    parser.add_argument("--retries", type=int, default=1, help="Retries per OCR request (default: 1)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_path)
    out_path = Path(args.out) if args.out else default_output_path(input_path)

    try:
        sources = list_input_files(input_path)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not sources:
        print("Error: no supported input files found", file=sys.stderr)
        sys.exit(1)
    if out_path.exists() and not args.overwrite:
        print(f"Error: output already exists: {out_path} (use --overwrite)", file=sys.stderr)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    api_key = get_api_key()
    model_id = resolve_model_id(args.model)
    prompt = build_book_prompt(args.writing_mode, args.page_separator, args.furigana_mode)

    print(f"Input: {input_path}")
    print(f"Items: {len(sources)}")
    print(f"Model profile: {args.model}")
    print(f"Model ID: {model_id}")
    print(f"Writing mode: {args.writing_mode}")
    print(f"Linebreak mode: {args.linebreak_mode}")
    print(f"Furigana mode: {args.furigana_mode}")
    print(f"Paren policy: {args.paren_policy}")
    print(f"Output file: {out_path}")
    print()

    all_pages_processed: List[str] = []
    all_pages_raw: List[str] = []
    failures: List[str] = []

    for source in sources:
        try:
            response = make_api_request_with_retry(api_key, model_id, prompt, source, max(0, args.retries))
            raw_text = extract_text(response)
            raw_pages = split_pages(raw_text, args.page_separator)
            processed_pages: List[str] = []
            for page in raw_pages:
                page_text = normalize_linebreaks_page(page, args.linebreak_mode)
                page_text = normalize_furigana(page_text, args.furigana_mode)
                page_text = normalize_parenthetical_noise(page_text, args.paren_policy)
                processed_pages.append(page_text)
            all_pages_raw.extend(raw_pages)
            all_pages_processed.extend(processed_pages)
            print(f"OK: {source} pages={len(raw_pages)}")
        except Exception as error:
            msg = f"{source} ({error})"
            failures.append(msg)
            print(f"NG: {msg}", file=sys.stderr)
            if args.fail_fast:
                break

    if failures and (args.fail_fast or not all_pages_processed):
        print("Error: OCR run failed", file=sys.stderr)
        for row in failures:
            print(f"- {row}", file=sys.stderr)
        sys.exit(2)

    output_text = join_pages(all_pages_processed, args.page_separator)
    out_path.write_text(ensure_text_newline(output_text), encoding="utf-8")

    raw_path = None
    if args.keep_raw:
        raw_path = out_path.with_suffix(out_path.suffix + ".raw.txt")
        raw_text = join_pages(all_pages_raw, args.page_separator)
        raw_path.write_text(ensure_text_newline(raw_text), encoding="utf-8")

    print()
    print(f"Completed: {len(all_pages_processed)} pages, {len(failures)} failures")
    print(f"Wrote: {out_path}")
    if raw_path:
        print(f"Wrote raw: {raw_path}")
    if failures:
        print("Failed items:", file=sys.stderr)
        for row in failures:
            print(f"- {row}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
