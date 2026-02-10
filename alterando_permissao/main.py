from conectando_exechange_online import ProcessoRun
from dotenv import load_dotenv
from os import getenv
import json
import re

load_dotenv()

class AlterarPermissaoReunioes:

    AppId = getenv('AppId')
    CertificateThumbprint = getenv('CertificateThumbprint')
    Organization = getenv('Organization')

    def __init__(self):

        self.cmd = (
            f'Import-Module ExchangeOnlineManagement; '
            f'Connect-ExchangeOnline -AppId "{self.AppId}" '
            f' -CertificateThumbprint "{self.CertificateThumbprint}" '
            f' -Organization "{self.Organization}" -ShowBanner:$false; '
            f'Get-EXOMailbox -ResultSize 1 | Select-Object DisplayName,PrimarySmtpAddress; '
            f'Disconnect-ExchangeOnline -Confirm:$false;'
        )

        self.init_conectar_exchange = ProcessoRun()

    def chamando_obj_conexao(self):
        self.init_conectar_exchange = ProcessoRun()
        resultado = self.init_conectar_exchange.run_spinner(self.cmd, 'Conectando... ')
        print()
        print('---' * 20)
        print(resultado)
        return resultado

    def verificando_modulo(self):
        comando_shell = (
            'Get-Module ExchangeOnlineManagement -ListAvailable | ConvertTo-Json -Depth 3'
        )
        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Conectando... ')
        print()
        print('---' * 20)
        print(resultado)

        return resultado


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    # resultando_comando = init_obj_calendar.chamando_obj_conexao()
    resultando_comando = init_obj_calendar.verificando_modulo()

    # Tenta achar um bloco JSON {} ou []
    m = re.search(r'(\{.*\}|\[.*\])', resultando_comando.strip(), re.S)
    if not m:
        # Se não achou JSON, retorna vazio
        return []



