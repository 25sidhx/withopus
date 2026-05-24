"""Opus Autopilot Telegram Bot — New Carousel Pipeline.

Workflow:
    /generate <topic>
      → AI generates slide texts + master image prompt
      → Bot sends slide reference + copy-paste prompt
    User generates ONE canvas in Midjourney/Flux
      → Sends image to chat
    Bot auto-slices into 6 slides → preview grid → approval → posts to IG
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from brand_context import load_brand_context

logger = logging.getLogger("autopilot.telegram")

# ── State machine ────────────────────────────────────────────────
# {user_id: {"state": str, "draft_id": str, "draft": dict}}
user_sessions: dict[int, dict] = {}

IDLE = "idle"
AWAITING_CANVAS = "awaiting_canvas"
APPROVAL = "approval"

autopilot_paused = False


def is_owner(user_id: int) -> bool:
    return user_id == config.TELEGRAM_OWNER_ID


def _session(user_id: int) -> dict:
    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": IDLE, "draft_id": None, "draft": None}
    return user_sessions[user_id]


# ── Draft helpers ─────────────────────────────────────────────────

def load_drafts(status: str = "pending") -> list[dict]:
    drafts = []
    for path in config.DRAFTS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status") == status:
                drafts.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return sorted(drafts, key=lambda d: d.get("created_at", ""), reverse=True)


def load_draft(draft_id: str) -> dict | None:
    path = config.DRAFTS_DIR / f"{draft_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    # Also check carousels dir for non-hash filenames
    for p in config.DRAFTS_DIR.glob("*.json"):
        if p.stem == draft_id:
            return json.loads(p.read_text(encoding="utf-8"))
    return None


def save_draft(draft: dict) -> None:
    path = config.DRAFTS_DIR / f"{draft['id']}.json"
    path.write_text(json.dumps(draft, indent=2), encoding="utf-8")


# ── Prompt delivery ───────────────────────────────────────────────

def _slide_reference_text(slides: list[dict]) -> str:
    """Build the slide reference block sent above the prompt."""
    lines = ["📋 *SLIDE CONTENT REFERENCE*", "━━━━━━━━━━━━━━━━━━━━━━━━"]
    type_emoji = {"cover": "🎬", "content": "📝", "hook": "💬", "call_to_action": "🎯", "cta": "🎯"}
    for s in slides:
        num = s.get("slide_number", "?")
        emoji = type_emoji.get(s.get("type", "content"), "📝")
        text = s.get("text", "").replace("\n", " ").strip()
        if len(text) > 90:
            text = text[:87] + "..."
        lines.append(f"{emoji} *{num:02d}* — {text}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


# ── Commands ──────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("⛔ Unauthorized.")
        return
    await update.message.reply_text(
        "🤖 *Opus Social Autopilot* is online\\!\n\n"
        "*Commands:*\n"
        "/generate \\<topic\\> — Generate carousel prompt\n"
        "/scrape — Scrape \\.\\. generate from source accounts\n"
        "/drafts — Show pending drafts\n"
        "/status — System health\n"
        "/clearseen — Reset scrape cache\n"
        "/cancel — Cancel current session\n"
        "/pause \\| /resume — Toggle autopilot",
        parse_mode="MarkdownV2",
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return
    pending = load_drafts("pending")
    published = load_drafts("published")
    rejected = load_drafts("rejected")

    sess = _session(update.effective_user.id)
    state_label = sess["state"].replace("_", " ").title()
    packaged = load_drafts("packaged")

    await update.message.reply_text(
        f"🤖 *Opus Social Autopilot*\n\n"
        f"📦 Mode: Manual Posting (safe mode)\n"
        f"Engine: {'⏸ Paused' if autopilot_paused else '▶️ Running'}\n"
        f"Session: {state_label}\n\n"
        f"📝 Pending: {len(pending)}\n"
        f"📦 Packaged (post these): {len(packaged)}\n"
        f"✅ Published: {len(published)}\n"
        f"❌ Rejected: {len(rejected)}",
        parse_mode="Markdown",
    )


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return
    uid = update.effective_user.id
    user_sessions[uid] = {"state": IDLE, "draft_id": None, "draft": None}
    await update.message.reply_text("🛑 Session cancelled. Ready for /generate.")


async def cmd_generate(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate carousel text + master image prompt."""
    if not is_owner(update.effective_user.id):
        return

    uid = update.effective_user.id
    sess = _session(uid)

    if not ctx.args:
        await update.message.reply_text(
            "Usage: /generate <topic> [num\\_slides]\n"
            "Example: /generate Why templates kill your brand 6",
            parse_mode="Markdown",
        )
        return

    num_slides = 6
    args = list(ctx.args)
    if args[-1].isdigit():
        num_slides = int(args[-1])
        args = args[:-1]
    topic = " ".join(args)
    if not topic:
        await update.message.reply_text("Please provide a topic.")
        return

    await update.message.reply_text(
        f"🧠 Generating *{num_slides}\\-slide* carousel\\.\\.\\.\n_Topic: {topic}_",
        parse_mode="MarkdownV2",
    )

    from text_generator import generate_carousel_text, save_carousel_text, build_master_prompt

    try:
        data = generate_carousel_text(topic, num_slides)
        if not data:
            await update.message.reply_text("❌ Generation failed. Try again.")
            return

        # Attach metadata
        data["status"] = "pending"
        data["created_at"] = datetime.now().isoformat()
        path = save_carousel_text(data)
        draft_id = path.stem

        # Store session
        sess["state"] = AWAITING_CANVAS
        sess["draft_id"] = draft_id
        sess["draft"] = data

        # ── Message 1: Title + slide reference ──
        ref_text = _slide_reference_text(data["slides"])
        await update.message.reply_text(
            f"✅ *{data['title']}*\n📊 {num_slides} slides\n\n{ref_text}",
            parse_mode="Markdown",
        )

        # ── Message 2: Caption for IG (reference) ──
        caption = data.get("caption", "")
        hashtags = data.get("hashtags", "")
        await update.message.reply_text(
            f"📱 *Instagram Caption:*\n\n{caption}\n\n{hashtags}",
            parse_mode="Markdown",
        )

        # ── Message 3: Master prompt as code block ──
        master_prompt = build_master_prompt(topic, data["slides"], caption)

        # Telegram has 4096 char limit per message — split if needed
        prompt_header = (
            "🎨 *IMAGE GENERATION PROMPT*\n"
            "_Long\\-press the code block to copy_\n\n"
        )
        await update.message.reply_text(prompt_header, parse_mode="MarkdownV2")

        # Send prompt in chunks if > 4000 chars
        chunk_size = 3900
        chunks = [master_prompt[i:i+chunk_size] for i in range(0, len(master_prompt), chunk_size)]
        for i, chunk in enumerate(chunks):
            label = f"Prompt ({i+1}/{len(chunks)}):" if len(chunks) > 1 else "Prompt:"
            await update.message.reply_text(
                f"*{label}*\n```\n{chunk}\n```",
                parse_mode="Markdown",
            )
            await asyncio.sleep(0.3)

        # ── Message 4: Instruction ──
        await update.message.reply_text(
            "🖼 *Now generate your canvas\\.*\n\n"
            "→ Use the prompt above in Midjourney / Flux / DALL\\-E\n"
            "→ Generate ONE image with all 6 panels connected\n"
            "→ Send it here at highest quality\n\n"
            "_I'll auto\\-slice it into 6 slides and post to @with\\_opus_",
            parse_mode="MarkdownV2",
        )

    except Exception as exc:
        logger.error("Generate failed: %s", exc, exc_info=True)
        await update.message.reply_text(f"❌ Error: {exc}")


