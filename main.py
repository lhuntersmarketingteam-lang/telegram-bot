"""
main.py — Telegram-бот для анализа рекламных креативов
Логика: /start → пользователь шлёт фото (1-10) → /done → пишет бриф → GPT-4o анализирует → выдаёт ТЗ
"""
import base64
import logging
import os
import sys
from io import BytesIO

from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
        logger.critical("BOT_TOKEN not set.")
        sys.exit(1)
    if not OPENAI_API_KEY:
            logger.critical("OPENAI_API_KEY not set.")
            sys.exit(1)

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Состояния диалога
WAITING_PHOTOS, WAITING_BRIEF = range(2)

SYSTEM_PROMPT = """Ты — профессиональный арт-директор и дизайн-стратег с опытом работы в digital-рекламе.

Твоя задача — проанализировать рекламные креативы (изображения-референсы), которые прислал пользователь, и на основе его брифа составить детальное техническое задание (ТЗ) для дизайнера.

Структура твоего ответа:

1. АНАЛИЗ РЕФЕРЕНСОВ
— Визуальный стиль (минимализм, гранж, корпоративный и т.д.)
— Цветовая палитра (основные цвета, акценты, настроение)
— Типографика (засечки/без засечек, вес шрифта, иерархия)
— Композиция и layout (расположение элементов, сетка)
— Настроение и эмоция (что транслирует креатив)

2. ВЫВОДЫ ПО СТИЛЮ
— Общие паттерны среди референсов
— Что работает хорошо и почему

3. ТЕХНИЧЕСКОЕ ЗАДАНИЕ ДЛЯ ДИЗАЙНЕРА
— Концепция и идея
— Цветовая палитра с HEX-кодами
— Шрифты (конкретные названия + Google Fonts если возможно)
— Композиция и структура
— Графические элементы и текстуры
— Размеры и форматы (если указано в брифе)
— Tone of voice визуала

Отвечай на русском языке. Будь конкретным — дай практически применимое ТЗ."""


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data.clear()
        context.user_data["photos"] = []
        logger.info("User %s started", update.effective_user.id)
        await update.message.reply_text(
            "👋 Привет! Я помогу проанализировать твои рекламные креативы и составить ТЗ для дизайнера.\n\n"
            "📸 Шаг 1: Пришли мне изображения-референсы (от 1 до 10 штук).\n"
            "Это могут быть рекламные баннеры, посты, принты — любые визуальные примеры стиля, который тебе нравится.\n\n"
            "Когда загрузишь все фото — напиши /done"
        )
        return WAITING_PHOTOS


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        photos = context.user_data.setdefault("photos", [])

    if len(photos) >= 10:
                await update.message.reply_text("⚠️ Максимум 10 изображений. Напиши /done чтобы продолжить.")
                return WAITING_PHOTOS

    photo = update.message.photo[-1]
    file = await photo.get_file()
    buf = BytesIO()
    await file.download_to_memory(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    photos.append(b64)

    count = len(photos)
    await update.message.reply_text(
                f"✅ Фото {count} получено!\n"
                f"{'Пришли ещё или напиши /done чтобы перейти к брифу.' if count < 10 else 'Максимум достигнут. Напиши /done.'}"
    )
    return WAITING_PHOTOS


async def receive_photo_doc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        doc = update.message.document
        if not doc.mime_type or not doc.mime_type.startswith("image/"):
                    await update.message.reply_text("⚠️ Пожалуйста, присылай только изображения.")
                    return WAITING_PHOTOS

        photos = context.user_data.setdefault("photos", [])
        if len(photos) >= 10:
                    await update.message.reply_text("⚠️ Максимум 10 изображений. Напиши /done.")
                    return WAITING_PHOTOS

        file = await doc.get_file()
        buf = BytesIO()
        await file.download_to_memory(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        photos.append(b64)

    count = len(photos)
    await update.message.reply_text(f"✅ Фото {count} получено! Пришли ещё или напиши /done.")
    return WAITING_PHOTOS


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        photos = context.user_data.get("photos", [])
        if not photos:
                    await update.message.reply_text("⚠️ Сначала пришли хотя бы одно изображение-референс!")
                    return WAITING_PHOTOS

        await update.message.reply_text(
            f"👍 Отлично! Получено {len(photos)} фото.\n\n"
            "📝 Шаг 2: Теперь опиши проект.\n\n"
            "Напиши в одном сообщении:\n"
            "• Название бренда и сфера деятельности\n"
            "• Целевая аудитория\n"
            "• Задача креатива (баннер, пост, флаер и т.д.)\n"
            "• Желаемый стиль или настроение\n"
            "• Любые дополнительные пожелания"
        )
        return WAITING_BRIEF


async def receive_brief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        brief = update.message.text
        photos = context.user_data.get("photos", [])

    await update.message.reply_text("⏳ Анализирую референсы и готовлю ТЗ... Это займёт около 30–60 секунд.")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
                content = []
                for b64 in photos:
                                content.append({
                                                    "type": "image_url",
                                                    "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}
                                })
                            content.append({"type": "text", "text": f"Бриф от клиента:\n{brief}"})

        response = await openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                                            {"role": "system", "content": SYSTEM_PROMPT},
                                            {"role": "user", "content": content},
                        ],
                        max_tokens=4000,
                        temperature=0.7,
        )
        result = response.choices[0].message.content
        logger.info("OpenAI replied %d chars", len(result))

        max_len = 4096
        for i in range(0, len(result), max_len):
                        await update.message.reply_text(result[i:i + max_len])

        await update.message.reply_text(
                        "✨ Готово! Напиши /start чтобы проанализировать новый набор референсов."
        )

except Exception as exc:
        logger.error("OpenAI error: %s", exc, exc_info=True)
        await update.message.reply_text(
                        f"❌ Ошибка при обращении к OpenAI: {exc}\nПопробуй снова — напиши /start."
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data.clear()
    await update.message.reply_text("❌ Отменено. Напиши /start чтобы начать заново.")
    return ConversationHandler.END


async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        state = context.user_data.get("_state")
    await update.message.reply_text(
                "📸 Жду изображения-референсы. Пришли фото или напиши /done если уже загрузил все."
    )


def main() -> None:
        logger.info("Bot starting...")
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
                entry_points=[CommandHandler("start", cmd_start)],
                states={
                                WAITING_PHOTOS: [
                                                    MessageHandler(filters.PHOTO, receive_photo),
                                                    MessageHandler(filters.Document.IMAGE, receive_photo_doc),
                                                    CommandHandler("done", cmd_done),
                                ],
                                WAITING_BRIEF: [
                                                    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_brief),
                                ],
                },
                fallbacks=[
                                CommandHandler("cancel", cmd_cancel),
                                MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_text),
                ],
    )

    app.add_handler(conv)
    logger.info("Polling started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
        main()
