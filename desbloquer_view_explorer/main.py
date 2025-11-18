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
    comando_powershell_desbloquear_MOTW = f"Get-ChildItem -Path {home_usuario} -Recurse -Include '*.pdf' | Unblock-File"
    comando_powershell_bloquear_MOTW = f"Get-ChildItem -Path {home_usuario} -Recurse -Include '*.pdf' | Block-File"
    comando_powershell_reiniciar_explorer = 'taskkill /f /im explorer.exe; Start-Process explorer.exe'
    comando_powershell_registro_windows = f"reg add \"{reg_key_local_machine}\" /v ScanWithAntiVirus /t REG_DWORD /d 1 /f"

    def desbloquear_view_windows(self):
        try:
            print('Iniciando desbloqueio, processo pode levar alguns minutos\n')
            result_shell = run(
                ['powershell', "-Command", self.comando_powershell_desbloquear_MOTW],
                shell=True,
                capture_output=True,
                check=True
            )

            print('Reiniciando o Windows Explorer.exe para aplicar as mudanças')
            sleep(5)
            run(
                ['powershell', '-Command', self.comando_powershell_reiniciar_explorer],
                shell=True,
                capture_output=True,
                check=True
            )
            print("Windows Explorer reiniciado. Verifique agora o Painel de Visualização.")

        except CalledProcessError as error:
            print(f'\n Erro ao executar o PowerShell: ', error)
            print(f'Stdout: {error.stdout} ')
            print(f'Stderr: {error.stderr} ')
            print('Verifique se o perfil foi executado como administrador.')
        except Exception as error:
            print('Ocorreu um erro inesperado:', error)

    def bloquear_view_windows(self):
        try:
            print('Iniciando desbloqueio, processo pode levar alguns minutos\n')
            result_shell = run(
                ['powershell', "-Command", self.comando_powershell_bloquear_MOTW],
                shell=True,
                capture_output=True,
                check=True
            )
            print('Reiniciando o Windows Explorer.exe para aplicar as mudanças')
            sleep(5)
            run(
                ['powershell', '-Command', self.comando_powershell_reiniciar_explorer],
                shell=True,
                capture_output=True,
                check=True
            )
            print("Windows Explorer reiniciado. Verifique agora o Painel de Visualização.")

        except CalledProcessError as error:
            print(f'\n Erro ao executar o PowerShell: ', error)
            print('Verifique se o perfil foi executado como administrador.')
        except Exception as error:
            print('Ocorreu um erro inesperado:', error)

if __name__ == '__main__':

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        try:
            run([sys.executable] + sys.argv, shell=False, check=True, ver='RunAs')
        except Exception as error:
            print('Não foi possível elevar o processo; ', error)

    obj_desbloqueio = DesbloqueioViewWindows()
    print(
        "[ 1 ] Desbloquear visualização do Windows"
        "[ 2 ] Bloquear visualização do Windows"
    )
    resposta = int(input("Escolha uma opção: "))
    if resposta == 1:
        obj_desbloqueio.desbloquear_view_windows()
    elif resposta == 2:
        obj_desbloqueio.bloquear_view_windows()

