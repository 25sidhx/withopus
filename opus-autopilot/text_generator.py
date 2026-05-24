"""Carousel Text Generator - outputs JSON for Nano Banana Pro.

Takes a topic or scraped content and generates slide-by-slide text
optimized for manual image generation in Nano Banana Pro.

Each slide text is under 200 words. Includes visual direction hints.
Integrated with OPUS brand context from MD files.
"""

import json, logging, hashlib, re
from datetime import datetime
from pathlib import Path

import config
from openai import OpenAI
from brand_context import load_brand_context, get_brand_prompt_addition

logger = logging.getLogger("autopilot.text_gen")

# -- AI Client --------------------------------------------------------

def _get_ai_client() -> OpenAI:
    return OpenAI(
        base_url=config.NVIDIA_BASE_URL,
        api_key=config.NVIDIA_API_KEY,
    )

# -- Slide Text Generation --------------------------------------------

def _build_system_prompt() -> str:
    """Build system prompt with brand context."""
    ctx = load_brand_context()
    
    return f"""You are a GENIUS content strategist for {ctx['brand_name']}, a premium creative agency in {ctx['location']}.

Your job: create Instagram carousel slide text that is sharp, minimal, and on-brand.

BRAND VOICE RULES:
- Short sentences. One idea at a time.
- Confident statements, not qualified opinions.
- Warm but professional. No corporate jargon.
- Say less than you think you need to.
- Lead with insight, not promotion.
- NEVER use: {', '.join(ctx['words_to_avoid'])}
- USE words like: {', '.join(ctx['words_to_use'])}

VISUAL DIRECTION RULES FOR NANO BANANA PRO:
- Background: ALWAYS dark near-black ({ctx['colors']['void_black']})
- Accent: ALWAYS amber ({ctx['colors']['amber']}) for highlights, arrows, pills
- Text: ALWAYS warm cream ({ctx['colors']['warm_cream']}) for primary
- Composition: Minimal, one focal point, 80px safe zone
- Elements: Arrows (→), circles, accent lines, geometric shapes
- NEVER suggest: bright backgrounds, neon colors, busy compositions, light mode

OUTPUT FORMAT:
- Each slide text MUST be under 200 words
- Slide 1: Hook/cover - provocative statement or question
- Slides 2-N: Value delivery - one insight per slide
- Final slide: CTA - soft, not pushy
- Visual directions must be specific and actionable for image generation
"""


def _build_user_prompt(topic: str, num_slides: int, audience: str) -> str:
    """Build user prompt with topic and visual examples."""
    ctx = load_brand_context()
    
    return f"""Create a {num_slides}-slide Instagram carousel about: {topic}

Target audience: {audience}

OPUS VISUAL SYSTEM (use these for visual_direction field):
- Background: Dark near-black ({ctx['colors']['void_black']})
- Accent: Amber ({ctx['colors']['amber']})
- Text: Warm cream ({ctx['colors']['warm_cream']})
- Composition: Minimal, one focal point, geometric elements

VISUAL DIRECTION EXAMPLES:
- "Dark near-black background, subtle amber light streak from bottom-left, minimal composition, no text in background"
- "Dark background with faint amber circle outline top-right, clean negative space, editorial mood"
- "Near-black background with subtle amber dot grid pattern, minimal geometric, premium brand aesthetic"
- "Dark background with warm amber center glow, cinematic editorial, no text in background"
- "Dark near-black background, subtle amber accent line bottom-left, one focal point"

Output ONLY valid JSON with this exact structure:

{{
  "title": "The carousel title (max 8 words)",
  "slides": [
    {{
      "slide_number": 1,
      "type": "cover",
      "text": "The text for this slide (under 200 words)",
      "visual_direction": "Dark near-black background, subtle amber light streak from bottom-left, minimal composition"
    }},
    {{
      "slide_number": 2,
      "type": "content",
      "text": "The text for this slide (under 200 words)",
      "visual_direction": "Dark background with faint amber circle outline top-right, clean negative space"
    }}
  ],
  "caption": "Instagram caption (under 200 words, with soft CTA)",
  "hashtags": "#tag1 #tag2 #tag3 #tag4 #tag5"
}}

Output ONLY the JSON object, no markdown, no extra text.
"""

