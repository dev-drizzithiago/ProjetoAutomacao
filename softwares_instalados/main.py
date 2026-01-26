import subprocess



class RelatorioSoftwareInstalados:

    CAMANDO_SCAN_SOFTWARE_MICROSOFT = (
        r"Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* , "
        r"HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | "
        r"Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | "
        r"Where-Object { $_.DisplayName } | "
        r"Sort-Object DisplayName "
    )

    def __init__(self):
        pass

    def scan_software(self):
        response_scan = subprocess.run(
            ["powershell -Command", self.CAMANDO_SCAN_SOFTWARE_MICROSOFT],
            text=True, capture_output=True
        )
        print(response_scan.stdout)

if __name__ == '__main__':
    obj_scan_software = RelatorioSoftwareInstalados()
    obj_scan_software.scan_software()
