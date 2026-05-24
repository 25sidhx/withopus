"""
OPUS Content Engine Bot
Scrapes trends → AI transforms into premium carousel concepts → Telegram.

Run: python news_bot.py
"""

import os
import json
import asyncio
import feedparser
import httpx
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
)

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID     = int(os.getenv("TELEGRAM_OWNER_ID", "0"))
INTERVAL_HR  = int(os.getenv("DIGEST_INTERVAL_HOURS", "6"))
NIM_BASE_URL = os.getenv("NIM_BASE_URL", "http://localhost:8082")
NIM_API_KEY  = os.getenv("NVIDIA_API_KEY", "not-needed")

# ── Topics to scrape ────────────────────────────────────────────────────────
TOPICS = [
    {"name": "🏙️ Nagpur",       "query": "Nagpur startups tech",          "max": 5},
    {"name": "📈 Marketing",     "query": "digital marketing trends 2025", "max": 5},
    {"name": "🎓 Education",     "query": "education edtech India 2025",   "max": 5},
    {"name": "🤖 AI",            "query": "artificial intelligence tools 2025", "max": 5},
    {"name": "🚀 Startups",      "query": "startup trends founder 2025",   "max": 4},
    {"name": "🎨 Design",        "query": "design trends branding 2025",   "max": 4},
    {"name": "⚡ Creator Economy","query": "creator economy tools 2025",    "max": 4},
]

# ── OPUS System Prompt (Elite Content Strategist) ───────────────────────────
SYSTEM_PROMPT = """You are an elite AI content strategist, editorial designer, and viral growth operator for the brand "OPUS" — a future-focused creative technology studio.

Your job: transform raw news/trend data into ONE premium editorial carousel concept.

RULES:
- NOT generic motivational junk. NOT fake hustle. NOT LinkedIn garbage.
- Every carousel must: educate, create authority, feel premium, trigger curiosity, encourage swiping.
- The brand voice is: intelligent, modern, cinematic, minimal, bold.

OUTPUT FORMAT (use this EXACT structure):

## 🔥 TREND DISCOVERY
**Topic:** [specific topic from the data]
**Why It Matters:** [2-3 lines]  
**Viral Angle:** [why this can blow up]
**Target:** [who cares about this]

## 🎯 CAROUSEL CONCEPT
**Title:** [punchy 3-6 word title]
**Hook:** [first-slide hook that stops scrolling]
**Emotional Angle:** [what feeling drives engagement]
**Structure:** [how 6 slides tell a story]

## 📐 6-SLIDE BREAKDOWN

**SLIDE 1 — THE HOOK**
- Headline: [bold, oversized, provocative]
- Sub: [one line context]
- Visual: [layout direction]
- Transition: [how it connects to slide 2]

**SLIDE 2 — THE CONTEXT**
- Headline: [what's happening]
- Sub: [data point or insight]
- Visual: [layout direction]
- Transition: [→ slide 3]

**SLIDE 3 — THE INSIGHT**
- Headline: [the "aha" moment]
- Sub: [supporting detail]
- Visual: [layout direction]
- Transition: [→ slide 4]

**SLIDE 4 — THE DEPTH**
- Headline: [deeper analysis]
- Sub: [framework or breakdown]
- Visual: [layout direction]
- Transition: [→ slide 5]

**SLIDE 5 — THE APPLICATION**
- Headline: [how to use this]
- Sub: [actionable takeaway]
- Visual: [layout direction]
- Transition: [→ slide 6]

**SLIDE 6 — THE CTA**
- Headline: [final punch]
- Sub: [follow/save/share trigger]
- Visual: [layout direction]

## 🎨 DESIGN DIRECTION
- **Typography:** [font pairing suggestion]
- **Colors:** [specific palette, hex codes]
- **Composition:** [grid style]
- **Mood:** [visual feeling]

## 🖼️ IMAGE GENERATION PROMPT
[One detailed prompt to generate a SINGLE connected 2x3 grid canvas with all 6 slides as one editorial image. Include: style, typography, colors, layout, mood, brand elements. This should be copy-paste ready for Midjourney/DALL-E/Ideogram.]

## 📝 CAPTION
[Instagram caption with hooks, value, CTA. Include line breaks. 5-8 relevant hashtags at end.]

## 🐦 X/TWITTER THREAD
[3-5 tweet thread version. Punchy, insight-driven.]

## 🧠 VIRALITY ANALYSIS
- **Save trigger:** [why someone saves this]
- **Share trigger:** [why someone shares this]
- **Psychological hook:** [what makes it sticky]
- **Engagement prediction:** [low/medium/high/viral]

HARD CONSTRAINTS:
- Do NOT use cliché phrases like "game changer", "unlock your potential", "hustle harder"
- Do NOT suggest centered text layouts everywhere — use asymmetric, Swiss, editorial
- The image prompt MUST specify: one canvas, 6 connected panels, premium typography, OPUS branding
- Color palette MUST include OPUS signature: deep blacks (#0A0A0A), warm cream (#F5F0E8), accent gold (#C4A265)
- Every slide must have visual continuation to the next"""


