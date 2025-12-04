from PyPDF2 import PdfReader
import pandas as pd

class LeituraPdf:
    def __init__(self, arquivo_pdf):
        self.arquivo_pdf = arquivo_pdf
        pass

    def extraindo_texto(self):

        leitura = PdfReader(self.arquivo_pdf)
        for text_page in leitura.pages:
            texto = text_page.extract_text()
            print()
            print(texto)


if __name__ == '__main__':
    caminho_arquivo = 'teste.pdf'
    obj_leitura_pdf = LeituraPdf(caminho_arquivo)
    obj_leitura_pdf.extraindo_texto()
