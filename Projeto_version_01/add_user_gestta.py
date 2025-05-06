""" https://googlechromelabs.github.io/chrome-for-testing/#stable """
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')
DRIVE_CHROME = webdriver.Chrome()
webdriver.get('https://app.gestta.com.br/#/login/auth?isInitialPage=true')

def site_gessta(dados_entrada):
    ...