async def cmd_scrape(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Scrape source accounts and generate carousel prompt."""
    if not is_owner(update.effective_user.id):
        return

    uid = update.effective_user.id
    sess = _session(uid)

    await update.message.reply_text("🔍 Scraping source accounts...")

    from scraper import scrape_source_accounts
    from text_generator import generate_from_scraped, save_carousel_text, build_master_prompt

    try:
        posts = scrape_source_accounts()
        if not posts:
            await update.message.reply_text(
                "📭 No new posts found.\nRun /clearseen to reset the cache."
            )
            return

        await update.message.reply_text(f"📡 Found {len(posts)} new posts. Rewriting best one...")

        best = posts[0]
        data = generate_from_scraped(scraped_caption=best["caption"], source=best["source"], num_slides=6)
        if not data:
            await update.message.reply_text("❌ AI rewrite failed.")
            return

        data["status"] = "pending"
        data["source_account"] = best["source"]
        data["source_post_id"] = best["post_id"]
        data["created_at"] = datetime.now().isoformat()

        from text_generator import save_carousel_text
        path = save_carousel_text(data)
        draft_id = path.stem

        sess["state"] = AWAITING_CANVAS
        sess["draft_id"] = draft_id
        sess["draft"] = data

        topic = data.get("title", best["source"])
        ref_text = _slide_reference_text(data["slides"])
        await update.message.reply_text(
            f"✅ *Scraped from @{best['source']}*\n\n{ref_text}",
            parse_mode="Markdown",
        )

        master_prompt = build_master_prompt(topic, data["slides"], data.get("caption", ""))
        await update.message.reply_text(
            f"🎨 *IMAGE PROMPT:*\n```\n{master_prompt[:3900]}\n```",
            parse_mode="Markdown",
        )
        await update.message.reply_text(
            "🖼 Generate your canvas and send it here.\n"
            "I'll slice it into 6 slides and post to @with_opus."
        )

    except Exception as exc:
        logger.error("Scrape failed: %s", exc, exc_info=True)
        await update.message.reply_text(f"❌ Error: {exc}")


async def cmd_drafts(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return
    pending = load_drafts("pending")
    if not pending:
        await update.message.reply_text("📭 No pending drafts.")
        return
    for draft in pending[:5]:
        title = draft.get("title", "Untitled")
        slides = len(draft.get("slides", []))
        source = draft.get("source_account", "manual")
        draft_id = draft.get("id", draft.get("title", "unknown"))
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📋 Get Prompt", callback_data=f"get_prompt:{draft_id}"),
            InlineKeyboardButton("🗑 Delete", callback_data=f"delete_draft:{draft_id}"),
        ]])
        await update.message.reply_text(
            f"📝 *{title}*\n📊 {slides} slides | 📡 @{source}\n🆔 `{draft_id}`",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def cmd_clearseen(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return
    log_path = config.DATA_DIR / "scraped_log.json"
    if log_path.exists():
        old = json.loads(log_path.read_text(encoding="utf-8"))
        count = len(old.get("seen_ids", []))
        log_path.write_text(json.dumps({"seen_ids": []}, indent=2), encoding="utf-8")
        await update.message.reply_text(f"🗑 Cleared {count} cached IDs. Run /scrape now.")
    else:
        await update.message.reply_text("📭 No scrape log yet.")


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    global autopilot_paused
    if not is_owner(update.effective_user.id):
        return
    autopilot_paused = True
    await update.message.reply_text("⏸ Autopilot paused.")


async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    global autopilot_paused
    if not is_owner(update.effective_user.id):
        return
    autopilot_paused = False
    await update.message.reply_text("▶️ Autopilot resumed.")


# ── Photo handler — receives the user's generated canvas ─────────

async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Receives the single canvas image, slices it into 6 slides."""
    if not is_owner(update.effective_user.id):
        return

    uid = update.effective_user.id
    sess = _session(uid)

    if sess["state"] != AWAITING_CANVAS:
        await update.message.reply_text(
            "💡 Run /generate <topic> first, then send your canvas image."
        )
        return

    draft = sess.get("draft")
    draft_id = sess.get("draft_id", "output")

    await update.message.reply_text("📥 Got it! Slicing your canvas into 6 slides...")

    # Download highest-quality version
    photo = update.message.photo[-1]
    file = await ctx.bot.get_file(photo.file_id)
    canvas_dir = config.CAROUSELS_DIR / draft_id
    canvas_dir.mkdir(parents=True, exist_ok=True)
    canvas_path = canvas_dir / "canvas.jpg"
    await file.download_to_drive(str(canvas_path))

    # Also handle document uploads (full-quality photos sent as files)
    # (This branch handled below in handle_document)

    try:
        from image_slicer import slice_canvas, build_preview_grid

        slides = slice_canvas(canvas_path, num_slides=6, draft_id=draft_id)

        if len(slides) != 6:
            await update.message.reply_text(
                f"⚠️ Got {len(slides)} slices instead of 6. "
                "Make sure your canvas has 6 equal panels."
            )
            return

        # Build preview grid
        preview_path = canvas_dir / "preview_grid.jpg"
        build_preview_grid(slides, preview_path)

        # Store slices in session
        sess["slides"] = [str(s) for s in slides]
        sess["state"] = APPROVAL

        # Send preview
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📦 Get Post Package", callback_data=f"package_ready:{draft_id}"),
            InlineKeyboardButton("🔄 Redo Prompt", callback_data=f"redo_prompt:{draft_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject:{draft_id}"),
        ]])
        with open(preview_path, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=(
                    f"🎨 *{draft.get('title', 'Carousel')}*\n"
                    f"✅ 6 slides sliced and ready\.\n\n"
                    f"Tap *Get Post Package* to receive caption \+ slides for manual posting\."
                ),
                parse_mode="MarkdownV2",
                reply_markup=keyboard,
            )

    except Exception as exc:
        logger.error("Slicing failed: %s", exc, exc_info=True)
        await update.message.reply_text(f"❌ Slice failed: {exc}")


