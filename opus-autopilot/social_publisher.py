"""Social Publisher — packages approved carousels for manual posting.

OLD approach: auto-posted to Instagram via instagrapi → account flagged.
NEW approach: sends a ready-to-post package to Telegram. You post manually.

This is safer, legal, and actually better because:
- Zero risk of account suspension
- You review before posting
- Full control over timing
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger("autopilot.publisher")


def load_draft(draft_id: str) -> dict | None:
    path = config.DRAFTS_DIR / f"{draft_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def save_draft(draft: dict) -> None:
    path = config.DRAFTS_DIR / f"{draft['id']}.json"
    path.write_text(json.dumps(draft, indent=2), encoding="utf-8")


def build_post_package(draft_id: str) -> dict | None:
    """Build a complete post package ready for manual Instagram posting.

    Returns a dict with:
        - caption: full Instagram caption with hashtags
        - slide_paths: list of image file paths
        - instructions: step-by-step posting guide
    """
    draft = load_draft(draft_id)
    if not draft:
        logger.error("Draft not found: %s", draft_id)
        return None

    if not draft.get("images_generated"):
        logger.error("Images not generated yet for draft %s", draft_id)
        return None

    image_paths = draft.get("image_paths", [])
    if not image_paths or not all(Path(p).exists() for p in image_paths):
        logger.error("Carousel images missing for draft %s", draft_id)
        return None

    caption = draft.get("caption", "")
    hashtags = draft.get("hashtags", "")
    full_caption = f"{caption}\n\n{hashtags}".strip()

    instructions = (
        "📲 *HOW TO POST ON INSTAGRAM*\n\n"
        "1️⃣ Save all slide images to your phone\n"
        "2️⃣ Open Instagram → Tap + → Post\n"
        "3️⃣ Select all 6 slides IN ORDER (left to right)\n"
        "4️⃣ Paste the caption below\n"
        "5️⃣ Tag location: Nagpur, Maharashtra\n"
        "6️⃣ Post during peak hours (7–9pm IST)\n"
    )

    # Mark as packaged (not published — you'll do that manually)
    draft["status"] = "packaged"
    draft["packaged_at"] = datetime.now().isoformat()
    save_draft(draft)

    logger.info("Post package built for draft %s", draft_id)
    return {
        "draft_id": draft_id,
        "title": draft.get("title", ""),
        "caption": full_caption,
        "slide_paths": image_paths,
        "instructions": instructions,
    }


def mark_as_posted(draft_id: str) -> bool:
    """Mark a draft as manually posted. Call after you've posted on IG."""
    draft = load_draft(draft_id)
    if not draft:
        return False
    draft["status"] = "published"
    draft["published_at"] = datetime.now().isoformat()
    save_draft(draft)
    logger.info("Draft %s marked as published", draft_id)
    return True


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print("Usage: python social_publisher.py <draft_id>")
        sys.exit(1)
    pkg = build_post_package(sys.argv[1])
    if pkg:
        print(f"✅ Package ready: {pkg['title']}")
        print(f"📝 Caption ({len(pkg['caption'])} chars):")
        print(pkg["caption"])
        print(f"\n🖼 Slides ({len(pkg['slide_paths'])}):")
        for p in pkg["slide_paths"]:
            print(f"  {p}")
    else:
        print("❌ Failed to build package.")
