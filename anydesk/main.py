import subprocess


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
        comando_shell = "Get-Process -Name 'AnyDesk*' -ErrorAction SilentlyContinue | Stop-Process -Force"


if __name__ == '__main__':
    obj_pacote = GeranciadorDePacotes()

    obj_pacote.desinstalar_pocotes()