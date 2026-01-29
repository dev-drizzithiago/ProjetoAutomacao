import pandas as pd


class CreaterPlanilha:

    def __init__(self):
        self.DATA_FRAME_APP = None
        self.CAMINHO_ABS_PLANILHA = None


    def dados_to_pandas(self, dados_entrada):
        self.CAMINHO_ABS_PLANILHA = (f"{dados_entrada[0]['DisplayName']} - "
                                     f"{str(dados_entrada[0]['DisplayVersion']).replace('.', '-')}.xlsx")

        self.DATA_FRAME_APP = pd.DataFrame(dados_entrada)

    def criar_planilha_dados_app(self):
        print('Criando a Planilha!')

        # Abre um ExcelWriter apontando para o caminho absoluto
        # engine='xlsxwriter': usa o motor xlsxwriter (excelente para formatação rica).
        with pd.ExcelWriter(self.CAMINHO_ABS_PLANILHA, engine='xlsxwriter') as writer:
            # sheet: nome da planilha na aba.
            sheet = 'Relatório APPs'

            # Escreve os dados do DataFrame no arquivo Excel, sem a coluna de índice.
            self.DATA_FRAME_APP.to_excel(writer, sheet_name=sheet, index=False)

            work_sheet = writer.sheets[sheet]

            work_sheet.set_column("A:A", 600)
            work_sheet.set_column("B:B", 180)

            rows, cols = self.DATA_FRAME_APP.shape