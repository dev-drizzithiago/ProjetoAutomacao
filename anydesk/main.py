import subprocess


class GeranciadorDePacotes:
    def __init__(self):
        pass


    def procurar_pacotes(self):
        pacote = ' word'
        comando_powershell = f"winget search {pacote}"

        response_powershell = subprocess.run(
            ['powershell', '-Command', comando_powershell],
            text=True, capture_output=True
        )

        print(response_powershell.stdout)


if __name__ == '__main__':
    obj_pacote = GeranciadorDePacotes()

    obj_pacote.procurar_pacotes()