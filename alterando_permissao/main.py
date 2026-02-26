from dotenv import load_dotenv
from os import getenv
import os

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

    def conexao_grupo_gti(self):
        comando_shell = rf"""
            Import-Module ExchangeOnlineManagement -ErrorAction Stop;
                Connect-ExchangeOnline -AppId '{os.getenv('AppId')}' `
                  -Organization '{os.getenv('Organization')}' `
                  -CertificateFilePath 'C:\\Temp\\ExchangeOnlineAutomation.pfx' `
                  -CertificatePassword (ConvertTo-SecureString '{os.getenv('PASSWORD')}' -AsPlainText -Force) `
                  -ShowBanner:$false; 
                  
            # Funcionando
            # ----------------------------------------------------------------------------------------------

            # Parâmetros
            $groupNameOrSmtp = "{os.getenv('NOME_GRUPO')}"     # pode ser nome do Team ou smtp do grupo

            # Resolve o Microsoft 365 Group
            $grp = Get-UnifiedGroup -Identity $groupNameOrSmtp -ErrorAction Stop; 
            
            # Pegue o SMTP do GroupMailbox
            $groupSmtp = $grp.PrimarySmtpAddress;
            
            Get-EXORecipient -PrimarySmtpAddress $groupSmtp -RecipientTypeDetails GroupMailbox | 
            Format-Table DisplayName,PrimarySmtpAddress,RecipientTypeDetails
                
            # $principal = "{os.getenv('ORGANIZADOR_GRUPO')}" `
            # $calendarIdentity {os.getenv('ORGANIZADOR_GRUPO')}:\Calendar `
            # try {{
            #     Set-MailboxFolderPermission `
            #     -Identity $calendarIdentity `
            #     -User $principal `
            #     -AccessRights Editor `
            #     -ErrorAction Stop
            # }} catch {{
            #     if ($_.Exception.Message -match "Cannot find an existing permission entry") {{
            #         Add-MailboxFolderPermission `
            #         -Identity $calendarIdentity `
            #         User $principal `
            #         -AccessRights Editor ´
            #         -ErrorAction Stop
            #     }} elseif ($_.Exception.Message -match "already has") {{
            #         # já possui a entrada — segue
            #     }} else {{
            #         throw
            #     }}
            # }}
            
            Get-EXOMailboxFolderPermission -Identity $calendarIdentity | Format-Table -AutoSize
        """

        resultado = self.init_conectar_exchange.run_spinner(
            str(comando_shell).strip(),
            'Conectando ao office 365... '
        )

        return resultado

    def chamando_obj_conexao(self):
        self.init_conectar_exchange = ProcessoRun()

        comando_shell = rf"""\
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
            $shared = Get-Mailbox -Identity {os.getenv('ORGANIZADOR_GRUPO')} -ErrorAction SilentlyContinue           
            
            if (-not $shared) {{
                Write-Host "Criando mailbox compartilhado {os.getenv('ORGANIZADOR_GRUPO')}" `
                -ForegroundColor Cyan
                New-Mailbox -Shared `
                    -Name "{os.getenv('NOME_GRUPO')}" `
                    -PrimarySmtpAddress "{os.getenv('ORGANIZADOR_GRUPO')}" `
                    -ErrorAction Stop
            }} else {{
                Write-Host ">> Mailbox compartilhado já existe: {os.getenv('ORGANIZADOR_GRUPO')}" `
                -ForegroundColor Yellow
            }}

            # 2° etapa; concedendo permissões e testes
            # 3) Conceder permissões (FullAccess + SendAs) aos membros listados no CSV;

            if (-not $sharedSmtp -or -not $usuario) {{
                throw "Defina ORGANIZADOR_GRUPO (shared SMTP) e USUARIO_TESTE (UPN)."
            }}

            Write-Host "Concedendo FullAccess a $usuario no shared $sharedSmtp ..." -ForegroundColor Cyan

            try {{
                Add-MailboxPermission -Identity $sharedSmtp `
                -User "{os.getenv('ORGANIZADOR_PARTICULAR')}" `
                -AccessRights FullAccess `
                -AutoMapping:$true `
                -ErrorAction Stop
                Write-Host "✓ FullAccess concedido" `
                -ForegroundColor Green
            }} catch {{
                if ($_.Exception.Message -match 'already on the permission entry list') {{
                    Write-Host "ℹ FullAccess já existia" -ForegroundColor Yellow
                }} else {{ throw }}
            }}
            
            Write-Host "Concedendo SendAs a "{os.getenv('ORGANIZADOR_PARTICULAR')}" no shared $sharedSmtp ..." `
            -ForegroundColor Cyan
            try {{
                Add-RecipientPermission -Identity $sharedSmtp `
                -Trustee "{os.getenv('ORGANIZADOR_PARTICULAR')}" `
                -AccessRights SendAs `
                -ErrorAction Stop
                Write-Host "✓ SendAs concedido" `
                -ForegroundColor Green
            }} catch {{
                if ($_.Exception.Message -match 'already has SendAs rights') {{
                    Write-Host "ℹ SendAs já existia" -ForegroundColor Yellow
                }} else {{ throw }}
            }}            
            
            # Validações rápidas
            Write-Host "`n=== Validação de permissões no shared ===" -ForegroundColor Cyan
            Write-Host "FullAccess:" -ForegroundColor Cyan
            Get-MailboxPermission -Identity "{os.getenv('ORGANIZADOR_GRUPO')}" |
              Where-Object {{ $_.User -notlike 'NT AUTHORITY*' -and -not $_.IsInherited }} |
              Select-Object User,AccessRights,IsInherited | Format-Table -AutoSize
            
            Write-Host "`nSendAs:" -ForegroundColor Cyan
            Get-RecipientPermission -Identity "{os.getenv('ORGANIZADOR_GRUPO')}" |
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

    def _instalando_modulo(self):
        comando_shell = rf"Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force"
        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Conectando ao office 365... ')
        return resultado

    def _verif_calendarios(self):

        comando_shell = rf"Get-MailboxFolderPermission -Identity '{os.getenv('MAIL_CONEXAO')}:\Calendário'"

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Conectando ao office 365... ')

        print(resultado)

    def editando_calendario(self):

        # Dar acesso de Editor a todos da organização (cuidado!)
        # Isso torna o calendário do organizador editável por qualquer usuário interno.
        # Use apenas se for realmente a intenção:
        comando_shell = (
            rf"Add - MailboxFolderPermission - Identity 'organizador@empresa.com:\Calendar' `"
            rf"-User Default -AccessRights Editor"
        )

        # # Crie/Use um grupo de segurança ou de distribuição com os convidados da reunião e conceda Editor
        # comando_shell = (
        #     rf"Add - MailboxFolderPermission - Identity 'organizador@empresa.com:\Calendar' `"
        #     rf"-User 'Grupo-Convidados@empresa.com' -AccessRights Editor"
        # )

        #Tornar alguém delegado com poder de edição Delegados recebem comportamento especial
        # (encaminhamento de convites, etc.):
        # -SharingPermissionFlags Delegate adiciona como delegado do calendário do usuário.
        # comando_shell = (
        #     "Add - MailboxFolderPermission - Identity 'organizador@empresa.com:\Calendar' `"
        #     "-User 'assistente@empresa.com' -AccessRights Editor -SharingPermissionFlags Delegate"
        # )

        # Ajustar uma permissão que já existe (em vez de adicionar)
        # comando_shell = (
        #     "Set - MailboxFolderPermission - Identity 'organizador@empresa.com:\Calendar' `"
        #     "-User 'usuario@empresa.com' -AccessRights Editor"
        # )

        # comando_shell = (
        #     # Conferir
        #     "Get - MailboxFolderPermission - Identity 'organizador@empresa.com:\Calendar' "
        #
        #     # Remover a permissão de alguém
        #     "Remove - MailboxFolderPermission - Identity 'organizador@empresa.com:\Calendar' "
        #     "-User 'usuario@empresa.com' - Confirm "
        # )

        # comando_shell = "Disconnect-ExchangeOnline"

        resultado = self.init_conectar_exchange.run_spinner(comando_shell, 'Conectando ao office 365... ')
        return resultado

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

    def _verificar_certificados(self):
        # Verifica o certificado da máquina.
        # comando_shell = (
        #     'Get-ChildItem Cert:\LocalMachine\My '
        # )

        # Verifica o certificado do usuário
        comando_shell = (
                'Get - ChildItem Cert:\CurrentUser\My '
        )

if __name__ == '__main__':
    init_obj_calendar = AlterarPermissaoReunioes()
    while True:
        print()
        print(
            '[1] Conectar\n'
            '[2] Verificar Modulo\n'
            '[3] Analisar ThumpPrint\n'
            '[4] Criar novo Certificado\n'
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
            init_obj_calendar.criar_novo_certificado()

        else:
            print()
            print('---' * 20)
            input('Opção Invalida. Enter para continuar...')

