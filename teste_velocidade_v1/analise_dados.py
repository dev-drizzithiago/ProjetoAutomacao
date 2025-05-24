import pandas as pd


class AnaliseDados:
    def __init__(self, dados_entrada):
        self._dados_entrada = dados_entrada

    def view_dados_(self):
        return self._dados_entrada

    def create_dataframe(self):
        data_speedtest = {
            'Download': self._dados_entrada['teste_download'],
            'Upload': self._dados_entrada['teste_upload'],
            'Tempo de Resposta': self._dados_entrada['data_teste'],
            'Endereço de Internet': self._dados_entrada['dados_cliente'][0],
            'Operadora': self._dados_entrada['dados_cliente'][1],
        }
        data_speedtest_pd = pd.DataFrame(
            data_speedtest,
            columns=['Download', 'Upload', 'Tempo de Resposta'],
        )

        data_horario_teste = {
            'Horario do Teste': self._dados_entrada['data_teste'],
        }
        return data_speedtest_pd

if __name__ == '__main__':
    dados_teste_velocidade = {
        'data_teste': '14/05/2025 - 21:39:50',
        'teste_download': '329.70 mbps',
        'teste_upload': '351.25 mbps',
        'tempo_resposta': '6.877 ms',
        'dados_cliente': ['179.228.37.110', 'Vivo'],
    }

    iniciando_obj_analise_dados = AnaliseDados(dados_teste_velocidade)

    print(iniciando_obj_analise_dados.create_dataframe())

