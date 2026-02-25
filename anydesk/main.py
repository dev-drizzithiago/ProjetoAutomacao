import os
import shutil
import subprocess
from time import sleep

from proccess_spinner import ProcessoRun

import ctypes
import sys

from pathlib import Path

path_home = Path.home()
pasta_download_onedrive = Path(path_home, 'Downloads')
file_name = os.path.join(pasta_download_onedrive, 'AnyDesk.exe')
path_appdata = Path(path_home, 'AppData', 'Roaming', 'AnyDesk')


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
        self.init_spinner_class = None

        self.init_spinner_class = ProcessoRun()

    def remover_processo(self, mensagem):
        comando_shell = (
            "Get-Process -Name 'AnyDesk*' "
            "-ErrorAction SilentlyContinue | "
            "Stop-Process -Force "
            )

        self.init_spinner_class.run_spinner(comando_shell, mensagem)


    def removendo_config_anydesk(self):
        print()
        print('Configurações do Anydesk no sistema sendo removido...')
        print('---' * 30)
        caminho_confi_anydesk = r"C:\ProgramData\AnyDesk"

        # Verifica se a pasta existe, se for True tudo é removido.
        if os.path.exists(caminho_confi_anydesk):
            shutil.rmtree(caminho_confi_anydesk)
        else:
            print()
            print('---' * 30)
            print('Pasta não existe.')
            sleep(5)

    def abrir_processo(self, mensagem):
        caminho_app = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
        comando_shell = fr'Start-Process "{caminho_app}" -WindowStyle Minimized'
        self.init_spinner_class.run_spinner(comando_shell, mensagem)

if __name__ == '__main__':

    if verificar_elevacao():
        obj_pacote = GeranciadorDePacotes()

        # Para iniciar, o anydesk é fechado
        obj_pacote.remover_processo('Processo do Anydesk sendo finalizado, aguarde...')

        # Remove as configurações do anydesk.
        sleep(3)
        resp_processo = obj_pacote.removendo_config_anydesk()

        # Abre o processo pela primeira vez, depois do reset
        sleep(3)
        obj_pacote.abrir_processo('reAbrindo o AnyDesk, aguarde...')

        # Geralmente o anydesk não pega de primeira o ID. É preciso fechar e reabri-lo
        sleep(3)
        obj_pacote.remover_processo('Testando Anydesk, aguarde...')

        # Abre o processo pela segunda vez.
        sleep(3)
        obj_pacote.abrir_processo('Finalizando o teste, aguarde...')

        sleep(5)
        os.system('cls')

        for contagem in range(5, 0, -1):
            print()
            print()
            print('Finalizando em:', end=' ')
            print(contagem)
            sleep(1)
            os.system('cls')
