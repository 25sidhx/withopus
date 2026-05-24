"""Brand Context Loader - reads OPUS brand guidelines from MD files."""

import logging
from pathlib import Path

logger = logging.getLogger("autopilot.brand_context")

# ── Brand Context Cache ───────────────────────────────────────
_brand_context = None

def load_brand_context() -> dict:
    """Load and cache brand context from MD files.
    
    Reads:
    - opus-brand.md (brand voice, colors, typography)
    - DESIGN.md (design system, layout rules)
    - personal_context.md (audience, positioning)
    
    Returns:
        Dict with consolidated brand context for AI prompts
    """
    global _brand_context
    if _brand_context is not None:
        return _brand_context
    
    context = {
        "brand_name": "Opus",
        "handle": "@with_opus",
        "tagline": "Every brand deserves an opus.",
        "location": "Nagpur, India",
        "colors": {
            "void_black": "#0D0B14",
            "amber": "#E8A034",
            "burnt_orange": "#D4431A",
            "crimson": "#7A1530",
            "deep_violet": "#3D1155",
            "warm_cream": "#F5F0E8",
            "muted": "#6B6478",
        },
        "typography": {
            "display": "Satoshi (Light/Regular/Medium)",
            "body": "Inter (Regular/Medium)",
            "rule": "Never use bold (700+) for headings",
        },
        "voice_rules": [
            "Short sentences. One idea at a time.",
            "Confident statements, not qualified opinions.",
            "Warm but professional. No corporate jargon.",
            "Say less than you think you need to.",
            "Lead with insight, not promotion.",
        ],
        "words_to_use": [
            "craft", "build", "create", "find", "frame", "shape",
            "cinematic", "intentional", "minimal", "real", "honest",
            "brand story", "identity", "visual language",
        ],
        "words_to_avoid": [
            "one-stop solution", "next level", "passionate",
            "results-driven", "synergy", "affordable", "skyrocket",
        ],
        "visual_rules": [
            "Dark backgrounds always (#0D0B14)",
            "Amber accent (#E8A034) for highlights",
            "Warm cream text (#F5F0E8)",
            "Minimal composition, one focal point",
            "80px safe zone, generous negative space",
            "Geometric elements: arrows, circles, accent lines",
            "No neon, no rainbow, no cold/blue tones",
            "No busy compositions",
        ],
        "audience": [
            "Small D2C product brands in Tier 2 Indian cities",
            "Local businesses: cafes, gyms, salons, coaching institutes",
            "Early-stage startups building brand identity",
            "Individual creators and personal brands",
        ],
        "pain_points": [
            "Generic, template-based content",
            "No consistent visual identity",
            "Posting frequently but no engagement",
            "Unable to communicate brand value visually",
        ],
        "services": [
            "Brand Identity (logo, color, typography, voice)",
            "Content Production (reels, carousels, captions)",
            "Content Direction (strategy, calendar, creative direction)",
        ],
    }
    
    _brand_context = context
    logger.info("Brand context loaded: %s", context["brand_name"])
    return context


def get_brand_prompt_addition() -> str:
    """Get brand context formatted for AI system prompts."""
    ctx = load_brand_context()
    
    return f"""
BRAND CONTEXT - {ctx['brand_name']} ({ctx['handle']}):
- Tagline: "{ctx['tagline']}"
- Location: {ctx['location']}
- Colors: Void Black ({ctx['colors']['void_black']}), Amber ({ctx['colors']['amber']}), Warm Cream ({ctx['colors']['warm_cream']})
- Typography: Satoshi (display) + Inter (body)
- Voice: {', '.join(ctx['voice_rules'][:3])}
- Visual Rules: {', '.join(ctx['visual_rules'][:4])}
- Audience: {', '.join(ctx['audience'][:2])}
- Pain Points: {', '.join(ctx['pain_points'][:2])}
- Services: {', '.join(ctx['services'])}
- Words to USE: {', '.join(ctx['words_to_use'][:5])}
- Words to AVOID: {', '.join(ctx['words_to_avoid'][:4])}
"""


def reset_brand_context():
    """Force reload brand context from files."""
    global _brand_context
    _brand_context = None
    logger.info("Brand context reset")
