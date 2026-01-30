from subprocess import run, PIPE
from time import sleep

USUARIO_LOCAL = ''
PASSWORD_USER_LOCAL = ''
PASTA_COMPARTILHADA = 'Digitalização'


class ConfigNovoNote:


    def __init__(self):
        pass

    def conf_pasta_scan(self):
        SCRIPT_CRIAR_PASTA = rf"""
            New-Item -ItemType Directory -Path {PASTA_COMPARTILHADA} -Force | Out-Null
        """
        print(f'Criando pasta: "{PASTA_COMPARTILHADA}"...')
        run([
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            SCRIPT_CRIAR_PASTA
        ],  text=True,   # retorna stdout como str (não bytes)  faz o stdout vir já como string.
            stdout=PIPE  # captura a saída padrão para uso no Python  captura a saída do comando dentro do Python.
        )

        SCRIPT_COMPARTILHAMENTO = rf"""
            New-SmbShare -Name {PASTA_COMPARTILHADA} 
            -Path {PASTA_COMPARTILHADA} -Description "Compartilhamento restrito para .\ti" \
            -CachingMode None | Out-Null
        """

        print(f'Configurando compartilhamento da pasta: "{PASTA_COMPARTILHADA}"')

        run([
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            SCRIPT_COMPARTILHAMENTO
        ], text=True,  # retorna stdout como str (não bytes)  faz o stdout vir já como string.
            stdout=PIPE  # captura a saída padrão para uso no Python  captura a saída do comando dentro do Python.
        )

        SCRIPT_CONCEDENDO_ACESSO = (
             rf"Grant-SmbShareAccess "
             rf"-Name {PASTA_COMPARTILHADA} "
             rf"-AccountName '.\ti' "
             rf"-AccessRight Change -Force"
        )
        print('Concedendo acesso ao usuário...')

        run([
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            SCRIPT_CONCEDENDO_ACESSO
        ], text=True,  # retorna stdout como str (não bytes)  faz o stdout vir já como string.
            stdout=PIPE  # captura a saída padrão para uso no Python  captura a saída do comando dentro do Python.
        )

    def conf_dominio(self):
        pass


if __name__ == '__main__':
    init_obj_config = ConfigNovoNote()
    init_obj_config.conf_pasta_scan()

    # init_obj_config.conf_pasta_scan()