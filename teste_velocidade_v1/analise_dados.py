import pandas as pd


class AnaliseDados:
    def __init__(self, dados_entrada):
        self._dados_entrada = dados_entrada

    def view_dados_(self):
        try:
            leitura_arquivo_dados = pd.read_csv('data.csv')
            return leitura_arquivo_dados
        except FileNotFoundError:
            return 'Arquivo não encontrado'

    def create_dataframe(self):

        data_speedtest = {
            'Horario do Teste': self._dados_entrada['data_teste'],
            'Download': self._dados_entrada['teste_download'],
            'Upload': self._dados_entrada['teste_upload'],
            'Tempo de Resposta': self._dados_entrada['tempo_resposta'],
            'Endereço de Internet': self._dados_entrada['dados_cliente'][0],
            'Operadora': self._dados_entrada['dados_cliente'][1],
        }

        return pd.DataFrame([data_speedtest])


if __name__ == '__main__':
    dados_teste_velocidade = {
        'data_teste': '14/05/2025 - 21:39:50',
        'teste_download': '329.70 mbps',
        'teste_upload': '351.25 mbps',
        'tempo_resposta': '6.877 ms',
        'dados_cliente': ['179.228.37.110', 'Vivo'],
    }

    iniciando_obj_analise_dados = AnaliseDados(dados_teste_velocidade)
    dados_para_salvar = iniciando_obj_analise_dados.create_dataframe()
    dados_para_salvar.to_csv('data.csv')

    for k, v in iniciando_obj_analise_dados.view_dados_().items():
        print(k, v)
