import sys
import os
import zipfile
import webbrowser
import json
import shutil
import subprocess
import platform
import glob
import time
import logging
import traceback
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLabel, 
                            QFileDialog, QMessageBox, QProgressBar, QTabWidget,
                            QSplitter, QMenu, QFrame, QComboBox, QTreeWidget,
                            QTreeWidgetItem, QInputDialog, QSystemTrayIcon, QDialog,
                            QAbstractItemView, QLineEdit)
from PySide6.QtCore import Qt, QMimeData, QThread, Signal, QPoint, QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QColor, QAction, QIcon

# Настройка логирования
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_manager.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WhatsAppSessionManager")

# Логируем информацию о системе
logger.info(f"Запуск приложения. Версия Python: {sys.version}")
logger.info(f"Операционная система: {platform.system()} {platform.version()}")
logger.info(f"Текущая директория: {os.getcwd()}")

# Вспомогательная функция для безопасного декодирования вывода процесса
def safe_decode(text, encodings=('cp866', 'utf-8', 'cp1251')):
    """Пытается декодировать текст из разных кодировок"""
    if not text:
        return ""
        
    for encoding in encodings:
        try:
            return text.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # Если все попытки не удались, используем replace для игнорирования ошибок
    return text.decode('utf-8', errors='replace')

# Функция для запуска процесса с обработкой ошибок
def run_process(command, shell=True):
    """Запускает процесс и возвращает результат с обработкой ошибок"""
    try:
        logger.info(f"Выполнение команды: {command}")
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            shell=shell,
            universal_newlines=False  # Работаем с байтами
        )
        stdout, stderr = process.communicate()
        
        # Декодируем вывод
        stdout_text = safe_decode(stdout)
        stderr_text = safe_decode(stderr)
        
        logger.info(f"Код возврата: {process.returncode}")
        if stdout_text:
            logger.info(f"Стандартный вывод: {stdout_text[:500]}{'...' if len(stdout_text) > 500 else ''}")
        if stderr_text:
            logger.warning(f"Стандартный вывод ошибок: {stderr_text}")
            
        return {
            "success": process.returncode == 0,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "returncode": process.returncode
        }
    except Exception as e:
        logger.error(f"Ошибка при выполнении процесса: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

# Функция для распаковки архивов с помощью 7z.exe
def extract_with_7zip(archive_path, output_dir):
    try:
        logger.info(f"Запрос на распаковку архива: {archive_path} -> {output_dir}")
        
        # Проверяем, что архив существует
        if not os.path.exists(archive_path):
            error_msg = f"Архив не найден: {archive_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Проверяем расширение файла
        file_ext = os.path.splitext(archive_path)[1].lower()
        if file_ext not in ['.zip', '.rar', '.7z']:
            logger.warning(f"Необычное расширение файла для архива: {file_ext}")
            
        # Проверяем размер файла
        file_size = os.path.getsize(archive_path)
        if file_size < 100:  # Слишком маленький размер для архива
            error_msg = f"Архив слишком мал ({file_size} байт), вероятно поврежден: {archive_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Ищем 7z.exe в нескольких местах
        seven_zip_locations = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "7z.exe"),  # В директории приложения
            os.path.join(os.getcwd(), "7z.exe"),  # В текущей рабочей директории
            "C:\\Program Files\\7-Zip\\7z.exe",  # Стандартный путь установки
            "C:\\Program Files (x86)\\7-Zip\\7z.exe",  # Для 32-битной версии на 64-битных системах
        ]
        
        # Перебираем все возможные места расположения 7z.exe
        seven_zip_path = None
        for location in seven_zip_locations:
            if os.path.exists(location):
                # Проверяем, что файл исполняемый и имеет правильный размер
                if os.path.getsize(location) > 100000:  # Минимальный размер 7z.exe в байтах
                    seven_zip_path = location
                    break
                else:
                    logger.warning(f"Найден 7z.exe по пути {location}, но файл слишком мал, возможно поврежден")
            else:
                logger.debug(f"7z.exe не найден по пути: {location}")
        
        if not seven_zip_path:
            # Если 7z не найден в стандартных местах, пробуем найти через PATH
            try:
                # Проверяем, существует ли 7z в системном PATH
                result = run_process("where 7z")
                
                if result["success"]:
                    # Используем первый найденный путь
                    seven_zip_path = result["stdout"].strip().split('\n')[0]
                    logger.info(f"7z.exe найден в PATH: {seven_zip_path}")
                    
            except Exception as e:
                logger.error(f"Ошибка при поиске 7z в PATH: {str(e)}")
                # Если где-то произошла ошибка, пробуем прямое имя команды
                seven_zip_path = "7z"
        
        if not seven_zip_path:
            error_msg = "7z.exe не найден. Пожалуйста, установите 7-Zip или поместите 7z.exe в директорию программы."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.info(f"Найден 7z.exe по пути: {seven_zip_path}")
        
        # Проверяем существование и доступность архива
        if not os.path.exists(archive_path):
            error_msg = f"Архив не найден: {archive_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not os.access(archive_path, os.R_OK):
            error_msg = f"Нет прав на чтение архива: {archive_path}"
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        # Логируем информацию о файле
        file_size = os.path.getsize(archive_path)
        logger.info(f"Размер архива: {file_size} байт")
        
        # Проверяем доступность директории для записи
        output_dir_parent = os.path.dirname(output_dir)
        if not os.path.exists(output_dir_parent):
            try:
                os.makedirs(output_dir_parent, exist_ok=True)
                logger.info(f"Создана родительская директория: {output_dir_parent}")
            except Exception as e:
                error_msg = f"Не удалось создать родительскую директорию: {str(e)}"
                logger.error(error_msg)
                raise PermissionError(error_msg)
                
        if not os.access(output_dir_parent, os.W_OK):
            error_msg = f"Нет прав на запись в директорию: {output_dir_parent}"
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        # Если целевая директория существует, проверяем права на запись
        if os.path.exists(output_dir) and not os.access(output_dir, os.W_OK):
            error_msg = f"Нет прав на запись в директорию: {output_dir}"
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        # Тест архива перед распаковкой
        logger.info(f"Тестирование архива: {seven_zip_path} t \"{archive_path}\"")
        test_result = run_process([seven_zip_path, "t", archive_path])
        
        if not test_result["success"]:
            error_msg = f"Ошибка при проверке архива: {test_result['stderr'] or test_result['stdout']}"
            logger.error(error_msg)
            # Попробуем распаковать архив даже если тест не прошел, но с предупреждением
            logger.warning("Попытка распаковки архива, несмотря на ошибку при тестировании")
        
        # Создаем директорию, если она не существует
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Директория для распаковки: {output_dir}")
        
        # Проверяем свободное место на диске
        try:
            disk = os.path.splitdrive(output_dir)[0] or os.path.dirname(output_dir)
            free_space = shutil.disk_usage(disk).free
            logger.info(f"Свободное место на диске {disk}: {free_space / (1024*1024):.2f} МБ")
            
            # Примерная оценка: сжатый архив может быть в ~2-10 раз меньше распакованного
            # Берем запас с коэффициентом 15, чтобы быть уверенными
            if free_space < file_size * 15:
                logger.warning(f"Мало свободного места на диске. Это может привести к проблемам при распаковке.")
        except Exception as e:
            logger.warning(f"Не удалось проверить свободное место на диске: {str(e)}")
        
        # Выполняем команду для распаковки
        extract_cmd = [seven_zip_path, "x", archive_path, f"-o{output_dir}", "-y"]
        logger.info(f"Распаковка архива: {' '.join(extract_cmd)}")
        extract_result = run_process(extract_cmd)
        
        if not extract_result["success"]:
            error_msg = f"Ошибка при распаковке: {extract_result['stderr'] or extract_result['stdout']}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Проверяем, что хоть что-то было распаковано
        if not os.path.exists(output_dir):
            error_msg = f"Директория распаковки не существует: {output_dir}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        extracted_files = os.listdir(output_dir)
        if not extracted_files:
            error_msg = "Архив пуст или ошибка при распаковке"
            logger.error(f"Предупреждение: директория распаковки пуста: {output_dir}")
            raise Exception(error_msg)
        
        logger.info(f"Архив успешно распакован, файлов извлечено: {len(extracted_files)}")
        logger.info(f"Первые 5 файлов: {', '.join(extracted_files[:5]) if len(extracted_files) > 5 else ', '.join(extracted_files)}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при распаковке: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Ошибка при распаковке: {str(e)}")

# Определение пути к Chrome на разных платформах
def get_chrome_path():
    if platform.system() == 'Windows':
        return 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    elif platform.system() == 'Darwin':  # macOS
        return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    elif platform.system() == 'Linux':
        return '/usr/bin/google-chrome'
    return None

class WhatsAppSessionManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Настройка логирования в конструкторе для отслеживания инициализации
        logger.info(f"Инициализация WhatsAppSessionManager")
        
        # Настройки окна
        self.setWindowTitle("WhatsApp Session Manager")
        self.setMinimumSize(950, 720)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dddddd;
                border-radius: 4px;
                color: #333333;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 16px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #e9f0fe;
                border-color: #a5c8fe;
                color: #1a73e8;
            }
            QPushButton:pressed {
                background-color: #d2e3fc;
            }
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QListWidget::item {
                height: 36px;
                padding: 4px 8px;
                border-bottom: 1px solid #f1f1f1;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f5f5f5;
                color: #333333;
                text-align: center;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #1a73e8;
                border-radius: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #1a73e8;
                color: #1a73e8;
            }
            QSplitter::handle {
                background-color: #e0e0e0;
                width: 1px;
            }
            QTreeWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 4px;
            }
            QTreeWidget::item {
                height: 32px;
                padding: 4px 8px;
            }
            QTreeWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
            QInputDialog {
                background-color: #ffffff;
            }
            QInputDialog QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Основной виджет и layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        title_label = QLabel("WhatsApp Session Manager")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("color: #1a73e8; margin-bottom: 10px;")
        
        # Информационный блок справа
        info_layout = QHBoxLayout()
        info_layout.setSpacing(0)
        
        info_text = QLabel("""<p style="font-size: 12px; color: #5f6368;">
            <b style="color: #1a73e8;">Идея:</b> <a href="https://t.me/tnwfo" style="color: #1a73e8; text-decoration: none;">@tnwfo</a> | 
            <b style="color: #1a73e8;">Кодер:</b> <a href="https://t.me/wrldxrd" style="color: #1a73e8; text-decoration: none;">@wrldxrd</a> | 
            <b style="color: #1a73e8;">TRC-20:</b> <span style="color: #5f6368;">TERAVgCGcU7gfeeft88kFgtQgxKCpvraKB</span> | 
            <b style="color: #1a73e8;">Наш канал:</b> <a href="https://t.me/psina_gggggg" style="color: #1a73e8; text-decoration: none;">t.me/psina_gggggg</a>
        </p>""")
        info_text.setOpenExternalLinks(True)
        info_text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        
        # Версия приложения
        version_label = QLabel("v0.8.3")
        version_label.setStyleSheet("""
            color: #5f6368; 
            font-size: 12px; 
            padding: 4px 8px;
            margin-right: 8px;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            background-color: #f8f9fa;
        """)
        version_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        version_label.setCursor(Qt.PointingHandCursor)  # Изменение курсора при наведении
        version_label.setToolTip("Нажмите, чтобы скачать исходный код")
        version_label.mousePressEvent = lambda event: self.download_source_code()
        
        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(info_text, 2)
        header_layout.addWidget(version_label)
        
        layout.addLayout(header_layout)
        
        # Область для drag & drop
        self.drop_area = QLabel("Перетащите RAR/ZIP архив или папку с ZIP/RAR файлами сессий сюда")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #dadce0;
                border-radius: 8px;
                padding: 20px;
                background-color: #f8f9fa;
                color: #5f6368;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #1a73e8;
                color: #1a73e8;
                background-color: #f2f7fe;
            }
        """)
        self.drop_area.setMinimumHeight(60)
        self.drop_area.setAcceptDrops(True)
        layout.addWidget(self.drop_area)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #f5f5f5;
                height: 8px;
                margin-top: 8px;
                margin-bottom: 8px;
            }
            QProgressBar::chunk {
                background-color: #1a73e8;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Кнопки управления
        top_button_layout = QHBoxLayout()
        top_button_layout.setSpacing(12)
        
        self.select_button = QPushButton("Добавить архив или папку")
        self.select_button.setStyleSheet("background-color: #e8f0fe; color: #1a73e8; border-color: #d2e3fc;")
        
        self.add_single_session_button = QPushButton("Добавить сессию")
        self.add_single_session_button.setStyleSheet("background-color: #f1f3f4; color: #202124; border-color: #dadce0;")
        
        top_button_layout.addWidget(self.select_button)
        top_button_layout.addWidget(self.add_single_session_button)
        top_button_layout.addStretch()
        layout.addLayout(top_button_layout)
        
        # Создаем разделитель для вкладок и списка аккаунтов
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter, 1)  # растягиваем сплиттер
        
        # Левая панель - дерево категорий и архивов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        archives_label = QLabel("Категории и архивы")
        archives_label.setStyleSheet("font-weight: 500; font-size: 14px; margin-bottom: 8px;")
        
        # Кнопки для управления категориями
        category_buttons_layout = QHBoxLayout()
        
        self.add_category_button = QPushButton("Новая категория")
        self.add_category_button.setStyleSheet("padding: 5px 10px;")
        self.add_category_button.clicked.connect(self.add_category)
        
        category_buttons_layout.addWidget(self.add_category_button)
        category_buttons_layout.addStretch()
        
        # Дерево категорий и архивов
        self.archives_tree = QTreeWidget()
        self.archives_tree.setHeaderHidden(True)
        self.archives_tree.setAnimated(True)
        self.archives_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.archives_tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.archives_tree.itemClicked.connect(self.on_tree_item_clicked)
        
        left_layout.addWidget(archives_label)
        left_layout.addLayout(category_buttons_layout)
        left_layout.addWidget(self.archives_tree)
        
        # Правая панель - список сессий и кнопки действий
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        sessions_label = QLabel("Сессии WhatsApp в выбранном архиве (ZIP/RAR)")
        sessions_label.setStyleSheet("font-weight: 500; font-size: 14px; margin-bottom: 8px;")
        
        self.sessions_list = QListWidget()
        self.sessions_list.setAlternatingRowColors(True)
        self.sessions_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.sessions_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sessions_list.customContextMenuRequested.connect(self.show_sessions_context_menu)
        
        # Кнопки управления сессиями
        session_button_layout = QHBoxLayout()
        session_button_layout.setSpacing(12)
        
        self.start_button = QPushButton("Открыть выбранные сессии")
        self.start_button.setStyleSheet("background-color: #1a73e8; color: white; border: none;")
        
        self.delete_button = QPushButton("Удалить выбранные сессии")
        self.delete_button.setStyleSheet("color: #d93025;")
        
        session_button_layout.addWidget(self.start_button)
        session_button_layout.addWidget(self.delete_button)
        
        right_layout.addWidget(sessions_label)
        right_layout.addWidget(self.sessions_list)
        right_layout.addLayout(session_button_layout)
        
        # Добавляем панели в сплиттер
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])  # Начальные размеры
        
        # Подключаем сигналы
        self.select_button.clicked.connect(self.select_file_or_folder)
        self.add_single_session_button.clicked.connect(self.add_single_session)
        self.start_button.clicked.connect(self.open_sessions)
        self.delete_button.clicked.connect(self.delete_selected_sessions)
        
        # Данные приложения
        self.categories = []  # список категорий
        self.archives = []  # список всех архивов
        self.current_archive_index = -1  # индекс текущего выбранного архива
        self.current_category_index = -1  # индекс текущей выбранной категории
        
        # Загружаем сохраненные данные
        self.load_data()
        
    def load_data(self):
        try:
            if os.path.exists('whatsapp_data.json'):
                logger.info(f"Загрузка данных из файла whatsapp_data.json")
                with open('whatsapp_data.json', 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self.categories = saved_data.get('categories', [])
                    self.archives = saved_data.get('archives', [])
                    
                    # Логируем количество загруженных элементов
                    logger.info(f"Загружено категорий: {len(self.categories)}, архивов: {len(self.archives)}")
                    
                    # Заполняем дерево категорий и архивов
                    self.refresh_categories_tree()
            else:
                logger.info("Файл whatsapp_data.json не найден, создаем новую конфигурацию")
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {str(e)}")
            logger.error(traceback.format_exc())
            
    def save_data(self):
        try:
            logger.info(f"Сохранение данных в файл whatsapp_data.json")
            with open('whatsapp_data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'categories': self.categories,
                    'archives': self.archives
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"Данные успешно сохранены. Категорий: {len(self.categories)}, архивов: {len(self.archives)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных: {str(e)}")
            logger.error(traceback.format_exc())
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.info("Перетаскивание файлов/папок начато")
            
    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        logger.info(f"Файлы/папки перетащены: {files}")
        for path in files:
            self.process_path(path)
            
    def is_session_name(self, filename):
        """Проверяет, является ли имя файла/папки похожим на название сессии WhatsApp"""
        basename = os.path.basename(filename)
        return basename.startswith('session-') or 'whatsapp' in basename.lower()
    
    def process_path(self, path):
        """Универсальная обработка пути (файл или папка)"""
        try:
            logger.info(f"Обработка пути: {path}")
            
            if not os.path.exists(path):
                error_msg = f"Путь не существует: {path}"
                logger.error(error_msg)
                QMessageBox.critical(self, "Ошибка", error_msg)
                return
                
            if os.path.isdir(path):
                logger.info(f"Путь является директорией: {path}")
                # Если это папка с именем, похожим на сессию
                if self.is_session_name(path):
                    logger.info(f"Имя пути похоже на сессию: {os.path.basename(path)}")
                    # Проверяем через анализ папки
                    session_info = self.analyze_session_folder(path)
                    if session_info['is_chrome_profile']:
                        logger.info(f"Путь содержит профиль Chrome: {path}")
                        reply = QMessageBox.question(
                            self, 
                            "Добавление сессии", 
                            f"Папка '{os.path.basename(path)}' похожа на сессию WhatsApp. Добавить её как отдельную сессию?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            # Обрабатываем как одиночную сессию
                            self.process_single_session(path)
                            return
                
                # Обрабатываем как папку с возможными архивами сессий
                self.process_folder(path)
            
            elif os.path.isfile(path) and path.lower().endswith(('.rar', '.zip', '.7z')):
                logger.info(f"Путь является архивом: {path}")
                # Если архив с именем, похожим на сессию
                if self.is_session_name(path):
                    logger.info(f"Имя архива похоже на сессию: {os.path.basename(path)}")
                    reply = QMessageBox.question(
                        self, 
                        "Добавление сессии", 
                        f"Архив '{os.path.basename(path)}' похож на сессию WhatsApp. Добавить его как отдельную сессию?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        # Обрабатываем как одиночную сессию в архиве
                        self.process_single_session_archive(path)
                        return
                
                # Обычная обработка архива с возможными множественными сессиями
                self.process_archive(path)
            else:
                error_msg = f"Неподдерживаемый тип файла: {os.path.basename(path)}.\nПожалуйста, выберите ZIP, RAR архив или папку."
                logger.warning(error_msg)
                QMessageBox.warning(self, "Предупреждение", error_msg)
        except Exception as e:
            error_msg = f"Ошибка при обработке элемента: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", error_msg)
    
    def select_file_or_folder(self):
        """Универсальный метод выбора архива или папки"""
        options = QFileDialog.Options()
        
        dialog = QFileDialog(self, "Выберите архив или папку с сессиями WhatsApp")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("Архивы (*.rar *.zip *.7z);;Все файлы (*)")
        dialog.setOptions(options)
        
        # Добавляем кнопку для выбора папки
        folder_button = QPushButton("Выбрать папку", dialog)
        folder_button.clicked.connect(lambda: self.select_folder_from_dialog(dialog))
        dialog.layout().addWidget(folder_button)
        
        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.process_path(selected_files[0])
    
    def select_folder_from_dialog(self, dialog):
        """Вспомогательный метод для выбора папки из диалога"""
        dialog.reject()  # Закрываем текущий диалог
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку с сессиями WhatsApp")
        if folder_path:
            self.process_path(folder_path)
            
    def process_archive(self, archive_path):
        try:
            logger.info(f"Начало обработки архива: {archive_path}")
            
            # Проверяем доступность архива
            if not os.access(archive_path, os.R_OK):
                error_msg = f"Нет прав на чтение архива: {archive_path}"
                logger.error(error_msg)
                QMessageBox.critical(self, "Ошибка", error_msg)
                return
                
            # Проверяем, не добавлен ли уже этот архив
            for archive in self.archives:
                if archive['path'] == archive_path:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText("Этот архив уже добавлен!")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setStyleSheet("QMessageBox { background-color: white; }")
                    msg.exec()
                    return
            
            # Создаем временную директорию для распаковки
            archive_name = os.path.basename(archive_path)
            archive_dir = os.path.dirname(archive_path)
            temp_dir = os.path.join(archive_dir, f"extracted_{archive_name}")
            
            logger.info(f"Создание временной директории: {temp_dir}")
            
            # Проверяем, существует ли временная директория и удаляем ее при необходимости
            if os.path.exists(temp_dir):
                try:
                    logger.info(f"Удаление существующей временной директории: {temp_dir}")
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Не удалось очистить временную директорию: {str(e)}")
                    QMessageBox.warning(self, "Предупреждение", 
                        f"Не удалось очистить временную директорию: {str(e)}\n"
                        f"Будет использована существующая директория.")
            
            try:
                os.makedirs(temp_dir, exist_ok=True)
                logger.info(f"Временная директория создана: {temp_dir}")
            except Exception as e:
                error_msg = f"Не удалось создать временную директорию: {str(e)}"
                logger.error(error_msg)
                QMessageBox.critical(self, "Ошибка", error_msg)
                return
            
            # Показываем прогресс-бар
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            try:
                # Создаем и запускаем worker
                logger.info(f"Запуск ExtractionWorker для архива: {archive_path}")
                self.worker = ExtractionWorker(archive_path, temp_dir, is_archive=True)
                self.worker.progress.connect(self.update_progress)
                self.worker.finished.connect(self.extraction_finished)
                self.worker.error.connect(self.extraction_error)
                self.worker.start()
            except Exception as e:
                error_msg = f"Ошибка при запуске распаковки архива: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Ошибка", error_msg)
            
        except Exception as e:
            error_msg = f"Ошибка при обработке файла: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Ошибка", error_msg)
    
    def process_folder(self, folder_path):
        try:
            # Проверяем, не добавлена ли уже эта папка
            for archive in self.archives:
                if archive['path'] == folder_path:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText("Эта папка уже добавлена!")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setStyleSheet("QMessageBox { background-color: white; }")
                    msg.exec()
                    return
            
            # Создаем временную директорию для распаковки
            folder_name = os.path.basename(folder_path)
            temp_dir = os.path.join(os.path.dirname(folder_path), f"extracted_{folder_name}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Показываем прогресс-бар
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Создаем и запускаем worker
            self.worker = ExtractionWorker(folder_path, temp_dir, is_archive=False)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.extraction_finished)
            self.worker.error.connect(self.extraction_error)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обработке папки: {str(e)}")
            
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def extraction_finished(self, sessions, archive_name, archive_path):
        # Добавляем новый архив в список
        new_archive = {
            'name': archive_name,
            'path': archive_path,
            'extracted_path': sessions[0]['path'].replace('\\' + sessions[0]['name'], '') if sessions else '',
            'sessions': sessions,
            'category_index': self.current_category_index if self.current_category_index >= 0 else None
        }
        
        self.archives.append(new_archive)
        
        # Обновляем дерево категорий и архивов
        self.refresh_categories_tree()
        
        # Выбираем новый архив
        self.current_archive_index = len(self.archives) - 1
        
        # Находим элемент нового архива в дереве и выбираем его
        for i in range(self.archives_tree.topLevelItemCount()):
            top_item = self.archives_tree.topLevelItem(i)
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)
                data = child_item.data(0, Qt.UserRole)
                if data.get('type') == 'archive' and data.get('index') == self.current_archive_index:
                    self.archives_tree.setCurrentItem(child_item)
                    break
        
        # Загружаем сессии для нового архива
        self.load_sessions_for_current_archive()
        
        self.progress_bar.setVisible(False)
        self.save_data()
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Успех")
        msg.setText(f"Архив '{archive_name}' успешно добавлен и распакован!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("QMessageBox { background-color: white; }")
        msg.exec()
        
    def extraction_error(self, error_msg):
        self.progress_bar.setVisible(False)
        
        # Проверяем тип ошибки и делаем сообщение более понятным
        user_friendly_message = error_msg
        
        if "Cannot open the file as archive" in error_msg:
            user_friendly_message = "Невозможно открыть файл как архив. Возможно формат архива поврежден или не поддерживается."
        elif "Wrong password" in error_msg:
            user_friendly_message = "Архив защищен паролем. Пожалуйста, разархивируйте его вручную, а затем добавьте папку с сессиями."
        elif "Unexpected end of archive" in error_msg:
            user_friendly_message = "Архив поврежден или неполный. Пожалуйста, проверьте целостность архива."
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка")
        msg.setText(f"Ошибка при обработке: {user_friendly_message}")
        
        # Добавляем детали ошибки в раскрывающуюся секцию
        msg.setDetailedText(error_msg)
        
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStyleSheet("QMessageBox { background-color: white; }")
        msg.exec()
    
    def on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        item_type = data.get("type")
        
        if item_type == "archive":
            self.current_archive_index = data.get("index")
            self.load_sessions_for_current_archive()
        elif item_type == "category":
            self.current_category_index = data.get("index")
            # При клике на категорию очищаем список сессий
            self.sessions_list.clear()
        elif item_type == "root":
            # При клике на корневую категорию очищаем список сессий
            self.sessions_list.clear()
            
    def load_sessions_for_current_archive(self):
        """Загружает сессии для текущего выбранного архива"""
        if self.current_archive_index >= 0 and self.current_archive_index < len(self.archives):
            # Очищаем список сессий
            self.sessions_list.clear()
            
            # Загружаем сессии для выбранного архива
            archive = self.archives[self.current_archive_index]
            for session in archive['sessions']:
                self.sessions_list.addItem(session['name'])
            
    def add_category(self):
        """Добавляет новую категорию"""
        name, ok = QInputDialog.getText(self, "Новая категория", "Введите название категории:")
        
        if ok and name:
            # Проверяем, что такой категории еще нет
            if any(category['name'] == name for category in self.categories):
                QMessageBox.warning(self, "Предупреждение", "Категория с таким названием уже существует!")
                return
                
            # Добавляем новую категорию
            self.categories.append({
                'name': name,
                'created_at': time.time()
            })
            
            # Обновляем дерево и сохраняем данные
            self.refresh_categories_tree()
            self.save_data()
            
    def rename_category(self, category_index):
        """Переименовывает категорию"""
        if category_index < 0 or category_index >= len(self.categories):
            return
            
        old_name = self.categories[category_index]['name']
        name, ok = QInputDialog.getText(self, "Переименовать категорию", 
                                       "Введите новое название категории:", 
                                       text=old_name)
        
        if ok and name and name != old_name:
            # Проверяем, что такой категории еще нет
            if any(category['name'] == name for category in self.categories):
                QMessageBox.warning(self, "Предупреждение", "Категория с таким названием уже существует!")
                return
                
            # Обновляем название категории
            self.categories[category_index]['name'] = name
            
            # Обновляем дерево и сохраняем данные
            self.refresh_categories_tree()
            self.save_data()
            
    def delete_category(self, category_index):
        """Удаляет категорию"""
        if category_index < 0 or category_index >= len(self.categories):
            return
            
        category = self.categories[category_index]
        
        # Проверяем, есть ли архивы в этой категории
        archives_in_category = [a for a in self.archives if a.get('category_index') == category_index]
        
        if archives_in_category:
            msg_text = f"Категория '{category['name']}' содержит {len(archives_in_category)} архивов. При удалении категории все архивы будут перемещены в корневую категорию. Продолжить?"
        else:
            msg_text = f"Вы уверены, что хотите удалить категорию '{category['name']}'?"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText(msg_text)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("QMessageBox { background-color: white; }")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            # Перемещаем архивы из удаляемой категории в корневую категорию (без категории)
            for archive in self.archives:
                if archive.get('category_index') == category_index:
                    archive['category_index'] = None
                # Корректируем индексы для архивов в категориях с большим индексом
                elif archive.get('category_index') is not None and archive.get('category_index') > category_index:
                    archive['category_index'] -= 1
            
            # Удаляем категорию
            self.categories.pop(category_index)
            
            # Обновляем текущий индекс категории
            if category_index == self.current_category_index:
                self.current_category_index = -1
            elif self.current_category_index > category_index:
                self.current_category_index -= 1
            
            # Обновляем дерево и сохраняем данные
            self.refresh_categories_tree()
            self.save_data()
            
    def move_archive_to_category(self, archive_index, category_index):
        """Перемещает архив в указанную категорию"""
        if archive_index < 0 or archive_index >= len(self.archives):
            return
            
        # Если category_index is None, то архив перемещается в корневую категорию (без категории)
        if category_index is not None and (category_index < 0 or category_index >= len(self.categories)):
            return
            
        # Обновляем категорию архива
        self.archives[archive_index]['category_index'] = category_index
        
        # Обновляем дерево и сохраняем данные
        self.refresh_categories_tree()
        self.save_data()
    
    def refresh_categories_tree(self):
        """Обновляет дерево категорий и архивов"""
        self.archives_tree.clear()
        
        # Добавляем корневую категорию "Все архивы"
        root_item = QTreeWidgetItem(self.archives_tree, ["Все архивы"])
        root_item.setData(0, Qt.UserRole, {"type": "root"})
        root_item.setExpanded(True)
        
        # Добавляем пользовательские категории
        for i, category in enumerate(self.categories):
            category_item = QTreeWidgetItem(self.archives_tree, [category['name']])
            category_item.setData(0, Qt.UserRole, {"type": "category", "index": i})
            category_item.setExpanded(True)
            
            # Добавляем архивы в категорию
            for j, archive in enumerate(self.archives):
                if archive.get('category_index') == i:
                    archive_item = QTreeWidgetItem(category_item, [archive['name']])
                    archive_item.setData(0, Qt.UserRole, {"type": "archive", "index": j})
                    
        # Добавляем архивы без категории в корневую категорию
        for j, archive in enumerate(self.archives):
            if archive.get('category_index') is None:
                archive_item = QTreeWidgetItem(root_item, [archive['name']])
                archive_item.setData(0, Qt.UserRole, {"type": "archive", "index": j})
                
        # Выбираем первый архив если есть
        if self.archives:
            first_archive = self.archives_tree.findItems("", Qt.MatchContains | Qt.MatchRecursive)[1]
            if first_archive:
                self.archives_tree.setCurrentItem(first_archive)
                self.on_tree_item_clicked(first_archive, 0)
    
    def show_tree_context_menu(self, position):
        item = self.archives_tree.itemAt(position)
        if not item:
            return
            
        data = item.data(0, Qt.UserRole)
        item_type = data.get("type")
        
        menu = QMenu()
        
        if item_type == "root":
            add_category_action = menu.addAction("Добавить категорию")
            action = menu.exec(self.archives_tree.mapToGlobal(position))
            
            if action == add_category_action:
                self.add_category()
                
        elif item_type == "category":
            rename_action = menu.addAction("Переименовать категорию")
            delete_action = menu.addAction("Удалить категорию")
            
            action = menu.exec(self.archives_tree.mapToGlobal(position))
            
            if action == rename_action:
                self.rename_category(data.get("index"))
            elif action == delete_action:
                self.delete_category(data.get("index"))
                
        elif item_type == "archive":
            open_action = menu.addAction("Открыть архив")
            move_menu = menu.addMenu("Переместить в категорию")
            
            # Добавляем пункт "Без категории"
            no_category_action = move_menu.addAction("Без категории")
            move_menu.addSeparator()
            
            # Добавляем существующие категории
            category_actions = []
            for i, category in enumerate(self.categories):
                action = move_menu.addAction(category['name'])
                category_actions.append((action, i))
            
            delete_action = menu.addAction("Удалить архив")
            
            action = menu.exec(self.archives_tree.mapToGlobal(position))
            
            if action == open_action:
                self.on_tree_item_clicked(item, 0)
            elif action == delete_action:
                self.delete_selected_archive()
            elif action == no_category_action:
                self.move_archive_to_category(data.get("index"), None)
            else:
                for cat_action, cat_index in category_actions:
                    if action == cat_action:
                        self.move_archive_to_category(data.get("index"), cat_index)
                        break
    
    def show_sessions_context_menu(self, position):
        if not self.sessions_list.count() or not self.sessions_list.selectedItems():
            return
            
        menu = QMenu()
        open_action = menu.addAction("Открыть выбранные сессии")
        menu.addSeparator()
        delete_action = menu.addAction("Удалить выбранные сессии")
        
        action = menu.exec(self.sessions_list.mapToGlobal(position))
        
        if action == open_action:
            self.open_sessions()
        elif action == delete_action:
            self.delete_selected_sessions()
            
    def delete_selected_archive(self):
        if self.current_archive_index < 0:
            return
            
        archive = self.archives[self.current_archive_index]
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText(f"Вы уверены, что хотите удалить архив '{archive['name']}' и все его сессии?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("QMessageBox { background-color: white; }")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Удаляем физически распакованные файлы
                if os.path.exists(archive['extracted_path']):
                    shutil.rmtree(archive['extracted_path'])
                
                # Сохраняем индекс категории перед удалением архива
                category_index = archive.get('category_index')
                
                # Удаляем из списка
                self.archives.pop(self.current_archive_index)
                
                # Корректируем индексы для элементов дерева
                for i, a in enumerate(self.archives):
                    for item in self.archives_tree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                        data = item.data(0, Qt.UserRole)
                        if data.get('type') == 'archive' and data.get('index') > self.current_archive_index:
                            item.setData(0, Qt.UserRole, {"type": "archive", "index": data.get('index') - 1})
                
                # Обновляем интерфейс
                self.current_archive_index = -1
                self.sessions_list.clear()
                self.refresh_categories_tree()
                
                # Сохраняем изменения
                self.save_data()
                
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Успех")
                success_msg.setText("Архив успешно удален!")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setStyleSheet("QMessageBox { background-color: white; }")
                success_msg.exec()
                
            except Exception as e:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Ошибка")
                error_msg.setText(f"Ошибка при удалении архива: {str(e)}")
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setStyleSheet("QMessageBox { background-color: white; }")
                error_msg.exec()
            
    def analyze_session_folder(self, folder_path):
        """Анализирует структуру папки для определения, является ли она профилем Chrome"""
        result = {
            'is_chrome_profile': False,
            'has_default_folder': False,
            'default_path': None
        }
        
        try:
            # Проверяем, существует ли директория
            if not os.path.exists(folder_path):
                logger.warning(f"Директория не существует: {folder_path}")
                return result
                
            if not os.path.isdir(folder_path):
                logger.warning(f"Указанный путь не является директорией: {folder_path}")
                return result
                
            if not os.access(folder_path, os.R_OK):
                logger.warning(f"Нет прав на чтение директории: {folder_path}")
                return result
            
            # Ключевые файлы профиля Chrome
            chrome_profile_files = ['Cookies', 'Web Data', 'History', 'Login Data', 'Preferences']
            
            # Если сама папка называется 'Default'
            if os.path.basename(folder_path) == 'Default':
                # Проверяем наличие ключевых файлов
                profile_files_present = [f for f in chrome_profile_files if os.path.exists(os.path.join(folder_path, f))]
                if profile_files_present:
                    logger.info(f"Найден профиль Chrome в папке Default, найдены файлы: {', '.join(profile_files_present)}")
                    result['is_chrome_profile'] = True
                    result['has_default_folder'] = True
                    result['default_path'] = os.path.dirname(folder_path)
                    return result
            
            # Проверяем наличие папки Default внутри
            default_folder = os.path.join(folder_path, 'Default')
            if os.path.exists(default_folder) and os.path.isdir(default_folder):
                result['has_default_folder'] = True
                result['default_path'] = folder_path
                
                # Проверяем наличие ключевых файлов в Default
                profile_files_present = [f for f in chrome_profile_files if os.path.exists(os.path.join(default_folder, f))]
                if profile_files_present:
                    logger.info(f"Найден профиль Chrome в папке {folder_path}/Default, найдены файлы: {', '.join(profile_files_present)}")
                    result['is_chrome_profile'] = True
                    return result
            
            # Проверяем, не является ли сама папка профилем Chrome (без папки Default)
            profile_files_present = [f for f in chrome_profile_files if os.path.exists(os.path.join(folder_path, f))]
            if profile_files_present:
                logger.info(f"Найден профиль Chrome в папке {folder_path}, найдены файлы: {', '.join(profile_files_present)}")
                result['is_chrome_profile'] = True
                return result
            
            # Проверяем также файлы Local Storage, которые часто есть в профилях Chrome
            if os.path.exists(os.path.join(folder_path, 'Local Storage')):
                logger.info(f"Найдена папка Local Storage в {folder_path}, возможно это профиль Chrome")
                if len(profile_files_present) > 0 or os.path.exists(os.path.join(folder_path, 'Local Storage', 'leveldb')):
                    result['is_chrome_profile'] = True
                    return result
                
        except Exception as e:
            logger.error(f"Ошибка при анализе папки {folder_path}: {str(e)}")
            logger.error(traceback.format_exc())
            
        return result

    def open_sessions(self):
        """Открывает выбранные сессии WhatsApp в Chrome в одном окне"""
        try:
            logger.info("Запуск функции open_sessions")
            
            if self.current_archive_index < 0:
                logger.warning("Нет выбранного архива")
                msg = QMessageBox(self)
                msg.setWindowTitle("Предупреждение")
                msg.setText("Нет выбранного архива")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setStyleSheet("QMessageBox { background-color: white; }")
                msg.exec()
                return
                
            archive = self.archives[self.current_archive_index]
            logger.info(f"Выбранный архив: {archive['name']}")
            
            if not archive['sessions']:
                logger.warning("Нет доступных сессий в выбранном архиве")
                msg = QMessageBox(self)
                msg.setWindowTitle("Предупреждение")
                msg.setText("Нет доступных сессий в выбранном архиве")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setStyleSheet("QMessageBox { background-color: white; }")
                msg.exec()
                return
            
            # Получаем путь к Chrome
            chrome_path = get_chrome_path()
            logger.info(f"Путь к Chrome: {chrome_path}")
            
            if not chrome_path or not os.path.exists(chrome_path):
                error_msg = "Chrome не найден. Установите Google Chrome для работы с сессиями WhatsApp."
                logger.error(error_msg)
                QMessageBox.warning(self, "Предупреждение", error_msg)
                return
            
            # Проверяем, выбраны ли сессии в списке
            selected_items = self.sessions_list.selectedItems()
            sessions_to_open = []
            
            if selected_items:
                # Открываем только выбранные сессии
                logger.info(f"Выбрано сессий: {len(selected_items)}")
                for item in selected_items:
                    session_name = item.text()
                    session = next((s for s in archive['sessions'] if s['name'] == session_name), None)
                    if session:
                        sessions_to_open.append(session)
                        logger.info(f"Добавлена сессия для открытия: {session_name}")
            else:
                # Если ничего не выбрано, открываем все сессии
                logger.info("Нет выбранных сессий, открываем все")
                sessions_to_open = archive['sessions']
            
            if not sessions_to_open:
                logger.warning("Нет сессий для открытия")
                return
                
            logger.info(f"Всего сессий для открытия: {len(sessions_to_open)}")
            
            # Формируем базовую команду для Chrome
            session_path = sessions_to_open[0]['path']
            logger.info(f"Путь к первой сессии: {session_path}")
            
            # Анализируем структуру папки первой сессии для определения правильного пути
            session_info = self.analyze_session_folder(session_path)
            logger.info(f"Анализ первой сессии {sessions_to_open[0]['name']}: {session_info}")
            
            # Используем правильный путь к данным профиля для первой сессии
            user_data_path = session_info['default_path'] if session_info['has_default_folder'] else session_path
            logger.info(f"user_data_path для первой сессии: {user_data_path}")
            
            # Для первой сессии открываем новое окно с первой вкладкой
            whatsapp_url = "https://web.whatsapp.com/"
            cmd = f'"{chrome_path}" --user-data-dir="{user_data_path}" --new-window --no-first-run --no-default-browser-check --disable-extensions {whatsapp_url}'
            
            logger.info(f"Команда для открытия первой сессии: {cmd}")
            try:
                first_process = subprocess.Popen(cmd, shell=True)
                logger.info(f"Первая сессия запущена, PID: {first_process.pid if hasattr(first_process, 'pid') else 'неизвестно'}")
            except Exception as e:
                error_msg = f"Ошибка при запуске Chrome: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                QMessageBox.critical(self, "Ошибка", error_msg)
                return
            
            # Ждем немного, чтобы первое окно успело запуститься
            logger.info("Ожидание 3 секунды для запуска первого окна")
            time.sleep(3)
            
            # Открываем остальные сессии в разных профилях одного окна
            for i, session in enumerate(sessions_to_open[1:], 1):
                try:
                    session_path = session['path']
                    logger.info(f"Обработка сессии {i+1}: {session['name']}, путь: {session_path}")
                    
                    if os.path.exists(session_path):
                        # Анализируем структуру папки текущей сессии
                        session_info = self.analyze_session_folder(session_path)
                        logger.info(f"Анализ сессии {session['name']}: {session_info}")
                        
                        # Используем правильный путь к данным профиля
                        user_data_path = session_info['default_path'] if session_info['has_default_folder'] else session_path
                        logger.info(f"user_data_path для сессии {i+1}: {user_data_path}")
                        
                        # Открываем новую вкладку в том же окне, запуская Chrome с другим профилем
                        cmd = f'"{chrome_path}" --user-data-dir="{user_data_path}" --no-first-run --no-default-browser-check --disable-extensions {whatsapp_url}'
                        
                        logger.info(f"Команда для открытия сессии {i+1}: {cmd}")
                        subprocess.Popen(cmd, shell=True)
                        
                        # Пауза между запусками
                        time.sleep(1)
                    else:
                        error_msg = f"Папка сессии не найдена: {session_path}"
                        logger.warning(error_msg)
                        QMessageBox.warning(self, "Предупреждение", error_msg)
                except Exception as e:
                    error_msg = f"Не удалось открыть сессию {session['name']}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    QMessageBox.critical(self, "Ошибка", error_msg)
        except Exception as e:
            error_msg = f"Ошибка при открытии сессий: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", error_msg)
    
    def delete_selected_sessions(self):
        if self.current_archive_index < 0:
            return
            
        selected_items = self.sessions_list.selectedItems()
        if not selected_items:
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Выберите сессии для удаления")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("QMessageBox { background-color: white; }")
            msg.exec()
            return
        
        count = len(selected_items)
        msg_text = f"Вы уверены, что хотите удалить {count} выбранных сессий?" if count > 1 else f"Вы уверены, что хотите удалить сессию {selected_items[0].text()}?"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText(msg_text)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("QMessageBox { background-color: white; }")
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            archive = self.archives[self.current_archive_index]
            
            for item in selected_items:
                session_name = item.text()
                session = next((s for s in archive['sessions'] if s['name'] == session_name), None)
                
                if session:
                    try:
                        # Удаляем директорию сессии
                        if os.path.exists(session['path']):
                            shutil.rmtree(session['path'])
                        
                        # Удаляем из списка
                        archive['sessions'].remove(session)
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении сессии: {str(e)}")
            
            # Обновляем интерфейс и сохраняем изменения
            self.load_sessions_for_current_archive()
            self.save_data()
            
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("Успех")
            success_msg.setText("Выбранные сессии успешно удалены!")
            success_msg.setIcon(QMessageBox.Icon.Information)
            success_msg.setStyleSheet("QMessageBox { background-color: white; }")
            success_msg.exec()

    def process_single_session(self, session_path):
        """Обрабатывает одиночную сессию WhatsApp"""
        try:
            # Проверяем, не добавлена ли уже эта сессия
            for archive in self.archives:
                for session in archive['sessions']:
                    if session['path'] == session_path:
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Предупреждение")
                        msg.setText("Эта сессия уже добавлена!")
                        msg.setIcon(QMessageBox.Icon.Warning)
                        msg.setStyleSheet("QMessageBox { background-color: white; }")
                        msg.exec()
                        return
                        
            folder_name = os.path.basename(session_path)
            
            # Создаем "искусственный" архив с одной сессией
            sessions = [{
                'name': folder_name,
                'path': session_path
            }]
            
            # Используем имя папки как имя архива, добавив приставку "Сессия:"
            archive_name = f"Сессия: {folder_name}"
            
            # Добавляем новый "архив" (одиночную сессию) в список
            new_archive = {
                'name': archive_name,
                'path': session_path,
                'extracted_path': session_path,
                'sessions': sessions,
                'is_single_session': True,  # Отмечаем, что это одиночная сессия
                'category_index': self.current_category_index if self.current_category_index >= 0 else None
            }
            
            self.archives.append(new_archive)
            
            # Обновляем дерево категорий и архивов
            self.refresh_categories_tree()
            
            # Выбираем новый архив
            self.current_archive_index = len(self.archives) - 1
            
            # Находим элемент нового архива в дереве и выбираем его
            for i in range(self.archives_tree.topLevelItemCount()):
                top_item = self.archives_tree.topLevelItem(i)
                for j in range(top_item.childCount()):
                    child_item = top_item.child(j)
                    data = child_item.data(0, Qt.UserRole)
                    if data.get('type') == 'archive' and data.get('index') == self.current_archive_index:
                        self.archives_tree.setCurrentItem(child_item)
                        break
            
            # Загружаем сессии для нового архива
            self.load_sessions_for_current_archive()
            
            # Сохраняем данные
            self.save_data()
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Успех")
            msg.setText(f"Сессия '{folder_name}' успешно добавлена!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("QMessageBox { background-color: white; }")
            msg.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении сессии: {str(e)}")

    def add_single_session(self):
        """Добавляет одиночную сессию WhatsApp (папку session-XXX)"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        # Создаем диалог выбора файла с возможностью выбора как папок, так и архивов
        dialog = QFileDialog(self, "Выберите сессию WhatsApp")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("Сессии WhatsApp (*.rar *.zip *.7z);;Все файлы (*)")
        dialog.setOptions(options)
        
        if dialog.exec():
            selected_files = dialog.selectedFiles()
            if not selected_files:
                return
                
            source_path = selected_files[0]
            
            # Проверяем, является ли выбранный файл архивом
            if os.path.isfile(source_path) and source_path.lower().endswith(('.rar', '.zip', '.7z')):
                # Обрабатываем архив
                self.process_single_session_archive(source_path)
            elif os.path.isdir(source_path):
                # Обрабатываем папку как раньше
                session_info = self.analyze_session_folder(source_path)
                
                if not session_info['is_chrome_profile']:
                    reply = QMessageBox.question(
                        self, 
                        "Подтверждение", 
                        "Эта папка не похожа на сессию WhatsApp. Вы уверены, что хотите добавить ее как сессию?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                self.process_single_session(source_path)
                
    def process_single_session_archive(self, archive_path):
        """Обрабатывает одиночный архив с сессией WhatsApp"""
        try:
            # Проверяем, не добавлен ли уже этот архив
            for archive in self.archives:
                if archive['path'] == archive_path:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText("Этот архив уже добавлен!")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setStyleSheet("QMessageBox { background-color: white; }")
                    msg.exec()
                    return
            
            # Создаем временную директорию для распаковки
            archive_name = os.path.basename(archive_path)
            archive_basename = os.path.splitext(archive_name)[0]
            archive_dir = os.path.dirname(archive_path)
            
            temp_dir = os.path.join(archive_dir, f"extracted_single_{archive_basename}")
            
            # Проверяем, существует ли временная директория и удаляем ее при необходимости
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    QMessageBox.warning(self, "Предупреждение", 
                        f"Не удалось очистить временную директорию: {str(e)}\n"
                        f"Будет использована существующая директория.")
            
            os.makedirs(temp_dir, exist_ok=True)
            
            # Показываем прогресс-бар
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            try:
                # Распаковываем архив с помощью 7-Zip
                extract_with_7zip(archive_path, temp_dir)
                self.progress_bar.setValue(50)  # Устанавливаем прогресс 50% после распаковки
                
                # Находим распакованную сессию
                session_info = None
                session_path = None
                
                # Пытаемся найти сессию в распакованных файлах
                for root, dirs, files in os.walk(temp_dir):
                    current_info = self.analyze_session_folder(root)
                    if current_info['is_chrome_profile']:
                        session_info = current_info
                        session_path = root
                        break
                
                self.progress_bar.setValue(75)  # Устанавливаем прогресс 75% после анализа
                
                if not session_path:
                    # Если не нашли Chrome профиль, используем корневую директорию
                    session_path = temp_dir
                    session_info = {'is_chrome_profile': False, 'has_default_folder': False, 'default_path': None}
                    
                    # Спрашиваем пользователя
                    reply = QMessageBox.question(
                        self, 
                        "Подтверждение", 
                        "В архиве не найдена структура WhatsApp сессии. Хотите всё равно продолжить?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        # Удаляем временную директорию
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        self.progress_bar.setVisible(False)
                        return
                
                # Создаем "искусственный" архив с одной сессией
                sessions = [{
                    'name': archive_basename,
                    'path': session_path
                }]
                
                # Используем имя архива как имя архива, добавив приставку "Сессия:"
                new_archive_name = f"Сессия из архива: {archive_basename}"
                
                # Добавляем новый "архив" (одиночную сессию) в список
                new_archive = {
                    'name': new_archive_name,
                    'path': archive_path,
                    'extracted_path': temp_dir,
                    'sessions': sessions,
                    'is_single_session': True,  # Отмечаем, что это одиночная сессия
                    'is_unpacked_archive': True,  # Отмечаем, что это распакованный архив
                    'category_index': self.current_category_index if self.current_category_index >= 0 else None
                }
                
                self.archives.append(new_archive)
                
                # Обновляем дерево категорий и архивов
                self.refresh_categories_tree()
                
                # Выбираем новый архив
                self.current_archive_index = len(self.archives) - 1
                
                # Находим элемент нового архива в дереве и выбираем его
                for i in range(self.archives_tree.topLevelItemCount()):
                    top_item = self.archives_tree.topLevelItem(i)
                    for j in range(top_item.childCount()):
                        child_item = top_item.child(j)
                        data = child_item.data(0, Qt.UserRole)
                        if data.get('type') == 'archive' and data.get('index') == self.current_archive_index:
                            self.archives_tree.setCurrentItem(child_item)
                            break
                
                # Загружаем сессии для нового архива
                self.load_sessions_for_current_archive()
                
                # Обновляем прогресс и скрываем прогресс-бар
                self.progress_bar.setValue(100)
                self.progress_bar.setVisible(False)
                
                # Сохраняем данные
                self.save_data()
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Успех")
                msg.setText(f"Архив с сессией '{archive_basename}' успешно добавлен и распакован!")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setStyleSheet("QMessageBox { background-color: white; }")
                msg.exec()
                
            except Exception as e:
                # Удаляем временную директорию в случае ошибки
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
                self.progress_bar.setVisible(False)
                raise Exception(f"Ошибка при распаковке архива сессии: {str(e)}")
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении архива сессии: {str(e)}")

    def get_resource_path(self, relative_path):
        """Возвращает путь к ресурсу, работает как в режиме разработки, так и при запуске из exe"""
        logger.info(f"Запрошен путь к ресурсу: {relative_path}")
        try:
            # Определяем, запущены ли мы из exe или из скрипта
            if getattr(sys, 'frozen', False):
                # Если запущено из exe
                base_path = sys._MEIPASS
                logger.info(f"Запуск из exe, базовый путь: {base_path}")
            else:
                # Если запущено из скрипта
                base_path = os.path.dirname(os.path.abspath(__file__))
                logger.info(f"Запуск из скрипта, базовый путь: {base_path}")
            
            # Формируем полный путь
            full_path = os.path.join(base_path, relative_path)
            
            # Проверяем существование файла
            if not os.path.exists(full_path):
                # Если файл не существует, проверяем альтернативные пути
                alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
                if os.path.exists(alt_path):
                    logger.info(f"Ресурс найден по альтернативному пути: {alt_path}")
                    return alt_path
                
                # Если файл и по альтернативному пути не найден, используем пустую иконку
                logger.warning(f"Ресурс не найден: {full_path}")
                return ""
            
            logger.info(f"Ресурс найден: {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Ошибка при определении пути к ресурсу: {str(e)}")
            logger.error(traceback.format_exc())
            return ""
            
    def download_source_code(self):
        """Скачать архив с исходным кодом"""
        try:
            logger.info("Запрос на скачивание исходного кода")
            
            # Проверяем наличие архива
            archive_path = self.get_resource_path("archive.zip")
            
            if not archive_path or not os.path.exists(archive_path):
                # Если архив не найден по стандартному пути
                archive_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive.zip")
                if not os.path.exists(archive_path):
                    logger.error(f"Архив с исходным кодом не найден: {archive_path}")
                    QMessageBox.warning(self, "Предупреждение", "Архив с исходным кодом не найден.")
                    return
            
            # Выбираем место для сохранения
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить исходный код",
                "WhatsAppSessionManager_source.zip",
                "ZIP архивы (*.zip)"
            )
            
            if not save_path:
                logger.info("Пользователь отменил сохранение")
                return
                
            # Копируем архив
            try:
                shutil.copy2(archive_path, save_path)
                logger.info(f"Архив успешно сохранен: {save_path}")
                QMessageBox.information(
                    self, 
                    "Успех", 
                    f"Исходный код успешно сохранен в {save_path}",
                    QMessageBox.StandardButton.Ok
                )
            except Exception as e:
                logger.error(f"Ошибка при копировании архива: {str(e)}")
                QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    f"Не удалось сохранить архив: {str(e)}",
                    QMessageBox.StandardButton.Ok
                )
                
        except Exception as e:
            logger.error(f"Ошибка при скачивании исходного кода: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(
                self, 
                "Ошибка", 
                f"Не удалось скачать исходный код: {str(e)}",
                QMessageBox.StandardButton.Ok
            )

