class TesteDownload:
    def __init__(self, modulo_speedtest):
        self.st.modulo_speedtest

    def processo_teste(self):
        teste_download = f'{self.st.download() / 1_000_000:.2f} mbps'
        return teste_download
