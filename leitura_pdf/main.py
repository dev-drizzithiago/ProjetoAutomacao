from PyPDF2 import PdfReader
import pandas as pd
import re

class LeituraPdf:
    def __init__(self, arquivo_pdf):
        self.arquivo_pdf = arquivo_pdf
        self.paginas_texto = []  # 1) lista com o texto de cada página
        self.texto_completo = ''      # 2) texto concatenado de todas as páginas
        self.tabela_campos = None     # 3) DataFrame com campos extraídos (opcional)

    def extraindo_texto(self):
        leitura = PdfReader(self.arquivo_pdf)
        self.paginas_texto = []

        for index, text_page in enumerate(leitura.pages, start=1):
            texto = text_page.extract_text() or ''  # evita Non
            self.paginas_texto.append(texto)

        # 2) Concatenar tudo
        self.texto_completo = '\n'.join(self.paginas_texto)

    def criar_dataFrame_por_pagina(self):
        df = pd.DataFrame({
            "numero_pagina": list(range(1, len(self.paginas_texto) + 1)),
            'texto': self.paginas_texto
        })
        return df

    def buscar_ocorrencia(self, pattern, text, flags=0, default=None):
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else default

    def extrair_campos_com_regex(self):
        texto = self.texto_completo
        texto_normalizado = texto.replace('**', ''). replace('\\-', '-')

        periodo = self.buscar_ocorrencia(
            r"Período de Apuração:.*?([0-9]{2}/[0-9]{4}\s*a\s*[0-9]{2}/[0-9]{4})", texto, flags=re.DOTALL)

        print(periodo)


if __name__ == '__main__':
    caminho_arquivo = 'teste.pdf'
    obj_leitura_pdf = LeituraPdf(caminho_arquivo)
    obj_leitura_pdf.extraindo_texto()
    response_texto_df = obj_leitura_pdf.criar_dataFrame_por_pagina()
    response_regex = obj_leitura_pdf.extrair_campos_com_regex()


