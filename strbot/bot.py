import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv
import os
from handlers import register_handlers
from database import init_db

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not BOT_TOKEN:
    raise ValueError("Необходимо указать BOT_TOKEN в файле .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    # Инициализация базы данных
    await init_db()

    # Регистрация обработчиков
    await register_handlers(dp, bot, ADMIN_ID)

    # Установка команд бота
    await bot.set_my_commands([BotCommand(command="start", description="Запуск бота")])

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
