import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Настройка Selenium
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

# Парсинг email:password из txt файла
def parse_accounts(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [line.strip().split(':') for line in lines if ':' in line]

# Процесс регистрации на ChatGPT
def register_account(email, password, driver):
    driver.get("https://chat.openai.com/auth/register")  # URL регистрации
    time.sleep(2)
    
    # Ввод email
    email_input = driver.find_element(By.NAME, 'email')
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # Ввод пароля
    password_input = driver.find_element(By.NAME, 'password')
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(2)

# Получение кода подтверждения из временной почты
def get_verification_code(email):
    email_api_url = f"https://api.firstmail.com/get_mail/{email}"
    time.sleep(5)  # Ожидание для получения письма
    response = requests.get(email_api_url)
    if response.status_code == 200:
        # Используем регулярное выражение для поиска кода
        match = re.search(r'(\d{6})', response.text)
        if match:
            return match.group(1)
    return None

# Подтверждение аккаунта
def confirm_account(driver, code):
    code_input = driver.find_element(By.NAME, 'verification_code')
    code_input.send_keys(code)
    code_input.send_keys(Keys.RETURN)
    time.sleep(2)

# Основной цикл регистрации
def main(file_path):
    driver = setup_driver()
    accounts = parse_accounts(file_path)
    
    total_accounts = len(accounts)  # Количество строк
    print(f"Всего аккаунтов для регистрации: {total_accounts}")

    for i, (email, password) in enumerate(accounts, start=1):
        print(f"Регистрация аккаунта {i}/{total_accounts}: {email}")
        try:
            register_account(email, password, driver)
            verification_code = get_verification_code(email)
            
            if verification_code:
                confirm_account(driver, verification_code)
                print(f"Аккаунт {email} успешно зарегистрирован.")
            else:
                print(f"Не удалось получить код подтверждения для {email}.")
                
        except Exception as e:
            print(f"Ошибка при регистрации {email}: {str(e)}")
    
    driver.quit()
    print("Процесс завершен. Все аккаунты обработаны.")

# Запуск основного цикла с указанием пути к файлу с данными
main('accounts.txt')
