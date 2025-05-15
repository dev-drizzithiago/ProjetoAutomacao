import pandas


class AnaliseDados:
    def __init__(self, dados_entrada):
        self._dados_entrada = dados_entrada

    def _view_dados(self):
        return self._dados_entrada


if __name__ == '__main__':
    dados_teste_velocidade = {
        'data_teste': '14/05/2025 - 21:39:50',
        'teste_download': '329.70 mbps',
        'teste_upload': '351.25 mbps',
        'tempo_resposta': '6.877 ms',
        'dados_cliente': ['179.228.37.110', 'Vivo'],
    }

    iniciando_obj_analise_dados = AnaliseDados(dados_teste_velocidade)

    print(iniciando_obj_analise_dados._view_dados())

