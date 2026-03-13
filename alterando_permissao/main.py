from collections import defaultdict
from pkgutil import iter_modules
from time import sleep

from dotenv import load_dotenv
from os import getenv
import os
import json

from pprint import pprint

from conectando_exechange_online import ProcessoRun
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
        self.init_conectar_exchange = ProcessoRun()

    def chamando_obj_conexao(self, nome_grupo, email_permissao):
        self.init_conectar_exchange = ProcessoRun()

        comando_shell = rf"""        
        
            $sharedSmtp = "{nome_grupo}"
            $usuario = "{email_permissao}"

            # 1) Importa e conecta ao 365;
            Import-Module ExchangeOnlineManagement -ErrorAction Stop;
            Connect-ExchangeOnline -AppId '{os.getenv('AppId')}' `
              -Organization '{os.getenv('Organization')}' `
              -CertificateFilePath '{os.getenv('PATH_CERTIFICADO')}' `
              -CertificatePassword (ConvertTo-SecureString '{os.getenv('PASSWORD')}' -AsPlainText -Force) `
              -ShowBanner:$false;
            # ----------------------------------------------------------------------------------------------
            # Funcionando 
            
            # 2) Criar o mailbox compartilhado (se não existir);
            $shared = Get-Mailbox -Identity $sharedSmtp -ErrorAction SilentlyContinue           

            if (-not $shared) {{
                Write-Host "Criando mailbox compartilhado $sharedSmtp" -ForegroundColor Cyan 
                New-Mailbox -Shared -Name "{os.getenv('NOME_GRUPO')}" -PrimarySmtpAddress $sharedSmtp ` 
                    -ErrorAction Stop
            }} else {{
                Write-Host "! já existe o Mailbox compartilhado com o endereço: $sharedSmtp" -ForegroundColor Yellow 
            }} 

            # 2° etapa; concedendo permissões e testes
            # 3) Conceder permissões (FullAccess + SendAs) aos membros listados no CSV; 

            if (-not $sharedSmtp -or -not $usuario) {{
                throw "Defina ORGANIZADOR_GRUPO (shared SMTP) e USUARIO_TESTE (UPN)." 
            }} 

            Write-Host ">> Concedendo FullAccess a $usuario no shared $sharedSmtp ..." -ForegroundColor Cyan 
            try {{
                Add-MailboxPermission -Identity $sharedSmtp `
                -User $usuario -AccessRights FullAccess -AutoMapping:$true -ErrorAction Stop 
                Write-Host "✓ FullAccess concedido" -ForegroundColor Green 
            }} catch {{
                if ($_.Exception.Message -match 'already on the permission entry list') {{
                    Write-Host "! FullAccess existe para o usuario: $usuario" -ForegroundColor Yellow
                }} else {{ throw }}
            }} 
            
            Write-Host "Concedendo SendAs a $usuario no shared $sharedSmtp " -ForegroundColor Cyan;
            try {{ 
                Add-RecipientPermission -Identity $sharedSmtp -Trustee $usuario `
                  -AccessRights SendAs -Confirm:$false -ErrorAction Stop
                Write-Host "✓ SendAs concedido" -ForegroundColor Green
            }} catch {{ 
                if ($_.Exception.Message -match 'already has SendAs rights') {{ 
                    Write-Host "! SendAs existe o usuário: $usuario" -ForegroundColor Yellow
                }} else {{ throw }} 
            }} 
            
            # Validações rápidas
            Write-Host "`n=== Validação de permissões no shared ===" -ForegroundColor Cyan
            Write-Host "FullAccess:" -ForegroundColor Cyan
            Get-MailboxPermission -Identity $sharedSmtp | 
              Where-Object {{ $_.User -notlike 'NT AUTHORITY*' -and -not $_.IsInherited }} | 
              Select-Object User,AccessRights,IsInherited | Format-Table -AutoSize

            Write-Host "`nSendAs:" -ForegroundColor Cyan
            Get-RecipientPermission -Identity $sharedSmtp | 
              Where-Object {{ $_.Trustee -notlike 'NT AUTHORITY*' -and -not $_.IsInherited }} | 
              Select-Object Trustee,AccessRights,IsInherited | Format-Table -AutoSize

            # 5) Desconectar
            Disconnect-ExchangeOnline -Confirm:$false
        """

        resultado = self.init_conectar_exchange.run_spinner(
            str(comando_shell).strip(),
            'Conectando ao office 365... '
        )

        return resultado

    def verificando_permissoes(self, grupo_pesquisa: str):

        comando_shell = rf"""
        
        $sharedSmtp = "{grupo_pesquisa}"
        
        Import-Module ExchangeOnlineManagement -ErrorAction Stop; 
            Connect-ExchangeOnline -AppId '{os.getenv('AppId')}' `
              -Organization '{os.getenv('Organization')}' `
              -CertificateFilePath 'C:\\Temp\\ExchangeOnlineAutomation.pfx' `
              -CertificatePassword (ConvertTo-SecureString '{os.getenv('PASSWORD')}' -AsPlainText -Force) `
              -ShowBanner:$false; 
              
        # Funcionando
        # ----------------------------------------------------------------------------------------------
        
        # Permissões de mailbox (EXO V3)
        
        # Permissões de 'FullAccess' (quem pode enviar como o mailbox) 
        $fullAccess = Get-MailboxPermission -Identity $sharedSmtp | 
          Where-Object {{ -not $_.IsInherited -and $_.User -notlike 'NT AUTHORITY*' -and $_.User -ne 'SELF' }} | 
          Select-Object @{{ n='Principal';e={{$_.User}} }}, @{{n='Access';e={{'FullAccess'}} }}, Deny, IsInherited 
        
        # Permissões de "Send As" (quem pode enviar como o mailbox) 
        $sendAs = Get-RecipientPermission -Identity $sharedSmtp | 
          Where-Object {{ -not $_.IsInherited -and $_.Trustee -notlike 'NT AUTHORITY*' }} | 
          Select-Object @{{ n='Principal';e={{$_.Trustee}} }}, @{{n='Access';e={{'SendAs'}} }}, `
          @{{ n='Deny';e={{$false}} }}, IsInherited 
          
        $both = @(); $both += $fullAccess; $both += $sendAs
        $both | ConvertTo-Json -Depth 4
        
        Disconnect-ExchangeOnline -Confirm:$false | Out-Null
        """

        resultado = self.init_conectar_exchange.run_spinner(
            str(comando_shell).strip(),
            'Verificando permissão ao office 365... '
        )

        saida_json = json.loads(resultado)
        return saida_json

    def concedendo_permissoes_shared(self, nome_grupo, email_permissao):

        comando_shell = rf"""
        # 1) Importa e conecta ao 365;
        
        $sharedSmtp = "{nome_grupo}"
        $usuario = "{email_permissao}"
        
        Import-Module ExchangeOnlineManagement -ErrorAction Stop;
        Connect-ExchangeOnline -AppId '{os.getenv('AppId')}' `
          -Organization '{os.getenv('Organization')}' `
          -CertificateFilePath '{os.getenv('PATH_CERTIFICADO')}' `
          -CertificatePassword (ConvertTo-SecureString '{os.getenv('PASSWORD')}' -AsPlainText -Force) `
          -ShowBanner:$false;
        # ----------------------------------------------------------------------------------------------
            
        Write-Host ">> Concedendo FullAccess a $usuario no shared $sharedSmtp ..." -ForegroundColor Cyan 
        try {{
            Add-MailboxPermission -Identity $sharedSmtp `
            -User $usuario -AccessRights FullAccess -AutoMapping:$true -ErrorAction Stop 
            Write-Host "✓ FullAccess concedido" -ForegroundColor Green 
        }} catch {{
            if ($_.Exception.Message -match 'already on the permission entry list') {{
                Write-Host "! FullAccess existe para o usuario: $usuario" -ForegroundColor Yellow
            }} else {{ throw }}
        }} 
        
        Write-Host "Concedendo SendAs a $usuario no shared $sharedSmtp " -ForegroundColor Cyan;
        try {{ 
            Add-RecipientPermission -Identity $sharedSmtp -Trustee $usuario `
              -AccessRights SendAs -Confirm:$false -ErrorAction Stop
            Write-Host "✓ SendAs concedido" -ForegroundColor Green
        }} catch {{ 
            if ($_.Exception.Message -match 'already has SendAs rights') {{ 
                Write-Host "! SendAs existe o usuário: $usuario" -ForegroundColor Yellow
            }} else {{ throw }} 
        }} 
        """

        resultado = self.init_conectar_exchange.run_spinner(
            str(comando_shell).strip(),
            f'Atribuindo permissão ao grupo {grupo}... '
        )

        return resultado

    def compartilhando_caixa_calendario(self, calendario_shared, usuario,  permissao):

        comando_shell = rf"""
        # 1) Importa e conecta ao 365;
            Import-Module ExchangeOnlineManagement -ErrorAction Stop;
            Connect-ExchangeOnline -AppId '{os.getenv('AppId')}' `
              -Organization '{os.getenv('Organization')}' `
              -CertificateFilePath '{os.getenv('PATH_CERTIFICADO')}' `
              -CertificatePassword (ConvertTo-SecureString '{os.getenv('PASSWORD')}' -AsPlainText -Force) `
              -ShowBanner:$false;
            # ----------------------------------------------------------------------------------------------
            # Funcionando 
            
        # 2) Conceder Editor
        Add-MailboxFolderPermission -Identity "{calendario_shared}:\Calendário" -User "{usuario}" -AccessRights {permissao}
        
        # 3) Ajustar permissão existente
        Set-MailboxFolderPermission -Identity "{calendario_shared}:\Calendário" -User "{usuario}" -AccessRights {permissao}

        """
        
        resultado = self.init_conectar_exchange.run_spinner(
            comando_shell,
            'Verificando seu calendário... '
        )
        return resultado

    def _instalando_modulo(self):
        comando_shell = rf"Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force"
        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Conectando ao office 365... ')
        return resultado

    def _verif_calendarios(self, email: str):
        """
        Lista as permissões da pasta de calendário do mailbox {email} no Exchange Online:

        Ex:
        Usuário com calendário em PT‑BR: joao@contoso.com:\Calendário
        Usuário com calendário em EN: joao@contoso.com:\Calendar

        """

        comando_shell = rf"""
        Import-Module ExchangeOnlineManagement -ErrorAction Stop; 
            Connect-ExchangeOnline -AppId '{os.getenv('AppId')}' `
              -Organization '{os.getenv('Organization')}' `
              -CertificateFilePath 'C:\\Temp\\ExchangeOnlineAutomation.pfx' `
              -CertificatePassword (ConvertTo-SecureString '{os.getenv('PASSWORD')}' -AsPlainText -Force) `
              -ShowBanner:$false;
        # Funcionando
        # ----------------------------------------------------------------------------------------------
                         
        Get-MailboxFolderPermission -Identity '{email}:\Calendário'
        
        # Desconecta do exchange
        Disconnect-ExchangeOnline -Confirm:$false | Out-Null
        """

        resultado = self.init_conectar_exchange.run_spinner(
            comando_shell,
            'Verificando seu calendário... '
        )

        return resultado

    def analisando_thumbprint(self):
        """
        Objetivo: verificar se o certificado PFX instalado (que você usa no Connect-ExchangeOnline e no MSAL
        para o Graph) está realmente no repositório correto do Windows do usuário que está executando o script,
        e confirmar o Thumbprint e se a chave privada está presente.

        Uso típico no seu fluxo:

        Antes de conectar ao EXO por certificado ou gerar token MSAL, você confere se o cert está visível em
        CurrentUser\My. Copia/valida o Thumbprint e HasPrivateKey=True.
        Se não aparecer, normalmente o PFX foi importado no repositório errado (ex.: LocalMachine\My) ou
        sem chave exportável; ou o processo está rodando sob uma conta diferente.

        >> Get-ChildItem Cert:\CurrentUser\My: Lista todos os certificados armazenados no repositório Pessoal do
        Usuário Atual (Store: CurrentUser\My).
        * Essa “unidade” Cert:\ é o provedor de certificados do PowerShell.
        * Cada item retornado é um certificado (objeto X509Certificate2).

        >> Select-Object Subject, Thumbprint, HasPrivateKey; Extrai apenas 3 propriedades úteis de cada certificado:
        * Subject → para quem o certificado foi emitido (DN).
        * Thumbprint → impressão digital (hash) única do certificado; é o valor que você costuma usar para
        identificar/casar o certificado em scripts.
        * HasPrivateKey → indica se a chave privada está presente (⚠️ necessária para assinar/obter tokens
        com MSAL ou conectar no EXO por certificado).

        >> Format-List;
        * Formata a saída como lista (uma entrada por certificado, em múltiplas linhas).
        * Observação importante para automação: Format-* (ex.: Format-List, Format-Table) serve só para visualização.
        Se você vai consumir no Python, é melhor não formatar ou converter para JSON
        """

        comando_shell = (
            'Get-ChildItem Cert:\CurrentUser\My |'
            'Select-Object Subject, Thumbprint, HasPrivateKey |'
            'Format-List'
        )

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Analisando o Thumbprint... ')
        return resultado

    def criar_novo_certificado(self):
        """
        O certificado pode ser usado em outras aplicações, porém caso seja o primeiro para acessar o office 365 é
        preciso que seja carregado no site do Entra ID.
        """

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

