import logging
import aiohttp
import asyncio
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ChatMemberUpdated

# 🔐 Вставь свои токены
TELEGRAM_TOKEN = "7991964078:AAH52l2MVnbjtoQlU76AVJpBt7-2SJW1Nko"
OPENROUTER_API_KEY = "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"

# 🤖 Инициализация бота
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# 😂 Список анекдотов
jokes = [
    "Почему программисты путают Хэллоуин и Рождество? Потому что 31 Oct = 25 Dec.",
    "Я сказал жене, что её код — спагетти. Теперь я ужинаю один.",
    "Бот сломался... но не сдался! 🤖",
    "Программисты не спят, они просто в режиме ожидания."
]

# 📜 История переписки
conversation_history = []

# 🧠 Получение ответа от OpenRouter GPT с историей
async def get_openrouter_response(user_message: str, conversation_history: list) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    conversation_history.append({"role": "user", "content": user_message})

    json_data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": conversation_history
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as resp:
            try:
                result = await resp.json()
                logging.info(f"Ответ OpenRouter: {result}")  # логируем ответ

                if "choices" not in result:
                    error_message = result.get("error", {}).get("message", "Неизвестная ошибка")
                    raise ValueError(f"Ошибка OpenRouter: {error_message}")

                reply = result["choices"][0]["message"]["content"]
                conversation_history.append({"role": "assistant", "content": reply})

                return reply, conversation_history
            except Exception as e:
                raise RuntimeError(f"Ошибка при запросе к OpenRouter: {e}")

# 📌 Команда /анекдот
@dp.message(F.text.lower() == "/анекдот")
async def send_joke(message: Message):
    await message.reply(random.choice(jokes))

# 📌 Команда /помощь
@dp.message(F.text.lower() == "/помощь")
async def send_help(message: Message):
    @dp.message(F.text.lower() == "/помощь")
async def send_help(message: Message):
    help_text = (
        "🤖 Я — умный Telegram бот!\n\n"
        "• Просто напиши что-то — и я отвечу через GPT\n"
        "• /анекдот — получи шутку\n"
        "• /помощь — покажу это меню"
    )
    await message.reply(help_text)
