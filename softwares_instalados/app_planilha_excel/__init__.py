import pandas as pd


class CreaterPlanilha:

    def dados_to_pandas(self, dados_entrada):
        data_frame_app = pd.DataFrame(dados_entrada)
        print(data_frame_app)

    def criar_planilha_dados_app(self, dados_pandas):
        for item in dados_pandas:
            print(f"{item['DisplayName']} => {item['DisplayVersion']}")
