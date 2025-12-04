from PyPDF2 import PdfReader
import pandas as pd

class LeituraPdf:
    def __init__(self, arquivo_pdf):
        self.arquivo_pdf = arquivo_pdf
        self.lista_dados_pandas = []  # 1) lista com o texto de cada página
        self.texto_completo = ''      # 2) texto concatenado de todas as páginas
        self.tabela_campos = None     # 3) DataFrame com campos extraídos (opcional)

    def extraindo_texto(self):
        leitura = PdfReader(self.arquivo_pdf)
        for text_page in leitura.pages:
            texto = text_page.extract_text()
            print()
            print(texto)
            print(type(texto))

if __name__ == '__main__':
    caminho_arquivo = 'teste.pdf'
    obj_leitura_pdf = LeituraPdf(caminho_arquivo)
    obj_leitura_pdf.extraindo_texto()
