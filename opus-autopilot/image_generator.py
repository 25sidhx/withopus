"""Image Generator - FLUX 2 Klein 4B via NVIDIA NIM."""

import requests, base64, os
from config import NVIDIA_API_KEY

FLUX_ENDPOINT = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.2-klein-4b"

def generate_background(prompt: str, output_path: str, seed: int = 42) -> str:
    """Generate a background image using FLUX 2 Klein 4B.
    
    Args:
        prompt: Image description (keep it clean, no text, no people)
        output_path: Where to save the generated image
        seed: Random seed for reproducibility
    
    Returns:
        Path to the saved image
    """
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "seed": seed,
        "steps": 4
    }
    
    r = requests.post(FLUX_ENDPOINT, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    
    response_body = r.json()
    img_b64 = response_body["artifacts"][0]["base64"]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(img_b64))
    
    return output_path


# ── Curated Background Prompts ──────────────────────────────────
# Each prompt is crafted for FLUX to produce clean, editorial backgrounds.
# No text, no people, no busy compositions.

BG_PROMPTS = {
    "cover": [
        "dark near-black background with subtle warm amber light streak, cinematic editorial, minimal composition, no text, no people, high contrast, premium brand aesthetic, 1:1 square",
        "deep charcoal background with faint amber gradient glow from bottom-left, editorial photography style, clean negative space, no text, no people, luxury minimal",
        "black background with soft warm amber bokeh blur in center, cinematic depth of field, editorial magazine style, no text, no people, premium dark aesthetic",
    ],
    "hook": [
        "dark textured background with subtle amber light from top-left, editorial photography, moody atmosphere, clean composition, no text, no people, premium minimal",
        "near-black background with faint warm amber rim light, cinematic editorial style, dramatic negative space, no text, no people, high-end brand aesthetic",
        "dark background with subtle amber light leak effect, editorial photography, moody and atmospheric, no text, no people, premium minimal composition",
    ],
    "content": [
        "dark background with subtle geometric amber line accent, editorial minimal, clean composition, no text, no people, premium brand aesthetic, 1:1 square",
        "near-black background with faint amber circle outline, editorial photography style, minimal geometric, no text, no people, luxury brand aesthetic",
        "dark background with subtle amber dot grid pattern, editorial minimal, clean negative space, no text, no people, premium aesthetic",
        "black background with subtle amber horizontal line accent, editorial photography, minimal composition, no text, no people, high-end brand style",
        "dark background with faint amber diagonal line, editorial minimal, clean composition, no text, no people, premium brand aesthetic",
        "near-black background with subtle amber corner rectangle outline, editorial photography, minimal geometric, no text, no people, luxury aesthetic",
    ],
    "cta": [
        "dark background with warm amber center glow, cinematic editorial, minimal composition, no text, no people, premium brand aesthetic, 1:1 square",
        "near-black background with subtle amber radial gradient from center, editorial photography style, clean negative space, no text, no people, luxury minimal",
        "dark background with faint amber light burst from center, cinematic editorial, moody atmosphere, no text, no people, premium brand aesthetic",
    ],
}

def get_bg_prompt(category: str, variant: int = 0) -> str:
    """Get a curated FLUX prompt for a background category.
    
    Args:
        category: One of 'cover', 'hook', 'content', 'cta'
        variant: Which prompt variant to use (cycles through available)
    
    Returns:
        A FLUX prompt string
    """
    prompts = BG_PROMPTS.get(category, BG_PROMPTS["content"])
    return prompts[variant % len(prompts)]
