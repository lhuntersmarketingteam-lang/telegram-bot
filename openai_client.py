"""
openai_client.py — клиент для работы с OpenAI API (GPT-4 Vision)
"""

import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Создаём асинхронный клиент OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Модель с поддержкой изображений
VISION_MODEL = "gpt-4o"  # gpt-4o поддерживает vision и дешевле gpt-4-vision-preview


async def analyze_creatives(images_b64: list, brief: str, system_prompt: str) -> str:
    """
    Анализирует изображения-референсы с помощью OpenAI GPT-4o Vision.
    
    Аргументы:
        images_b64: список изображений в формате base64
        brief: текстовое описание проекта от пользователя
        system_prompt: системный промпт с инструкциями для анализа
    
    Возвращает:
        Строку с полным анализом и ТЗ
    """
    
    # Формируем список сообщений с изображениями
    # OpenAI Vision принимает изображения как часть user-сообщения
    content = []
    
    # Добавляем все изображения в запрос
    for i, img_b64 in enumerate(images_b64):
        content.append({
            "type": "image_url",
            "image_url": {
                # Формат: data:image/jpeg;base64,<base64_string>
                "url": f"data:image/jpeg;base64,{img_b64}",
                "detail": "high"  # high = детальный анализ, low = быстро и дёшево
            }
        })
    
    # Добавляем текстовое описание после изображений
    content.append({
        "type": "text",
        "text": f"Вот бриф и описание проекта от клиента:\n\n{brief}"
    })
    
    # Отправляем запрос к OpenAI
    response = await client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=4000,  # Достаточно для детального анализа
        temperature=0.7,  # Баланс между креативностью и точностью
    )
    
    # Извлекаем текст ответа
    return response.choices[0].message.content
