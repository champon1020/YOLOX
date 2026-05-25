#!/usr/bin/env python3
"""Convert a range of PDF pages to JPEG files using ``convert_pdf_to_images``.

This is a thin CLI around ``libs.pdf_handlers.convert_pdf_to_images``: same
rendering (pypdfium2, ``scale=dpi/72``, ``rotation=0``), same JPEG settings
(quality 85, dpi tuple), and the same ``resize_and_compress_image`` post-step.

Page indices are **0-based** and **inclusive** on both ends, matching the
``for page_num in range(start_page, end_page + 1)`` loop inside
``convert_pdf_to_images``. Output files are named ``page-{1-based}.jpg`` as in
``pdf_handlers``.

Usage:
    poetry run python scripts/pdf_to_images.py path/to/file.pdf -o ./out
    # writes JPEGs under ./out/file/ when the input is file.pdf

    poetry run python scripts/pdf_to_images.py path/to/file.pdf -o ./out --start-page 0 --end-page 2
    poetry run python scripts/pdf_to_images.py path/to/file.pdf -o ./out --dpi 200
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from libs.pdf_handlers import (  # noqa: E402  (import after sys.path)
    PDFDivider,
    convert_pdf_to_images,
    pdf2img_tmpdir_var,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert PDF page(s) to JPEG via libs.pdf_handlers.convert_pdf_to_images.",
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the PDF file.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        required=True,
        help=(
            "Base output directory (created if missing). A subdirectory named after the PDF "
            "(filename without extension) is created under this path; JPEGs go there via pdf2img_tmpdir_var."
        ),
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=0,
        help="First page index to render (0-based, inclusive). Default: 0.",
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=None,
        help="Last page index to render (0-based, inclusive). Default: last page of the PDF.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Dots per inch for rendered images. Default: 300 (same as convert_pdf_to_images).",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path.expanduser().resolve()
    if not pdf_path.is_file():
        print(f"error: PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    base_output_dir = args.output_dir.expanduser().resolve()
    base_output_dir.mkdir(parents=True, exist_ok=True)

    pdf_stem = pdf_path.stem or pdf_path.name
    image_dir = base_output_dir / pdf_stem
    image_dir.mkdir(parents=True, exist_ok=True)

    total_pages = PDFDivider.get_pdf_page_count(str(pdf_path))
    end_page = args.end_page if args.end_page is not None else total_pages - 1

    if args.start_page < 0 or end_page < 0:
        print("error: start-page and end-page must be non-negative.", file=sys.stderr)
        return 1
    if args.start_page > end_page:
        print("error: start-page must be <= end-page.", file=sys.stderr)
        return 1
    if args.start_page >= total_pages:
        print(f"error: start-page ({args.start_page}) is out of range (PDF has {total_pages} pages).", file=sys.stderr)
        return 1

    token = pdf2img_tmpdir_var.set(str(image_dir))
    try:
        paths = convert_pdf_to_images(str(pdf_path), args.start_page, end_page, dpi=args.dpi)
    finally:
        pdf2img_tmpdir_var.reset(token)

    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
