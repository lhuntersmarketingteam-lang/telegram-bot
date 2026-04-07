"""
main.py -- Telegram-bot via python-telegram-bot + OpenAI
Required env vars: BOT_TOKEN, OPENAI_API_KEY
"""

import logging
import os
import sys

from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Env vars check
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN not set. Add it in Railway Variables.")
    sys.exit(1)

if not OPENAI_API_KEY:
    logger.critical("OPENAI_API_KEY not set. Add it in Railway Variables.")
    sys.exit(1)

# OpenAI client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# System prompt
PROMPT = """
TUT BUDET MOY GOTOVIY PROMPT
"""


# Handlers

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info("Start from user %s (id=%s)", user.username, user.id)
    await update.message.reply_text("Hello! Send me a message.")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Send any text and I reply via OpenAI.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_text = update.message.text
    logger.info("Message from %s (id=%s): %s", user.username, user.id, user_text[:80])
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PROMPT.strip()},
                {"role": "user", "content": user_text},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        logger.info("OpenAI replied (%d chars)", len(answer))
    except Exception as exc:
        logger.error("OpenAI error: %s", exc, exc_info=True)
        answer = "Error calling OpenAI. Try again later."
    max_len = 4096
    for i in range(0, len(answer), max_len):
        await update.message.reply_text(answer[i : i + max_len])


# Entry point

def main() -> None:
    logger.info("Bot starting...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Polling started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

