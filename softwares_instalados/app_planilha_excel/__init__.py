import pandas as pd


class CreaterPlanilha:
    CAMINHO_ABS_PLANILHA = 'PLANILHA-TESTE.xlsx'
    def dados_to_pandas(self, dados_entrada):
        data_frame_app = pd.DataFrame(dados_entrada)

    def criar_planilha_dados_app(self, dados_pandas):
        with pd.ExcelWriter(self.CAMINHO_ABS_PLANILHA, engine='xlsxwriter') as writer:
            sheet = 'Relatório APPs'