class ExtractionWorker(QThread):
    progress = Signal(int)
    finished = Signal(list, str, str)  # sessions, archive_name, archive_path
    error = Signal(str)
    
    def __init__(self, source_path, temp_dir, is_archive=True):
        super().__init__()
        self.source_path = source_path
        self.temp_dir = temp_dir
        self.is_archive = is_archive
        logger.info(f"Создан ExtractionWorker: source_path={source_path}, temp_dir={temp_dir}, is_archive={is_archive}")
        
    def run(self):
        try:
            source_dir = ""
            
            if self.is_archive:
                # Распаковываем архив с помощью 7-Zip (поддерживает и RAR, и ZIP)
                logger.info(f"Начало распаковки архива: {self.source_path}")
                self.progress.emit(5)  # Начальный прогресс
                
                try:
                    # Проверяем существование и доступность архива
                    if not os.path.exists(self.source_path):
                        raise FileNotFoundError(f"Архив не найден: {self.source_path}")
                    
                    if not os.access(self.source_path, os.R_OK):
                        raise PermissionError(f"Нет прав на чтение архива: {self.source_path}")
                    
                    # Проверяем, что это действительно файл, а не директория
                    if not os.path.isfile(self.source_path):
                        raise ValueError(f"Указанный путь не является файлом: {self.source_path}")
                        
                    # Проверяем расширение файла
                    file_ext = os.path.splitext(self.source_path)[1].lower()
                    if file_ext not in ['.zip', '.rar', '.7z']:
                        logger.warning(f"Необычное расширение файла для архива: {file_ext}")
                        
                    # Проверяем, что директория назначения доступна для записи
                    output_dir_parent = os.path.dirname(self.temp_dir)
                    if not os.path.exists(output_dir_parent):
                        try:
                            os.makedirs(output_dir_parent, exist_ok=True)
                        except Exception as e:
                            raise PermissionError(f"Не удалось создать директорию для распаковки: {str(e)}")
                            
                    # Создаем временную директорию, если она не существует
                    if not os.path.exists(self.temp_dir):
                        try:
                            os.makedirs(self.temp_dir, exist_ok=True)
                            logger.info(f"Создана временная директория: {self.temp_dir}")
                        except Exception as e:
                            raise PermissionError(f"Не удалось создать временную директорию: {str(e)}")
                    
                    # Распаковываем архив
                    extract_with_7zip(self.source_path, self.temp_dir)
                    self.progress.emit(30)  # Прогресс после распаковки основного архива
                    source_dir = self.temp_dir
                    logger.info(f"Архив успешно распакован в {self.temp_dir}")
                    
                    # Проверяем, что в директории есть хотя бы один файл
                    if not os.listdir(self.temp_dir):
                        raise Exception("Архив пуст или произошла ошибка при распаковке")
                        
                except Exception as e:
                    logger.error(f"Ошибка при распаковке архива {self.source_path}: {str(e)}")
                    self.error.emit(str(e))
                    return
            else:
                # Если это папка, используем ее напрямую
                if not os.path.exists(self.source_path):
                    self.error.emit(f"Папка не найдена: {self.source_path}")
                    return
                    
                if not os.path.isdir(self.source_path):
                    self.error.emit(f"Указанный путь не является директорией: {self.source_path}")
                    return
                    
                source_dir = self.source_path
                logger.info(f"Используем папку напрямую: {source_dir}")
                self.progress.emit(30)  # Устанавливаем прогресс
            
            # Шаг 1: Проверяем, может быть сама директория - это профиль Chrome
            logger.info(f"Шаг 1: Проверка, является ли {source_dir} профилем Chrome")
            source_dir_info = self.analyze_session_folder(source_dir)
            if source_dir_info['is_chrome_profile']:
                logger.info(f"Найден профиль Chrome в корне распакованной директории")
                session_name = os.path.basename(source_dir)
                sessions = [{
                    'name': session_name,
                    'path': source_dir
                }]
                archive_name = os.path.basename(self.source_path)
                self.progress.emit(100)
                logger.info(f"Найдена сессия непосредственно в {source_dir}")
                self.finished.emit(sessions, archive_name, self.source_path)
                return
            
            # Шаг 2: Ищем ZIP и RAR файлы сессий
            logger.info(f"Шаг 2: Поиск архивов сессий в {source_dir}")
            session_archives = []
            
            try:
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        if file.lower().endswith(('.zip', '.rar', '.7z')):
                            full_path = os.path.join(root, file)
                            # Проверяем размер файла, чтобы исключить пустые архивы
                            try:
                                file_size = os.path.getsize(full_path)
                                if file_size < 100:  # Слишком маленький размер для архива
                                    logger.warning(f"Архив слишком мал ({file_size} байт), вероятно поврежден: {full_path}")
                                    continue
                            except Exception as e:
                                logger.warning(f"Не удалось получить размер файла {full_path}: {str(e)}")
                                continue
                                
                            logger.info(f"Найден архив: {full_path} (размер: {file_size} байт)")
                            session_archives.append(full_path)
            except Exception as e:
                logger.error(f"Ошибка при поиске архивов: {str(e)}")
                self.error.emit(f"Ошибка при поиске архивов сессий: {str(e)}")
                return
            
            logger.info(f"Найдено архивов сессий: {len(session_archives)}")
            self.progress.emit(40)  # Прогресс после поиска архивов
            
            # Шаг 3: Если не нашли архивов, поищем структуру профиля Chrome в подпапках
            if not session_archives:
                logger.info(f"Шаг 3: Поиск профилей Chrome в подпапках {source_dir}")
                chrome_profiles = []
                
                try:
                    for root, dirs, _ in os.walk(source_dir):
                        # Ограничиваем глубину поиска для производительности
                        depth = root.replace(source_dir, '').count(os.sep)
                        if depth > 3:  # Максимальная глубина поиска - 3 уровня
                            continue
                            
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            # Пропускаем директории, к которым нет доступа
                            if not os.access(dir_path, os.R_OK):
                                logger.warning(f"Нет доступа к директории: {dir_path}")
                                continue
                                
                            folder_info = self.analyze_session_folder(dir_path)
                            
                            if folder_info['is_chrome_profile']:
                                chrome_profiles.append({
                                    'name': dir_name,
                                    'path': dir_path
                                })
                                logger.info(f"Найден профиль Chrome в {dir_path}")
                except Exception as e:
                    logger.error(f"Ошибка при поиске профилей Chrome: {str(e)}")
                    self.error.emit(f"Ошибка при поиске профилей: {str(e)}")
                    return
                
                if chrome_profiles:
                    logger.info(f"Найдено готовых профилей Chrome: {len(chrome_profiles)}")
                    archive_name = os.path.basename(self.source_path)
                    self.progress.emit(100)
                    self.finished.emit(chrome_profiles, archive_name, self.source_path)
                    return
                else:
                    logger.warning(f"Не найдено профилей Chrome в подпапках")
            
            # Шаг 4: Если нашли архивы сессий, распаковываем их
            total_files = len(session_archives)
            if total_files == 0:
                error_msg = "Не найдено архивов сессий (ZIP, RAR или 7Z) или профилей Chrome"
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
                
            # Распаковываем архивы с помощью 7-Zip
            sessions = []
            failed_archives = []
            
            logger.info(f"Шаг 4: Распаковка {total_files} архивов сессий")
            for i, archive_path in enumerate(session_archives):
                try:
                    session_name = os.path.splitext(os.path.basename(archive_path))[0]
                    session_dir = os.path.join(self.temp_dir, session_name)
                    
                    # Создаем директорию для сессии
                    os.makedirs(session_dir, exist_ok=True)
                    
                    logger.info(f"Распаковка архива сессии {i+1}/{total_files}: {archive_path} -> {session_dir}")
                    
                    # Распаковываем архив с помощью 7-Zip
                    try:
                        extract_with_7zip(archive_path, session_dir)
                        sessions.append({
                            'name': session_name,
                            'path': session_dir
                        })
                        logger.info(f"Архив сессии успешно распакован: {session_name}")
                    except Exception as e:
                        logger.error(f"Ошибка при распаковке вложенного архива {archive_path}: {str(e)}")
                        failed_archives.append({
                            'path': archive_path,
                            'error': str(e)
                        })
                        # Пропускаем этот архив, но продолжаем с остальными
                        continue
                    
                    # Проверяем, что в распакованной директории есть структура профиля Chrome
                    session_info = self.analyze_session_folder(session_dir)
                    if session_info['is_chrome_profile']:
                        logger.info(f"Найден профиль Chrome в {session_dir}")
                    else:
                        # Если не нашли профиль Chrome в корне, ищем в подпапках
                        found_profile = False
                        for root, dirs, _ in os.walk(session_dir):
                            if found_profile:
                                break
                                
                            for dir_name in dirs:
                                dir_path = os.path.join(root, dir_name)
                                folder_info = self.analyze_session_folder(dir_path)
                                
                                if folder_info['is_chrome_profile']:
                                    # Обновляем путь к сессии
                                    for session in sessions:
                                        if session['name'] == session_name:
                                            session['path'] = dir_path
                                            logger.info(f"Обновлен путь к сессии {session_name}: {dir_path}")
                                            break
                                    found_profile = True
                                    break
                        
                        if not found_profile:
                            logger.warning(f"Структура профиля Chrome не найдена в {session_dir}")
                    
                    progress = int(40 + (i + 1) / total_files * 60)  # Масштабируем прогресс от 40% до 100%
                    self.progress.emit(progress)
                    
                except Exception as e:
                    logger.error(f"Ошибка при обработке архива {archive_path}: {str(e)}")
                    logger.error(traceback.format_exc())
                    failed_archives.append({
                        'path': archive_path,
                        'error': str(e)
                    })
                    # Продолжаем с остальными архивами
            
            if not sessions:
                if failed_archives:
                    error_details = "\n".join([f"{i+1}. {a['path']}: {a['error']}" for i, a in enumerate(failed_archives)])
                    error_msg = f"Не удалось распаковать ни одного архива сессии. Ошибки:\n{error_details}"
                else:
                    error_msg = "Не удалось найти или распаковать архивы сессий"
                    
                logger.error(error_msg)
                self.error.emit(error_msg)
                return
                
            archive_name = os.path.basename(self.source_path)
            logger.info(f"Завершение работы, найдено {len(sessions)} сессий")
            self.progress.emit(100)
            self.finished.emit(sessions, archive_name, self.source_path)
            
        except Exception as e:
            logger.error(f"Ошибка в ExtractionWorker: {str(e)}")
            logger.error(traceback.format_exc())
            self.error.emit(f"Критическая ошибка: {str(e)}")
            
    def analyze_session_folder(self, folder_path):
        """Анализирует структуру папки для определения, является ли она профилем Chrome"""
        result = {
            'is_chrome_profile': False,
            'has_default_folder': False,
            'default_path': None
        }
        
        try:
            # Проверяем, существует ли директория
            if not os.path.exists(folder_path):
                logger.warning(f"Директория не существует: {folder_path}")
                return result
                
            if not os.path.isdir(folder_path):
                logger.warning(f"Указанный путь не является директорией: {folder_path}")
                return result
                
            if not os.access(folder_path, os.R_OK):
                logger.warning(f"Нет прав на чтение директории: {folder_path}")
                return result
            
            # Ключевые файлы профиля Chrome
            chrome_profile_files = ['Cookies', 'Web Data', 'History', 'Login Data', 'Preferences']
            
            # Если сама папка называется 'Default'
            if os.path.basename(folder_path) == 'Default':
                # Проверяем наличие ключевых файлов
                profile_files_present = [f for f in chrome_profile_files if os.path.exists(os.path.join(folder_path, f))]
                if profile_files_present:
                    logger.info(f"Найден профиль Chrome в папке Default, найдены файлы: {', '.join(profile_files_present)}")
                    result['is_chrome_profile'] = True
                    result['has_default_folder'] = True
                    result['default_path'] = os.path.dirname(folder_path)
                    return result
            
            # Проверяем наличие папки Default внутри
            default_folder = os.path.join(folder_path, 'Default')
            if os.path.exists(default_folder) and os.path.isdir(default_folder):
                result['has_default_folder'] = True
                result['default_path'] = folder_path
                
                # Проверяем наличие ключевых файлов в Default
                profile_files_present = [f for f in chrome_profile_files if os.path.exists(os.path.join(default_folder, f))]
                if profile_files_present:
                    logger.info(f"Найден профиль Chrome в папке {folder_path}/Default, найдены файлы: {', '.join(profile_files_present)}")
                    result['is_chrome_profile'] = True
                    return result
            
            # Проверяем, не является ли сама папка профилем Chrome (без папки Default)
            profile_files_present = [f for f in chrome_profile_files if os.path.exists(os.path.join(folder_path, f))]
            if profile_files_present:
                logger.info(f"Найден профиль Chrome в папке {folder_path}, найдены файлы: {', '.join(profile_files_present)}")
                result['is_chrome_profile'] = True
                return result
            
            # Проверяем также файлы Local Storage, которые часто есть в профилях Chrome
            if os.path.exists(os.path.join(folder_path, 'Local Storage')):
                logger.info(f"Найдена папка Local Storage в {folder_path}, возможно это профиль Chrome")
                if len(profile_files_present) > 0 or os.path.exists(os.path.join(folder_path, 'Local Storage', 'leveldb')):
                    result['is_chrome_profile'] = True
                    return result
                
        except Exception as e:
            logger.error(f"Ошибка при анализе папки {folder_path}: {str(e)}")
            logger.error(traceback.format_exc())
            
        return result

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WhatsAppSessionManager()
    window.show()
    sys.exit(app.exec()) 