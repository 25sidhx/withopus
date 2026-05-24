"""Carousel Generator v5.0 - OPUS Editorial System with FLUX backgrounds.

Architecture: FLUX 2 Klein 4B for editorial backgrounds + Pillow typography compositor.
Curated prompts produce clean, dark, minimal backgrounds - no muddy blobs.

v5.0 Changes:
- FLUX 2 Klein 4B via NVIDIA NIM for background generation
- Curated prompts per slide type (cover, hook, content, cta)
- Cached backgrounds (generate once, reuse)
- Pure OPUS palette: Void Black, Amber accent, Warm Cream text
- Solid color blocking + subtle geometric elements
- Swipe continuity system (arrows, numbers flowing across slides)
- Data visualization slides with giant stat numbers
"""

import json, logging, os, random, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageOps
import config
from image_generator import generate_background, get_bg_prompt

logger = logging.getLogger("autopilot.carousel_gen")

# -- Design Tokens (Pure OPUS Palette) --------------------------------
W, H = config.CAROUSEL_SIZE
PAD = 80

# OPUS Brand Colors
VOID_BLACK = (13, 11, 20)        # #0D0B14 - primary background
AMBER = (232, 160, 52)           # #E8A034 - accent
AMBER_DIM = (180, 120, 35)       # muted amber for secondary elements
CREAM = (245, 240, 232)          # #F5F0E8 - primary text
CREAM_DIM = (200, 195, 185)      # muted cream for secondary text
MUTED = (107, 100, 120)          # #6B6478 - labels, captions
SURFACE_DARK = (19, 16, 30)      # #13101E - card backgrounds
SURFACE_MID = (42, 37, 53)       # #2A2535 - borders, dividers

# Geometric constants
ARROW_LEN = 40
ARROW_HEAD = 12
CIRCLE_R = 6
DOT_R = 4

# -- Asset Paths ------------------------------------------------------
BACKGROUNDS_DIR = config.AUTOPILOT_DIR / "assets" / "backgrounds"

# -- Font System ------------------------------------------------------
_fc = {}

def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    key = (str(path), size)
    if key not in _fc:
        try:
            _fc[key] = ImageFont.truetype(str(path), size)
        except OSError:
            _fc[key] = ImageFont.load_default()
    return _fc[key]

def _text_size(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def _wrap(text: str, font, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for w in words:
        test = f"{cur} {w}".strip()
        if _text_size(tmp, test, font)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# -- FLUX Background System -------------------------------------------

def _get_flux_background(slide_type: str, slide_index: int) -> Image.Image:
    """Get a FLUX-generated background, cached on disk.
    
    Uses curated prompts for clean editorial results.
    Falls back to solid black if FLUX fails.
    """
    # Cache path
    variant = slide_index % 3  # 3 prompt variants per type
    cache_name = f"flux_{slide_type}_v{variant}.jpg"
    cache_path = BACKGROUNDS_DIR / cache_name
    
    # Try cached first
    if cache_path.exists():
        try:
            img = Image.open(cache_path).convert("RGB")
            img = ImageOps.fit(img, (W, H), method=Image.LANCZOS)
            # Subtle desaturation for editorial feel
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.8)
            # Darken slightly to ensure text readability
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.7)
            return img
        except Exception as e:
            logger.warning("Cached background load failed: %s", e)
    
    # Generate via FLUX
    try:
        prompt = get_bg_prompt(slide_type, variant)
        logger.info("Generating FLUX background: %s (variant %d)", slide_type, variant)
        generate_background(prompt, str(cache_path), seed=slide_index * 100 + variant)
        
        img = Image.open(cache_path).convert("RGB")
        img = ImageOps.fit(img, (W, H), method=Image.LANCZOS)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.8)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)
        return img
    except Exception as e:
        logger.warning("FLUX generation failed: %s - using solid black", e)
        return Image.new("RGB", (W, H), VOID_BLACK)

# -- Logo -------------------------------------------------------------

