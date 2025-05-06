""" https://googlechromelabs.github.io/chrome-for-testing/#stable """
from pathlib import Path
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from time import sleep

def site_gessta(url_entrada, email, senha):
    DRIVE_CHROME.get(url_entrada)
    elemento_login = DRIVE_CHROME.find_element(By.ID, "email")
    elemento_senha = DRIVE_CHROME.find_element(By.XPATH, "//input[@id='password']")

    sleep(2)
    elemento_login.send_keys('email@email.com')
    sleep(2)
    elemento_senha.send_keys('senha')
    elemento_senha.send_keys(Keys.ENTER)
    sleep(10)


ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = str(Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')).replace('\\', '/')

DRIVE_CHROME = webdriver.Chrome()
CHROME_SERVICE = Service(executable_path=str(PATH_CHROME_DRIVER))

if __name__ == '__main__':
    load_dotenv()
    email_acesso = os.getenv('EMAIL_ACESSO')
    senha_acesso = os.getenv('SENHA_ACESSO')

    url = 'https://app.gestta.com.br/#/login/auth?isInitialPage=true'
    site_gessta(url_entrada=url, email=email_acesso, senha=senha_acesso)
