import re
from subprocess import (
    PIPE, # sinaliza que queremos capturar a saída do processo (em vez de deixar ela ir para o console).
    run,  # executa um comando externo (no nosso caso, o PowerShell) e retorna um objeto com a saída (stdout)
)

from turtledemo.penrose import start

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


    def scan_software(self):

        # Lista final de dicionários: {"DisplayName": "...", "DisplayVersion": "..."}
        # Cria resultado, a lista que vamos retornar, formada por dicionários com as chaves DisplayName e
        # DisplayVersion.
        resultado = []

        # Executa PowerShell sem carregar perfis do usuário (-NoProfile) e sem travar por política
        # (-ExecutionPolicy Bypass)
        # -Command recebe o script a executar (aqui usamos o comando "simples")
        # -NoProfile: não carrega perfis do usuário (evita ruídos e lentidão).
        # -ExecutionPolicy Bypass: evita que políticas de execução bloqueiem o comando.
        # -Command <script>: executa o conteúdo da constante COMANDO_SCAN_SOFTWARE.
        response_scan = run(
            ["powershell", "NoProfile", "-ExecutionPolicy", "Bypass", "-Command", self.COMANDO_SCAN_SOFTWARE],
            text=True,   # retorna stdout como str (não bytes)  faz o stdout vir já como string.
            stdout=PIPE  # captura a saída padrão para uso no Python  captura a saída do comando dentro do Python.
        )

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
