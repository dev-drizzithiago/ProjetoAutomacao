from conectando_exechange_online import ConexaoExchangeOnline

class AlterarPermissaoReunioes:
    def __init__(self, *credenciais):
        self.init_conectar_exchange = ConexaoExchangeOnline()

    def chamando_obj_conexao(self, cmd, text):
        self.init_conectar_exchange = ConexaoExchangeOnline()
        self.init_conectar_exchange.processando_modulo_exchange(cmd, text)


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    init_obj_calendar.chamando_obj_conexao(
        "Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force",
        'Instalando o modúlo... '
    )
    init_obj_calendar.chamando_obj_conexao(
        "Import-Module ExchangeOnlineManagement",
        'Importando Modúlo... '
    )
    init_obj_calendar.chamando_obj_conexao(
        "Connect-ExchangeOnline -UserPrincipalName thiago.pinheiro@segeticonsultoria.com",
        'Conectando ao modulo... '
    )

