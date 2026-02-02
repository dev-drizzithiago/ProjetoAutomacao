import pandas as pd
import os

from pathlib import Path


HOME_USUARIO = Path.home()
PASTA_DOWNLOAD_WIN = 'Downloads'
CAMINHO_ABS_SERVIDOR = r'\\192.168.0.10\Programas ADM\PLANILHAS_EXCEL_APPS'

class CreaterPlanilha:

    def __init__(self):

        self.DATA_FRAME_APP = None
        self.NOME_PLANILHA = None
        self.local_save_planilha = None

        self.local_path = os.path.join(HOME_USUARIO, PASTA_DOWNLOAD_WIN)

    def dados_to_pandas(self, dados_entrada):
        self.NOME_PLANILHA = (
            f"software_instalados_"
            f"{
            str(dados_entrada[0]['DisplayVersion'])
            .replace('.', '-')
            }.xlsx"
        )

        self.DATA_FRAME_APP = pd.DataFrame(dados_entrada)

    def criar_planilha_dados_app(self):
        print()
        print('---' * 10)
        print('Criando a Planilha...!')

        try:
            print()
            print('---' * 10)
            print('Enviando relatório ao servidor...')
            os.listdir(CAMINHO_ABS_SERVIDOR)
            self.local_save_planilha = os.path.join(CAMINHO_ABS_SERVIDOR, self.NOME_PLANILHA)
            print(self.local_save_planilha)
        except:
            print()
            print('---' * 10)
            print('Servidor não respondeu, arquivo sendo salvo no computador local...')
            print('Pasta Local: ', self.local_save_planilha)
            self.local_save_planilha = self.local_path

        # Abre um ExcelWriter apontando para o caminho absoluto
        # engine='xlsxwriter': usa o motor xlsxwriter (excelente para formatação rica).
        with pd.ExcelWriter(self.local_save_planilha, engine='xlsxwriter') as writer:

            # sheet: nome da planilha na aba.
            sheet = 'Relatório APPs'

            wb = writer.book

            # Escreve os dados do DataFrame no arquivo Excel, sem a coluna de índice.
            self.DATA_FRAME_APP.to_excel(writer, sheet_name=sheet, index=False)

            work_sheet = writer.sheets[sheet]
            bold = wb.add_format({'bold': True})

            work_sheet.set_column("A:A", 80, bold)
            work_sheet.set_column("B:B", 25)

            rows, cols = self.DATA_FRAME_APP.shape

            work_sheet.add_table(0, 0, rows, cols - 1, {
                "name": "TabelaSoftware",

                # Define um estilo de tabela (TableStyleMedium9) — dá zebra e filtros nativos.
                "style": "TableStyleMedium9",

                # Define o texto do cabeçalho de cada coluna a partir de df.columns.
                "columns": [{"header": c} for c in self.DATA_FRAME_APP.columns]
            })

            work_sheet.freeze_panes(1, 0)
            work_sheet.freeze_panes(2, 0)

        return self.NOME_PLANILHA