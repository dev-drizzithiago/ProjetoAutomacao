"""
[^\n]+ significa “uma ou mais ocorrências de qualquer character que não seja quebra de linha
^ dentro da classe significa negação;
. → qualquer caractere (exceto \n, a menos que você use re.DOTALL);
* → zero ou mais ocorrências;
? → modo não guloso (lazy), ou seja, vai pegar o mínimo necessário até conseguir casar a próxima parte da expressão.
"""

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

    def buscar_duplo(self, pattern, text, flags=0, default=(None, None)):
        m = re.search(pattern, text, flags)
        print(m)
        return (m.group(1), m.group(2)) if m else default

    def extrair_campos_com_regex(self):
        flags = re.DOTALL | re.IGNORECASE
        texto = self.texto_completo
        print(texto)

        periodo = self.buscar_ocorrencia(
            r"Período de Apuração:.*?([0-9]{2}/[0-9]{4}\s*a\s*[0-9]{2}/[0-9]{4})",
            texto,
            flags=re.DOTALL
        )

        cpf_matriz = self.buscar_ocorrencia(
            r'CNPJ Matriz:.*?([0-9]{2}\.[0-9]{3}\.[0-9]{3}\-[0-9]{4}\.[0-9]{2})',
            texto,
            flags=re.DOTALL
        )
        nome_empresaria = self.buscar_ocorrencia(
            r'Nome empresarial:\s*([^\n]+)',
            texto,
            flags=re.DOTALL
        )

        data_abertura = self.buscar_ocorrencia(
            r'Data de abertura no CNPJ:.*?([0-9]{2}/[0-9]{2}/[0-9]{4})',
            texto,
            flags=re.DOTALL
        )

        optante_simples_nacional = self.buscar_ocorrencia(
            r'Optante pelo Simples Nacional:\s*([^\n]+)',
            texto,
            flags=re.DOTALL
        )

        regime_apuracao = self.buscar_ocorrencia(
            r'Regime de Apuração:\s*([^\n]+)',
            texto,
            flags=re.DOTALL
        )

        num_declaracao = self.buscar_ocorrencia(
            r'Nº da Declaração:\s*([^\n]+)',
            texto,
            flags=re.DOTALL
        )

        RPA = self.buscar_ocorrencia(
            r'Receita Bruta do PA \(RPA\).*?([0-9.,]+)\s+0,00\s+[0-9.,]+',
            texto,
            flags=re.DOTALL
        )

        RBT12 = self.buscar_ocorrencia(
            r"ao PA\s*\(RBT12\)\s*([0-9\.,]+)",
            texto,
            flags=re.DOTALL
        )

        RBA = self.buscar_ocorrencia(
            r"\(RBA\)\s*([0-9\.,]+)",
            texto,
            flags=re.DOTALL
        )

        RBAA = self.buscar_ocorrencia(
            r"\(RBAA\)\s*([0-9\.,]+)",
            texto,
            flags=re.DOTALL
        )

        limite_receita_1, limite_receita_2 = self.buscar_duplo(
            r"Limite de receita bruta proporcionalizado\s*([0-9\.,]+)\s+([0-9.,]+)",
            texto,
            flags=flags,
        )

        receita_brutas = self.buscar_ocorrencia(
            r"(2\.2\.1\)\s*Mercado Interno)",
            texto,
            flags=flags,
        )

        print('1', receita_brutas)
        # print(cpf_matriz)
        # print(nome_empresaria)
        # print(data_abertura)
        # print(optante_simples_nacional)
        # print(regime_apuracao)
        # print(num_declaracao)


if __name__ == '__main__':
    caminho_arquivo = 'teste.pdf'
    obj_leitura_pdf = LeituraPdf(caminho_arquivo)
    obj_leitura_pdf.extraindo_texto()
    response_texto_df = obj_leitura_pdf.criar_dataFrame_por_pagina()
    response_regex = obj_leitura_pdf.extrair_campos_com_regex()


