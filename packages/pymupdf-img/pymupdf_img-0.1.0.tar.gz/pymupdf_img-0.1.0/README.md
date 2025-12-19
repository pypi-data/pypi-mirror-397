# `pdf-to-img`

Fast PDF to image converter with batch processing and multi-threading support using PyMuPDF.

## Installation

```bash
pip install pdf-to-img
# or
uv pip install pdf-to-img
```

# Quick start
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
