"""
main.py -- Telegram-bot powered by python-telegram-bot + OpenAI API

Start command: python main.py

Required environment variables:
    BOT_TOKEN       -- Telegram bot token from @BotFather
    OPENAI_API_KEY  -- OpenAI API key
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

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment variables check
# ---------------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    logger.critical(
        "BOT_TOKEN environment variable is not set. "
        "Add it in Railway -> Variables and restart the service."
    )
    sys.exit(1)

if not OPENAI_API_KEY:
    logger.critical(
        "OPENAI_API_KEY environment variable is not set. "
        "Add it in Railway -> Variables and restart the service."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# OpenAI async client
# ---------------------------------------------------------------------------
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------------------------
# System prompt -- replace with your own ready prompt text
# ---------------------------------------------------------------------------
PROMPT = """
TUT BUDET MOY GOTOVIY PROMPT
"""

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info("cmd_start from user %s (id=%s)", user.username, user.id)
    await update.message.reply_text(
        f"Hello, {user.first_name}! Send me any message and I will reply via OpenAI."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "Send me any text message and I will answer using OpenAI API."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages and reply via OpenAI."""
    user = update.effective_user
    user_text = update.message.text
    logger.info(
        "Message from %s (id=%s): %s",
