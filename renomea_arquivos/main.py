
from pypdf import PdfReader
import os
import re

class RenomeandoPdfComprovantePagamento:
    def __init__(self):
        self.data_pagamento = None
        self.favorecido = None
        self.valor_documento = None

        self.arquivo_pdf = None
        self.reader = None
        self.texto = ''
        self.novo_nome = None


    def leitura_pasta(self, pasta):
        dados = os.listdir(pasta)

        return dados

    def leitura_arquivo_pdf(self, lista_arquivos):

        reader = PdfReader(lista_arquivos)
        for page in reader.pages:
            self.texto += page.extract_text() or ''


    def regex_favorecido(self):
        match_favorecido = re.search(r"Favorecido\s*(.+)", self.texto)

        print(match_favorecido)

        favorecido = match_favorecido.group(1).strip()

        if not favorecido:
            raise ValueError('favorecido não encontrado no PDF')

        self.favorecido = favorecido.split(':')[1].replace(':', '').strip()
        print(self.favorecido)


    def regex_data_pagamento(self):
        match_data_pagamento = re.search(r"Data\s+de\s+Pagamento:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})", self.texto)
        data_pagamento = match_data_pagamento.group(0).strip()

        if not data_pagamento:
            raise ValueError('Data vencimento não encontrado no PDF')

        self.data_pagamento =  data_pagamento.strip().replace('\n', ' ').strip().split(':')[1].replace('/', '-').strip()
    def regex_valor_pagamento(self):

        match_valor = re.search(r"Valor\s*\(R\$\):?\s*([0-9]+,[0-9]{2})", self.texto)
        valor = match_valor.group(0).strip()

        if not valor:
            raise ValueError('Valor não encontrado no PDF')

        self.valor_documento =  valor.strip().split(':')[1].replace(',', '.').strip()

        return f"{self.favorecido}_{self.data_pagamento}_{self.valor_documento}.pdf"


if __name__ == '__main__':
    init_renomear = RenomeandoPdfComprovantePagamento()
    pasta = rf'C:\gitHub\ProjetoAutomacao\renomea_arquivos\comprovante_bradesco'
    lista_arquivos = init_renomear.leitura_pasta(pasta)

    for pdf in lista_arquivos:
        path = os.path.join(pasta, pdf)
        print(pdf)

        init_renomear.leitura_arquivo_pdf(path)

        init_renomear.regex_favorecido()
        init_renomear.regex_data_pagamento()
        novo_nome = init_renomear.regex_valor_pagamento()

        novo_path = os.path.join(pasta, novo_nome)

        print(novo_path)

        os.rename(path, novo_path)
