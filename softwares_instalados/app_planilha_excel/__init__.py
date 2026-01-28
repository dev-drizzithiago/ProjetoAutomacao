import pandas as pd


class CreaterPlanilha:

    def __init__(self):
        self.DATA_FRAME_APP = None
        self.CAMINHO_ABS_PLANILHA = None


    def dados_to_pandas(self, dados_entrada):
        self.CAMINHO_ABS_PLANILHA = f"{
        dados_entrada['DisplayName'] - str(dados_entrada['DisplayVersion']).replace('.', '-')
        }"
        self.DATA_FRAME_APP = pd.DataFrame(dados_entrada)

    def criar_planilha_dados_app(self):

        print('Criando a planilha!')

        print()
        with pd.ExcelWriter(self.CAMINHO_ABS_PLANILHA, engine='xlsxwriter') as writer:
            sheet = 'Relatório APPs'
            self.DATA_FRAME_APP.to_excel(writer, sheet_name=sheet, index=False)