async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle full-quality images sent as documents (files)."""
    if not is_owner(update.effective_user.id):
        return

    uid = update.effective_user.id
    sess = _session(uid)

    if sess["state"] != AWAITING_CANVAS:
        return

    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        return  # not an image file

    draft_id = sess.get("draft_id", "output")
    draft = sess.get("draft", {})

    await update.message.reply_text("📥 Got full-quality image! Slicing...")

    canvas_dir = config.CAROUSELS_DIR / draft_id
    canvas_dir.mkdir(parents=True, exist_ok=True)
    canvas_path = canvas_dir / "canvas.jpg"

    file = await ctx.bot.get_file(doc.file_id)
    await file.download_to_drive(str(canvas_path))

    try:
        from image_slicer import slice_canvas, build_preview_grid

        slides = slice_canvas(canvas_path, num_slides=6, draft_id=draft_id)
        preview_path = canvas_dir / "preview_grid.jpg"
        build_preview_grid(slides, preview_path)

        sess["slides"] = [str(s) for s in slides]
        sess["state"] = APPROVAL

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📦 Get Post Package", callback_data=f"package_ready:{draft_id}"),
            InlineKeyboardButton("🔄 Redo Prompt", callback_data=f"redo_prompt:{draft_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject:{draft_id}"),
        ]])
        with open(preview_path, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=(
                    f"🎨 *{draft.get('title', 'Carousel')}*\n"
                    f"✅ 6 slides sliced \\(full quality\\)\.\n\nTap *Get Post Package* to receive everything for manual posting\."
                ),
                parse_mode="MarkdownV2",
                reply_markup=keyboard,
            )
    except Exception as exc:
        logger.error("Document slice failed: %s", exc, exc_info=True)
        await update.message.reply_text(f"❌ Error: {exc}")


# ── Button callbacks ──────────────────────────────────────────────

async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        await query.edit_message_text("⛔ Unauthorized.")
        return

    uid = query.from_user.id
    sess = _session(uid)
    action, draft_id = query.data.split(":", 1)

    # ── Package ready — send caption + slides to Telegram for manual posting ──
    if action == "package_ready":
        slide_paths = sess.get("slides", [])
        draft = load_draft(draft_id) or sess.get("draft", {})

        if not slide_paths:
            await query.edit_message_caption("❌ No slides found. Redo the flow.")
            return

        await query.edit_message_caption("📦 Building your post package...")

        caption = draft.get("caption", "")
        hashtags = draft.get("hashtags", "")
        full_caption = f"{caption}\n\n{hashtags}".strip()
        title = draft.get("title", "Carousel")

        # Send caption as copyable text
        await ctx.bot.send_message(
            chat_id=query.message.chat_id,
            text=(
                f"📋 *{title}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"*CAPTION (copy this):*\n\n"
                f"{full_caption}"
            ),
            parse_mode="Markdown",
        )

        # Send each slide as a file (full quality)
        await ctx.bot.send_message(
            query.message.chat_id,
            "🖼 *Slides (save these in order):*",
            parse_mode="Markdown",
        )
        for i, path in enumerate(slide_paths, 1):
            from pathlib import Path as _Path
            p = _Path(path)
            if p.exists():
                with open(p, "rb") as f:
                    await ctx.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=f,
                        filename=f"slide_{i:02d}.jpg",
                        caption=f"Slide {i}/{len(slide_paths)}",
                    )

        # Posting instructions
        await ctx.bot.send_message(
            query.message.chat_id,
            "📲 *HOW TO POST:*\n"
            "1\. Save all slides to your phone\n"
            "2\. Open Instagram → Tap \+ → Post\n"
            "3\. Select all slides IN ORDER\n"
            "4\. Paste the caption above\n"
            "5\. Tag location: Nagpur\n"
            "6\. Post at 7\-9pm IST for best reach\n\n"
            "After posting, send /posted to mark it done\.\n"
            f"_(draft\_id: `{draft_id}`)_",
            parse_mode="MarkdownV2",
        )

        # Mark as packaged
        draft["status"] = "packaged"
        draft["packaged_at"] = datetime.now().isoformat()
        save_draft(draft)
        user_sessions[uid] = {"state": IDLE, "draft_id": None, "draft": None}

    # ── Redo prompt ────────────────────────────────────────────────
    elif action == "redo_prompt":
        draft = load_draft(draft_id) or sess.get("draft", {})
        if not draft:
            await ctx.bot.send_message(query.message.chat_id, "❌ Draft not found.")
            return

        from text_generator import build_master_prompt
        topic = draft.get("title", "")
        slides = draft.get("slides", [])
        caption = draft.get("caption", "")

        master_prompt = build_master_prompt(topic, slides, caption)
        sess["state"] = AWAITING_CANVAS

        await ctx.bot.send_message(
            query.message.chat_id,
            f"🎨 *Prompt (regenerated):*\n```\n{master_prompt[:3900]}\n```\n\n"
            "Generate a new canvas and send it here.",
            parse_mode="Markdown",
        )

    # ── Get prompt from draft ──────────────────────────────────────
    elif action == "get_prompt":
        draft = load_draft(draft_id)
        if not draft:
            await ctx.bot.send_message(query.message.chat_id, "❌ Draft not found.")
            return

        from text_generator import build_master_prompt
        master_prompt = build_master_prompt(
            draft.get("title", ""),
            draft.get("slides", []),
            draft.get("caption", ""),
        )
        sess["state"] = AWAITING_CANVAS
        sess["draft_id"] = draft_id
        sess["draft"] = draft

        ref_text = _slide_reference_text(draft.get("slides", []))
        await ctx.bot.send_message(
            query.message.chat_id, ref_text, parse_mode="Markdown"
        )
        await ctx.bot.send_message(
            query.message.chat_id,
            f"🎨 *Prompt:*\n```\n{master_prompt[:3900]}\n```",
            parse_mode="Markdown",
        )
        await ctx.bot.send_message(
            query.message.chat_id,
            "Generate your canvas and send it here.",
        )

    # ── Reject ─────────────────────────────────────────────────────
    elif action == "reject":
        draft = load_draft(draft_id) or sess.get("draft", {})
        if draft:
            draft["status"] = "rejected"
            save_draft(draft)
        user_sessions[uid] = {"state": IDLE, "draft_id": None, "draft": None}
        await query.edit_message_caption("❌ Rejected. Draft saved.")

    # ── Delete draft ───────────────────────────────────────────────
    elif action == "delete_draft":
        path = config.DRAFTS_DIR / f"{draft_id}.json"
        if path.exists():
            path.unlink()
        await query.edit_message_text("🗑 Draft deleted.")


# ── Main ──────────────────────────────────────────────────────────

def run_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("generate", cmd_generate))
    app.add_handler(CommandHandler("scrape", cmd_scrape))
    app.add_handler(CommandHandler("drafts", cmd_drafts))
    app.add_handler(CommandHandler("clearseen", cmd_clearseen))
    app.add_handler(CommandHandler("posted", cmd_posted))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Photo + document handlers (for canvas image collection)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    logger.info("🤖 Opus Social Autopilot Bot started (safe mode — no IG login)!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
