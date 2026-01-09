import os
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
TASKS_FILE = "tasks.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [t for t in data if isinstance(t, dict)]
            return []
    except Exception:
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


async def send_reminder(chat_id, text):
    await bot.send_message(chat_id, f"⏰ Напоминание:\n{text}")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет 👋\n\n"
        "Я бот-напоминалка.\n\n"
        "Добавить задачу:\n"
        "/add Текст | ДД.ММ.ГГГГ ЧЧ:ММ\n\n"
        "Посмотреть задачи:\n"
        "/list"
    )


@dp.message_handler(commands=["add"])
async def add_task(message: types.Message):
    try:
        content = message.text.replace("/add", "").strip()
        text, time_str = content.split("|")
        text = text.strip()
        time_str = time_str.strip()

        run_date = datetime.strptime(time_str, "%d.%m.%Y %H:%M")

        task = {
            "chat_id": message.chat.id,
            "text": text,
            "time": run_date.isoformat(),
        }

        tasks.append(task)
        save_tasks(tasks)

        scheduler.add_job(
            send_reminder,
            "date",
            run_date=run_date,
            args=[message.chat.id, text],
        )

        await message.answer("✅ Задача добавлена")

    except Exception:
        await message.answer(
            "Ошибка формата.\n"
            "Пример:\n"
            "/add Позвонить | 11.01.2026 10:00"
        )


@dp.message_handler(commands=["list"])
async def list_tasks(message: types.Message):
    user_tasks = [
        t for t in tasks
        if isinstance(t, dict) and t.get("chat_id") == message.chat.id
    ]

    if not user_tasks:
        await message.answer("У тебя нет задач")
        return

    text = "Твои задачи:\n\n"
    for i, t in enumerate(user_tasks, 1):
        time = datetime.fromisoformat(t["time"]).strftime("%d.%m.%Y %H:%M")
        text += f"{i}. {t['text']} — {time}\n"

    await message.answer(text)


if __name__ == "__main__":
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
