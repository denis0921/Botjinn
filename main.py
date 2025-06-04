import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from collections import defaultdict
import asyncio
import os

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_data = defaultdict(lambda: {
    "balance": 0,
    "level": 1,
    "taps": 0,
    "last_reset": None
})

# Кнопка "Тапнуть"
tap_kb = ReplyKeyboardMarkup(resize_keyboard=True)
tap_kb.add(KeyboardButton("👆 Тапнуть"))

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в Crypto Jinn TapBot!\n"
        "Нажимай 👆 'Тапнуть', чтобы зарабатывать монеты.",
        reply_markup=tap_kb
    )

@dp.message_handler(lambda message: message.text == "👆 Тапнуть")
async def tap_handler(message: types.Message):
    user = user_data[message.from_user.id]
    if user["taps"] >= 1000:
        await message.answer("⚠️ Лимит 1000 тапов в час исчерпан. Жди восстановления.")
        return
    user["balance"] += 1
    user["taps"] += 1
    await message.answer(f"😄 Ты заработал 1 монету!\n💰 Баланс: {user['balance']}\n📈 Уровень: {user['level']}")

@dp.message_handler(commands=["level"])
async def level_handler(message: types.Message):
    user = user_data[message.from_user.id]
    next_level_cost = int(user["balance"] * 0.35)
    if user["balance"] >= next_level_cost:
        user["balance"] -= next_level_cost
        user["level"] += 1
        await message.answer(
            f"🚀 Ты повысил уровень!\n📈 Новый уровень: {user['level']}\n💰 Баланс: {user['balance']}"
        )
    else:
        await message.answer(
            f"❌ Нужно {next_level_cost} монет для повышения уровня.\n💰 Текущий баланс: {user['balance']}"
        )

async def reset_taps():
    while True:
        await asyncio.sleep(3600)
        for user in user_data.values():
            user["taps"] = 0

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(reset_taps())
    executor.start_polling(dp, skip_updates=True)

