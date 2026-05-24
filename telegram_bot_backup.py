"""Opus Autopilot Telegram Bot — draft delivery and approval workflow."""

import json
import logging
import asyncio
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import config

logger = logging.getLogger("autopilot.telegram")

# State
autopilot_paused = False


def is_owner(user_id: int) -> bool:
    return user_id == config.TELEGRAM_OWNER_ID


def load_drafts(status: str = "pending") -> list[dict]:
    drafts = []
    for path in config.DRAFTS_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status") == status:
            drafts.append(data)
    return sorted(drafts, key=lambda d: d.get("created_at", ""), reverse=True)


def load_draft(draft_id: str) -> dict | None:
    path = config.DRAFTS_DIR / f"{draft_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def save_draft(draft: dict) -> None:
    path = config.DRAFTS_DIR / f"{draft['id']}.json"
    path.write_text(json.dumps(draft, indent=2), encoding="utf-8")


# --- Command Handlers ---


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("⛔ Unauthorized.")
        return

    await update.message.reply_text(
        "🤖 *Opus Autopilot* is online\\!\n\n"
        "Commands:\n"
        "/status — System health\n"
        "/drafts — Pending drafts\n"
        "/approve `<id>` — Approve a draft\n"
        "/reject `<id>` — Reject a draft\n"
        "/pause — Pause autopilot\n"
        "/resume — Resume autopilot\n"
        "/generate — Generate next blog post now",
        parse_mode="MarkdownV2",
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return

    pending = load_drafts("pending")
    approved = load_drafts("approved")
    rejected = load_drafts("rejected")

    # Check Hermes connectivity
    from hermes import HermesClient

    hermes_ok = "✅" if HermesClient().health_check() else "❌"

    status_text = (
        f"🤖 *Opus Autopilot Status*\n\n"
        f"Hermes API: {hermes_ok}\n"
        f"Autopilot: {'⏸ Paused' if autopilot_paused else '▶️ Running'}\n\n"
        f"📝 Pending drafts: {len(pending)}\n"
        f"✅ Approved: {len(approved)}\n"
        f"❌ Rejected: {len(rejected)}\n"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def cmd_drafts(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return

    pending = load_drafts("pending")
    if not pending:
        await update.message.reply_text("📭 No pending drafts.")
        return

    for draft in pending[:5]:  # Show max 5
        draft_type = draft.get("type", "unknown")
        title = draft.get("title", draft.get("topic", "Untitled"))
        draft_id = draft["id"]
        created = draft.get("created_at", "unknown")

        if draft_type == "blog_post":
            preview = draft.get("html_content", "")[:300] + "..."
            text = (
                f"📝 *Blog Post Draft*\n\n"
                f"*Title:* {title}\n"
                f"*Keywords:* {', '.join(draft.get('keywords', []))}\n"
                f"*Created:* {created}\n"
                f"*ID:* `{draft_id}`\n\n"
                f"Preview:\n{_strip_html(preview)}"
            )
        else:
            caption = draft.get("caption", "")[:300]
            text = (
                f"📱 *Social Caption Draft*\n\n"
                f"*Topic:* {title}\n"
                f"*Created:* {created}\n"
                f"*ID:* `{draft_id}`\n\n"
                f"{caption}"
            )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve:{draft_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject:{draft_id}"),
                ],
                [
                    InlineKeyboardButton("🔄 Regenerate", callback_data=f"regen:{draft_id}"),
                ],
            ]
        )
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def cmd_approve(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return

    if not ctx.args:
        await update.message.reply_text("Usage: /approve <draft_id>")
        return

    draft_id = ctx.args[0]
    result = await _approve_draft(draft_id)
    await update.message.reply_text(result)


async def cmd_reject(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return

    if not ctx.args:
        await update.message.reply_text("Usage: /reject <draft_id>")
        return

    draft_id = ctx.args[0]
    draft = load_draft(draft_id)
    if not draft:
        await update.message.reply_text(f"❌ Draft not found: {draft_id}")
        return

    draft["status"] = "rejected"
    save_draft(draft)
    await update.message.reply_text(f"❌ Draft rejected: {draft.get('title', draft_id)}")


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    global autopilot_paused
    if not is_owner(update.effective_user.id):
        return
    autopilot_paused = True
    await update.message.reply_text("⏸ Autopilot paused. No new content will be generated.")


async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    global autopilot_paused
    if not is_owner(update.effective_user.id):
        return
    autopilot_paused = False
    await update.message.reply_text("▶️ Autopilot resumed.")


async def cmd_generate(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update.effective_user.id):
        return

    await update.message.reply_text("⏳ Generating next blog post... This may take a minute.")

    from content_writer import get_next_topic, generate_blog_post

    topic_data = get_next_topic()
    if not topic_data:
        await update.message.reply_text("📋 All calendar topics already drafted.")
        return

    try:
        draft = generate_blog_post(
            topic=topic_data["topic"],
            keywords=topic_data["keywords"],
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve:{draft['id']}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject:{draft['id']}"),
                ],
            ]
        )

        preview = _strip_html(draft["html_content"][:400]) + "..."
        text = (
            f"📝 *New Blog Post Ready!*\n\n"
            f"*Title:* {draft['title']}\n"
            f"*Keywords:* {', '.join(draft['keywords'])}\n\n"
            f"Preview:\n{preview}"
        )
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

    except Exception as exc:
        await update.message.reply_text(f"❌ Generation failed: {exc}")


# --- Callback Query Handler (inline buttons) ---


async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        await query.edit_message_text("⛔ Unauthorized.")
        return

    action, draft_id = query.data.split(":", 1)

    if action == "approve":
        result = await _approve_draft(draft_id)
        await query.edit_message_text(result)

    elif action == "reject":
        draft = load_draft(draft_id)
        if draft:
            draft["status"] = "rejected"
            save_draft(draft)
            await query.edit_message_text(f"❌ Rejected: {draft.get('title', draft_id)}")
        else:
            await query.edit_message_text(f"❌ Draft not found: {draft_id}")

    elif action == "regen":
        await query.edit_message_text("🔄 Regenerating... please wait.")
        # Delete old draft and generate a new one
        draft = load_draft(draft_id)
        if draft:
            old_path = config.DRAFTS_DIR / f"{draft_id}.json"
            old_path.unlink(missing_ok=True)

            from content_writer import generate_blog_post

            try:
                new_draft = generate_blog_post(
                    topic=draft.get("title", ""),
                    keywords=draft.get("keywords", []),
                )
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "✅ Approve",
                                callback_data=f"approve:{new_draft['id']}",
                            ),
                            InlineKeyboardButton(
                                "❌ Reject",
                                callback_data=f"reject:{new_draft['id']}",
                            ),
                        ],
                    ]
                )
                preview = _strip_html(new_draft["html_content"][:400]) + "..."
                await query.edit_message_text(
                    f"🔄 *Regenerated!*\n\n*Title:* {new_draft['title']}\n\n{preview}",
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )
            except Exception as exc:
                await query.edit_message_text(f"❌ Regeneration failed: {exc}")


