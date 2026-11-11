import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Check your .env file.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Telegram chat ID: {update.effective_chat.id}")
    await update.message.reply_text(
        "Investment Monitor is online! 🚀"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Pong! The monitoring program is running."
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    print("Investment Monitor started.")
    app.run_polling()


if __name__ == "__main__":
    main()