# ── Scraper ──────────────────────────────────────────────────────────────────
def fetch_news(query: str, max_items: int = 5) -> list[dict]:
    """Pull from Google News RSS — free, no API key."""
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:max_items]:
        articles.append({
            "title":  entry.get("title", "Untitled"),
            "link":   entry.get("link", ""),
            "source": entry.get("source", {}).get("title", "Unknown"),
            "date":   entry.get("published", ""),
        })
    return articles


def fetch_all() -> str:
    """Scrape all topics, return as formatted text for the AI."""
    lines = [f"=== SCRAPED TRENDS DATA — {datetime.now().strftime('%d %b %Y %H:%M')} ===\n"]
    for t in TOPICS:
        articles = fetch_news(t["query"], t["max"])
        lines.append(f"\n--- {t['name']} ---")
        if not articles:
            lines.append("  No articles found.")
        for i, a in enumerate(articles, 1):
            lines.append(f"  {i}. {a['title']}")
            lines.append(f"     Source: {a['source']} | {a['date']}")
    return "\n".join(lines)


# ── AI Engine ────────────────────────────────────────────────────────────────
async def generate_carousel_concept(raw_data: str) -> str:
    """Send scraped data to NVIDIA NIM → get carousel concept back."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{NIM_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {NIM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta/llama-3.1-8b-instruct",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        "Here is the latest scraped trend data. Analyze ALL of it, "
                        "pick the SINGLE most viral-worthy topic, and create a complete "
                        "OPUS carousel concept using the exact output format.\n\n"
                        f"{raw_data}"
                    )},
                ],
                "temperature": 0.8,
                "max_tokens": 4000,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


# ── Telegram Helpers ─────────────────────────────────────────────────────────
def escape_md(text: str) -> str:
    """Escape for MarkdownV2."""
    for ch in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
        text = text.replace(ch, f"\\{ch}")
    return text


async def send_long_message(bot, chat_id: int, text: str, parse_mode=None):
    """Split and send messages that exceed Telegram's 4096 char limit."""
    max_len = 4000
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Find a good split point
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    for chunk in chunks:
        await bot.send_message(chat_id=chat_id, text=chunk, parse_mode=parse_mode)


# ── Command Handlers ─────────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ OPUS Content Engine — Live\n\n"
        "Commands:\n"
        "/generate — Scrape trends → AI carousel concept\n"
        "/news — Raw news digest (no AI)\n"
        "/topics — See tracked topics\n\n"
        f"Auto-generates every {INTERVAL_HR}h."
    )


