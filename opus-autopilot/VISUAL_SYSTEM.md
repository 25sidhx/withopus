# OPUS Carousel Visual System v5.0

## Architecture

FLUX 2 Klein 4B (NVIDIA NIM) generates editorial backgrounds + Pillow composites typography.

**Key: 1024x1024 generation, cropped to 1080x1080. Backgrounds cached on disk after first generation.**

---

## What Changed from v4.0

| v4.0 | v5.0 |
|---|---|
| Local image library | FLUX 2 Klein 4B via NVIDIA NIM |
| Procedural geometric fallbacks | FLUX with curated prompts |
| Manual image curation | Auto-generated per carousel |
| No API dependency | NVIDIA API key required |

---

## FLUX Setup

**Endpoint:** `https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b`
**Dimensions:** 1024x1024 (max pixel count: 1,062,400)
**Steps:** 4 (fast generation)
**Cached:** Yes - backgrounds saved to `assets/backgrounds/flux_{type}_v{variant}.jpg`

**API Key:** Set via `NVIDIA_API_KEY` env var or in `config.py`

---

## Color System (Pure OPUS)

```
VOID_BLACK  #0D0B14  (13, 11, 20)   - All backgrounds
AMBER       #E8A034  (232, 160, 52)  - Accent, arrows, pills, numbers
AMBER_DIM   (180, 120, 35)           - Secondary accents
CREAM       #F5F0E8  (245, 240, 232) - Primary text
CREAM_DIM   (200, 195, 185)          - Body text
MUTED       #6B6478  (107, 100, 120) - Labels, captions
SURFACE_DARK #13101E (19, 16, 30)    - Card backgrounds
```

---

## FLUX Background Prompts

Each slide type has 3 prompt variants that cycle:

### Cover Backgrounds
- Dark near-black with subtle warm amber light streak
- Deep charcoal with faint amber gradient glow from bottom-left
- Black with soft warm amber bokeh blur in center

### Hook Backgrounds
- Dark textured with subtle amber light from top-left
- Near-black with faint warm amber rim light
- Dark with subtle amber light leak effect

### Content Backgrounds
- Dark with subtle geometric amber line accent
- Near-black with faint amber circle outline
- Dark with subtle amber dot grid pattern
- Black with subtle amber horizontal line accent
- Dark with faint amber diagonal line
- Near-black with subtle amber corner rectangle outline

### CTA Backgrounds
- Dark with warm amber center glow
- Near-black with subtle amber radial gradient from center
- Dark with faint amber light burst from center

---

## Slide Types

### 1. Cover (Slide 1)
- FLUX dark background with amber light
- Title anchored bottom-left, large bold
- Accent line above title
- "NEXT" pill + arrow bottom-right

### 2. Hook (Slide 2, optional)
- FLUX dark background with amber rim light
- Large quotation mark top-left in amber
- Provocative statement left-aligned
- Accent line after text

### 3. Content (Slides 3-N)
- FLUX background with geometric elements
- Large step number (01, 02, 03) top-right, subtle
- Solid dark card with amber top-border accent
- Step badge pill
- Heading + body text
- Arrow at bottom-right pointing to next slide

### 4. Data (Optional slides)
- Giant stat number (84%, 2.4K) as visual anchor
- Label below stat
- Context text

### 5. CTA (Final slide)
- FLUX background with amber center glow
- Centered "FOLLOW" text
- @with_opus in amber
- Logo bottom-center

---

## Swipe Continuity System

| Element | How it continues |
|---|---|
| Step numbers | 01, 02, 03 top-right on content slides |
| Arrows | Right arrow at bottom-right of content slides |
| Accent lines | Consistent position across slides |
| Pagination dots | Bottom-left, amber for current slide |
| Brand stamp | Top-left on every slide |

---

## Geometric Language

| Element | Purpose |
|---|---|
| Arrow | Direction, swipe trigger |
| Circle/dot | Pagination, bullet points |
| Accent line | Visual hierarchy, section break |
| Pill badge | Step labels, CTAs |
| Large number | Data visualization anchor |

---

## Typography

| Element | Font | Weight | Size |
|---|---|---|---|
| Cover title | Satoshi | Bold | 64px |
| Hook text | Satoshi | Bold | 42px |
| Content heading | Satoshi | Bold | 36px |
| Body text | Inter | Regular | 19px |
| Step number | Satoshi | Bold | 100px |
| Stat number | Satoshi | Bold | 140px |
| Labels | Inter | SemiBold | 12px |
| Brand stamp | Inter | SemiBold | 14px |

---

## Content Structure (for AI/drafts)

```json
{
  "title": "Cover headline (max 8 words)",
  "hook": "Provocative 1-sentence hook (optional)",
  "slides": [
    {"heading": "3-5 words", "body": "2-3 sentences"},
    {"heading": "3-5 words", "body": "2-3 sentences"},
    {"heading": "3-5 words", "body": "2-3 sentences"}
  ],
  "data_slides": [
    {"stat": "84%", "label": "Short label", "context": "Supporting text"}
  ],
  "caption": "Instagram caption",
  "hashtags": "#tag1 #tag2"
}
```

---

## What Makes It Premium

- FLUX editorial backgrounds - dark, minimal, amber accents
- Solid color blocking - not muddy gradients
- Geometric directionals - arrows guide the eye
- Data as design - numbers ARE the visual anchor
- Swipe continuity - elements flow across slides
- OPUS palette enforced - no color drift
- One focal point per slide
- 80px safe zone - generous breathing room

## What Destroys the Premium Feel

- AI-generated blob backgrounds (fixed with curated prompts)
- Glassmorphism floating on nothing
- Centered everything
- Rainbow/neon colors
- Cluttered compositions
- Template-looking layouts
- Generic motivational text
- Poor typography spacing

---

## Performance Notes

- First carousel: ~30-60s (FLUX generates 6 backgrounds)
- Subsequent carousels: ~2-5s (backgrounds cached)
- Cache location: `assets/backgrounds/flux_{type}_v{variant}.jpg`
- To regenerate backgrounds: delete cache files