# --- Internal Helpers ---


async def _approve_draft(draft_id: str) -> str:
    """Approve a draft: publish to site and deploy."""
    draft = load_draft(draft_id)
    if not draft:
        return f"❌ Draft not found: {draft_id}"

    if draft.get("type") != "blog_post":
        draft["status"] = "approved"
        save_draft(draft)
        return f"✅ Social caption approved: {draft.get('topic', draft_id)}"

    # Publish blog post
    from publisher import publish_blog_post

    try:
        url = publish_blog_post(draft)
        draft["status"] = "approved"
        draft["approved_at"] = __import__("datetime").datetime.now().isoformat()
        save_draft(draft)
        return f"✅ Published and deployed!\n\n🔗 {url}"
    except Exception as exc:
        return f"❌ Publish failed: {exc}"


def _strip_html(text: str) -> str:
    """Remove HTML tags for Telegram preview."""
    import re

    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


# --- Notification Helper (called by other modules) ---


async def notify_owner(text: str, keyboard=None) -> None:
    """Send a message to the owner. Call from other modules."""
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    async with app:
        await app.bot.send_message(
            chat_id=config.TELEGRAM_OWNER_ID,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


def send_notification(text: str) -> None:
    """Sync wrapper for notify_owner."""
    asyncio.run(notify_owner(text))


# --- Main ---


def run_bot() -> None:
    """Start the Telegram bot (long polling)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("drafts", cmd_drafts))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(CommandHandler("reject", cmd_reject))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    app.add_handler(CommandHandler("generate", cmd_generate))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("🤖 Opus Autopilot Telegram Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
