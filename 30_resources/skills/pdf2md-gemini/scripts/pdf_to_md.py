#!/usr/bin/env python3
"""
PDF2MD-GEMINI - Japanese OCR to Markdown using Gemini API.
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_OUTPUT_ROOT = Path("/mnt/e/Documents/Workspace/ocr")
DEFAULT_PAGE_SEPARATOR = "---"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}

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
    ".pdf": "application/pdf",
}


def run_command(command: List[str]) -> str:
    process = subprocess.run(command, text=True, capture_output=True)
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or "command failed")
    return process.stdout


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


def sanitize_name(name: str) -> str:
    value = name.strip()
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" ", "_")
    value = re.sub(r"_+", "_", value)
    return value or "untitled"


def is_directory_hint(path_str: str, path_obj: Path) -> bool:
    return path_str.endswith(("/", "\\")) or path_obj.is_dir() or path_obj.suffix == ""


def make_default_run_dir(input_path: Path) -> Path:
    base = sanitize_name(input_path.name if input_path.is_dir() else input_path.stem)
    run_dir = DEFAULT_OUTPUT_ROOT / base
    if run_dir.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = DEFAULT_OUTPUT_ROOT / f"{base}_{stamp}"
    return run_dir


def list_input_files(input_path: Path) -> List[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported input extension: {input_path.suffix}")
        return [input_path]

    if not input_path.is_dir():
        raise ValueError(f"Input path does not exist: {input_path}")

    files: List[Path] = []
    for item in sorted(input_path.iterdir()):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(item)
    return files


def build_prompt(writing_mode: str, page_separator: str) -> str:
    return (
        "あなたは日本語OCR専用アシスタントです。次の入力文書を原文忠実で抽出してください。\n"
        "要件:\n"
        "1) 文字列は日本語として扱う。\n"
        f"2) 文字方向は {writing_mode} として解釈する。\n"
        "3) 改行、句読点、段落順を維持する。\n"
        "4) 推測補完しない。読めない箇所は [判読不能] と記す。\n"
        f"5) 文書が複数ページの場合、ページ境界に必ず {page_separator} を1行で挿入する。\n"
        "6) 出力は本文テキストのみ。コードブロックや説明文を付けない。"
    )


def make_api_request(api_key: str, model_id: str, prompt: str, file_path: Path) -> dict:
    endpoint = f"{API_BASE_URL}/{model_id}:generateContent"
    url = f"{endpoint}?key={api_key}"
    suffix = file_path.suffix.lower()
    mime_type = MIME_MAP[suffix]
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(file_path.read_bytes()).decode("utf-8"),
                        }
                    },
                ],
            }
        ],
        "generationConfig": {"temperature": 0},
    }

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = ""
        if error.fp:
            detail = error.fp.read().decode("utf-8")
        print(f"Error: Gemini API request failed (HTTP {error.code})", file=sys.stderr)
        if detail:
            print(detail, file=sys.stderr)
        raise


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


def list_pdf_image_pages(pdf_path: Path) -> List[int]:
    output = run_command(["pdfimages", "-list", str(pdf_path)])
    pages: List[int] = []
    for line in output.splitlines():
        match = re.match(r"^\s*(\d+)\s+\d+\s+image\s+", line)
        if match:
            pages.append(int(match.group(1)))
    return pages


def extract_pdf_images(
    pdf_path: Path,
    image_dir: Path,
    md_parent: Path,
    image_format: str,
) -> List[Tuple[int, str]]:
    if image_format != "png":
        raise ValueError("Only png image format is currently supported")

    page_entries = list_pdf_image_pages(pdf_path)
    if not page_entries:
        return []

    ensure_dir(image_dir)
    references: List[Tuple[int, str]] = []
    per_page_index: Dict[int, int] = defaultdict(int)

    with tempfile.TemporaryDirectory(prefix="pdf2md-gemini-img-") as temp_dir:
        temp_path = Path(temp_dir)
        prefix = temp_path / "img"
        run_command(["pdfimages", "-png", str(pdf_path), str(prefix)])

        generated = sorted(
            p
            for p in temp_path.iterdir()
            if p.is_file() and p.name.startswith("img-") and p.suffix.lower() == ".png"
        )
        if not generated:
            return []

        count = min(len(page_entries), len(generated))
        for idx in range(count):
            page = page_entries[idx]
            per_page_index[page] += 1
            target = image_dir / f"p{page:03d}_img{per_page_index[page]:03d}.png"
            shutil.copy2(generated[idx], target)
            relative = os.path.relpath(target, md_parent).replace("\\", "/")
            references.append((page, relative))

        if len(page_entries) != len(generated):
            print(
                f"Warning: image count mismatch for {pdf_path.name} (listed={len(page_entries)}, extracted={len(generated)})",
                file=sys.stderr,
            )

    return references


def split_pages_from_text(text: str, page_separator: str) -> List[str]:
    if not text:
        return [""]
    pattern = rf"\n{re.escape(page_separator)}\n"
    return [part.strip("\n") for part in re.split(pattern, text.strip())]


def to_markdown(pages: List[str], page_separator: str) -> str:
    normalized = [page.strip("\n") for page in pages]
    return (f"\n{page_separator}\n").join(normalized).strip()


def inject_image_blocks(pages: List[str], refs: List[Tuple[int, str]]) -> List[str]:
    refs_by_page: Dict[int, List[str]] = defaultdict(list)
    for page, path in refs:
        refs_by_page[page].append(path)

    output_pages: List[str] = []
    for idx, page_text in enumerate(pages, start=1):
        page_body = page_text.strip("\n")
        images = refs_by_page.get(idx, [])
        if images:
            lines = [f"### Page {idx} Figures", ""]
            lines.extend(f"![p{idx}-img{n}]({path})" for n, path in enumerate(images, start=1))
            image_block = "\n".join(lines)
            page_body = f"{page_body}\n\n{image_block}".strip("\n") if page_body else image_block
        output_pages.append(page_body)

    return output_pages


def resolve_output_base(output_arg: Optional[str], input_path: Path) -> Tuple[Path, Optional[Path]]:
    if not output_arg:
        return make_default_run_dir(input_path), None

    out_path = Path(output_arg)
    if is_directory_hint(output_arg, out_path):
        return out_path, None

    return out_path.parent, out_path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Japanese OCR to Markdown with Gemini API")
    parser.add_argument("--in", dest="input_path", required=True, help="Input file or directory")
    parser.add_argument("--writing-mode", required=True, choices=["vertical", "horizontal"])
    parser.add_argument("--model", required=True, choices=["flash", "thinking", "pro"])
    parser.add_argument("--out", help="Output file path or directory path")
    parser.add_argument("--page-separator", default=DEFAULT_PAGE_SEPARATOR)
    parser.add_argument("--no-save-raw", action="store_true", help="Disable raw OCR output")
    parser.add_argument(
        "--extract-images",
        dest="extract_images",
        action="store_true",
        default=True,
        help="Extract embedded PDF images (default: enabled)",
    )
    parser.add_argument(
        "--no-extract-images",
        dest="extract_images",
        action="store_false",
        help="Disable embedded image extraction",
    )
    parser.add_argument(
        "--embed-images",
        dest="embed_images",
        action="store_true",
        default=True,
        help="Embed extracted image links into Markdown (default: enabled)",
    )
    parser.add_argument(
        "--no-embed-images",
        dest="embed_images",
        action="store_false",
        help="Do not inject extracted image links into Markdown",
    )
    parser.add_argument("--images-dir", help="Override images output root directory")
    parser.add_argument("--image-format", choices=["png"], default="png")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.extract_images and shutil.which("pdfimages") is None:
        print("Warning: pdfimages not found, disabling image extraction", file=sys.stderr)
        args.extract_images = False

    input_path = Path(args.input_path)
    try:
        input_files = list_input_files(input_path)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not input_files:
        print("Error: no supported input files found", file=sys.stderr)
        sys.exit(1)

    output_base, explicit_file = resolve_output_base(args.out, input_path)
    input_is_dir = input_path.is_dir()
    if explicit_file and input_is_dir:
        print("Error: --out file path is only valid for single-file input", file=sys.stderr)
        sys.exit(1)

    md_dir = output_base / "md"
    raw_dir = output_base / "raw"
    images_root = Path(args.images_dir) if args.images_dir else (output_base / "images")

    ensure_dir(md_dir)
    if not args.no_save_raw:
        ensure_dir(raw_dir)
    if args.extract_images:
        ensure_dir(images_root)

    api_key = get_api_key()
    model_id = resolve_model_id(args.model)
    prompt = build_prompt(args.writing_mode, args.page_separator)

    print(f"Input: {input_path}")
    print(f"Files: {len(input_files)}")
    print(f"Model profile: {args.model}")
    print(f"Model ID: {model_id}")
    print(f"Writing mode: {args.writing_mode}")
    print(f"Extract images: {args.extract_images}")
    print(f"Embed images: {args.embed_images}")
    print(f"Output base: {output_base}")
    print()

    success: List[str] = []
    failed: List[str] = []

    for source in input_files:
        stem = source.stem
        md_path = explicit_file if explicit_file else md_dir / f"{stem}.md"
        raw_path = raw_dir / f"{stem}.raw.txt"

        try:
            response = make_api_request(api_key, model_id, prompt, source)
            raw_text = extract_text(response)
            raw_pages = split_pages_from_text(raw_text, args.page_separator)
            md_pages = list(raw_pages)

            extracted_images = 0
            if args.extract_images and source.suffix.lower() == ".pdf":
                file_image_dir = images_root / stem
                refs = extract_pdf_images(source, file_image_dir, md_path.parent, args.image_format)
                extracted_images = len(refs)
                if args.embed_images and refs:
                    md_pages = inject_image_blocks(md_pages, refs)

            md_text = to_markdown(md_pages, args.page_separator)
            write_text(md_path, md_text)
            if not args.no_save_raw:
                write_text(raw_path, to_markdown(raw_pages, args.page_separator))
            success.append(str(source))
            print(f"OK: {source} -> {md_path} images={extracted_images}")
        except Exception as error:
            failed.append(f"{source} ({error})")
            print(f"NG: {source} ({error})", file=sys.stderr)

    print()
    print(f"Completed: {len(success)} success, {len(failed)} failed")
    if failed:
        print("Failed files:", file=sys.stderr)
        for row in failed:
            print(f"- {row}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
