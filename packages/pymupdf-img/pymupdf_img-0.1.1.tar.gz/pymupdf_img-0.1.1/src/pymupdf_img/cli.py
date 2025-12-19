import argparse
import time
from pathlib import Path
from pymupdf_img import convert_pdf, MAX_RES, MAX_SIZE, MAX_QUAL, IMG_PATH


def parse_page_range(value: str) -> tuple[int, int]:
    if not value:
        return None
    start, end = map(int, value.split("-"))
    return (start, end)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to images with PyMuPDF",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("pdf_path", type=Path, help="Path to PDF file")
    parser.add_argument("-o", "--output-dir", type=Path, default=IMG_PATH,
                        help="Output directory")
    parser.add_argument("-p", "--prefix", type=str, default=None,
                        help="Image filename prefix")
    parser.add_argument("-r", "--range", type=str, default=None,
                        help="Page range (e.g., '1-10')")
    parser.add_argument("-d", "--dpi", type=int, default=MAX_RES,
                        help="Resolution in DPI")
    parser.add_argument("-e", "--ext", type=str, default="jpg",
                        choices=["jpg", "png", "webp"],
                        help="Output image format")
    parser.add_argument("-q", "--quality", type=int, default=MAX_QUAL,
                        help="Image quality (1-100)")
    parser.add_argument("-m", "--max-size", type=int, default=MAX_SIZE,
                        help="Maximum width/height in pixels")
    parser.add_argument("-b", "--batch-size", type=int, default=25,
                        help="Pages per batch")
    parser.add_argument("-a", "--auto-alpha", action="store_true",
                        help="Use PNG for pages with transparency")

    args = parser.parse_args()

    page_range = parse_page_range(args.range) if args.range else None

    print(f"Converting: {args.pdf_path}")
    print(f"Output: {args.output_dir}")
    if page_range:
        print(f"Pages: {page_range[0]}-{page_range[1]}")

    start_time = time.perf_counter()

    result_files = convert_pdf(
        pdf_path=args.pdf_path,
        page_range=page_range,
        output_dir=args.output_dir,
        img_prefix=args.prefix,
        dpi=args.dpi,
        ext=args.ext,
        quality=args.quality,
        max_size=args.max_size,
        batch_size=args.batch_size,
        auto_alpha_format=args.auto_alpha,
    )

    elapsed = time.perf_counter() - start_time

    print(f"\n✓ Converted {len(result_files)} pages in {elapsed:.2f}s")
    print(f"  ({len(result_files) / elapsed:.1f} pages/s)")


if __name__ == "__main__":
    main()
