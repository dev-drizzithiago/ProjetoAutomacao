from subprocess import run, PIPE
from ..spinner_run import run_spinner

class ConexaoExchangeOnline:
    def __init__(self):
        pass

    def conectando(self, *credenciais):
        print(credenciais)

    def install_modulo_exchange(self):
        COMANDO_SHELL = """Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force"""
        result_comando = run_spinner(COMANDO_SHELL)
        print(result_comando)

if __name__ == '__main__':
    init_obj_conexao_exchange_online = ConexaoExchangeOnline()
    init_obj_conexao_exchange_online.conectando('thiago', '123')
