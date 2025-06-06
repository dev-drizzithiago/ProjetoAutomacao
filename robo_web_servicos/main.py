
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


if __name__ == "__main__":
    lista_dados_acesso = {
        'site': '',
        'user_acesso': '',
        'pass_acesso': '',
        'email_usuario': '',
        'senha_usuario': '',
        'cpf': '',
    }

    inicio_obj = RoboSites()

