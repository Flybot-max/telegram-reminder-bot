import os
import json
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TASKS_FILE = "tasks.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()


# === ЗАГРУЗКА / СОХРАНЕНИЕ ЗАДАЧ ===
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


# === НАПОМИНАНИЕ ===
async def send_reminder(chat_id: int, text: str):
    await bot.send_message(chat_id, f"⏰ Напоминание:\n{text}")


# === ВОССТАНОВЛЕНИЕ ЗАДАЧ ПОСЛЕ ПЕРЕЗАПУСКА ===
def restore_jobs():
    for task in tasks:
