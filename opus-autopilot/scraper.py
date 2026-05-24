"""Scraper — generates content from topics. NO Instagram login required.

Old approach: instagrapi → logged into IG → scraped private API → got flagged.
New approach: pick a topic → AI generates fresh carousel content → no IG touch.
"""

import hashlib
import json
import logging
import random
import re
from datetime import datetime

from openai import OpenAI

import config

logger = logging.getLogger("autopilot.scraper")

SCRAPED_LOG = config.DATA_DIR / "topic_log.json"


def _load_used_topics() -> set[str]:
    if SCRAPED_LOG.exists():
        data = json.loads(SCRAPED_LOG.read_text(encoding="utf-8"))
        return set(data.get("used_topics", []))
    return set()


def _save_used_topics(used: set[str]) -> None:
    SCRAPED_LOG.write_text(
        json.dumps({"used_topics": list(used)}, indent=2), encoding="utf-8"
    )


def get_next_topic() -> str | None:
    """Pick a topic from config that hasn't been used recently."""
    used = _load_used_topics()
    available = [t for t in config.CONTENT_TOPICS if t not in used]

    if not available:
        # All topics used — reset and start over
        _save_used_topics(set())
        available = list(config.CONTENT_TOPICS)
        logger.info("All topics cycled — resetting log.")

    topic = random.choice(available)
    used.add(topic)
    _save_used_topics(used)
    logger.info("Selected topic: %s", topic)
    return topic


def scrape_source_accounts() -> list[dict]:
    """Return a topic-based 'post' for downstream generation.

    Named scrape_source_accounts() for backwards compatibility with telegram_bot.py.
    No Instagram login, no private API calls.
    """
    topic = get_next_topic()
    if not topic:
        return []

    # Return a fake 'post' dict matching the shape the rest of the pipeline expects
    return [{
        "post_id": hashlib.md5(f"{topic}-{datetime.now().date()}".encode()).hexdigest()[:8],
        "source": "opus_topics",
        "caption": topic,  # used as the generation prompt
        "timestamp": datetime.now().isoformat(),
        "media_type": "topic",
    }]


def _get_ai_client() -> OpenAI:
    return OpenAI(
        base_url=config.NVIDIA_BASE_URL,
        api_key=config.NVIDIA_API_KEY,
    )


REWRITE_SYSTEM = f"""You are a content strategist for {config.BRAND_NAME}, a premium creative agency in {config.TARGET_CITY}.

Your job: take a content topic and create a BRAND-NEW carousel post for {config.BRAND_HANDLE}.

Rules:
- Tone: professional, warm, cinematic. No cringe, no corporate jargon.
- Output must be structured for a 6-slide Instagram carousel.
- Educate or inspire small business owners and founders.
- Never use: game-changer, hustle, crush it, leveling up, synergy.
"""

REWRITE_PROMPT = """Create a 6-slide carousel for {handle} about this topic:

"{topic}"

Output ONLY valid JSON:

{{
  "title": "The catchy cover-slide title (max 8 words)",
  "hook": "A provocative 1-sentence hook that makes people stop scrolling (15-25 words max)",
  "slides": [
    {{"heading": "Slide heading (3-5 words)", "body": "2-3 sentences of actionable value"}},
    {{"heading": "Slide heading (3-5 words)", "body": "2-3 sentences of actionable value"}},
    {{"heading": "Slide heading (3-5 words)", "body": "2-3 sentences of actionable value"}}
  ],
  "caption": "Instagram caption (hook, body, soft CTA — under 200 words)",
  "hashtags": "#tag1 #tag2 #tag3 #tag4 #tag5"
}}

Output ONLY the JSON object, no markdown, no extra text.
"""


def rewrite_for_carousel(source: str, caption: str) -> dict | None:
    """Generate carousel content from a topic string via NVIDIA AI."""
    client = _get_ai_client()

    prompt = REWRITE_PROMPT.format(
        handle=config.BRAND_HANDLE,
        topic=caption,  # caption is the topic string from scrape_source_accounts()
    )

    try:
        resp = client.chat.completions.create(
            model=config.NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        raw = resp.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

        return json.loads(raw)

    except json.JSONDecodeError as e:
        logger.error("AI returned invalid JSON: %s\n%s", e, raw[:500])
        return None
    except Exception as e:
        logger.error("AI generation failed: %s", e)
        return None


def generate_carousel_draft(scraped_post: dict) -> dict | None:
    """Generate a draft from a topic post dict."""
    content = rewrite_for_carousel(
        source=scraped_post["source"],
        caption=scraped_post["caption"],
    )
    if not content:
        return None

    if not all(k in content for k in ("title", "slides", "caption")):
        logger.error("AI output missing required keys: %s", list(content.keys()))
        return None

    raw_id = f"{datetime.now().isoformat()}-{scraped_post['source']}"
    draft_id = hashlib.md5(raw_id.encode()).hexdigest()[:8]

    draft = {
        "id": draft_id,
        "type": "carousel",
        "status": "pending",
        "source_account": scraped_post["source"],
        "source_post_id": scraped_post["post_id"],
        "original_topic": scraped_post["caption"],
        "title": content["title"],
        "hook": content.get("hook", ""),
        "slides": content["slides"],
        "caption": content["caption"],
        "hashtags": content.get("hashtags", ""),
        "created_at": datetime.now().isoformat(),
        "images_generated": False,
    }

    draft_path = config.DRAFTS_DIR / f"{draft_id}.json"
    draft_path.write_text(json.dumps(draft, indent=2), encoding="utf-8")
    logger.info("Draft saved: %s (topic: %s)", draft_id, scraped_post["caption"])

    return draft


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    posts = scrape_source_accounts()
    if posts:
        draft = generate_carousel_draft(posts[0])
        if draft:
            print(f"✅ Draft created: {draft['id']}")
            print(f"📄 Title: {draft['title']}")
        else:
            print("❌ AI generation failed.")
    else:
        print("📭 No topics available.")
