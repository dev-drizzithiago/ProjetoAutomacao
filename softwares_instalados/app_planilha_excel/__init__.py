


class CreaterPlanilha:
    def __init__(self):
        pass

    def criar_planilha_dados_app(self, dados_entrada):
        for item in dados_entrada:
            print(f"{item['DisplayName']} => {item['DisplayVersion']}")
        pass