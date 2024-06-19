import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    login_url = "https://login.1c.ru/login?service=https%3A%2F%2Fits.1c.kz%2Flogin%2F%3Faction%3Daftercheck%26provider%3Dlogin"
    driver.get(login_url)
    input("Please log in through the browser and press Enter to continue...")

def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_and_handle_alerts(driver):
    try:
        while True:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.dismiss()
            print("Alert dismissed")
    except Exception:
        print("No more alerts to dismiss")

def fetch_content(driver, content_id):
    content_url = f"https://its.1c.kz/db/accountingkz#content:{content_id}:hdoc"
    if not is_url_accessible(content_url):
        print(f"URL not accessible or does not exist: {content_url}")
        return

    driver.get(content_url)
    check_and_handle_alerts(driver)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "w_metadata_doc_frame")))
        driver.switch_to.frame("w_metadata_doc_frame")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "paywall"))
        )
        h2 = element.find_element(By.TAG_NAME, "h2").text
        date = element.find_element(By.CLASS_NAME, "date").text
        content = element.text
        images = element.find_elements(By.TAG_NAME, "img")

        folder_name = str(content_id)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        data = {"date": date, "instruction": h2, "info": content}
        with open(os.path.join(folder_name, f"{folder_name}.json"), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.flush()

        for index, img in enumerate(images):
            src = img.get_attribute('src')
            image_filename = f"{index}_{src.split('/')[-1].split('?')[0]}"
            image_path = os.path.join(folder_name, image_filename)
            with requests.get(src, stream=True) as r:
                with open(image_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    except Exception as e:
        print(f"Error fetching content: {e}")

def main():
    driver = setup_driver()
    login(driver)
    for content_id in range(102000, 105001):
        fetch_content(driver, content_id)
    driver.quit()

if __name__ == "__main__":
    main()