def _add_logo(img: Image.Image, pos: str = "top-left", size: int = 40):
    if not config.LOGO_PATH.exists():
        return img
    try:
        logo = Image.open(config.LOGO_PATH).convert("RGBA")
        ratio = size / max(logo.size)
        logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS)
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.6))
        logo.putalpha(alpha)
        
        positions = {
            "top-left": (PAD, 28),
            "top-right": (W - PAD - logo.width, 28),
            "bottom-right": (W - PAD - logo.width, H - PAD - logo.height),
            "bottom-center": ((W - logo.width) // 2, H - PAD - logo.height - 10),
        }
        xy = positions.get(pos, positions["top-left"])
        img.paste(logo, xy, logo)
    except Exception as e:
        logger.warning("Logo overlay failed: %s", e)
    return img

# -- Geometric Elements -----------------------------------------------

def _draw_arrow(draw, x: int, y: int, direction: str = "right", color=AMBER, size: int = ARROW_LEN):
    """Draw a directional arrow."""
    if direction == "right":
        draw.line([(x, y), (x + size - ARROW_HEAD, y)], fill=color, width=2)
        draw.polygon([
            (x + size, y),
            (x + size - ARROW_HEAD, y - ARROW_HEAD // 2),
            (x + size - ARROW_HEAD, y + ARROW_HEAD // 2)
        ], fill=color)
    elif direction == "left":
        draw.line([(x + ARROW_HEAD, y), (x + size, y)], fill=color, width=2)
        draw.polygon([
            (x, y),
            (x + ARROW_HEAD, y - ARROW_HEAD // 2),
            (x + ARROW_HEAD, y + ARROW_HEAD // 2)
        ], fill=color)
    return draw

def _draw_circle(draw, x: int, y: int, radius: int = CIRCLE_R, fill=AMBER, outline=None):
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=fill, outline=outline)
    return draw

def _draw_accent_line(draw, x: int, y: int, width: int = 50, thickness: int = 2, color=AMBER):
    draw.line([(x, y), (x + width, y)], fill=color, width=thickness)
    return draw

def _draw_pill(draw, x: int, y: int, text: str, font, bg=AMBER, fg=VOID_BLACK, pad_x=16, pad_y=8):
    tw, th = _text_size(draw, text, font)
    w, h = tw + pad_x * 2, th + pad_y * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, fill=fg, font=font)
    return w, h

# -- Header / Footer --------------------------------------------------

def _add_header(draw, label: str = None):
    """Top-left brand stamp."""
    f = _font(config.FONT_SEMIBOLD, 14)
    draw.text((PAD, 30), config.BRAND_NAME.upper(), fill=MUTED, font=f)
    if label:
        lf = _font(config.FONT_REGULAR, 11)
        draw.text((PAD, 48), label.upper(), fill=(*MUTED[:2], 100), font=lf)

def _add_footer(draw, slide_idx: int, total: int):
    """Bottom bar: pagination + handle."""
    dot_spacing = 14
    start_x = PAD
    y = H - 40
    for i in range(total):
        cx = start_x + i * dot_spacing
        if i == slide_idx:
            _draw_circle(draw, cx, y, DOT_R, fill=AMBER)
        else:
            _draw_circle(draw, cx, y, DOT_R, fill=(*MUTED, 80))
    
    # Swipe indicator arrow on non-last slides
    if slide_idx < total - 1:
        _draw_arrow(draw, W - PAD - 50, y, "right", color=(*AMBER, 120), size=20)
    
    # Handle
    f = _font(config.FONT_REGULAR, 12)
    tw, _ = _text_size(draw, config.BRAND_HANDLE, f)
    draw.text((W - PAD - tw, H - 38), config.BRAND_HANDLE, fill=(*MUTED, 120), font=f)

# -- Text Helpers -----------------------------------------------------

def _draw_text(draw, pos, text, font, fill=CREAM, shadow=False):
    x, y = pos
    if shadow:
        draw.text((x + 1, y + 1), text, fill=(0, 0, 0), font=font)
    draw.text((x, y), text, fill=fill, font=font)

# -- Slide Builders ---------------------------------------------------

def _build_cover(title: str, slide_idx: int, total: int, label: str = None) -> Image.Image:
    """Slide 1: Bold title + swipe trigger."""
    bg = _get_flux_background("cover", slide_idx)
    draw = ImageDraw.Draw(bg)
    
    _add_logo(bg, "top-left", 36)
    _add_header(draw, label)
    
    # Title - large, bottom-left anchored
    tf = _font(config.FONT_BOLD, 64)
    lines = _wrap(title, tf, W - PAD * 2 - 80)
    lh = 76
    sy = H - PAD - len(lines) * lh - 120
    
    # Accent line above title
    _draw_accent_line(draw, PAD, sy - 20, width=40, thickness=3)
    
    for i, ln in enumerate(lines):
        _draw_text(draw, (PAD, sy + i * lh), ln, tf)
    
    # Swipe trigger
    bf = _font(config.FONT_SEMIBOLD, 13)
    _draw_pill(draw, W - PAD - 100, H - PAD - 28, "NEXT", bf)
    _draw_arrow(draw, W - PAD - 110, H - PAD - 20, "right", color=AMBER, size=20)
    
    _add_footer(draw, slide_idx, total)
    return bg


def _build_hook(text: str, slide_idx: int, total: int, label: str = None) -> Image.Image:
    """Slide 2: Provocative hook statement."""
    bg = _get_flux_background("hook", slide_idx)
    # Darken for text readability
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)
    
    _add_logo(bg, "top-left", 36)
    _add_header(draw, label)
    
    # Large quotation mark
    qm_font = _font(config.FONT_BOLD, 90)
    _draw_text(draw, (PAD, PAD + 10), '"', qm_font, fill=(*AMBER, 80))
    
    # Hook text
    qf = _font(config.FONT_BOLD, 42)
    lines = _wrap(text, qf, W - PAD * 2 - 60)
    lh = 54
    sy = PAD + 70
    
    for i, ln in enumerate(lines):
        _draw_text(draw, (PAD + 30, sy + i * lh), ln, qf)
    
    # Accent line after
    last_y = sy + len(lines) * lh + 14
    _draw_accent_line(draw, PAD + 30, last_y, width=50, thickness=2)
    
    _add_footer(draw, slide_idx, total)
    return bg


def _build_content(heading: str, body: str, step_num: int,
                   slide_idx: int, total: int, label: str = None) -> Image.Image:
    """Slide 3-N: Content steps with geometric structure."""
    bg = _get_flux_background("content", slide_idx)
    draw = ImageDraw.Draw(bg)
    
    _add_logo(bg, "top-left", 36)
    _add_header(draw, label)
    
    # Large step number - top-right, subtle
    nf = _font(config.FONT_BOLD, 100)
    num_text = f"{step_num:02d}"
    _draw_text(draw, (W - PAD - 20, PAD - 10), num_text, nf, fill=(*AMBER, 25))
    
    # Content card
    card_x1 = PAD
    card_x2 = W - PAD
    card_y1 = int(H * 0.32)
    
    hf = _font(config.FONT_BOLD, 36)
    bdf = _font(config.FONT_REGULAR, 19)
    sf = _font(config.FONT_SEMIBOLD, 12)
    
    inner_w = card_x2 - card_x1 - 50
    
    hlines = _wrap(heading, hf, inner_w)
    hlh = 46
    heading_h = len(hlines) * hlh
    
    body_lines = []
    body_h = 0
    if body:
        body_lines = _wrap(body[:160], bdf, inner_w - 10)
        body_h = len(body_lines[:4]) * 28 + 10
    
    badge_text = f"STEP {step_num:02d}"
    _, badge_h = _text_size(draw, badge_text, sf)
    badge_total = badge_h + 20
    
    content_h = badge_total + heading_h + body_h + 36
    card_y2 = card_y1 + content_h
    
    # Card background
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=2, fill=SURFACE_DARK)
    # Top accent border
    draw.line([(card_x1, card_y1), (card_x1 + 50, card_y1)], fill=AMBER, width=2)
    
    # Step badge
    _draw_pill(draw, card_x1 + 20, card_y1 + 16, badge_text, sf, bg=AMBER, fg=VOID_BLACK, pad_x=12, pad_y=6)
    
    # Heading
    hy = card_y1 + 16 + badge_total + 6
    for i, ln in enumerate(hlines):
        _draw_text(draw, (card_x1 + 20, hy + i * hlh), ln, hf)
    
    # Body
    if body_lines:
        bdy = hy + len(hlines) * hlh + 10
        for i, ln in enumerate(body_lines[:4]):
            _draw_text(draw, (card_x1 + 20, bdy + i * 28), ln, bdf, fill=CREAM_DIM)
    
    # Arrow at bottom-right
    if slide_idx < total - 1:
        _draw_arrow(draw, W - PAD - 50, card_y2 - 20, "right", color=(*AMBER, 100), size=24)
    
    _add_footer(draw, slide_idx, total)
    return bg


def _build_data_slide(stat: str, label: str, context: str,
                      slide_idx: int, total: int, label_tag: str = None) -> Image.Image:
    """Data visualization slide - large number as visual anchor."""
    bg = _get_flux_background("content", slide_idx)
    draw = ImageDraw.Draw(bg)
    
    _add_logo(bg, "top-left", 36)
    _add_header(draw, label_tag)
    
    nf = _font(config.FONT_BOLD, 140)
    match = re.match(r"(\d+\.?\d*)(.*)", stat.strip())
    if match:
        num_part = match.group(1)
        suffix = match.group(2)
    else:
        num_part = stat
        suffix = ""
    
    num_tw, num_th = _text_size(draw, num_part, nf)
    sx = PAD
    sy = int(H * 0.3)
    
    _draw_text(draw, (sx, sy), num_part, nf)
    
    if suffix:
        sf = _font(config.FONT_BOLD, 60)
        _draw_text(draw, (sx + num_tw + 8, sy + num_th - 60), suffix, sf, fill=AMBER)
    
    lf = _font(config.FONT_BOLD, 28)
    _draw_text(draw, (sx, sy + num_th + 20), label, lf)
    
    if context:
        cf = _font(config.FONT_REGULAR, 18)
        ctx_lines = _wrap(context, cf, W - PAD * 2)
        cy = sy + num_th + 60
        for i, ln in enumerate(ctx_lines[:3]):
            _draw_text(draw, (sx, cy + i * 28), ln, cf, fill=CREAM_DIM)
    
    _draw_accent_line(draw, sx, cy + len(ctx_lines[:3]) * 28 + 16, width=40)
    
    _add_footer(draw, slide_idx, total)
    return bg


def _build_cta(slide_idx: int, total: int, cta_text: str = "FOLLOW",
               cta_sub: str = None) -> Image.Image:
    """Final slide: CTA with brand moment."""
    bg = _get_flux_background("cta", slide_idx)
    # Subtle center vignette
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for r in range(500, 0, -2):
        a = int(40 * (r / 500))
        vd.ellipse([W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r], fill=(0, 0, 0, a))
    bg = Image.alpha_composite(bg.convert("RGBA"), vig).convert("RGB")
    draw = ImageDraw.Draw(bg)
    
    # Small label
    lf = _font(config.FONT_REGULAR, 16)
    lt = "Want this for your brand?"
    tw, _ = _text_size(draw, lt, lf)
    _draw_text(draw, ((W - tw) // 2, H // 2 - 90), lt, lf, fill=CREAM_DIM)
    
    # Main CTA
    cf = _font(config.FONT_BOLD, 68)
    ctw, _ = _text_size(draw, cta_text, cf)
    _draw_text(draw, ((W - ctw) // 2, H // 2 - 35), cta_text, cf)
    
    # Handle in amber
    hf = _font(config.FONT_SEMIBOLD, 24)
    tw, _ = _text_size(draw, config.BRAND_HANDLE, hf)
    _draw_text(draw, ((W - tw) // 2, H // 2 + 45), config.BRAND_HANDLE, hf, fill=AMBER)
    
    # Accent line under handle
    _draw_accent_line(draw, (W - 40) // 2, H // 2 + 78, width=40)
    
    if cta_sub:
        sf = _font(config.FONT_REGULAR, 14)
        st = cta_sub
        tw, _ = _text_size(draw, st, sf)
        _draw_text(draw, ((W - tw) // 2, H // 2 + 98), st, sf, fill=CREAM_DIM)
    
    _add_logo(bg, "bottom-center", 44)
    
    _add_footer(draw, slide_idx, total)
    return bg

# -- Main Generator ---------------------------------------------------

def generate_carousel(content: dict, draft_id: str) -> list[Path]:
    """Generate a complete carousel from content dict."""
    carousel_dir = config.CAROUSELS_DIR / draft_id
    carousel_dir.mkdir(parents=True, exist_ok=True)
    
    slides_data = content.get("slides", [])
    data_slides = content.get("data_slides", [])
    hook = content.get("hook", "")
    
    while len(slides_data) < 2:
        slides_data.append({"heading": "Key Insight", "body": "More coming soon."})
    
    logger.info("Generating OPUS carousel: %s", content["title"][:40])
    
    total = 1
    if hook:
        total += 1
    total += min(len(slides_data), 4)
    total += len(data_slides)
    total += 1
    
    images: list[Image.Image] = []
    idx = 0
    
    images.append(_build_cover(content["title"], idx, total))
    idx += 1
    
    if hook:
        images.append(_build_hook(hook, idx, total))
        idx += 1
    
    for i, s in enumerate(slides_data[:4], 1):
        images.append(_build_content(
            s["heading"], s.get("body", ""), i, idx, total
        ))
        idx += 1
    
    for ds in data_slides:
        images.append(_build_data_slide(
            ds["stat"], ds["label"], ds.get("context", ""), idx, total
        ))
        idx += 1
    
    images.append(_build_cta(idx, total))
    
    paths = []
    for i, img in enumerate(images, 1):
        path = carousel_dir / f"slide_{i}.jpg"
        img.save(str(path), "JPEG", quality=config.CAROUSEL_QUALITY)
        paths.append(path)
        logger.info("Saved slide %d -> %s", i, path.name)
    
    return paths


def generate_carousel_for_draft(draft: dict) -> list[Path]:
    """Generate carousel from a draft dict and update it."""
    content = {
        "title": draft["title"],
        "slides": draft["slides"],
        "hook": draft.get("hook", ""),
        "data_slides": draft.get("data_slides", []),
    }
    paths = generate_carousel(content, draft["id"])
    
    draft["images_generated"] = True
    draft["image_paths"] = [str(p) for p in paths]
    draft_path = config.DRAFTS_DIR / f"{draft['id']}.json"
    draft_path.write_text(json.dumps(draft, indent=2), encoding="utf-8")
    return paths

# -- Test -------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    test_content = {
        "title": "Your Brand Looks Like Everyone Else",
        "hook": "Most brands post content. We build identity.",
        "slides": [
            {"heading": "Templates kill recognition", "body": "When every brand uses the same Canva templates, nobody remembers yours. Build from scratch."},
            {"heading": "Consistency beats volume", "body": "Posting daily with no visual system is noise. Posting weekly with intention is signal."},
            {"heading": "Identity compounds", "body": "A visual system that repeats becomes recognizable. Recognition becomes trust. Trust becomes revenue."},
        ],
    }
    paths = generate_carousel(test_content, "test_v5_flux")
    print(f"\nGenerated {len(paths)} slides:")
    for p in paths:
        print(f"  {p}")
