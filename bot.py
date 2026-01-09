import os
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


async def reminder(chat_id: int, text: str, delay: int):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id, f"⏰ Напоминание:\n{text}")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет.\n\n"
        "Я простой бот-напоминалка.\n\n"
        "Формат команды:\n"
        "/add Текст | ДД.ММ.ГГГГ ЧЧ:ММ\n\n"
        "Пример:\n"
        "/add Позвонить | 09.01.2026 15:30"
    )


@dp.message_handler(commands=["add"])
async def add(message: types.Message):
    try:
        content = message.text.replace("/add", "").strip()
        text, time_str = content.split("|")
        text = text.strip()
        time_str = time_str.strip()

        run_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
        now = datetime.now()

        delay = int((run_time - now).total_seconds())
        if delay <= 0:
            await message.answer("Время уже прошло.")
            return

        asyncio.create_task(reminder(message.chat.id, text, delay))
        await message.answer("✅ Напоминание установлено")

    except Exception:
        await message.answer(
            "❌ Ошибка формата.\n"
            "Используй:\n"
            "/add Текст | 09.01.2026 15:30"
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
