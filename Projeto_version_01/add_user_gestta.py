""" https://googlechromelabs.github.io/chrome-for-testing/#stable """
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')


def site_gessta(dados_entrada):
    print('Criando usuário no GESSTA')

