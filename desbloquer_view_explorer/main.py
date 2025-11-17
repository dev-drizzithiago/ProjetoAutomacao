"""
Detalhamento do Comando
Este comando combina duas ações essenciais, separadas por um ponto e vírgula (;):

taskkill /f /im explorer.exe:

taskkill: É o utilitário do Windows usado para encerrar processos em execução.

/f: Força o encerramento do processo (fundamental para garantir que o processo seja finalizado imediatamente).

/im explorer.exe: Especifica a imagem do processo a ser encerrado, que é o explorer.exe (o Explorador de Arquivos/Shell do Windows).

Start-Process explorer.exe:

Start-Process: É o cmdlet do PowerShell usado para iniciar um novo processo.

explorer.exe: Inicia uma nova instância do Explorador de Arquivos.
"""



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

    print('Reiniciando o Windows Explorer.exe para aplicar as mudanças')
    sleep(5)
    run(
        ['powershell', '-Command', comando_powershell_reiniciar_explorer],
        shell=True,
        capture_output=True,
        check=True
    )
    print("Windows Explorer reiniciado. Verifique agora o Painel de Visualização.")

except CalledProcessError as error:
    print(f'\n Erro ao executar o PowerShell: ')
    print(f'Stdout: {error.stdout} ')
    print(f'Stderr: {error.stderr} ')
    print('Verifique se o perfil foi executado como administrador.')
except Exception as error:
    print('Ocorreu um erro inesperado:', error)



