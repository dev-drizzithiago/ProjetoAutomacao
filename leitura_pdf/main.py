"""
[^\n]+ significa “uma ou mais ocorrências de qualquer character que não seja quebra de linha
^ dentro da classe significa negação;
. → qualquer caractere (exceto \n, a menos que você use re.DOTALL);
* → zero ou mais ocorrências;
? → modo não guloso (lazy), ou seja, vai pegar o mínimo necessário até conseguir casar a próxima parte da expressão.


1) Como o regex engine lê isso


2\.3\.1\) → casa literalmente 2.3.1).


\s* → espaços/brancos opcionais.


Total\ de\ Folhas\ de\ Salários\ Anteriores → cabeçalho literal.


.*? → lazy (mínimo possível) até encontrar o próximo trecho.


(R\$\).*?) → aqui há um ponto sensível:

( abre um grupo de captura.
R\$\) → casa R$) (atenção: você está escapando ) como literal, mas no texto real provavelmente existe (R$), não R$). Se o texto for ... (R$) ..., o padrão deveria ser \(\s*R\$\s*\) para bater com os parênteses.
.*? continua lazy,
) fecha o grupo 1.



\s*R\$\s* → encontra outro R$ (fora de parênteses).


([0-9\.,]+) → grupo 2: captura o número (ex.: 63.922,03).

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
        return (m.group(1), m.group(2)) if m else default

    def extrair_campos_com_regex(self):
        flags = re.DOTALL | re.VERBOSE | re.IGNORECASE
        texto = self.texto_completo

        # print(texto)

        periodo = self.buscar_ocorrencia(
            r"Período de Apuração:.*?([0-9]{2}/[0-9]{2}/[0-9]{4}\s*a\s*[0-9]{2}/[0-9]{2}/[0-9]{4})",
            texto,
            flags=re.DOTALL
        )

        cnpj_matriz = self.buscar_ocorrencia(
            r'CNPJ Matriz:.*?([0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}\-[0-9]{2})',
            texto,
            flags=re.DOTALL
        )

        nome_empresarial = self.buscar_ocorrencia(
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
            r"\(RBA\).*?([0-9.,]+)\s+[0-9.,]+\s+[0-9.,]+",
            texto,
            flags=re.DOTALL
        )
        # print(RBA)

        RBAA = self.buscar_ocorrencia(
            r"\(RBAA\)\s*([0-9\.,]+)",
            texto,
            flags=re.DOTALL
        )
        # print(RBAA)

        limite_receita_1, limite_receita_2 = self.buscar_duplo(
            r"Limite de receita bruta proporcionalizado\s*([0-9\.,]+)\s+([0-9.,]+)",
            texto,
            flags=flags,
        )

        # 1) Pega apenas o bloco 2.2) ... até 2.3)
        m_bloco = re.search(r'2\.2\)\s*Receitas Brutas Anteriores.*?(2\.3\))', texto, flags)
        if m_bloco:
            # Se encontramos o início e o marcador 2.3), cortamos até antes do 2.3)
            inicio = m_bloco.start()
            fim = m_bloco.start(1)  # posição onde começa "2.3)"
            bloco_22 = texto[inicio:fim]
        else:
            # fallback: pega a partir de "2.2)" até o fim
            m_inicio = re.search(r'2\.2\)\s*Receitas Brutas Anteriores', texto, flags)
            bloco_22 = texto[m_inicio.start():] if m_inicio else ""

        # 2) Separa sub-blocos
        # Mercado Interno
        m_interno = re.search(r'2\.2\.1\)\s*Mercado Interno(.*?)(2\.2\.2\))', bloco_22, flags)
        if m_interno:
            bloco_interno = m_interno.group(1)
        else:
            # se não achou delimitador do externo, tenta até o fim do bloco
            m_interno2 = re.search(r'2\.2\.1\)\s*Mercado Interno(.*)', bloco_22, flags)
            bloco_interno = m_interno2.group(1) if m_interno2 else ""

        # Mercado Externo
        m_externo = re.search(r'2\.2\.2\)\s*Mercado Externo(.*)', bloco_22, flags)
        bloco_externo = m_externo.group(1) if m_externo else ""

        padrao_par = re.compile(r'(\d{2}/\d{4})\s*([0-9\.,]+)', flags)
        pares_interno = padrao_par.findall(bloco_interno) if bloco_interno else []
        pares_externo = padrao_par.findall(bloco_externo) if bloco_externo else []

        f_salario = re.compile(r'2\.3\)\s*Folha\ de\ Salários\ Anteriores\s*\(R\$\).*?(?=2\.4\))', flags)
        busca_f_salario = f_salario.search(texto).group()

        valores_f_salarios = re.compile(r'(\d{2}/\d{4})\s*([0-9\.,]+)', flags)
        resultado_f_salarios = valores_f_salarios.findall(busca_f_salario) if busca_f_salario else []
        # print(resultado_f_salarios)

        sal_anteriores = re.compile(
            r'2\.3\.1\)\s*Total\ de\ Folhas\ de\ Salários\ Anteriores.*?(\s*R\$\s*\).*?)\s*R\$\s*([0-9\.,]+)',
            flags)
        busca_sal_anteriores = sal_anteriores.search(texto).group(2)

        fator_r = re.compile(r"2\.4\)\s*Fator\ r.*?(?=2\.5\))", flags)
        busca_fator_r = fator_r.search(texto)
        bloco_24 = busca_fator_r.group(0)
        bloco_24_fator_r = re.compile('Fator r.s*\s*.*?([0-9.,]+)')
        bloco_24_fator_r_busca = bloco_24_fator_r.search(bloco_24)
        # print(bloco_24_fator_r_busca.group(1))

        resumo_declaracao = re.compile(r'2\.6\)\s*Resumo\ da\ Declaração\s*.*?(?=2\.7\))', flags)
        buscar_resumo_declaracao = resumo_declaracao.search(texto)
        bloco_26 = buscar_resumo_declaracao.group(0) if buscar_resumo_declaracao else ''

        compile_resumo_26 = re.compile(r'\s*\(R\$\).*?([0-9.,]+).*?([0-9.,]+)', flags)
        busca_compile_resumo_26 = compile_resumo_26.search(bloco_26)
        bloco_26_valor_auferida = busca_compile_resumo_26.group(1)
        bloco_26_valor_debito_declarado = busca_compile_resumo_26.group(2)
        # print(bloco_26_valor_auferida, bloco_26_valor_debito_declarado)

        compile_bloco_27 = re.compile(
            r"2\.7\)\s*Informações\ da\ Declaração\ por\ Estabelecimento\s*.*?(?=2\.8\))",
            flags
        )
        busca_compile_bloco_27 = compile_bloco_27.search(texto)
        compile_bloco_27_sublime_receita_anual = re.compile(
            r'\s*Sublimite\ de\ Receita\ Anual.*?([0-9.,]+)', flags
        )
        bloco_27 = busca_compile_bloco_27.group(0) if busca_compile_bloco_27 else ''

        busca_bloco_27_sublime_receita_anual = compile_bloco_27_sublime_receita_anual.search(bloco_27)
        sublime_receita_anual = busca_bloco_27_sublime_receita_anual.group(1) if busca_compile_bloco_27 else ''
        # print(bloco_27_sublime_receita_anual)

        bloco_27_recolher_imcs_iss = re.compile(
            r'\s*Impedido\ de\ recolher\ ICMS/ISS\ no\ DAS:\s*.*?([^\n]+)',flags)
        recolher_imcs_iss = bloco_27_recolher_imcs_iss.search(bloco_27).group(1) if busca_compile_bloco_27 else ''
        # print(recolher_imcs_iss)

        bloco_27_receita_bruta_infomada = re.compile(
            r'Receita\ Bruta\ Informada:\s*(\s*R\$\s*).*?([0-9.,]+)', flags)
        receita_bruta_infomada = bloco_27_receita_bruta_infomada.search(bloco_27).group(2) if busca_compile_bloco_27 else ''
        # print(receita_bruta_infomada)

        bloco_27_impostos = re.compile(r'\s*IRPJ.*?\s*Totais\ do\ Estabelecimento', flags)
        impostos = bloco_27_impostos.search(bloco_27).group()
        bloco_27_compile_impostos = re.compile(
            r'\s*Total\s*'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)'
            r'.*?([0-9.,]+)', flags
        )
        busca_valores_impostos = bloco_27_compile_impostos.search(impostos)
        tributos_01 = {
            'IRPJ': busca_valores_impostos.group(1),
            'CSLL': busca_valores_impostos.group(2),
            'COFINS': busca_valores_impostos.group(3),
            'PIS/Pasep': busca_valores_impostos.group(4),
            'INSS/CPP': busca_valores_impostos.group(5),
            'ICMS': busca_valores_impostos.group(6),
            'IPI': busca_valores_impostos.group(7),
            'ISS': busca_valores_impostos.group(8),
            'Total': busca_valores_impostos.group(9),
            'Parcela 1': busca_valores_impostos.group(11),
        }
        # print(tributos_01)

        bloco_27_totais_estabelecimentos = re.compile(
            r'\s*Valor\ Informado\s*.*([0-9.,]+)'
        )
        totais_estabelecimentos = bloco_27_totais_estabelecimentos.search(bloco_27)
        print(totais_estabelecimentos)

        registros = {
            'periodo': periodo,
            'cnpj_matriz': cnpj_matriz,
            'nome_empresarial': nome_empresarial,
            'data_abertura': data_abertura,
            'optante_simples_nacional': optante_simples_nacional,
            'regime_apuracao': regime_apuracao,
            'num_declaracao': num_declaracao,
            'RPA': RPA,
            'RBA': RBA,
            'RBT12': RBT12,
            'RBAA': RBAA,
            'interno': {k: v for (k, v) in pares_interno},
            'externo': {k: v for (k, v) in pares_externo},
            'f_salarios': {k: v for (k, v) in resultado_f_salarios},
        }

        # for k, v in registros.items():
        #     print(f'{k} - {v}')

        # df = pd.DataFrame(registros).sort_values(by=['mercado', 'mes_ano']).reset_index(drop=True)

        # print('1', df)
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
