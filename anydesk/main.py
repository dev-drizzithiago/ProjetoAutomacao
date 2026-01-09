import os
import shutil
import subprocess
from platform import system
from time import sleep

import ctypes
import sys

from pathlib import Path

path_home = Path.home()
pasta_download_onedrive = Path(path_home, 'Downloads')
path_file_name = os.path.join(pasta_download_onedrive, 'AnyDesk.exe')


def verificar_elevacao():
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
    return True

class GeranciadorDePacotes:
    def __init__(self):
        pass

    # def procurar_pacote_anydesk(self):
    #
    #     print('Procurando por um pacote AnyDesk instalado')
    #
    #     pacote = 'anydesk'
    #     comando_shell = f"winget search {pacote}"
    #
    #     response_powershell = subprocess.run(
    #         ['powershell', '-Command', comando_shell],
    #         text=True, capture_output=True
    #     )
    #     resultado_busca = response_powershell.stdout
    #
    #     print(resultado_busca)
    #
    # def instalar_pacote_anydesk(self):
    #     comando_shell = (
    #         f'Start-Process "{path_file_name}" --silent'
    #     )
    #
    #     response_powershell = subprocess.run(
    #         ['powershell', '-Command', comando_shell],
    #         text=True, capture_output=True
    #     )
    #
    #     print(response_powershell.stdout)
    #
    # def desinstalar_pocotes(self):
    #     pacote = 'AnyDesk.AnyDesk'
    #     comando_shell = f"winget uninstall --id {pacote} --silent"
    #
    #     response_powershell = subprocess.run(
    #         ['powershell', '-Command', comando_shell],
    #         text=True, capture_output=True
    #     )
    #
    #     print(response_powershell.stdout)

    def remover_processo(self):
        os.system('cls')
        print()
        print('Fechando Processo do Anydesk, aguarde...')
        print('---' * 30)
        print()
        comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue | Stop-Process -Force"
        # comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )
        if response_powershell.returncode == 0:
            print('Processo finalizado, aguardando próximo processo...')

    def removendo_config_anydesk(self):
        os.system('cls')
        print()
        print('Removendo Configurações do Anydesk')
        print('---' * 30)
        print()
        caminho_confi_anydesk = r"C:\ProgramData\AnyDesk"

        if os.path.exists(caminho_confi_anydesk):
            shutil.rmtree(caminho_confi_anydesk)

        print('Configuração removida, aguardando próximo processo...')
        sleep(3)

    def abrir_processo(self):
        os.system('cls')
        print()
        print('Abrindo o AnyDesk, aguarde...')
        print('---' * 30)
        print()
        caminho_app = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
        comando_shell = fr'Start-Process "{caminho_app}" -WindowStyle Minimized'

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

if __name__ == '__main__':

    if verificar_elevacao():
        obj_pacote = GeranciadorDePacotes()
        obj_pacote.remover_processo()
        sleep(5)
        obj_pacote.removendo_config_anydesk()
        sleep(5)
        obj_pacote.abrir_processo()

        print()
        input('Aperte ENTER para continuar...')
        os.system('cls')

        for contagem in range(5, 0, -1):
            print()
            print()
            print('Finalizando em:', end=' ')
            print(contagem)
            sleep(1)
            os.system('cls')
