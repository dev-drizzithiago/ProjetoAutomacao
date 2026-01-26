import re
from subprocess import PIPE, run
from turtledemo.penrose import start


class RelatorioSoftwareInstalados:

    CAMANDO_SCAN_SOFTWARE_MICROSOFT = (
        r"Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* , "
        r"HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | "
        r"Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | "
        r"Where-Object { $_.DisplayName } | "
        r"Sort-Object DisplayName "
    )

    COMANDO_SCAN_SOFTWARE = (
        r"""
            Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
            Select DisplayName, DisplayVersion |
            Sort DisplayName
        """
    )

    COMANDO_SCAN_SOFTWARE_COMPLETO = (
        r"""            
            Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* ,
            HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* |
            Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
            Where-Object { $_.DisplayName } |
            Sort-Object DisplayName
        """
    )

    def __init__(self):
        self.lista_itens = []


    def scan_software(self):
        resultado = []
        response_scan = run(
            ["powershell", "-Command", self.COMANDO_SCAN_SOFTWARE],
            text=True,  stdout=PIPE
        )

        # Separa o resultado por linhas e adiciona em uma lista
        for item in response_scan.stdout.splitlines():
            formatacao_item = re.sub(r"\s+", " ", item)
            self.lista_itens.append(formatacao_item)

        # Processo os dados e separa entre nome e versões.
        for row in self.lista_itens:
            linha = (row or '').strip()

            if not linha:
                continue

            if linha.startswith('DisplayName') or set(linha) <= {'-', ' '}:
                continue

            regex_result = re.search(r'(\d+(?:\.\d+)+)\s*$', linha)

            if regex_result:
                versao = regex_result.group(1).strip()
                nome_app = linha[:start()].rstrip()
                partes = nome_app.split()

                if partes and partes[-1] == versao:
                    nome_app = ' '.join(partes[:-1]).rstrip()
                resultado.append({'DisplayName': nome_app, 'DisplayVersion': versao})
            else:
                resultado.append({'DisplayName': linha, 'DisplayVersion': ''})

        return resultado


if __name__ == '__main__':
    obj_scan_software = RelatorioSoftwareInstalados()
    response_resultado = obj_scan_software.scan_software()
    for item in response_resultado:
        print(f"{item['DisplayName']} => {item['DisplayVersion']}")
