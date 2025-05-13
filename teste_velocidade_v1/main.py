import speedtest
import teste_download

class TesteVelocidade:

    def testando_conexao(self):
        return teste_download.TesteDownload(speedtest)


iniciando_obj = TesteVelocidade()
print(iniciando_obj.testando_conexao())
