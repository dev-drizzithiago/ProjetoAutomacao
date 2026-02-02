import ctypes
import re
import os
import sys
import getpass
from subprocess import (
    PIPE, # sinaliza que queremos capturar a saída do processo (em vez de deixar ela ir para o console).
    run,  # executa um comando externo (no nosso caso, o PowerShell) e retorna um objeto com a saída (stdout)
)

import socket
from time import sleep

# Chama o modulo.
from app_planilha_excel import CreaterPlanilha
from spinner import _run_spinner

def verificar_elevacao():
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    ## Se o app não foi elevado vai abrir a janela para solicita as credinciais de administrador.
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None,  # handle (não usado)
            "runas",  # O verbo que força o UAC
            sys.executable,  # O arquivo a ser executado (o interpretador Python)
            " ".join(sys.argv),  # Os argumentos (o nome do seu script)
            None,  # diretório de trabalho
            1  # mostra a janela
        )
        sys.exit(0)  # Sai do script original
    return True

class RelatorioSoftwareInstalados:

    # Comando PowerShell "simples": lê somente HKLM 64-bit (Uninstall) e escolhe DisplayName + DisplayVersion
    COMANDO_SCAN_SOFTWARE = (
        r"""
            Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
            Select DisplayName, DisplayVersion |
            Sort DisplayName
        """
    )

    # (Opcional) Versão mais completa do comando, cobrindo 64-bit e 32-bit (Wow6432Node) e com mais colunas.
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

        # Armazena as linhas "cruas" (normalizadas) vindas do PowerShell
        self.lista_itens = []
        self.host_name = socket.gethostname()
        self.user_logado = getpass.getuser()


    def scan_software(self):

        # Lista final de dicionários: {"DisplayName": "...", "DisplayVersion": "..."}
        # Cria resultado, a lista que vamos retornar, formada por dicionários com as chaves DisplayName e
        # DisplayVersion.
        resultado = []

        # Adiciona o usuário que esta logado.
        resultado.append({'DisplayName': 'Usuário Logado', 'DisplayVersion': self.user_logado})

        # Executa PowerShell sem carregar perfis do usuário (-NoProfile) e sem travar por política
        # (-ExecutionPolicy Bypass)
        # -Command recebe o script a executar (aqui usamos o comando "simples")
        # -NoProfile: não carrega perfis do usuário (evita ruídos e lentidão).
        # -ExecutionPolicy Bypass: evita que políticas de execução bloqueiem o comando.
        # -Command <script>: executa o conteúdo da constante COMANDO_SCAN_SOFTWARE.
        # response_scan = run(
        #     ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", self.COMANDO_SCAN_SOFTWARE],
        #     text=True,   # retorna stdout como str (não bytes)  faz o stdout vir já como string.
        #     stdout=PIPE  # captura a saída padrão para uso no Python  captura a saída do comando dentro do Python.
        # )
        response_scan = _run_spinner(self.COMANDO_SCAN_SOFTWARE, 'Buscando apps instalados...')
        # Quebra a saída em linhas e normaliza espaços:
        # - re.sub(r"\s+", " ", item) substitui blocos de espaços/tabs por um espaço simples
        # - .strip() remove espaços no início/fim
        # .strip(): remove espaços no início e no fim.
        # splitlines(): divide a saída em linhas.
        for item in response_scan.stdout.splitlines():

            # re.sub(r"\s+", " ", item): colapsa múltiplos espaços/tabs em um único espaço (ajuda a padronizar).
            formatacao_item = re.sub(r"\s+", " ", item)

            # Guarda cada linha normalizada em self.lista_itens.
            self.lista_itens.append(formatacao_item)

        # Para cada linha, tenta separar NOME e VERSÃO (quando a versão está no fim da linha)
        for row in self.lista_itens:

            # Garante que "linha" é string e remove espaços periféricos
            # (row or ""): evita None.
            # .strip(): reforça a limpeza de borda (por segurança).
            linha = (row or '').strip()

            # Ignora linhas vazia
            if not linha:
                # Pula linhas vazias.
                continue

            # Ignora cabeçalho ("DisplayName DisplayVersion") e linha de separadores ("----- -----")
            # "set(linha) <= {'-', ' '}" significa: a linha contém SOMENTE hifens e/ou espaços.
            if linha.startswith('DisplayName') or set(linha) <= {'-', ' '}:
                continue

            # Procura uma versão no FINAL da linha, como 1.2.3 ou 64.76.37566
            # (\d+(?:\.\d+)+)\s*$  => um ou mais números seguidos de um ou mais ".número", até o fim da linha
            # \d+ = número; (?:\.\d+)+ = um ou mais grupos de “.número”.
            # \s*$ = permite espaços e vai até o fim da linha. Ex.: “Git 2.45.1”, “WinRAR (64-bit) 7.10.0”.
            regex_result = re.search(r'(\d+(?:\.\d+)+)\s*$', linha)

            if regex_result:
                # Captura o texto da versão
                # Se achou a versão: extrai o grupo capturado (a versão).
                versao = regex_result.group(1).strip()

                # Tudo que vem antes do início da versão é considerado o "nome do app"
                # O nome do app é o texto antes da versão
                # regex_result.start() dá o índice onde a versão começa; fatiamos até ali.
                nome_app = linha[:regex_result.start()].rstrip()

                # Algumas saídas repetem a versão duas vezes (ex.: "... 8.0.61000 8.0.61000").
                # Se a "palavra" anterior já era igual à versão, removemos a duplicata.
                # Ex.: "Microsoft Visual C++ ... 8.0.61000 8.0.61000"
                # Aqui verificamos se a “palavra” anterior já era a mesma versão e removemos a duplicata.
                partes = nome_app.split()
                if partes and partes[-1] == versao:
                    nome_app = ' '.join(partes[:-1]).rstrip()

                # Adiciona o par nome/versão ao resultado
                # Guarda no formato limpo: {"DisplayName": <nome>, "DisplayVersion": <versão>}.
                resultado.append({'DisplayName': nome_app, 'DisplayVersion': versao})
            else:
                # Se não encontrou uma versão no fim, guarda só o nome
                # Se a linha não termina com um padrão de versão, guardamos só o nome e deixamos a versão vazia.
                resultado.append({'DisplayName': linha, 'DisplayVersion': ''})
        # Retorna a lista pronta para consumo (impressão, CSV, etc.)
        return resultado

if __name__ == '__main__':

    if verificar_elevacao():
        obj_scan_software = RelatorioSoftwareInstalados()
        response_resultado = obj_scan_software.scan_software()

        init_obj_creater_planilha = CreaterPlanilha()
        init_obj_creater_planilha.dados_to_pandas(response_resultado)
        init_obj_creater_planilha.criar_planilha_dados_app()

    os.system('cls')
    print()
    print('---' * 10)
    print('Relatório finalizado!')
    sleep(10)
    