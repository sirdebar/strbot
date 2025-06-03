import os
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

# Создаем каталог для хранения шаблонов, если его нет
os.makedirs("templates", exist_ok=True)

# Роутер для команды /zayvaru
zayvaru_router = Router()

# Определяем состояния FSM
class ZayvaruForm(StatesGroup):
    waiting_for_data = State()

@zayvaru_router.message(Command("zayvaru"))
async def cmd_zayvaru(message: Message, state: FSMContext):
    """Обработчик команды /zayvaru - начинает процесс создания заявления"""
    await message.answer(
        "Введите данные для заявления в следующем формате:\n"
        "ФИО и дата рождения подозреваемого\n\n"
        "Например: Петров Петр Петрович 01.01.2001"
    )
    await state.set_state(ZayvaruForm.waiting_for_data)

@zayvaru_router.message(ZayvaruForm.waiting_for_data, F.text)
async def process_data(message: Message, state: FSMContext):
    """Обработчик ввода персональных данных"""
    # Получаем данные от пользователя
    user_data = message.text.strip()
    
    # Создаем изображение заявления
    img_buffer = await create_complaint_image(user_data)
    
    # Отправляем изображение пользователю
    await message.answer_photo(
        types.BufferedInputFile(
            img_buffer.getvalue(),
            filename="complaint.png"
        ),
        caption="Скрин обращения на сайте МВД"
    )
    
    # Сбрасываем состояние
    await state.clear()

