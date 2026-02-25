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

    def remover_processo(self):
        os.system('cls')
        print()
        print('Fechando processo do Anydesk, aguarde...')
        print('---' * 30)
        print()
        comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue | Stop-Process -Force"
        # comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )
        if response_powershell.returncode == 0:
            print('Processo finalizado, próximo ...')

    def removendo_config_anydesk(self):
        os.system('cls')
        print()
        print('Configurações do Anydesk no sistema sendo removido...')
        print('---' * 30)
        print()
        caminho_confi_anydesk = r"C:\ProgramData\AnyDesk"

        if os.path.exists(caminho_confi_anydesk):
            shutil.rmtree(caminho_confi_anydesk)

        print('Configuração removida, próximo reabrindo Anydesk...')

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

        sleep(3)
        obj_pacote.removendo_config_anydesk()

        sleep(3)
        obj_pacote.abrir_processo()

        sleep(3)
        obj_pacote.remover_processo()

        sleep(3)
        obj_pacote.abrir_processo()

        print()
        print('Finalizando processo...')
        sleep(3)

        for contagem in range(5, 0, -1):
            print()
            print()
            print('Finalizando em:', end=' ')
            print(contagem)
            sleep(1)
            os.system('cls')
