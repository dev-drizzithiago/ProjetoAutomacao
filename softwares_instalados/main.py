import re
from subprocess import PIPE, run



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

    def __init__(self):
        self.lista_itens = []


    def scan_software(self):
        response_scan = run(
            ["powershell", "-Command", self.COMANDO_SCAN_SOFTWARE],
            text=True,  stdout=PIPE
        )
        for item in response_scan.stdout.splitlines():
            formatacao_item = re.sub(r"\s+", " ", item)


            self.lista_itens.append(formatacao_item)

        for row in self.lista_itens:
            linha = (row or '').strip()

            if not linha:
                continue

            if linha.startswith('DisplayName') or set(linha) <= {'-', ' '}:
                continue

            regex_result = re.search(r'(\d+(?:\.\d+)+)\s*$', linha)

            print(regex_result)
            print()
            print(linha)

if __name__ == '__main__':
    obj_scan_software = RelatorioSoftwareInstalados()
    obj_scan_software.scan_software()