if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    while True:
        print()
        print(
            '[1] Criar um e-mail Shared e atribuir permissão para um  \n'
            '[2] Verificar as permissões de um grupo \n'
            '[3] Conceder permissões de um grupo para um determinado usuário \n'
            '[4] Analisar "Thumbprint" e "HasPrivateKey" \n'
            '[5] Analisar Calendário do usuário \n'
            '[6] Compartilhar calendário \n'
            
            '[0] Sair\n'
        )
        print('---' * 20)
        try:
            resposta = int(input('Escolha uma opção: '))
        except ValueError:
            print()
            print('---' * 20)
            print('Valor inválido')
            continue

        if resposta == 1:
            print()
            print('Criar e conceder permissão para novo grupo Exchange')
            print('---' * 20)
            print()

            grupo = input('Digite o Grupo para adicionar: ')
            email = input('Conceder permissão para o e-mail: ')

            resultando_conexao = init_obj_calendar.chamando_obj_conexao(grupo, email)

            for item in resultando_conexao:
                print(item)

        elif resposta == 2:
            print()
            print('Analisar permissão de um grupo')
            print('---' * 20)
            print()

            # grupo_pesquisa = input('Digite o Grupo para pesquisa: ')
            grupo_pesquisa = os.getenv('ORGANIZADOR_GRUPO')
            resultado_permissao = init_obj_calendar.verificando_permissoes(grupo_pesquisa)

            print()
            dict_permissao_grupo = defaultdict(list)

            for item in resultado_permissao:

                if item['Access'] == 'FullAccess':
                    dict_permissao_grupo['FullAccess'].append(item['Principal'])

                elif item['Access'] == 'SendAs':
                    dict_permissao_grupo['SendAs'].append(item['Principal'])

            for k, v in dict_permissao_grupo.items():
                print(k, v)

        elif resposta == 3:
            print()
            print('Conceder permissão para um grupo Exchange')
            print('---' * 20)
            print()

            grupo = input('Digite o Grupo para adicionar: ')

            print()
            email = input('Conceder permissão para o e-mail: ')
            resultando_processo = init_obj_calendar.concedendo_permissoes_shared(grupo, email)

        elif resposta == 4:
            response = init_obj_calendar.analisando_thumbprint()
            print(response)

        elif resposta == 5:
            print()
            print('Criar e conceder permissão para novo grupo Exchange')
            print('---' * 20)
            print()

            # email = input('Digital seu e-mail: ')
            email = os.getenv('ORGANIZADOR_TESTE')
            response = init_obj_calendar._verif_calendarios(email)
            print(response)

        elif resposta == 6:
            print()
            print('Criar e conceder permissão para novo grupo Exchange')
            print('---' * 20)
            print()

            # (Editor, Author, Reviewer
            # email = input('Digital seu e-mail: ')
            # tipo_acesso = input('Digital seu e-mail: ')

            email = os.getenv('ORGANIZADOR_TESTE')
            tipo_acesso = 'Editor'

            response = init_obj_calendar.compartilhando_caixa_calendario(email, tipo_acesso)
            print(response)

        elif resposta == 0:
            print()
            print('Finalizando o programa...')
            print('---' * 20)
            sleep(2)
        else:
            print()
            print('---' * 20)
            input('Opção Invalida. Enter para continuar...')

