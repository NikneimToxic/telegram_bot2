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
TELEGRAM_TOKEN = "вставь_свой_токен_сюда"
OPENROUTER_API_KEY = "вставь_свой_api_ключ_сюда"

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
            result = await resp.json()
            reply = result['choices'][0]['message']['content']

            # Добавляем ответ ChatGPT в историю
            conversation_history.append({"role": "assistant", "content": reply})

            return reply, conversation_history

# 📌 Команда /анекдот
@dp.message(F.text.lower() == "/анекдот")
async def send_joke(message: Message):
    await message.reply(random.choice(jokes))

# 📌 Команда /помощь
@dp.message(F.text.lower() == "/помощь")
async def send_help(message: Message):
    help_text = (
        "👋 Я весёлый бот для чата!\n\n"
        "Вот что я умею:\n"
        "• Отвечаю на сообщения с помощью ИИ (ChatGPT)\n"
        "• /анекдот — расскажу шутку\n"
        "• /помощь — покажу это меню\n"
        "• Реагирую на 'бот ты тут?' 😄\n"
        "• Приветствую новых участников"
    )
    await message.reply(help_text)

# 🔍 Реакция на упоминание бота
@dp.message(F.text.lower().contains("бот"))
async def reply_to_bot_mention(message: Message):
    if "ты где" in message.text.lower() or "тут" in message.text.lower():
        await message.reply("Я тут! Не сплю 😄")

# 👋 Приветствие новых участников
@dp.chat_member()
async def greet_new_member(update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member

    if old.status in ("left", "kicked") and new.status == "member":
        user = new.user
        welcome_text = f"👋 Добро пожаловать, <b>{user.full_name}</b>!\nРассаживайся поудобнее 😄"
        await bot.send_message(update.chat.id, welcome_text)

# 🤖 Ответ по умолчанию через GPT с историей
conversation_history = []

@dp.message()
async def handle_message(message: Message):
    global conversation_history
    try:
        reply, conversation_history = await get_openrouter_response(message.text, conversation_history)
        await message.reply(reply)
    except Exception as e:
        await message.reply(f"Упс! Ошибка: {e}")

# 🚀 Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
