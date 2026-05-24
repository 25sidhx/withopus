"""Quick script to detect your Telegram user ID. Send /start to the bot after running this."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8685455902:AAGTpwZqSkYf5RGZRUP3h1WHeNinEEJ2ro4"

async def any_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    name = user.full_name
    username = user.username or "none"
    
    print(f"\n{'='*50}")
    print(f"  YOUR TELEGRAM USER ID: {user_id}")
    print(f"  Name: {name}")
    print(f"  Username: @{username}")
    print(f"{'='*50}\n")
    
    await update.message.reply_text(
        f"Got it! Your Telegram user ID is:\n\n"
        f"`{user_id}`\n\n"
        f"Name: {name}\n"
        f"Username: @{username}\n\n"
        f"I will use this to configure the autopilot bot.",
        parse_mode="Markdown",
    )

def main():
    print("Waiting for you to send ANY message to the bot...")
    print("Open Telegram -> find your bot -> send /start or any text\n")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, any_message))
    app.run_polling()

if __name__ == "__main__":
    main()
