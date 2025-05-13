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


iniciando_obj = TesteVelocidade()
print(iniciando_obj)
print(iniciando_obj.testando_conexao_down())
print(iniciando_obj.testando_conexao_up())
