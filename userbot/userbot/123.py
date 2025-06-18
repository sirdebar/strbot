from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

# Данные API (можно получить на my.telegram.org)
api_id = '23422308'       # Замените на ваш API ID
api_hash = '1da8d8d190e8fb59531b28258d1ed64c'   # Замените на ваш API Hash

# Имя пользователя или ссылка на канал
channel_username = 'antisemeth'  # Без t.me/

# Создаем клиент Telegram
with TelegramClient('session_name', api_id, api_hash) as client:
    try:
        # Получаем информацию о канале
        channel = client.get_entity(channel_username)
        print(f"ID канала '{channel_username}': {channel.id}")
    except Exception as e:
        print(f"Ошибка: {e}")