import os
import time
import json
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

content_id = 104044
folder_path = str(content_id)

def setup_driver():
    # Настройка параметров драйвера
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    # Открытие страницы для ручной авторизации
    login_url = "https://login.1c.ru/login?service=https%3A%2F%2Fits.1c.kz%2Flogin%2F%3Faction%3Daftercheck%26provider%3Dlogin"
    driver.get(login_url)
    input("Пожалуйста, авторизуйтесь в браузере и нажмите Enter для продолжения...")
def fetch_content(driver):
    content_url = f"https://its.1c.kz/db/accountingkz#content:{content_id}:hdoc"
    driver.get(content_url)
    time.sleep(5)

    if "w_metadata_doc_frame" in driver.page_source:
        try:
            WebDriverWait(driver, 30).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "w_metadata_doc_frame"))
            )
        except Exception as e:
            print(f"Не удалось переключиться на фрейм: {e}")
            return
    else:
        print("Фрейм не найден на странице")
        return

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "paywall"))
        )
        h2 = element.find_element(By.TAG_NAME, "h2").text
        date = element.find_element(By.CLASS_NAME, "date").text
        content = element.text
        images = element.find_elements(By.TAG_NAME, "img")

        # Сохранение текста в JSON
        data = {
            "date": date,
            "instruction": h2,
            "info": content
        }
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(os.path.join(folder_path, f"{h2.replace('/', '_')}.json"), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        # Сохранение изображений
        for index, img in enumerate(images):
            src = img.get_attribute('src')
            image_filename = src.split('/')[-1].split('?')[0]
            image_filename = f"{index}_{image_filename.replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')}"
            image_path = os.path.join(folder_path, image_filename)
            # Используем screenshot_as_png для сохранения изображения
            img.screenshot(image_path)

    except Exception as e:
        print(f"Ошибка при получении содержимого: {e}")


def main():
    driver = setup_driver()
    login(driver)
    fetch_content(driver)
    driver.quit()

if __name__ == "__main__":
    main()
