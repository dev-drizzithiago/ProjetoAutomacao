""" https://googlechromelabs.github.io/chrome-for-testing/#stable """
import os
from pathlib import Path
from dotenv import load_dotenv
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

load_dotenv()

def site_gessta(dados_entrada):
    DRIVE_CHROME.get(dados_entrada)

    elemento_login = DRIVE_CHROME.find_element(By.ID, "email")
    elemento_senha = DRIVE_CHROME.find_element(By.XPATH, "//input[@id='password']")

    elemento_login.send_keys(os.getenv('EMAIL_ACESSO', ''))
    sleep(0.5)
    elemento_senha.send_keys(os.getenv('SENHA_ACESSO', ''))
    elemento_senha.send_keys(Keys.ENTER)
    sleep(6)
    elemento_configuracao = DRIVE_CHROME.find_element(By.XPATH, "//svg[@xmlns='http://www.w3.org/2000/svg']")
    elemento_configuracao.send_keys(Keys.ENTER)

    sleep(10)



ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = str(Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')).replace('\\', '/')

DRIVE_CHROME = webdriver.Chrome()
CHROME_SERVICE = Service(executable_path=str(PATH_CHROME_DRIVER))

if __name__ == '__main__':
    url = 'https://app.gestta.com.br/#/login/auth?isInitialPage=true'
    site_gessta(url)
