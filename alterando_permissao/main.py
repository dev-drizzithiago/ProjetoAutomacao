from conectando_exechange_online import ProcessoRun
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class AlterarPermissaoReunioes:

    AppId = getenv('AppId')
    CertificateThumbprint = getenv('CertificateThumbprint')
    Organization = getenv('Organization')

    def __init__(self):

        self.cmd = (
            f'Import-Module ExchangeOnlineManagement | '
            f'Connect-ExchangeOnline -AppId "{self.AppId}" '
            f' -CertificateThumbprint "{self.CertificateThumbprint}" '
            f' -Organization "{self.Organization}" -ShowBanner:$false | '
            f'Get-EXOMailbox -ResultSize 1 | Select-Object DisplayName,PrimarySmtpAddress | '
            f'Disconnect-ExchangeOnline -Confirm:$false '
        )

        self.init_conectar_exchange = ProcessoRun()

    def chamando_obj_conexao(self):
        self.init_conectar_exchange = ProcessoRun()
        resultado = self.init_conectar_exchange.run_spinner(self.cmd, 'Conectando... ')
        print()
        print('---' * 20)
        print(resultado)


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    init_obj_calendar.chamando_obj_conexao()


