from conectando_exechange_online import ConexaoExchangeOnline

class AlterarPermissaoReunioes:
    def __init__(self, *credenciais):
        pass

    def chamando_obj_conexao(self):
        init_conectar_exchange = ConexaoExchangeOnline()
        init_conectar_exchange.install_modulo_exchange()

if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    init_obj_calendar.chamando_obj_conexao()