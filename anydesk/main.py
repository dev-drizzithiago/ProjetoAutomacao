import os
import subprocess
from time import sleep

import ctypes
import sys

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

    def procurar_pacotes(self):
        pacote = ' anydesk'
        comando_shell = f"winget search {pacote}"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)

    def desinstalar_pocotes(self):
        pacote = 'AnyDeskSoftwareGmbH.AnyDesk'
        comando_shell = f"winget uninstall --id {pacote} --silent"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)

    def abrir_processo(self):
        print('Abrindo pacote')
        caminho_app = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"

        # comando_shell = fr'Start-Service AnyDesk'
        # comando_shell = fr'Start-Process "{caminho_app}" -ArgumentList "--tray"'
        comando_shell = fr'Start-Process "{caminho_app}" -WindowStyle Minimized'

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)

    def remover_processo(self):
        print('Fechando Processo do Anydesk')
        comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue | Stop-Process -Force"
        # comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )
        print(response_powershell.stdout)

    def removendo_config_anydesk(self):
        print('Removendo Configuração do Anydesk')
        caminho_confi_anydesk = r"C:\ProgramData\AnyDesk"

        os.rmdir(caminho_confi_anydesk)
        # print(caminho_confi_anydesk)



if __name__ == '__main__':

    if verificar_elevacao():
        obj_pacote = GeranciadorDePacotes()

        obj_pacote.removendo_config_anydesk()
        # sleep(15)
        # obj_pacote.remover_processo()

        print('Finalizando o processo.')
        sleep(5)
