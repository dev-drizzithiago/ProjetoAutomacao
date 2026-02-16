
from conectando_exechange_online import ProcessoRun
from dotenv import load_dotenv
from os import getenv
import json
import re
import os

from gerar_certificado_microsoft import GerarCertificado

load_dotenv()

LOCAL_APP = os.path.abspath('')
LOCAL_CERTIFICADO_PUBLIC = os.path.join(LOCAL_APP, 'certificado_public_2.cert')
LOCAL_CERTIFICADO_PRIVATE = os.path.join(LOCAL_APP, 'certificado_private_2.pfx')

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

        # Ajuste estes caminhos conforme o seu projeto:
        OUT_DIR = r"C:\Temp"  # use um diretório existente
        os.makedirs(OUT_DIR, exist_ok=True)

        CER_DER = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.cer")  # DER
        CER_PEM = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.pem")  # PEM (opcional para upload no Entra ID)
        KEY_PEM = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.key")  # chave privada (use com proteção/segurança)
        PFX_PATH = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.pfx")  # PFX para o seu app
        PFX_PASSWORD = f"{os.getenv('PASSWORD')}"

        g = GerarCertificado(cn="ExchangeOnlineAutomation")
        g.gerar_chave_privada()
        g.gerar_certificado_self_signed(anos_validade=5)

        # Exportações
        g.salvar_certificado_der(CER_DER)  # ✅ suba este .cer no App Registration
        g.salvar_certificado_pem(CER_PEM)  # (opcional) alternativa em PEM/Base64
        g.salvar_chave_privada_pem(KEY_PEM)  # (opcional) se precisar em PEM
        g.salvar_pfx(PFX_PATH, PFX_PASSWORD, friendly_name="MeuApp-Autenticacao (Exportable)")

        # (Opcional) instalar no store do usuário (Windows)
        # g.instalar_no_windows_currentuser_my(PFX_PATH, PFX_PASSWORD)

        print("Certificado criado!")
        print("Thumbprint (SHA1):", g.get_thumbprint_sha1())
        print("Arquivos:")
        print("  CER (DER):", CER_DER)
        print("  PEM (cert):", CER_PEM)
        print("  KEY (privada PEM):", KEY_PEM)
        print("  PFX:", PFX_PATH)

    def gerar_pfx(self):
        comando_shell = (
            rf'Export-Certificate '
            rf'-Cert "Cert:\CurrentUser\My\{os.getenv('CertificateThumbprint')}" '
            rf'-FilePath "{LOCAL_CERTIFICADO_PUBLIC}"')

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Exportando a chave publica... ')
        return resultado


if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()

    print()
    print(
        """
        [1] Conectar
        [2] Verificar Modulo
        [3] Analisar ThumpPrint
        [4] Criar novo Certificado
        [5] Criar Certificado Privado
        """
    )
    print('---' * 20)
    resposta = int(input('Escolha uma opção: '))

    if resposta == 1:
        resultando_conexao = init_obj_calendar.chamando_obj_conexao()
        for item in resultando_conexao:
            print(item)

    elif resposta == 2:
        resultando_modulo = init_obj_calendar.verificando_modulo()
        response = init_obj_calendar.parse_json(resultando_modulo)
        for item in response:
            print(item)

    elif resposta == 3:
        resultando_thumbprint = init_obj_calendar.analisando_thumbprint()
        for item in resultando_thumbprint:
            print(item)

    elif resposta == 4:
        resultando_criar_novo_certificado = init_obj_calendar.criar_novo_certificado()
        for item in resultando_criar_novo_certificado:
            print(item)

    elif resposta == 5:
        resultando_pfx = init_obj_calendar.gerar_pfx()
        for item in resultando_pfx:
            print(item)

