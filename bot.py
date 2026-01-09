import asyncio
import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8560822174:AAFCDaWwp1jLzLmURq28FvbY0nv_HBUOLas"
DATA_FILE = "tasks.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

user_state = {}


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить задачу")],
            [KeyboardButton(text="📋 Список задач")]
        ],
        resize_keyboard=True
    )


async def remind(chat_id, text):
    await bot.send_message(chat_id, f"⏰ Напоминание:\n{text}")


@dp.message(F.text == "/start")
async def start(message: Message):
    chat_id = str(message.chat.id)
    tasks.setdefault(chat_id, [])
    save_tasks(tasks)

    await message.answer(
        "Я бот-напоминалка.\nВыбери действие:",
        reply_markup=main_keyboard()
    )


@dp.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: Message):
    user_state[message.chat.id] = {"step": "text"}
    await message.answer("Что нужно напомнить?")


@dp.message(F.text == "📋 Список задач")
async def list_tasks(message: Message):
    chat_id = str(message.chat.id)
    user_tasks = tasks.get(chat_id, [])

    if not user_tasks:
        await message.answer("Задач пока нет.")
        return

    text = ""
    for i, t in enumerate(user_tasks, 1):
        text += f"{i}. {t['text']} — {t['time']}\n"

    await message.answer(text)


@dp.message()
async def process_steps(message: Message):
    state = user_state.get(message.chat.id)
    if not state:
        return

    if state["step"] == "text":
        state["text"] = message.text
        state["step"] = "time"
        await message.answer("Когда напомнить?\nФормат: ДД.ММ.ГГГГ ЧЧ:ММ")
        return

    if state["step"] == "time":
        try:
            remind_time = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
            chat_id = str(message.chat.id)

            task = {
                "text": state["text"],
                "time": message.text
            }

            tasks.setdefault(chat_id, []).append(task)
            save_tasks(tasks)

            scheduler.add_job(
                remind,
                "date",
                run_date=remind_time,
                args=[message.chat.id, task["text"]]
            )

            user_state.pop(message.chat.id)

            await message.answer(
                "Задача сохранена ✅",
                reply_markup=main_keyboard()
            )

        except:
            await message.answer("Неверный формат даты. Попробуй ещё раз.")


async def main():
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
