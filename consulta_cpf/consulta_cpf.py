#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests,json,sys

# Script simples para consulta de dados na base dados nacional do SUS utilizando o CPF.
# Jhonathan Davi A.K.A jh00nbr / Insightl4b lab.insightsecurity.com.br
# Blog: lab.insightsecurity.com.br
# Github: github.com/jh00nbr
# Twitter @jh00nbr

cpf = 'xx'
link = f"https://api.cpfhub.io/cpf/{cpf}"
try:
    req = requests.get(link, headers={'x-api-key': ''})
    dados = json.loads(req.content.decode("utf-8"))
    print(dados)
except IndexError:
    print ("Entrada inválida! Adicione o CPF válido como argumento.\nEx.: ~$ python cpf_consulta_api_sus.py 00000000000")