import asyncio
import logging
import sys
from os import getenv

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from handlers.pasta_handler import pasta_router
from handlers.zayvaru_handler import zayvaru_router

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Токен бота из переменной окружения
BOT_TOKEN = getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("Не указан токен бота! Установите переменную окружения BOT_TOKEN или создайте .env файл.")
    sys.exit(1)

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Диспетчер с хранилищем состояний в памяти
dp = Dispatcher(storage=MemoryStorage())

# Главный роутер
main_router = Router()

# Обработчик команды /start
@main_router.message(CommandStart())
async def command_start(message: types.Message):
    await message.answer(
        "Привет! Я бот с полезными командами:\n"
        "/pasta - получить текст для отправки\n"
        "/zayvaru - создать фейк-скрин обращения в гос. структуры"
    )

# Регистрация роутеров
dp.include_router(main_router)
dp.include_router(pasta_router)
dp.include_router(zayvaru_router)

# Функция запуска бота
async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 