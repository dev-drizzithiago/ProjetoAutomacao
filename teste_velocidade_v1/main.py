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
        :return: retorna o endereço de ip e o nome da operadora
        """
        dados_cliente = dict(self.modulo_speed.results.client)

        servidor = dict(
            IP=dados_cliente['ip'],
            Operadora=dados_cliente['isp']
        )
        return servidor

linha_formatacao = '- - ' * 20
contador_teste = 1

while True:

    iniciando_obj = TesteVelocidade()
    print(f'{contador_teste}° teste de velocidade')
    print(linha_formatacao)

    try:
        print(f'Teste Download: [{iniciando_obj.testando_conexao_down()}]')
        print(f'Teste Upload: [{iniciando_obj.testando_conexao_up()}]')
        print(f'Tempo de resposta: [{iniciando_obj.teste_conexao_tempo_resposta()}]')

        print(f'Seu endereço de internet: [{iniciando_obj.dados_cliente()["IP"]}]')
        print(f'Sua operadora: [{iniciando_obj.dados_cliente()["Operadora"]}]')

        print(f'{contador_teste}° Finalizado!')
        print(linha_formatacao)
        sleep(120)
    except speedtest.ConfigRetrievalError:
        print('Você tentou várias em um curto periodo, aguarda alguns minutos')
        sleep(120)
                
    contador_teste += 1
