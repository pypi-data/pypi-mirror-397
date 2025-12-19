import concurrent.futures
import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import Tuple, List, Optional

from .const import *

pdf_doc: Optional[fitz.Document] = None
pdf_len: Optional[int] = None


def open_pdf(pdf_path: Path):
    """
    Open PDF and keep it in memory for the worker process.
    """
    global pdf_doc
    global pdf_len
    try:
        pdf_doc = fitz.open(pdf_path)
        pdf_len = pdf_doc.page_count
    except Exception as e:
        print(f"Impossible to initialise worker for {pdf_path}: {e}")
        pdf_doc = None
        pdf_len = None


def calculate_matrix(page: fitz.Page, dpi: int, max_size: int) -> fitz.Matrix:
    zoom = dpi / 72.0
    rect = page.rect
    width, height = rect.width * zoom, rect.height * zoom

    if max(width, height) > max_size:
        scale = max_size / max(width, height)
        return fitz.Matrix(zoom * scale, zoom * scale)

    return fitz.Matrix(zoom, zoom)


def _process_batch(
    start: int,
    end: int,
    output_dir: Path,
    img_prefix: str,
    dpi: int = MAX_RES,
    ext: str = "jpg",
    quality: int = MAX_QUAL,
    max_size: int = MAX_SIZE,
    auto_alpha_format: bool = False,
) -> List[str]:
    result_files = []
    global pdf_doc
    global pdf_len

    if pdf_doc is None:
        print("Critical error: PDF document was not loaded")
        return []

    for page_idx in range(start - 1, end):
        if page_idx >= pdf_len:
            break

        try:
            page = pdf_doc[page_idx]

            matrix = calculate_matrix(page, dpi, max_size)
            pixmap = page.get_pixmap(matrix=matrix, alpha=auto_alpha_format)

            output_ext = "png" if auto_alpha_format and pixmap.alpha else ext

            output_filename = f"{img_prefix}_{page_idx + 1:04d}.{output_ext}"
            output_path = output_dir / output_filename

            if output_ext.lower() in ["jpg", "jpeg"]:
                pixmap.save(str(output_path), output=output_ext.lower(), jpg_quality=quality)
            else:
                pixmap.save(str(output_path), output=output_ext.lower())

            result_files.append(output_filename)

            del pixmap
            del page

        except Exception as e:
            print(f"Error when processing {page_idx + 1}: {e}")
            continue

    return result_files


def convert_batch(
    start: int,
    end: int,
    output_dir: Path,
    img_prefix: str,
    dpi: int = MAX_RES,
    ext: str = "jpg",
    quality: int = MAX_QUAL,
    max_size: int = MAX_SIZE,
    auto_alpha_format: bool = False,
) -> List[str]:
    try:
        return _process_batch(
            start, end, output_dir, img_prefix, dpi, ext, quality, max_size, auto_alpha_format
        )
    except Exception as e:
        print(f"Batch processing failed ({start}-{end}): {e}")
        if dpi > 150:
            return _process_batch(
                start, end, output_dir, img_prefix, int(dpi * 0.6), ext, quality, max_size, auto_alpha_format
            )
        return []


def convert_pdf(
    pdf_path: Path,
    page_range: Optional[Tuple[int, int]] = None,
    output_dir: Path = IMG_PATH,
    img_prefix: Optional[str] = None,
    dpi: int = MAX_RES,
    ext: str = "jpg",
    quality: int = MAX_QUAL,
    max_size: int = MAX_SIZE,
    batch_size: int = 25,
    auto_alpha_format: bool = False,
) -> List[str]:
    result_files = []

    pdf_path = Path(pdf_path).resolve()

    try:
        if not pdf_path.exists() or not pdf_path.is_file():
            print(f"[convert_pdf] PDF file not found: {pdf_path}")
            return []

        output_dir = Path(output_dir)
        if not output_dir.exists() or not output_dir.is_dir():
            os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"[convert_pdf] Error with paths: {e}")
        return []

    try:
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count
        doc.close()

        if not page_range:
            page_range = (1, total_pages)

        start_page, end_page = page_range
        end_page = min(end_page, total_pages)

        max_workers = min(5, os.cpu_count() or 1)

        batches = []
        current_start = start_page
        while current_start <= end_page:
            current_end = min(current_start + batch_size - 1, end_page)
            batches.append((current_start, current_end))
            current_start = current_end + 1

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=open_pdf,
            initargs=(pdf_path,)
        ) as executor:

            futures = [
                executor.submit(
                    convert_batch,
                    batch[0],
                    batch[1],
                    output_dir,
                    img_prefix,
                    dpi,
                    ext,
                    quality,
                    max_size,
                    auto_alpha_format,
                )
                for batch in batches
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    batch_results = future.result()
                    result_files.extend(batch_results)
                except Exception as e:
                    print(f"Batch processing failed for {pdf_path}: {e}")

        result_files.sort()
        return result_files

    except fitz.FileDataError as e:
        print(f"PDF file is corrupted or invalid: {e}")
        return []
    except Exception as e:
        print(f"PyMuPDF conversion failed: {e}")
        return []
