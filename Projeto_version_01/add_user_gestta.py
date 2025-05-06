""" https://googlechromelabs.github.io/chrome-for-testing/#stable """
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from time import sleep

ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = str(Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')).replace('\\', '/')

DRIVE_CHROME = webdriver.Chrome()
CHROME_SERVICE = Service(executable_path=str(PATH_CHROME_DRIVER))

def site_gessta(dados_entrada):
    DRIVE_CHROME.get(dados_entrada)
    elemento_login = DRIVE_CHROME.find_element(By.ID, "email")
    elemento_senha = DRIVE_CHROME.find_element(By.XPATH, "//input[@id='password'")
    sleep(2)
    elemento_login()


    sleep(10)


if __name__ == '__main__':
    url = 'https://app.gestta.com.br/#/login/auth?isInitialPage=true'
    site_gessta(url)
