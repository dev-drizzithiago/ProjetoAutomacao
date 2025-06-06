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

        DRIVE_CHROME.get('https://app.gestta.com.br/')
        print(f'Acesso o site {self.LINK_COMPLETO}')
        elemento_login = DRIVE_CHROME.find_element(By.ID, "email")
        elemento_senha = DRIVE_CHROME.find_element(By.XPATH, "//input[@id='password']")

        elemento_login.send_keys(self.dados_usuario['user_acesso_site'])
        print('Entrando com usuário...')
        sleep(1)

        elemento_senha.send_keys(self.dados_usuario['pass_acesso_site'])
        print('Entrando com a senha...')
        sleep(1)

        elemento_senha.send_keys(Keys.ENTER)
        print("Entrando no portal...")
        sleep(10)

        # DRIVE_CHROME.get('https://app.gestta.com.br/admin/#/sidebar/user/list')
        # sleep(2)

        DRIVE_CHROME.get('https://app.gestta.com.br/admin/#/sidebar/user/create')
        sleep(2)

        elemento_nome_usuario = DRIVE_CHROME.find_element(By.ID, "name")
        elemento_email_empresa = DRIVE_CHROME.find_element(By.ID, "email")
        elemento_senha_login = DRIVE_CHROME.find_element(By.NAME, "password")
        elemento_papel = DRIVE_CHROME.find_element(By.XPATH, "//i[@class='caret pull-right']")
        elemento_btn_submit = DRIVE_CHROME.find_element(
            By.XPATH,
            "//button[span[contains(text(), 'Salvar')]]")

        elemento_nome_usuario.send_keys(self.dados_usuario['nome_completo'])
        print('Preenchendo o nome completo')
        sleep(1)

        elemento_email_empresa.send_keys(self.dados_usuario['email_usuario_empresa'])
        print('Preenchendo o email')
        sleep(1)

        elemento_senha_login.send_keys(self.dados_usuario['senha_usuario'])
        print('Preenchendo o a senha')
        sleep(1)

        elemento_papel.click()
        opc_select = DRIVE_CHROME.find_element(By.XPATH, "//span[contains(text(), 'Usuário')]")
        opc_select.click()

        elemento_btn_submit.send_keys(self.dados_usuario[''])


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
        sleep(2)

        DRIVE_CHROME.get(self.LINK_COMPLETO)
        print('Entrando na URL para adicionar usuários')
        sleep(2)

        DRIVE_CHROME.get(self.LINK_COMPLETO_FORMULARIO)
        print('Entrando no FORMS para adicionar usuários')
        sleep(2)

        elemento_nome_usuario = DRIVE_CHROME.find_element(By.ID, "nome")
        elemento_cpf = DRIVE_CHROME.find_element(By.ID, "cpf")
        elemento_data = DRIVE_CHROME.find_element(By.ID, "dataNascimento")
        elemento_data_admss = DRIVE_CHROME.find_element(By.ID, "dataAdmissao")
        elemento_email_pessoal = DRIVE_CHROME.find_element(By.ID, "email")
        elemento_email_empresa = DRIVE_CHROME.find_element(By.ID, "emailEmpresarial")
        elemento_usuario_login = DRIVE_CHROME.find_element(By.ID, "login")
        elemento_senha_login = DRIVE_CHROME.find_element(By.ID, "pwd")
        elemento_senha_login_confi = DRIVE_CHROME.find_element(By.ID, "pwd2")
        elemento_btn_submit = DRIVE_CHROME.find_element(By.ID, "botaoSubmit")

        elemento_nome_usuario.send_keys(self.dados_usuario['nome_completo'])
        sleep(1)

        elemento_cpf.send_keys(self.dados_usuario['cpf_usuario'])
        sleep(1)

        elemento_data.send_keys(self.dados_usuario['data_nasc_usuario'])
        sleep(1)

        elemento_data_admss.send_keys(self.dados_usuario['data_admissao_usario'])
        sleep(1)

        elemento_email_pessoal.send_keys(self.dados_usuario['email_usuario_pessoal'])
        sleep(1)

        elemento_email_empresa.send_keys(self.dados_usuario['email_usuario_empresa'])
        sleep(1)

        elemento_usuario_login.send_keys(self.dados_usuario['usuario_login'])
        sleep(1)

        elemento_senha_login.send_keys(self.dados_usuario['senha_usuario'])
        sleep(1)

        elemento_senha_login_confi.send_keys(self.dados_usuario['senha_usuario'])
        sleep(1)

        elemento_btn_submit.send_keys(Keys.ENTER)
        print('Cadastro finalizado')
        sleep(5)

ROOT_FOLDER = Path(__file__).parent
PATH_CHROME_DRIVER = str(Path(ROOT_FOLDER / 'driver_google' / 'chromedriver.exe')).replace('\\', '/')
DRIVE_CHROME = webdriver.Chrome()
CHROME_SERVICE = Service(executable_path=str(PATH_CHROME_DRIVER))


if __name__ == "__main__":
    SITE_TESTE = os.getenv('URL_ACESSO_SITE_SCI')
    lista_dados_acesso = {
        'url_site': os.getenv('URL_ACESSO_SITE_SCI'),
        'user_acesso_site': os.getenv('USER_ACESSO_GESTTA'),
        'pass_acesso_site': os.getenv('PASS_ACESSO_GESTTA'),
        'nome_completo': os.getenv('NOME_COMPLETO_SCI'),
        'cpf_usuario': '111.111.111-11',
        'data_nasc_usuario': '01/01/2000',
        'data_admissao_usario': '10/06/2025',
        'email_usuario_pessoal': os.getenv('EMAIL_USUARIO_PESSOAL_SCI'),
        'email_usuario_empresa': os.getenv('EMAIL_USUARIO_EMPRESA_SCI'),
        'usuario_login': os.getenv('LOGIN_SCI'),
        'senha_usuario': os.getenv('SENHA_SCI'),
    }

    inicio_obj = RoboSites()
    # inicio_obj.criacao_user_sci(lista_dados_acesso, SITE_TESTE)
    inicio_obj.criacao_user_gesta(lista_dados_acesso, SITE_TESTE)
