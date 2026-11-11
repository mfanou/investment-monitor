import os
import json
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from src.article_monitor import ArticleMonitor, CONFIG_FILE

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Check your .env file.")

if not CHAT_ID:
    raise RuntimeError("CHAT_ID is missing. Check your .env file.")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def collect_pending(source):
    monitor = ArticleMonitor()
    try:
        result = monitor.check_source(source)
        pending = monitor.pending_articles(
            source["name"],
            source.get("max_articles_per_check", 20),
        )
        return result, [dict(article) for article in pending]
    finally:
        monitor.close()


def mark_delivered(article_id):
    monitor = ArticleMonitor()
    try:
        monitor.mark_notified(article_id)
    finally:
        monitor.close()


async def check_source(context: ContextTypes.DEFAULT_TYPE):
    source = context.job.data

    try:
        result, articles = await asyncio.to_thread(
            collect_pending, source
        )

        if result["first_run"]:
            logger.info(
                "%s: initial baseline established; no old articles sent.",
                source["name"],
            )
            return

        if not articles:
            logger.info("%s: no new articles.", source["name"])
            return

        for article in articles:
            message = (
                f"📰 {source['name']}\n\n"
                f"{article['title']}\n\n"
                f"Published: {article['published_at'] or 'Date unavailable'}\n\n"
                f"{article['link']}"
            )

            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                disable_web_page_preview=False,
            )

            await asyncio.to_thread(
                mark_delivered, article["article_id"]
            )

            logger.info(
                "Delivered article: %s", article["title"]
            )

    except Exception:
        logger.exception(
            "Article check failed for %s", source["name"]
        )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    print(f"Telegram chat ID: {update.effective_chat.id}")
    await update.message.reply_text(
        "Investment Monitor is online! 🚀"
    )


async def ping(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "Pong! The monitoring program is running."
    )


async def post_init(application: Application):
    with CONFIG_FILE.open(encoding="utf-8") as file:
        config = json.load(file)

    for source in config["sources"]:
        if not source.get("enabled", False):
            continue

        interval = source.get("interval_minutes", 15)

        application.job_queue.run_repeating(
            check_source,
            interval=interval * 60,
            first=5,
            data=source,
            name=f"monitor_{source['name']}",
        )

        logger.info(
            "Scheduled %s every %s minutes.",
            source["name"],
            interval,
        )


def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    logger.info("Investment Monitor started.")
    app.run_polling()


if __name__ == "__main__":
    main()
