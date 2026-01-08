import os
import subprocess
from pathlib import Path

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

    def get_Processos(self):
        # comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue | Stop-Process -Force"
        comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)

    def abrir_app(self):
        caminho_app = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
        comando_shell = f'Start-Process "{caminho_app}"'

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)

if __name__ == '__main__':
    obj_pacote = GeranciadorDePacotes()

    obj_pacote.abrir_app()
    # obj_pacote.get_Processos()
