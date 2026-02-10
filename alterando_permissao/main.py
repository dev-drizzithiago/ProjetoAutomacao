from conectando_exechange_online import ProcessoRun

class AlterarPermissaoReunioes:
    def __init__(self):
        self.cmd = """
                Connect-ExchangeOnline `
                -AppId 00000002-0000-0ff1-ce00-000000000000 `
                -CertificateThumbprint 7278d039-3161-4e91-8d8f-4038e71aa776 `
                -Organization segeticonsultoria.onmicrosoft.com
                """
        self.init_conectar_exchange = ProcessoRun()

    def chamando_obj_conexao(self):
        self.init_conectar_exchange = ProcessoRun()
        self.init_conectar_exchange.run_spinner(self.cmd, 'Conectando... ')


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    init_obj_calendar.chamando_obj_conexao()


