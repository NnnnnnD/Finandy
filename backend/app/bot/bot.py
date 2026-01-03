from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
)
from telegram.request import HTTPXRequest

from app.bot.telegram import on_message, on_start
from app.core.config import settings


def run_bot():
    # 🔥 FIX TIMEOUT TELEGRAM
    request = HTTPXRequest(
        connect_timeout=20,
        read_timeout=20,
        write_timeout=20,
        pool_timeout=20,
    )

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    print("🤖 Finandy Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
