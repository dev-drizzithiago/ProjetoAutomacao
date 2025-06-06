import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from dotenv import load_dotenv
load_dotenv()

class RoboSites:
    def __init__(self):
        self.site_acesso = None
        self.dados_usuario = list()

    def criacao_user_gesta(self, dados_usuario, site):
        self.dados_usuario = dados_usuario
        self.site_acesso = site

    def criacao_user_sci(self, dados_usuario, site):
        self.dados_usuario = dados_usuario
        self.site_acesso = site

        DRIVE_CHROME.get(self.site_acesso)

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

if __name__ == "__main__":

    lista_dados_acesso = {
        'url_site': os.getenv('URL_ACESSO_SITE_SCI', ''),
        'user_acesso_site': os.getenv('USER_ACESSO_SITE_SCI', ''),
        'pass_acesso_site': os.getenv('PASS_ACESSO_SITE_SCI', ''),
        'email_usuario_pessoal': '',
        'email_usuario_empresa': '',
        'usuario_login': '',
        'senha_usuario': '',
        'cpf_usuario': '',
        'data_nasc_usuario': '',
        'data_admissao_usario': '',
    }

    inicio_obj = RoboSites()

