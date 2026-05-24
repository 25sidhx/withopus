"""Opus Social Carousel Autopilot — Centralized Configuration.

Secrets are loaded from environment variables ONLY.
Never hardcode credentials here.
Create a .env file from .env.example to run locally.
"""

import os
from pathlib import Path

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # dotenv optional — use system env vars directly

# ─ Paths ──────────────────────────────────────────────────────
AUTOPILOT_DIR = Path(__file__).parent
DRAFTS_DIR    = AUTOPILOT_DIR / "drafts"
CAROUSELS_DIR = AUTOPILOT_DIR / "carousels"
SESSIONS_DIR  = AUTOPILOT_DIR / "sessions"
DATA_DIR      = AUTOPILOT_DIR / "data"
FONTS_DIR     = AUTOPILOT_DIR / "fonts"
IMAGES_DIR    = AUTOPILOT_DIR / "assets" / "images"
LOGO_PATH     = AUTOPILOT_DIR / "opus_logo.png"

# ── Fonts ──────────────────────────────────────────────────────
FONT_BOLD     = FONTS_DIR / "Inter-Bold.ttf"
FONT_REGULAR  = FONTS_DIR / "Inter-Regular.ttf"
FONT_SEMIBOLD = FONTS_DIR / "Inter-SemiBold.ttf"

# ── Telegram ───────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_OWNER_ID  = int(os.environ["TELEGRAM_OWNER_ID"])

# ── AI (NVIDIA NIM — OpenAI-compatible) ───────────────────────
NVIDIA_API_KEY    = os.environ["NVIDIA_API_KEY"]
NVIDIA_BASE_URL   = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL      = "meta/llama-3.1-8b-instruct"
NVIDIA_FLUX_MODEL = "black-forest-labs/flux.2-klein-4b"

# ── Branding ───────────────────────────────────────────────────
BRAND_NAME    = "Opus"
BRAND_HANDLE  = "@with_opus"
BRAND_TAGLINE = "We craft visual stories."
SITE_URL      = "https://withopus.in"
TARGET_CITY   = "Nagpur"

# ── Carousel Design Tokens ─────────────────────────────────────
CAROUSEL_SIZE    = (1080, 1080)
CAROUSEL_BG      = (15, 15, 15)        # rich black  #0F0F0F
CAROUSEL_ACCENT  = (255, 180, 60)      # amber       #FFB43C
CAROUSEL_TEXT    = (240, 240, 240)     # off-white
CAROUSEL_MUTED   = (140, 140, 140)     # body text
CAROUSEL_SLIDES  = 6                   # total slides
CAROUSEL_PADDING = 80                  # px
CAROUSEL_QUALITY = 95                  # JPEG export quality

# ── Scraping ──────────────────────────────────────────────────
# NO Instagram login anymore. Topics are used for AI generation.
CONTENT_TOPICS = [
    "brand identity for small businesses",
    "social media strategy for local brands",
    "why most brands look the same",
    "content consistency vs content volume",
    "visual storytelling for startups",
    "how to build trust through design",
]
SCRAPE_POSTS_PER_ACCOUNT = 8

# ── Scheduling ─────────────────────────────────────────────────
POSTS_PER_DAY = 1

# Create required directories on import
for _d in [DRAFTS_DIR, CAROUSELS_DIR, SESSIONS_DIR, DATA_DIR,
           IMAGES_DIR / "covers", IMAGES_DIR / "editorial",
           IMAGES_DIR / "textures", IMAGES_DIR / "abstract"]:
    _d.mkdir(parents=True, exist_ok=True)
