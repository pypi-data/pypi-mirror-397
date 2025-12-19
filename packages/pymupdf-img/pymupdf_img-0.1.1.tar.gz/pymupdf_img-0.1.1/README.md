# `pymupdf-img`

Fast PDF to image converter with batch processing and multi-threading support using PyMuPDF.

## Installation

```bash
pip install pymupdf-img
# or
uv pip install pymupdf-img
```

## Quick start
### Command Line

```bash
pdf2img document.pdf
```

**Options:**
- `-o, --output-dir`: Output directory (default: `output`)
- `-p, --prefix`: Image filename prefix
- `-r, --range`: Page range, e.g., `1-10`
- `-d, --dpi`: Resolution in DPI (default: 95)
- `-e, --ext`: Format: `jpg`, `png`, `webp` (default: `jpg`)
- `-q, --quality`: Image quality 1-100 (default: 95)
- `-m, --max-size`: Max width/height in pixels (default: 2500)
- `-b, --batch-size`: Pages per batch (default: 25)
- `-a, --auto-alpha`: PNG for transparency, otherwise ext format


```python
from pymupdf_img import convert_pdf

# Basic conversion
images = convert_pdf("document.pdf")

# Advanced usage
images = convert_pdf(
    pdf_path="path/to/document.pdf",
    page_range=(1, 10),                 # None for all pages or (start, end) tuple
    output_dir="output/images",         # output directory
    img_prefix="img_",                  # prefix for image filenames
    dpi=150,                            # resolution
    ext="jpg",                          # output image format
    quality=95,                         # image quality for lossy formats
    max_size=2500,                      # max width/height in pixels
    batch_size=50,                      # number of pages to process per batch
    auto_alpha_format=True              # PNG if alpha channel detected, ext otherwise
)
```

## Development

```bash
# Build the package
uv run python -m build
# Check the package
uv run twine check dist/* 
# Upload the package
uv run twine upload dist/*
```