def generate_carousel_text(topic: str, num_slides: int = 6, audience: str = "small business owners and creators") -> dict | None:
    """Generate carousel slide text as JSON.
    
    Args:
        topic: What the carousel is about
        num_slides: Number of slides (default 6)
        audience: Target audience description
    
    Returns:
        Dict with carousel structure, or None on failure
    """
    client = _get_ai_client()
    
    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(topic, num_slides, audience)
    
    try:
        resp = client.chat.completions.create(
            model=config.NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        raw = resp.choices[0].message.content.strip()
        
        # Strip markdown code fences
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        
        data = json.loads(raw)
        
        # Validate structure
        if "slides" not in data or "title" not in data:
            logger.error("AI output missing required keys")
            return None
        
        # Validate word counts
        for slide in data["slides"]:
            word_count = len(slide.get("text", "").split())
            if word_count > 200:
                logger.warning("Slide %d exceeds 200 words (%d words)", slide["slide_number"], word_count)
        
        return data
        
    except json.JSONDecodeError as e:
        logger.error("AI returned invalid JSON: %s\n%s", e, raw[:500])
        return None
    except Exception as e:
        logger.error("Text generation failed: %s", e)
        return None

# -- Save/Load --------------------------------------------------------

def save_carousel_text(data: dict, filename: str = None) -> Path:
    """Save carousel text to JSON file."""
    if filename is None:
        topic_slug = data.get("title", "carousel").lower().replace(" ", "_")[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{timestamp}_{topic_slug}.json"
    
    output_path = config.DRAFTS_DIR / filename
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved carousel text: %s", output_path)
    return output_path

def load_carousel_text(filepath: str | Path) -> dict | None:
    """Load carousel text from JSON file."""
    path = Path(filepath)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None

# -- From Scraped Content ---------------------------------------------

def generate_from_scraped(scraped_caption: str, source: str = None, num_slides: int = 6) -> dict | None:
    """Generate carousel text from a scraped Instagram caption.
    
    Rewrites the scraped content into OPUS brand voice with full brand context.
    """
    client = _get_ai_client()
    ctx = load_brand_context()
    
    system = f"""You are a GENIUS content strategist for {ctx['brand_name']}.
    
    Take an Instagram caption from another account and transform it into
    a BRAND-NEW carousel for {ctx['handle']}.
    
    BRAND VOICE RULES:
    - NEVER copy text verbatim. Rewrite completely in Opus brand voice.
    - Tone: professional, warm, cinematic. No cringe, no corporate jargon.
    - Each slide text MUST be under 200 words.
    - Short sentences. One idea at a time.
    - Confident statements, not qualified opinions.
    - NEVER use: {', '.join(ctx['words_to_avoid'])}
    
    VISUAL DIRECTION RULES FOR NANO BANANA PRO:
    - Background: ALWAYS dark near-black ({ctx['colors']['void_black']})
    - Accent: ALWAYS amber ({ctx['colors']['amber']}) for highlights
    - Text: ALWAYS warm cream ({ctx['colors']['warm_cream']})
    - Composition: Minimal, one focal point, geometric elements
    - NEVER suggest: bright backgrounds, neon colors, busy compositions
    """
    
    user = f"""Here is the original caption from @{source or 'unknown'}:

---
{scraped_caption[:1000]}
---

Transform this into a {num_slides}-slide carousel for {ctx['brand_name']}.

OPUS VISUAL SYSTEM:
- Background: Dark near-black ({ctx['colors']['void_black']})
- Accent: Amber ({ctx['colors']['amber']})
- Text: Warm cream ({ctx['colors']['warm_cream']})
- Composition: Minimal, one focal point, geometric elements

VISUAL DIRECTION EXAMPLES:
- "Dark near-black background, subtle amber light streak from bottom-left, minimal composition"
- "Dark background with faint amber circle outline top-right, clean negative space"
- "Near-black background with subtle amber dot grid pattern, minimal geometric"
- "Dark background with warm amber center glow, cinematic editorial"

Output ONLY valid JSON:

{{
  "title": "The catchy cover-slide title (max 8 words)",
  "slides": [
    {{"slide_number": 1, "type": "cover", "text": "Slide text under 200 words", "visual_direction": "Dark near-black background, subtle amber light streak, minimal composition"}},
    {{"slide_number": 2, "type": "content", "text": "Slide text under 200 words", "visual_direction": "Dark background with faint amber circle outline, clean negative space"}}
  ],
  "caption": "Instagram caption under 200 words",
  "hashtags": "#tag1 #tag2 #tag3 #tag4 #tag5"
}}

Output ONLY the JSON object, no markdown, no extra text.
"""
    
    try:
        resp = client.chat.completions.create(
            model=config.NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        raw = resp.choices[0].message.content.strip()
        
        import re
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        
        return json.loads(raw)
        
    except Exception as e:
        logger.error("Scraped content rewrite failed: %s", e)
        return None

# -- Master Image Generation Prompt ----------------------------------

# The premium OPUS master prompt template (static portion)
_MASTER_PROMPT_TEMPLATE = """\
You are generating a PREMIUM editorial carousel image grid for the OPUS brand.

The output must look like a luxury creative agency campaign — NOT generic AI social media posts.

Style references:
* Swiss editorial design · Modern startup branding · Motion-aware layouts
* High-end typography · Minimal but bold · Modular storytelling
* Asymmetric grids · Premium spacing · Swipe-continuation visual language

The generated image MUST contain:
* ONE SINGLE CANVAS containing 6 connected slide panels
* Arranged in a clean 3×2 grid (3 columns, 2 rows)
* Each panel visually connected with shared visual rhythm
* Continuation elements between panels

---

VISUAL STYLE

Design feeling:
* Futuristic but elegant · Cinematic minimalism · Premium startup aesthetic
* Black / cream / graphite / warm gray palette
* Selective accent colors only · Subtle brutalism · Motion-inspired composition

Typography:
* Bold editorial sans serif mixed with elegant serif accents
* Oversized type hierarchy · Clean spacing · Modern agency feel

Graphics:
* Arrows · circles · data fragments · geometric symbols
* Abstract UI elements · connected lines · oversized numbers
* Partial cropped shapes

---

SWIPE CONTINUITY RULES

The 6 panels MUST visually flow together:
* Shapes continue into neighboring panels
* Typography evolves between frames
* Visual objects partially enter/exit panels
* Directional movement implied
* Shared grid alignment and lighting atmosphere

It should feel like: "one large moving canvas cut into 6 slides."

---

CONTENT STYLE

Use: strategic statements · bold startup insights · intelligent marketing copy
     modern business messaging · minimal but impactful text

Avoid: motivational cringe · generic startup quotes · overused AI phrases
       cluttered layouts · Canva-looking designs

---

IMAGE QUALITY

Generate:
* Ultra high detail · clean typography · realistic layout spacing
* Premium editorial composition · sharp vector-like appearance
* Realistic print-grade quality · high contrast · visually balanced hierarchy

The final output must feel: designed by elite designers, not AI.

---

OUTPUT FORMAT

* ONE single image containing 6 connected carousel slides
* High resolution · clean margins for cropping later
* Crop-safe layout · optimized for Instagram carousel splitting
* Each panel: square aspect ratio (1:1), mobile-first readability

---

AGGRESSIVE VERSION (apply this energy):

Design it like:
* Elite Swiss editorial branding · Cinematic startup advertising
* Apple-level visual hierarchy · Motion-first composition
* Luxury creative agency campaign

Every panel must connect with neighbors using:
* Continuing shapes · Typography progression · Motion direction
* Split objects · Flowing composition

Avoid:
* Canva aesthetics · Centered layouts · Startup cliché graphics
* Bad typography · Generic gradients · AI-looking compositions\
"""


def build_master_prompt(topic: str, slides: list[dict], caption: str = "") -> str:
    """Build the full image generation prompt for Telegram delivery.

    Injects topic + per-slide content into the static master template.

    Args:
        topic:   Carousel topic/title.
        slides:  List of slide dicts from generate_carousel_text().
        caption: Instagram caption (appended for reference).

    Returns:
        A single string ready to copy-paste into Midjourney / Flux / DALL-E.
    """
    # Build the panel content specification
    panel_lines = []
    type_label = {
        "cover": "HOOK/COVER",
        "content": "CONTENT",
        "hook": "HOOK",
        "call_to_action": "CTA",
        "cta": "CTA",
    }
    for slide in slides:
        num = slide.get("slide_number", len(panel_lines) + 1)
        stype = type_label.get(slide.get("type", "content"), "CONTENT")
        text = slide.get("text", "").replace("\n", " ").strip()
        # Keep text concise in the prompt
        if len(text) > 120:
            text = text[:117] + "..."
        panel_lines.append(f"Panel {num:02d} ({stype}): \"{text}\"")

    panels_spec = "\n".join(panel_lines)

    prompt = f"""\
# OPUS CAROUSEL GENERATION PROMPT
# Topic: {topic.upper()}

## PANEL CONTENT (what each slide must convey):
{panels_spec}

---

## VISUAL DIRECTION
Topic atmosphere: {topic}
Make the visual hierarchy and composition reinforce this message.
Every panel should feel like part of one unified editorial statement.

Color palette for THIS carousel:
* Background: near-black (#0D0B14) with subtle warm undertone
* Accent: amber (#E8A034) used sparingly for 1–2 highlighted words or shapes
* Text: warm cream (#F5F0E8) for primary copy
* Secondary: graphite gray (#2A2A2A) for panel divisions and subtle elements

Typography direction:
* Panels 01–02: oversized, bold, minimal — the hook must dominate
* Panels 03–05: medium weight editorial, content-driven
* Panel 06: soft CTA, lighter weight, inviting not pushy

---

## MASTER PROMPT
{_MASTER_PROMPT_TEMPLATE}
"""
    return prompt.strip()


# -- CLI --------------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python text_generator.py <topic> [num_slides]")
        print("Example: python text_generator.py 'Why templates kill your brand' 6")
        sys.exit(1)
    
    topic = sys.argv[1]
    num_slides = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    
    print(f"\nGenerating {num_slides}-slide carousel about: {topic}\n")
    
    data = generate_carousel_text(topic, num_slides)
    
    if data:
        path = save_carousel_text(data)
        print(f"\nSaved to: {path}")
        print(f"\nTitle: {data['title']}")
        print(f"Slides: {len(data['slides'])}")
        print(f"\n--- Slide Preview ---")
        for slide in data["slides"]:
            print(f"\nSlide {slide['slide_number']} ({slide['type']}):")
            print(f"  Text: {slide['text'][:100]}...")
            print(f"  Visual: {slide['visual_direction']}")
        print(f"\nCaption: {data.get('caption', '')[:100]}...")
        print(f"Hashtags: {data.get('hashtags', '')}")
    else:
        print("Failed to generate carousel text.")
