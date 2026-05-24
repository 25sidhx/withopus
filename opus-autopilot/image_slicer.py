"""Image Slicer — splits a single carousel canvas into 6 individual slides.

Workflow:
    User generates ONE connected canvas image (6 panels in a 3×2 or 2×3 grid)
    → This module slices it into 6 equal parts
    → Each slice is resized to 1080×1080 for Instagram
"""

import logging
from pathlib import Path

from PIL import Image

import config

logger = logging.getLogger("autopilot.slicer")


def detect_layout(width: int, height: int) -> tuple[int, int]:
    """Detect grid layout from image aspect ratio.

    Returns (cols, rows).
    """
    ratio = width / height
    if ratio >= 1.2:
        return 3, 2   # wide canvas → 3 cols, 2 rows
    return 2, 3       # tall canvas  → 2 cols, 3 rows


def slice_canvas(
    image_path: str | Path,
    num_slides: int = 6,
    layout: str = "auto",
    output_dir: str | Path | None = None,
    draft_id: str = "output",
) -> list[Path]:
    """Slice a connected carousel canvas into individual slides.

    Args:
        image_path: Path to the source canvas image.
        num_slides:  Number of slides (default 6).
        layout:      "3x2" | "2x3" | "auto" (detected from aspect ratio).
        output_dir:  Where to save slices. Defaults to carousels/<draft_id>/.
        draft_id:    Used to name the output folder.

    Returns:
        Ordered list of paths to sliced slides (slide_01.jpg … slide_06.jpg).
    """
    image_path = Path(image_path)
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    logger.info("Source canvas: %dx%d px (%s)", w, h, image_path.name)

    if layout == "auto":
        cols, rows = detect_layout(w, h)
    elif layout == "3x2":
        cols, rows = 3, 2
    else:
        cols, rows = 2, 3

    logger.info("Layout: %dx%d grid (%d cols × %d rows)", cols, rows, cols, rows)

    if output_dir is None:
        output_dir = config.CAROUSELS_DIR / draft_id
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    slide_w = w // cols
    slide_h = h // rows
    slides: list[Path] = []
    slide_num = 1

    # Slice left-to-right, top-to-bottom (reading order)
    for row in range(rows):
        for col in range(cols):
            left   = col * slide_w
            top    = row * slide_h
            right  = left  + slide_w
            bottom = top   + slide_h

            slide_img = img.crop((left, top, right, bottom))

            # Resize to 1080×1080 (Instagram square)
            slide_img = slide_img.resize((1080, 1080), Image.LANCZOS)

            out_path = output_dir / f"slide_{slide_num:02d}.jpg"
            slide_img.save(out_path, "JPEG", quality=95, optimize=True)
            logger.info("Saved slide %d → %s", slide_num, out_path.name)

            slides.append(out_path)
            slide_num += 1

    logger.info("Sliced %d slides into %s", len(slides), output_dir)
    return slides


def build_preview_grid(slide_paths: list[Path], output_path: Path) -> Path:
    """Stitch slices back into a small 3×2 preview mosaic for Telegram.

    Each slice is thumbnailed to 400×400 before stitching.
    """
    THUMB = 400
    cols, rows = 3, 2
    canvas = Image.new("RGB", (cols * THUMB, rows * THUMB), (15, 15, 15))

    for idx, path in enumerate(slide_paths[:6]):
        thumb = Image.open(path).resize((THUMB, THUMB), Image.LANCZOS)
        col = idx % cols
        row = idx // cols
        canvas.paste(thumb, (col * THUMB, row * THUMB))

    output_path = Path(output_path)
    canvas.save(output_path, "JPEG", quality=85)
    logger.info("Preview grid saved → %s", output_path)
    return output_path
