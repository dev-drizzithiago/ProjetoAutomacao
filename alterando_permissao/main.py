from conectando_exechange_online import ConexaoExchangeOnline

class AlterarPermissaoReunioes:
    def __init__(self, *credenciais):
        self.init_conectar_exchange = ConexaoExchangeOnline()

    def chamando_obj_conexao(self):
        self.init_conectar_exchange = ConexaoExchangeOnline()
        self.init_conectar_exchange.install_modulo_exchange()
        self.init_conectar_exchange.importando_modulo()
        self.init_conectar_exchange.conectando_exchange('thiago.pinheiro@segeticonsultoria.com')

if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    init_obj_calendar.chamando_obj_conexao()
