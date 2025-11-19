"""
Detalhamento do Comando
Este comando combina duas ações essenciais, separadas por um ponto e vírgula (;):

taskkill /f /im explorer.exe:

taskkill: É o utilitário do Windows usado para encerrar processos em execução.

/f: Força o encerramento do processo (fundamental para garantir que o processo seja finalizado imediatamente).

/im explorer.exe: Especifica a imagem do processo a ser encerrado, que é o explorer.exe (o Explorador de Arquivos/Shell
do Windows).

Start-Process explorer.exe:

Start-Process: É o cmdlet do PowerShell usado para iniciar um novo processo.

explorer.exe: Inicia uma nova instância do Explorador de Arquivos.

***********************************************************************************************************************
Get-ChildItem: Lista os arquivos.

-Recurse: Busca em todas as subpastas.

-Include '*.pdf': Este é o filtro. Ele garante que, dos arquivos encontrados recursivamente, apenas aqueles com a extensão .pdf sejam passados para a próxima etapa.

Unblock-File: Remove a "Marca da Web" (MOTW) somente dos arquivos .pdf filtrados
"""

from subprocess import run, CalledProcessError
from pathlib import Path
from time import sleep
import ctypes
import sys

class DesbloqueioViewWindows:

    home_usuario = Path.home()
    reg_key_local_machine = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Attachments'

    # Comando PowerShell para DESBLOQUEAR (remover MOTW) todos os PDFs no HOME
    comando_powershell_desbloquear_MOTW = (
            f"Get-ChildItem -Path '{home_usuario}' -Recurse -Include '*.pdf' | Unblock-File"
        )

    # Comando PowerShell para BLOQUEAR (adicionar MOTW) todos os PDFs no HOME
    comando_powershell_bloquear_MOTW = (rf'''
            Get-ChildItem -Path "{home_usuario}" -Filter *.pdf -Recurse -File | ForEach-Object {{
                $content = "[ZoneTransfer]`nZoneId=3"
                Set-Content -Path $_.FullName -Stream Zone.Identifier -Value $content -Encoding ASCII
            }}
        ''')

    comando_powershell_reiniciar_explorer = r'''
            taskkill /f /im explorer.exe; Start-Process explorer.exe
        '''

    comando_powershell_registro_windows_desbloqueio = (  # ex.: permitir verificação (exemplo)
        rf'reg add "{reg_key_local_machine}" /v ScanWithAntiVirus /t REG_DWORD /d 1 /f'
    )

    comando_powershell_registro_windows_bloqueio = (  # ex.: voltar ao padrão/sugerido pela sua política
        rf'reg add "{reg_key_local_machine}" /v ScanWithAntiVirus /t REG_DWORD /d 1 /f'
    )

    ## DESBLOQUEIA NOVAMENTE O VISUALIZADOR
    def desbloquear_view_windows(self):
        try:
            run(['powershell', '-Command', self.comando_powershell_desbloquear_MOTW],
                shell=True,
                check=True,
                capture_output=True
                )
            sleep(5)
            return True
        except CalledProcessError as error:
            print(f'\n Erro ao executar o PowerShell: ', error)
            print(f'Stdout: {error.stdout} ')
            print(f'Stderr: {error.stderr} ')
            print('Verifique se o perfil foi executado como administrador.')
            input('Aperte [ENTER] para finalizar')
            return False
        except Exception as error:
            print('Ocorreu um erro inesperado:', error)
            input('Aperte [ENTER] para finalizar')
            return False

    ## BLOQUEIA NOVAMENTE O VISUALIZADOR
    def bloquear_view_windows(self):
        try:
            print('Iniciando desbloqueio, processo pode levar alguns minutos\n')
            result_shell = self._run_powershell(self.comando_powershell_registro_windows_desbloqueio)
            print("✅ Bloqueio de arquivos PDF (MOTW) concluído com sucesso.")
            if result_shell.stdout:
                print(result_shell.stdout)
            if result_shell.stderr:
                print('[PowerShell avisos]:', result_shell.stderr)

            sleep(5)
            return True

        except CalledProcessError as error:
            print(f'\n Erro ao executar o PowerShell: ', error)
            print('Verifique se o perfil foi executado como administrador.')
            input('Aperte [ENTER] para finalizar')
            return False

        except Exception as error:
            print('Ocorreu um erro inesperado:', error)
            input('Aperte [ENTER] para finalizar')
            return False

    ## Modifica o registro do windows.
    def configurar_registro(self, valor_entrada):
        try:
            print('Iniciando desbloqueio, processo pode levar alguns minutos\n')

            result_shell = self._run_powershell(self.comando_powershell_registro_windows_desbloqueio)
            print('Registro modificado.')
            if result_shell.stdout:
                print(result_shell.stdout)
            if result_shell.stderr:
                print('[PowerShell avisos]:', result_shell.stderr)

            sleep(5)
            return True

        except CalledProcessError as error:
            print(f'\n Erro ao executar o PowerShell: ', error)
            print(f'Stdout: {error.stdout} ')
            print(f'Stderr: {error.stderr} ')
            print('Verifique se o perfil foi executado como administrador.')
            sleep(5)
            return False

        except Exception as error:
            print('Ocorreu um erro inesperado:', error)
            input('Aperte [ENTER] para finalizar')
            sleep(5)
            return False

    ## Reinicia o explorer do windows para aplicar as mudanças
    def reiniciar_explorer(self):
        print('Reiniciando o Windows Explorer.exe para aplicar as mudanças')
        sleep(5)
        run(
            ['powershell', '-Command', self.comando_powershell_reiniciar_explorer],
            capture_output=True,
            shell=True,
            check=True
        )
        print("Windows Explorer reiniciado. Verifique agora o Painel de Visualização.")


if __name__ == '__main__':

    ## Verifica se o app esta sendo executado com usuário elevado.
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    ## Se o app não foi elevado vai abrir a janela para solicita as credinciais de administrador.
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None,  # handle (não usado)
            "runas",  # O verbo que força o UAC
            sys.executable,  # O arquivo a ser executado (o interpretador Python)
            " ".join(sys.argv),  # Os argumentos (o nome do seu script)
            None,  # diretório de trabalho
            1  # mostra a janela
        )
        sys.exit(0)  # Sai do script original

    obj_desbloqueio = DesbloqueioViewWindows()
    print(
        "[ 1 ] Desbloquear visualização do Windows\n"
        "[ 2 ] Bloquear visualização do Windows\n"
    )

    comando_desbloqueio_registro = obj_desbloqueio.comando_powershell_registro_windows_desbloqueio
    comando_bloqueio_registro = obj_desbloqueio.comando_powershell_registro_windows_bloqueio

    resposta = int(input("Escolha uma opção: "))
    if resposta == 1:
        process_finalizado = obj_desbloqueio.desbloquear_view_windows()
        if process_finalizado:
            obj_desbloqueio.configurar_registro(comando_desbloqueio_registro)
            obj_desbloqueio.reiniciar_explorer()
    elif resposta == 2:
        process_finalizado = obj_desbloqueio.bloquear_view_windows()
        if process_finalizado:
            obj_desbloqueio.configurar_registro(comando_bloqueio_registro)
            obj_desbloqueio.reiniciar_explorer()


