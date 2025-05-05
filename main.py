import logging
import aiohttp
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from aiogram import Router
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("7991964078:AAH52l2MVnbjtoQlU76AVJpBt7-2SJW1Nko")
OPENROUTER_API_KEY = os.getenv("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")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing from the environment variables!")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing from the environment variables!")

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

logging.basicConfig(level=logging.INFO)

async def get_openrouter_response(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as resp:
            result = await resp.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "Извините, произошла ошибка при обработке вашего запроса."

@router.message()
async def handle_message(message: Message):
    reply = await get_openrouter_response(message.text)
    await message.reply(reply)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
