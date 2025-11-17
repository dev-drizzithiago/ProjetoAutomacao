import os
from pathlib import Path
from subprocess import run, CalledProcessError
from time import sleep

home_usuario = Path.home()

comando_powershell_desbloquear_MOTW = f"Get-ChildItem -Path {home_usuario} -Recurse | Unblock-File"
comando_powershell_reiniciar_explorer = 'taskkill /f /im explorer.exe; Start-Process explorer.exe'

try:
    result_shell = run(
        ['powershell', "-Command", comando_powershell_desbloquear_MOTW],
        shell=True,
        capture_output=True,
        check=True
    )

    sleep(2)
    print('Reiniciando o Windows Explorer.exe para aplicar as mudanças')
    run(
        ['powershell', '-Command', comando_powershell_reiniciar_explorer],
        shell=True,
        capture_output=True,
        check=True
    )

except CalledProcessError as error:
    print(f'\n Erro ao executar o PowerShell: ')
    print(f'Stdout: {error.stdout} ')
    print(f'Stderr: {error.stderr} ')
    print('Verifique se o perfil foi executado como administrador.')
except Exception as error:
    print('Ocorreu um erro inesperado:', error)



