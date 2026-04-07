"""
bot.py — главный файл Telegram-бота для анализа креативов
"""

import asyncio
import logging
import os
import base64

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from openai_client import analyze_creatives
from prompts import SYSTEM_PROMPT

# Загружаем переменные из .env
load_dotenv()

# Настройка логирования — видим что происходит в консоли
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# --- Состояния FSM (конечный автомат для сбора данных) ---
class CreativeAnalysis(StatesGroup):
    waiting_for_images = State()    # Ждём изображения
    waiting_for_brief = State()     # Ждём описание/бриф
    processing = State()            # Идёт обработка


# Хранилище данных сессии пользователя (в памяти)
user_sessions = {}


# --- Обработчик команды /start ---
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_sessions[message.from_user.id] = {"images": [], "brief": ""}

    await message.answer(
        "👋 Привет! Я бот для анализа креативов и генерации ТЗ для дизайнеров.\n\n"
        "📌 Как работать:\n"
        "1️⃣ Отправь мне изображения-референсы (1–10 штук)\n"
        "2️⃣ Напиши /done когда загрузишь все изображения\n"
        "3️⃣ Опиши проект, бренд и задачу\n"
        "4️⃣ Получи полный анализ и ТЗ\n\n"
        "🚀 Начни — отправь первое изображение!"
    )
    await state.set_state(CreativeAnalysis.waiting_for_images)


# --- Обработчик команды /help ---
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 Справка:\n\n"
        "/start — начать новый анализ\n"
        "/done — закончить загрузку изображений\n"
        "/cancel — отменить текущий анализ\n\n"
        "Бот принимает изображения референсов и текстовое описание проекта, "
        "после чего с помощью GPT-4 Vision анализирует визуальный стиль и "
        "генерирует профессиональное ТЗ для дизайнера."
    )


# --- Обработчик команды /cancel ---
@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in user_sessions:
        del user_sessions[message.from_user.id]
    await message.answer("❌ Анализ отменён. Напиши /start чтобы начать заново.")


# --- Приём изображений ---
@dp.message(CreativeAnalysis.waiting_for_images, F.photo)
async def receive_image(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Инициализируем сессию если нет
    if user_id not in user_sessions:
        user_sessions[user_id] = {"images": [], "brief": ""}

    # Ограничение: не более 10 изображений
    if len(user_sessions[user_id]["images"]) >= 10:
        await message.answer("⚠️ Максимум 10 изображений. Напиши /done для продолжения.")
        return

    # Берём фото лучшего качества (последнее в списке)
    photo = message.photo[-1]

    # Скачиваем файл и конвертируем в base64 для OpenAI Vision
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)
    image_b64 = base64.b64encode(file_bytes.read()).decode("utf-8")

    user_sessions[user_id]["images"].append(image_b64)
    count = len(user_sessions[user_id]["images"])

    await message.answer(
        f"✅ Изображение {count} получено!\n"
        f"Отправь ещё или напиши /done для продолжения."
    )


# --- Если прислали документ-изображение (не сжатое фото) ---
@dp.message(CreativeAnalysis.waiting_for_images, F.document)
async def receive_document(message: Message, state: FSMContext):
    if message.document.mime_type and message.document.mime_type.startswith("image/"):
        user_id = message.from_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = {"images": [], "brief": ""}

        if len(user_sessions[user_id]["images"]) >= 10:
            await message.answer("⚠️ Максимум 10 изображений.")
            return

        file = await bot.get_file(message.document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        image_b64 = base64.b64encode(file_bytes.read()).decode("utf-8")

        user_sessions[user_id]["images"].append(image_b64)
        count = len(user_sessions[user_id]["images"])
        await message.answer(f"✅ Изображение {count} получено! Отправь ещё или /done.")
    else:
        await message.answer("⚠️ Пожалуйста, отправляй только изображения.")


# --- Команда /done — переход к вводу брифа ---
@dp.message(Command("done"), CreativeAnalysis.waiting_for_images)
async def cmd_done(message: Message, state: FSMContext):
    user_id = message.from_user.id
    images = user_sessions.get(user_id, {}).get("images", [])

    if not images:
        await message.answer("⚠️ Сначала отправь хотя бы одно изображение!")
        return

    await state.set_state(CreativeAnalysis.waiting_for_brief)
    await message.answer(
        f"👍 Получено {len(images)} изображений.\n\n"
        "📝 Теперь опиши проект. Включи:\n"
        "• Название бренда и сфера деятельности\n"
        "• Целевая аудитория\n"
        "• Задача креатива (реклама, SMM, баннер и т.д.)\n"
        "• Желаемый стиль/настроение\n"
        "• Любые ссылки или дополнительные пожелания\n\n"
        "Просто напиши всё в одном сообщении:"
    )


# --- Приём брифа и запуск анализа ---
@dp.message(CreativeAnalysis.waiting_for_brief, F.text)
async def receive_brief(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_sessions[user_id]["brief"] = message.text

    await state.set_state(CreativeAnalysis.processing)
    await message.answer("⏳ Анализирую референсы... Это займёт 30–60 секунд.")

    try:
        images = user_sessions[user_id]["images"]
        brief = user_sessions[user_id]["brief"]

        # Вызываем OpenAI API
        result = await analyze_creatives(images, brief, SYSTEM_PROMPT)

        # Разбиваем на части если текст длинный (Telegram лимит 4096 символов)
        max_len = 4096
        for i in range(0, len(result), max_len):
            await message.answer(result[i:i + max_len])

        await message.answer(
            "✨ Анализ завершён!\n"
            "Напиши /start для нового анализа."
        )

    except Exception as e:
        logger.error(f"Ошибка при анализе: {e}")
        await message.answer(
            f"❌ Произошла ошибка при анализе: {str(e)}\n"
            "Попробуй снова или напиши /start."
        )
    finally:
        await state.clear()
        if user_id in user_sessions:
            del user_sessions[user_id]


# --- Запуск бота ---
async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
