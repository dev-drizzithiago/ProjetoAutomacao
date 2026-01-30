import pandas as pd


class CreaterPlanilha:

    def __init__(self):
        self.DATA_FRAME_APP = None
        self.CAMINHO_ABS_PLANILHA = None


    def dados_to_pandas(self, dados_entrada):
        self.CAMINHO_ABS_PLANILHA = (

            f"software_instalados_"
            f"{str(dados_entrada[0]['DisplayVersion']).replace('.', '-')}.xlsx"

        )

        self.DATA_FRAME_APP = pd.DataFrame(dados_entrada)

    def criar_planilha_dados_app(self):
        print('Criando a Planilha...!')

        # Abre um ExcelWriter apontando para o caminho absoluto
        # engine='xlsxwriter': usa o motor xlsxwriter (excelente para formatação rica).
        with pd.ExcelWriter(self.CAMINHO_ABS_PLANILHA, engine='xlsxwriter') as writer:

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

        return self.CAMINHO_ABS_PLANILHA