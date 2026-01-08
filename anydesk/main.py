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
        pacote = ' anydesk'
        comando_shell = f"winget uninstall --id {pacote} --si"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_shell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)

if __name__ == '__main__':
    obj_pacote = GeranciadorDePacotes()

    obj_pacote.procurar_pacotes()