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
            self.lista_itens.append(item)

        print(self.lista_itens)

if __name__ == '__main__':
    obj_scan_software = RelatorioSoftwareInstalados()
    obj_scan_software.scan_software()