async def cmd_topics(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lines = ["📡 Tracking:\n"]
    for t in TOPICS:
        lines.append(f"• {t['name']} — {t['query']}")
    await update.message.reply_text("\n".join(lines))


async def cmd_news(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Raw news dump — no AI processing."""
    msg = await update.message.reply_text("⏳ Scraping news...")
    raw = fetch_all()
    await msg.delete()
    await send_long_message(ctx.bot, update.effective_chat.id, raw)


async def cmd_generate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Full pipeline: Scrape → AI → Carousel Concept → Telegram."""
    msg = await update.message.reply_text(
        "🔄 OPUS Content Engine running...\n\n"
        "Step 1/3: Scraping trends...",
    )

    # Step 1: Scrape
    raw_data = fetch_all()
    article_count = raw_data.count(". ")
    await msg.edit_text(
        f"🔄 OPUS Content Engine running...\n\n"
        f"✅ Step 1/3: Scraped {article_count} articles\n"
        f"Step 2/3: AI analyzing trends..."
    )

    # Step 2: AI Generate
    try:
        concept = await generate_carousel_concept(raw_data)
    except httpx.ConnectError:
        await msg.edit_text(
            "❌ Can't reach AI server.\n\n"
            f"Make sure NIM proxy is running at: {NIM_BASE_URL}\n"
            "Start it with: uvicorn server:app --host 0.0.0.0 --port 8082"
        )
        return
    except httpx.HTTPStatusError as e:
        await msg.edit_text(f"❌ AI server error: {e.response.status_code}\n{e.response.text[:500]}")
        return
    except Exception as e:
        await msg.edit_text(f"❌ AI error: {str(e)[:500]}")
        return

    await msg.edit_text(
        f"🔄 OPUS Content Engine running...\n\n"
        f"✅ Step 1/3: Scraped {article_count} articles\n"
        f"✅ Step 2/3: AI analysis complete\n"
        f"Step 3/3: Sending to you..."
    )

    # Step 3: Send to Telegram
    header = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ OPUS CAROUSEL CONCEPT\n"
        f"📅 {datetime.now().strftime('%d %b %Y  %H:%M')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    await send_long_message(ctx.bot, update.effective_chat.id, header + concept)

    # Final status
    await msg.edit_text(
        f"✅ OPUS Content Engine — Done\n\n"
        f"📊 {article_count} articles analyzed\n"
        f"🎯 1 carousel concept generated\n\n"
        f"Use /generate again for a new concept."
    )


async def auto_generate(ctx: ContextTypes.DEFAULT_TYPE):
    """Auto job — runs every INTERVAL_HR hours."""
    try:
        raw_data = fetch_all()
        concept = await generate_carousel_concept(raw_data)
        header = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ AUTO OPUS CAROUSEL\n"
            f"📅 {datetime.now().strftime('%d %b %Y  %H:%M')}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        await send_long_message(ctx.bot, OWNER_ID, header + concept)
    except Exception as e:
        await ctx.bot.send_message(
            chat_id=OWNER_ID,
            text=f"⚠️ Auto-generate failed: {str(e)[:300]}"
        )


# ── Main ──────────────────────────────────────────────────────────────────────
async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start",    "Welcome + help"),
        BotCommand("generate", "Scrape → AI → Carousel concept"),
        BotCommand("news",     "Raw news digest"),
        BotCommand("topics",   "See tracked topics"),
    ])


def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not set in .env")
    if OWNER_ID == 0:
        raise RuntimeError("❌ TELEGRAM_OWNER_ID not set in .env")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("⚡ OPUS Content Engine")
    print(f"   AI Server: {NIM_BASE_URL}")
    print(f"   Auto-gen:  every {INTERVAL_HR}h")
    print(f"   Topics:    {len(TOPICS)}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("generate", cmd_generate))
    app.add_handler(CommandHandler("news",     cmd_news))
    app.add_handler(CommandHandler("topics",   cmd_topics))

    # Auto-generate: fires 30s after start, then every INTERVAL_HR hours
    app.job_queue.run_repeating(
        auto_generate,
        interval=INTERVAL_HR * 3600,
        first=30,
    )

    print("\n🤖 Bot polling... Send /generate in Telegram")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
