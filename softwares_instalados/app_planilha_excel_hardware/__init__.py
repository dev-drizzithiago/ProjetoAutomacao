import pandas as pd
import os
from time import sleep

class CreaterPlanilhaHardware:

    CAMINHO_ABS_SERVIDOR = r'\\192.168.0.10\APP Login\PLANILHAS_EXCEL_APPS'
    LOCAL_PATH_RELATORIO = r"c:\PLANILHAS_EXCEL_APPS_LOCAL"

    def __init__(self, dados_entrada):
        self.dados_de_entrada = dados_entrada

        self.NOME_PLANILHA = None
        self.local_save_planilha = None

        self.dataFrama_hardware = {}

        self.NOME_PLANILHA = (
            f"hardwares"
            f"{self.dados_de_entrada[0]['MainBoard']['Serial Number'].replace("/", '_')}.xlsx"
        )

        self.df_mb = None

        try:
            os.mkdir(self.LOCAL_PATH_RELATORIO)
        except FileExistsError:
            pass

    def dados_to_pandas(self):

        grupo_componentes = {
            'MainBoard': [],
            'Processador': [],
            'Memoria': [],
            'Unidade': [],
        }

        # Faz o loop dos dados de entrada.
        for item in self.dados_de_entrada:

            # Faz o loop os dicionários dentro da lista de entrada.
            for componente, payload in item.items():

                # Verificar se existe o componente e adiciona a na lista conforma o componente.
                if componente in grupo_componentes:
                    grupo_componentes[componente].append(payload)

        if grupo_componentes['MainBoard']:
            self.df_mb = pd.DataFrame(grupo_componentes['MainBoard'])
        else:
            self.df_mb = pd.DataFrame(columns=['Placa Mae','Fabricante','Serial Number','Numero Produto','Versao'])
            # self.dataFrama_hardware = pd.DataFrame(componente)
        print(self.df_mb)

    def criar_planilha_dados_app(self):
        os.system('cls')
        print()
        print('---' * 10)
        print('Criando a Planilha...!')

        try:
            print()
            print('---' * 10)
            print('Enviando relatório ao servidor, testando conexão...')

            os.listdir(self.CAMINHO_ABS_SERVIDOR)

            print(self.local_save_planilha)
            self.local_save_planilha = os.path.join(self.CAMINHO_ABS_SERVIDOR, self.NOME_PLANILHA)
        except:
            os.system('cls')
            print()
            print('---' * 10)
            print('Servidor não respondeu, arquivo sendo salvo no computador local...')
            print('Pasta Local: ', self.LOCAL_PATH_RELATORIO)
            self.local_save_planilha = os.path.join(self.LOCAL_PATH_RELATORIO, self.NOME_PLANILHA)

        # Abre um ExcelWriter apontando para o caminho absoluto
        # engine='xlsxwriter': usa o motor xlsxwriter (excelente para formatação rica).
        try:
            with pd.ExcelWriter(self.local_save_planilha, engine='xlsxwriter') as writer:

                # sheet: nome da planilha na aba.
                sheet = 'Relatório APPs'

                wb = writer.book

                # Escreve os dados do DataFrame no arquivo Excel, sem a coluna de índice.
                self.dataFrama_hardware.to_excel(writer, sheet_name=sheet, index=False)

                work_sheet = writer.sheets[sheet]
                bold = wb.add_format({'bold': True})

                work_sheet.set_column("A:A", 80, bold)
                work_sheet.set_column("B:B", 25)

                rows, cols = self.dataFrama_hardware.shape

                work_sheet.add_table(0, 0, rows, cols - 1, {
                    "name": "TabelaSoftware",

                    # Define um estilo de tabela (TableStyleMedium9) — dá zebra e filtros nativos.
                    "style": "TableStyleMedium9",

                    # Define o texto do cabeçalho de cada coluna a partir de df.columns.
                    "columns": [{"header": c} for c in self.dataFrama_hardware.columns]
                })

                work_sheet.freeze_panes(1, 0)
                work_sheet.freeze_panes(2, 0)
            os.system('cls')
            print()
            print('---' * 10)
            print('Planilha criada com sucesso!')
            sleep(5)
            return self.NOME_PLANILHA
        except Exception as error:
            os.system('cls')

            print()
            print('---' * 10)
            print('Erro ao criar a planilha: ', error)

            print()
            print('---' * 10)
            input('Aperta ENTER para finalizar!')

    @staticmethod
    def _to_gib(value):
        try:
            return int(int(value) / (1024 ** 3))
        except:
            return None
