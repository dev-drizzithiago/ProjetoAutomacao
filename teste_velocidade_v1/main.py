from time import sleep
import speedtest



class TesteVelocidade:
    def __init__(self):
        self.modulo_speed = speedtest.Speedtest()

    def testando_conexao_down(self):
        teste_download = f'{self.modulo_speed.download() / 1_000_000:.2f} mbps'
        return teste_download

    def testando_conexao_up(self):
        teste_download = f'{self.modulo_speed.upload() / 1_000_000:.2f} mbps'
        return teste_download

    def teste_conexao_tempo_resposta(self):
        teste_ms = f'{self.modulo_speed.results.ping} ms'
        return teste_ms

    def servidor_teste(self):
        servidor = f'{self.modulo_speed.get_best_server()}'
        return servidor

    def dados_cliente(self):
        """
        Indica os dados do cliente
        :return:
        """
        dados_cliente = dict(self.modulo_speed.results.client)

        servidor = dict(
            IP=dados_cliente['ip'],
            Operadora=dados_cliente['isp']
        )
        return servidor


while True:
    try:
        iniciando_obj = TesteVelocidade()
        print(f'Teste de velocidade para o servidor {iniciando_obj.servidor_teste()}')
        print(iniciando_obj.testando_conexao_down())
        print(iniciando_obj.testando_conexao_up())
        print(iniciando_obj.teste_conexao_tempo_resposta())
        print(iniciando_obj.dados_cliente()['IP'])
        print(iniciando_obj.dados_cliente()['Operadora'])
        sleep(60)
    except speedtest.ConfigRetrievalError:
        print('Você tentou várias em um curto periodo, aguarda alguns minutos')
        sleep(60)
