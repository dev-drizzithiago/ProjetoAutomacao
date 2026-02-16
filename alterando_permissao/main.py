import os

from conectando_exechange_online import ProcessoRun
from dotenv import load_dotenv
from os import getenv
import json
import re
import shlex

load_dotenv()

LOCAL_APP = os.path.abspath('')
LOCAL_CERTIFICADO_PUBLIC = os.path.join(LOCAL_APP, 'certificado_public.cert')
LOCAL_CERTIFICADO_PRIVATE = os.path.join(LOCAL_APP, 'certificado_private.pfx')

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
        resultado = self.init_conectar_exchange.run_spinner(self.cmd, 'Conectando ao office 365... ')
        return resultado

    def verificando_modulo(self):
        comando_shell = (
            'Get-Module ExchangeOnlineManagement -ListAvailable | '
            'Select-Object ModuleType, Version | '
            'ConvertTo-Json -Depth 3 '
        )
        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Verificando modulo instalado... ')
        return resultado

    def parse_json(self, linha: str):
        # Analisa o texto que chega do powerShell
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

    def analisando_thumbprint(self):
        # Liste de forma completa
        comando_shell = (
            'Get-ChildItem Cert:\CurrentUser\My |'
              'Select-Object Subject, Thumbprint, HasPrivateKey |'
              'Format-List'
        )

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Analisando o Thumbprint... ')
        return resultado

    def criar_novo_certificado(self):
        comando_shell = (
            # 1) Criar novo certificado self-signed COM CHAVE EXPORTÁVEL no Current
            rf'$cert = New-SelfSignedCertificate `'
            rf'-Subject "CN={os.getenv('CertificateThumbprint')}" '
            rf'-CertStoreLocation "Cert:\CurrentUser\My" '
            rf'-KeyAlgorithm RSA -KeyLength 2048 '
            rf'-KeyExportPolicy Exportable '
            rf'-KeySpec Signature '
            rf'-NotAfter (Get-Date).AddYears(5) '
            
            rf'$thumb = $cert.Thumbprint; '
            rf'$thumb; '
            
            # 2) Exportar a PÚBLICA (.cer) — para cadastrar no App Registrat
            rf'Export-Certificate -Cert ("Cert:\CurrentUser\My\" + $thumb) -FilePath {LOCAL_CERTIFICADO_PUBLIC} | '

            # 3) Exportar o PFX com senha (para usar em -CertificateFilePath)
            rf'Export-PfxCertificate '
            rf'-Cert ("Cert:\CurrentUser\My\" + $thumb) '
            rf'-FilePath {LOCAL_CERTIFICADO_PRIVATE} '
            rf'$password = ConvertTo-SecureString "{os.getenv('PASSWORD')}" -AsPlainText -Force'
            rf'Export-PfxCertificate ... -Password $password'
        )

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Criando novo certificado... ')
        return resultado

    def gerar_pfx(self):
        comando_shell = (
            rf'Export-Certificate '
            rf'-Cert "Cert:\CurrentUser\My\{os.getenv('CertificateThumbprint')}" '
            rf'-FilePath "{LOCAL_CERTIFICADO}"')

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Exportando a chave publica... ')
        return resultado


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    # resultando_pfx = init_obj_calendar.gerar_pfx()
    # resultando_thumbprint = init_obj_calendar.analisando_thumbprint()
    # resultando_modulo = init_obj_calendar.verificando_modulo()
    # resultando_conexao = init_obj_calendar.chamando_obj_conexao()
    resultando_criar_novo_certificado = init_obj_calendar.criar_novo_certificado()

    # for item in resultando_pfx:
    #     print(item)
    #
    for item in resultando_criar_novo_certificado:
        print(item)
    #
    #
    # for item in resultando_modulo:
    #     print(item)

    # for item in resultando_conexao:
    #     print(item)

    # resultado_parse = init_obj_calendar.parse_json(resultando_comando)
    # for item in resultado_parse:
    #     print(item['Modulo'])



