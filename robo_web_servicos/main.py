class RoboSites:
    def __init__(self):
        self.site_acesso = None
        self.dados_usuario = list()

    def criacao_user_gesta(self, dados_usuario, site):
        self.dados_usuario = dados_usuario
        self.site_acesso = site


if __name__ == "__main__":
    lista_dados_usuario = {
        'nome_usuario': '',
        'email_usuario': '',
        'senha_usuario': '',
    }

    inicio_obj = RoboSites()

