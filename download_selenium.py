import os
import time
import shutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Диапазон ID контента
start_id = 103732
end_id = 105000

# URL для получения контентаngkz/content/{}/hdoc"

# Инициализация драйвераь   ь
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Запуск в фоновом режиме (можно включить после отладки)
options.add_argument('--kiosk-printing')
download_path = "C:\\Pycharm\\1c_buh\\data"  # Измените на ваш путь к папке загрузок
prefs = {
    "savefile.default_directory": download_path,
    "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":"","capabilities":{}}],"selectedDestinationId":"Save as PDF","version":2}',
    "printing.default_destination_selection_rules": {
        "kind": "local",
        "namePattern": "Save as PDF",
        "idPattern": "Save as PDF"
    },
    "printing.print_preview_sticky_settings": {
        "appState": '{"version":2,"recentDestinations":[{"id":"Save as PDF","origin":"local","account":"","capabilities":{}}],"selectedDestinationId":"Save as PDF","lastUsedDisplayName":"Save as PDF"}',
        "selectedDestinationId": "Save as PDF",
        "selectedDestinationDisplayName": "Save as PDF",
        "lastUsedPrinterName": "Save as PDF"
    }
}
options.add_experimental_option("prefs", prefs)
options.add_argument('--kiosk-printing')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Открытие страницы для ручной авторизации
driver.get("https://login.1c.ru/login?service=https%3A%2F%2Fits.1c.kz%2Flogin%2F%3Faction%3Daftercheck%26provider%3Dlogin")

# Ожидание ввода от пользователя
input("Пожалуйста, авторизуйтесь в браузере и нажмите Enter для продолжения...")

# Открытие целевого домена в Selenium
driver.get("https://its.1c.kz")

# Функция для проверки доступности URL
def is_url_accessible(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Функция для прокрутки страницы до конца
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Ожидание загрузки нового контента
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Функция для сохранения страницы как PDF
def save_page_as_pdf(content_id, save_path):
    url = f"https://its.1c.kz/db/accountingkz#content:{content_id}:hdoc"
    if not is_url_accessible(url):
        print(f"Ошибка: контент с ID {content_id} недоступен.")
        return

    driver.get(url)

    try:
        # Ожидание загрузки страницы
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "w_metadata_print_href")))

        # Прокрутка страницы до конца
        scroll_to_bottom(driver)

        # Нахождение кнопки для печати и клик
        print_button = driver.find_element(By.ID, "w_metadata_print_href")
        print_button.click()

        # Ожидание загрузки страницы печати
        time.sleep(5)  # Время ожидания может быть изменено в зависимости от скорости сети и сайта

        # Сохранение страницы как PDF
        driver.execute_script('window.print();')

        # Ожидание завершения печати и сохранения файла
        time.sleep(10)  # Увеличьте это время, если файл не успевает сохраняться

        # Путь к скачанному PDF файлу по умолчанию
        downloaded_files = os.listdir(download_path)
        downloaded_pdf_path = None

        for file_name in downloaded_files:
            if file_name.endswith(".pdf"):
                downloaded_pdf_path = os.path.join(download_path, file_name)
                break

        if downloaded_pdf_path:
            shutil.move(downloaded_pdf_path, save_path)
            print(f"PDF сохранен: {save_path}")
        else:
            print(f"Ошибка: файл не найден в папке загрузок {download_path}")

    except TimeoutException:
        print(f"Ошибка: контент с ID {content_id} не найден или не загрузился вовремя.")

# Сохранение PDF файлов
base_path = "C:\\Pycharm\\1c_buh\\data"
if not os.path.exists(base_path):
    os.makedirs(base_path)

for i, content_id in enumerate(range(start_id, end_id + 1), start=1):
    save_path = f"{base_path}/1c_buh_{start_id}.pdf"
    start_id += 1
    save_page_as_pdf(content_id, save_path)

# Закрытие драйвера
driver.quit()
