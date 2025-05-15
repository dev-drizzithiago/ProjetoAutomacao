import pandas


class AnaliseDados:
    def __init__(self, dados_entrada):
        self._dados_entrada = dados_entrada

    def _view_dados(self):
        return self._dados_entrada


if __name__ == '__main__':
    dados_teste_velocidade = {
        'data_teste': '',
        'teste_download': '',
        'teste_upload': '',
        'tempo_resposta': '',
        'dados_cliente': ['', ''],
    }

    iniciando_obj_analise_dados = AnaliseDados(dados_teste_velocidade)
    print(iniciando_obj_analise_dados._view_dados)

