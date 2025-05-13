import speedtest
import teste_download
import teste_upload


class TesteVelocidade:
    def __init__(self):
        self.modulo_speed = speedtest.Speedtest()

    def testando_conexao_down(self):
        return teste_download(self.modulo_speed)

    def testando_conexao_up(self):
        return teste_upload(self.modulo_speed)


iniciando_obj = TesteVelocidade()
print(iniciando_obj)
print(iniciando_obj.testando_conexao_down())
print(iniciando_obj.testando_conexao_up())
