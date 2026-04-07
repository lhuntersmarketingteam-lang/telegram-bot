# 🎨 Creative Analysis Telegram Bot

Telegram-бот для анализа визуальных референсов и генерации ТЗ для дизайнеров.  
Использует GPT-4o Vision для анализа изображений.

## Что умеет бот

- Принимает до 10 изображений-референсов
- Анализирует визуальный стиль, палитру, типографику, композицию
- Определяет mood и tone
- Находит брендинговые паттерны
- Генерирует идеи новых креативов
- Создаёт техническое задание для дизайнера
- Пишет промпты для AI-генерации (Midjourney / DALL-E 3)

## Структура проекта

```
telegram-bot/
├── bot.py              # Главный файл бота (логика, FSM, обработчики)
├── openai_client.py    # Клиент OpenAI API (Vision)
├── prompts.py          # Системный промпт для GPT-4o
├── requirements.txt    # Зависимости Python
├── .env.example        # Пример файла с переменными окружения
├── .gitignore          # Исключения для git
├── Procfile            # Команда запуска для Railway
├── railway.json        # Конфигурация Railway
└── README.md           # Этот файл
```

---

## 🚀 Быстрый старт (локально)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/lhuntersmarketingteam-lang/telegram-bot.git
cd telegram-bot
```

### 2. Создать виртуальное окружение

```bash
# Создаём venv
python -m venv venv

# Активируем (Mac/Linux)
source venv/bin/activate

# Активируем (Windows)
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Получить токены

**Токен Telegram-бота:**
1. Открой Telegram, найди @BotFather
2. Напиши /newbot
3. Придумай имя и username для бота
4. Скопируй токен вида `123456789:AABBccDDeEFf...`

**API-ключ OpenAI:**
1. Зайди на https://platform.openai.com/api-keys
2. Нажми "Create new secret key"
3. Скопируй ключ вида `sk-proj-...`
4. ⚠️ Убедись что на аккаунте есть баланс (хотя бы $5)

### 5. Создать файл .env

```bash
cp .env.example .env
```

Открой `.env` в любом редакторе и заполни:

```
TELEGRAM_TOKEN=123456789:AABBccDDeEFfggHHiiJJkkLL
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
```

### 6. Запустить бота

```bash
python bot.py
```

Если видишь `INFO - Бот запускается...` — всё работает! ✅

---

## ☁️ Деплой на Railway

### 1. Зарегистрироваться на Railway

Зайди на https://railway.app и войди через GitHub.

### 2. Создать новый проект

1. Нажми **New Project**
2. Выбери **Deploy from GitHub repo**
3. Найди `telegram-bot` в списке репозиториев
4. Нажми **Deploy Now**

### 3. Добавить переменные окружения

1. В проекте нажми на сервис (карточка с именем)
2. Перейди во вкладку **Variables**
3. Добавь две переменные:
   - `TELEGRAM_TOKEN` = твой токен бота
   - `OPENAI_API_KEY` = твой ключ OpenAI

### 4. Проверить деплой

1. Перейди во вкладку **Deployments**
2. Нажми на последний деплой
3. Посмотри логи — должна быть строка `Бот запускается...`

### 5. Готово! 🎉

Railway автоматически передеплоит бота при каждом пуше в `main`.

---

## 💬 Как использовать бота

1. Найди своего бота в Telegram по username
2. Напиши `/start`
3. Отправь 1–10 изображений-референсов
4. Напиши `/done`
5. Опиши проект в одном сообщении
6. Получи полный анализ через 30–60 секунд

---

## 🔧 Чек-лист для отладки

- [ ] Файл `.env` создан и заполнен (не `.env.example`!)
- [ ] Токен бота начинается с цифр (формат `123456:AAB...`)
- [ ] OpenAI ключ начинается с `sk-`
- [ ] На OpenAI аккаунте есть баланс
- [ ] Все зависимости установлены (`pip install -r requirements.txt`)
- [ ] Python версии 3.9 или выше (`python --version`)
- [ ] Бот не запущен дважды одновременно

**Частые ошибки:**

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Unauthorized` | Неверный токен бота | Проверь TELEGRAM_TOKEN в .env |
| `AuthenticationError` | Неверный ключ OpenAI | Проверь OPENAI_API_KEY в .env |
| `RateLimitError` | Нет баланса OpenAI | Пополни счёт на platform.openai.com |
| `ModuleNotFoundError` | Не установлены зависимости | Запусти `pip install -r requirements.txt` |

---

## 📦 Технологии

- **Python 3.11**
- **aiogram 3.x** — асинхронный фреймворк для Telegram-ботов
- **OpenAI GPT-4o** — анализ изображений и генерация текста
- **Railway** — хостинг и деплой
- **python-dotenv** — управление переменными окружения