async def create_complaint_image(user_data: str) -> BytesIO:
    """
    Создает изображение заявления в формате веб-формы МВД
    
    Args:
        user_data: Данные пользователя
    
    Returns:
        BytesIO: Буфер с изображением в формате PNG
    """
    # Создаем новое изображение (белый фон)
    width, height = 1000, 900  # Уменьшенная высота
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Загружаем шрифт (используем системный шрифт)
    try:
        # Используем стандартные шрифты
        title_font = ImageFont.truetype("arial.ttf", 18)
        header_font = ImageFont.truetype("arial.ttf", 14)
        body_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
        button_font = ImageFont.truetype("arial.ttf", 14)
        caption_font = ImageFont.truetype("arial.ttf", 11)
    except IOError:
        # Если шрифт не найден, используем шрифт по умолчанию
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        button_font = ImageFont.load_default()
        caption_font = ImageFont.load_default()
    
    # --- ОСНОВНЫЕ ЭЛЕМЕНТЫ ФОРМЫ ---
    
    # Заголовок "Текст обращения" с звездочкой (обязательное поле)
    form_x = 10
    form_y = 10
    form_width = width - 20
    
    # Заголовок с красной звездочкой
    draw.text((form_x, form_y), "Текст обращения:", font=title_font, fill=(0, 0, 0))
    draw.text((form_x + 150, form_y), "*", font=title_font, fill=(255, 0, 0))  # Сдвинута правее
    form_y += 25
    
    # Рисуем рамку текстового поля (повторяем точно как на скриншоте)
    text_box_height = 400  # Уменьшенная высота
    draw.rectangle([(form_x, form_y), (form_x + form_width, form_y + text_box_height)], outline=(169, 169, 169), width=1, fill=(255, 255, 255))
    
    # Добавляем текст обращения в поле (черный цвет)
    complaint_text = f"""Прошу возбудить/рассмотреть уголовное дело по признакам состава преступления, предусмотренного статьей 135 УК РФ (развратные действия).

В соответствии с имеющейся у меня информацией, следующее лицо совершило противоправные действия, выразившиеся в совершении развратных действий без применения насилия, в отношении лица, не достигшего шестнадцатилетнего возраста:

{user_data}

Данное лицо совершило развратные действия в отношении лица, не достигшего шестнадцатилетнего возраста и половой зрелости при использовании платформы "Telegram", в целью распространения своего влияния и производных незаконных действий.

Прошу провести проверку указанных обстоятельств, установить виновных лиц, привлечь их к ответственности в соответствии с законодательством Российской Федерации и принять необходимые меры реагирования."""
    
    # Обрабатываем текст с переносами строк
    text_y = form_y + 10
    text_x = form_x + 10
    for line in complaint_text.split('\n'):
        # Разбиваем длинные строки
        wrapped_lines = textwrap.wrap(line, width=95)
        if not wrapped_lines and line.strip():  # Для пустых строк, но не для пробелов
            text_y += 20
            continue
            
        for wrapped_line in wrapped_lines:
            draw.text((text_x, text_y), wrapped_line, font=body_font, fill=(0, 0, 0))  # Черный цвет
            text_y += 20
    
    form_y += text_box_height + 10
    
    # Добавляем миниатюры прикрепленных файлов (3 скриншота)
    thumbnail_size = 60
    thumbnail_spacing = 10
    thumbnail_y = form_y
    
    # Создаем 3 миниатюры
    for i in range(3):
        thumbnail_x = form_x + i * (thumbnail_size + thumbnail_spacing)
        
        # Рисуем рамку миниатюры
        draw.rectangle([(thumbnail_x, thumbnail_y), (thumbnail_x + thumbnail_size, thumbnail_y + thumbnail_size)], outline=(169, 169, 169), width=1, fill=(240, 240, 240))
        
        # Добавляем текст "TG" в миниатюру
        draw.text((thumbnail_x + thumbnail_size//2, thumbnail_y + thumbnail_size//2), "TG", font=small_font, fill=(100, 100, 100), anchor="mm")
        
        # Добавляем номер скриншота
        draw.text((thumbnail_x + thumbnail_size//2, thumbnail_y + thumbnail_size - 5), f"Скрин {i+1}", font=small_font, fill=(100, 100, 100), anchor="mm")
    
    form_y += thumbnail_size + 20
    
    # Добавляем пояснительный текст (как на скриншоте)
    explanation_text = """Отсутствие возможности использовать механизм «копировать-вставить» предусмотрено в целях обеспечения защищенности сервиса от использования для рассылки рекламных сообщений (спам-рассылки). При этом реализована возможность прикрепления файлов различных форматов, за исключением исполняемых (имеющие расширения .exe, .jar и т.д.), суммарным объемом не более 30 Мб."""
    
    # Обрабатываем текст с переносами строк для объяснения
    wrapped_explanation = textwrap.wrap(explanation_text, width=110)
    for line in wrapped_explanation:
        draw.text((form_x, form_y), line, font=caption_font, fill=(100, 100, 100))
        form_y += 15
    
    form_y += 15
    
    # Кнопка "Прикрепить файл" (серая)
    button_width = 160
    button_height = 35
    button_color = (150, 150, 150)
    draw.rectangle([(form_x, form_y), (form_x + button_width, form_y + button_height)], fill=button_color)
    draw.text((form_x + button_width//2, form_y + button_height//2), "Прикрепить файл", font=button_font, fill=(255, 255, 255), anchor="mm")
    
    form_y += button_height + 30
    
    # Поле "Введите текст с изображения"
    draw.text((form_x, form_y), "Введите текст с изображения:", font=title_font, fill=(0, 0, 0))
    draw.text((form_x + 210, form_y), "*", font=title_font, fill=(255, 0, 0))
    form_y += 25
    
    # Поле для ввода капчи
    captcha_input_height = 40
    draw.rectangle([(form_x, form_y), (form_x + form_width, form_y + captcha_input_height)], outline=(169, 169, 169), width=1, fill=(255, 255, 255))
    form_y += captcha_input_height + 30
    
    # Кнопка "ОТПРАВИТЬ ОБРАЩЕНИЕ" (синяя)
    submit_button_width = 240
    submit_button_height = 40
    submit_button_x = width - form_x - submit_button_width
    submit_button_color = (51, 122, 183)  # Синий цвет как на скриншоте
    draw.rectangle([(submit_button_x, form_y), (submit_button_x + submit_button_width, form_y + submit_button_height)], fill=submit_button_color)
    draw.text((submit_button_x + submit_button_width//2, form_y + submit_button_height//2), "ОТПРАВИТЬ ОБРАЩЕНИЕ", font=button_font, fill=(255, 255, 255), anchor="mm")
    
    # Конвертируем изображение в байты и возвращаем
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    
    return img_buffer 