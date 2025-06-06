import os
from pathlib import Path
from time import sleep

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from dotenv import load_dotenv
load_dotenv()

class RoboSites:

    LINK_URL_SCI = 'https://areadocliente.sci10.com.br/'
    LINK_RELATIVO_INDEX = 'modulo/usuarioAdicional/index.php'
    LINK_RELATIVO_FORMS = 'modulo/usuarioAdicional/form.php'
    LINK_COMPLETO = urljoin(LINK_URL_SCI, LINK_RELATIVO_INDEX)
    LINK_COMPLETO_FORMULARIO = urljoin(LINK_URL_SCI, LINK_RELATIVO_FORMS)

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
        print(f'Acesso o site {self.LINK_COMPLETO}')
        elemento_login = DRIVE_CHROME.find_element(By.ID, "usuario")
        elemento_senha = DRIVE_CHROME.find_element(By.XPATH, "//input[@id='senha']")

        elemento_login.send_keys(self.dados_usuario['user_acesso_site'])
        print('Entrando com usuário')
        sleep(1)
        elemento_senha.send_keys(self.dados_usuario['pass_acesso_site'])
        print('Entrando com a senha')
        sleep(1)
        elemento_senha.send_keys(Keys.ENTER)
        print("Apertando no entrar")
        sleep(5)

        DRIVE_CHROME.get(self.LINK_COMPLETO)
        print('URL para adicionar usuários')
        sleep(5)

        DRIVE_CHROME.get(LINK_COMPLETO_FORMULARIO)

        input()


ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = str(Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')).replace('\\', '/')
DRIVE_CHROME = webdriver.Chrome()
CHROME_SERVICE = Service(executable_path=str(PATH_CHROME_DRIVER))


if __name__ == "__main__":
    SITE_TESTE = os.getenv('URL_ACESSO_SITE_SCI')
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
    inicio_obj.criacao_user_sci(lista_dados_acesso, SITE_TESTE)
