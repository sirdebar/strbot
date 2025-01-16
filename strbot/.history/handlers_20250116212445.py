from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import add_strings, get_unused_string, increment_usage_count
from aiogram.utils.markdown import escape_markdown

# Множество для хранения пользователей, которые уже взяли строку
received_users = set()

# Клавиатура для пользователя
def get_user_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Iphone", url="https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690")],
            [InlineKeyboardButton(text="Android", url="https://play.google.com/store/apps/details?id=dev.hexasoftware.v2box&hl=en_US")],
            [InlineKeyboardButton(text="Получить строку", callback_data="get_string")]
        ]
    )

# Клавиатура для администратора
def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Загрузить строки")]],
        resize_keyboard=True
    )

# Обработчик команды /start
async def start_command(message: Message, ADMIN_ID: int):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привет, Админ!", reply_markup=get_admin_keyboard())
    else:
        await message.answer_photo(
            photo="https://imgur.com/a/bMFpMwO",  # Укажите URL или путь к изображению
            caption="Добро пожаловать! Выберите тип устройства для загрузки клиента:",
            reply_markup=get_user_keyboard()  # Сразу показываем кнопки
        )

# Хэндлер для нажатия на кнопку "Получить строку"
async def send_string(callback_query):
    user_id = callback_query.from_user.id

    # Проверяем, если пользователь уже получил строку
    if user_id in received_users:
        await callback_query.message.answer("Вы уже получили строку. Больше нельзя.")
        await callback_query.answer()
        return

    # Получаем строку из базы данных
    string_data = await get_unused_string()

    if string_data:
        string_id, string = string_data

        # Отправляем строку пользователю
        await callback_query.message.answer(f"Ваша строка: {string}")

        # Увеличиваем счетчик использования строки
        await increment_usage_count(string_id)

        # Добавляем пользователя в список получивших строку
        received_users.add(user_id)

    else:
        # Если строки нет в базе данных
        await callback_query.message.answer("В базе данных пока нет строк. Обратитесь к администратору.")
    
    await callback_query.answer()

# Кнопка "Загрузить строки" для администратора
async def load_strings(message: Message, ADMIN_ID: int, dp: Dispatcher):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Отправьте строки для загрузки (по одной на строке):")

        @dp.message(F.text, F.from_user.id == ADMIN_ID)
        async def handle_uploaded_strings(upload_message: Message):
            strings = upload_message.text.splitlines()
            await add_strings(strings)
            await upload_message.answer(f"Добавлено строк: {len(strings)}")

# Регистрация хэндлеров
async def register_handlers(dp: Dispatcher, bot: Bot, ADMIN_ID: int):
    # Хэндлер для команды /start
    @dp.message(F.text == "/start")
    async def start_handler(message: Message):
        await start_command(message, ADMIN_ID)

    # Хэндлер для получения строки
    @dp.callback_query(F.data == "get_string")
    async def get_string_handler(callback_query):
        await send_string(callback_query)

    # Хэндлер для загрузки строк
    @dp.message(F.text == "Загрузить строки", F.from_user.id == ADMIN_ID)
    async def load_strings_handler(message: Message):
        await load_strings(message, ADMIN_ID, dp)
