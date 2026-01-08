import os
import subprocess
from time import sleep


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
        caminho_confi_anydesk = r"C:\ProgramData\AnyDesk"

        os.rmdir(caminho_confi_anydesk)
        # print(caminho_confi_anydesk)



if __name__ == '__main__':
    obj_pacote = GeranciadorDePacotes()

    obj_pacote.abrir_processo()
    sleep(15)
    obj_pacote.remover_processo()
