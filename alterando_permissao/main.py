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
        return resultado

    def verificando_modulo(self):
        comando_shell = (
            'Get-Module ExchangeOnlineManagement -ListAvailable | '
            'Select-Object ModuleType, Version | '
            'ConvertTo-Json -Depth 3 '
        )
        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Conectando... ')
        return resultado

    def parse_json(self, linha: str):
        linha = linha.strip()

        # Tenta achar um bloco JSON {} ou []
        m = re.search(r'(\{.*\}|\[.*\])', linha, re.S)

        if not m:
            # Se não achou JSON, retorna vazio
            return []

        dados = json.loads(m.group(1))

        if isinstance(dados, dict):
            dados = [dados]

        limpa = []

        for item in dados:
            limpa.append({
                'Modulo': str(item.get('ModuleType', '')),
                'Versao': str(item.get('Version', '')),
            })

        return limpa


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    resultando_comando = init_obj_calendar.chamando_obj_conexao()
    # resultando_comando = init_obj_calendar.verificando_modulo()

    for item in resultando_comando:
        print(item)

    # resultado_parse = init_obj_calendar.parse_json(resultando_comando)
    # for item in resultado_parse:
    #     print(item['Modulo'])



