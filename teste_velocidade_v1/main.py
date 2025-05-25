
import os
import sys
from time import sleep
import speedtest
import teste_velocidade
import analise_dados
from _janela_view import JanelaPrincipal
from threading import Thread

from PySide6.QtWidgets import QApplication

linha_formatacao = '- - ' * 20

app = QApplication(sys.argv)
janela = JanelaPrincipal()
janela.show()

def inicio_teste():
    contador_teste = 1
    os.system('cls')
    while True:
        try:
            iniciando_obj = teste_velocidade.TesteVelocidade()

            print()
            print(f'{contador_teste}° teste de velocidade - {iniciando_obj.data_hora_certa()} \nProcessando, aguarde...')
            print(linha_formatacao)

            dados_teste_velocidade = {
                'data_teste': iniciando_obj.data_hora_certa(),
                'teste_download': iniciando_obj.testando_conexao_down(),
                'teste_upload': iniciando_obj.testando_conexao_up(),
                'tempo_resposta': iniciando_obj.teste_conexao_tempo_resposta(),
                'dados_cliente': [iniciando_obj.dados_cliente()["IP"], iniciando_obj.dados_cliente()["Operadora"]],
            }

            print(f'Teste Download: [{iniciando_obj.testando_conexao_down()}]')
            print(f'Teste Upload: [{iniciando_obj.testando_conexao_up()}]')
            print(f'Tempo de resposta: [{iniciando_obj.teste_conexao_tempo_resposta()}]')

            print(f'Seu endereço de internet: [{iniciando_obj.dados_cliente()["IP"]}]')
            print(f'Sua operadora: [{iniciando_obj.dados_cliente()["Operadora"]}]')

            # Criando data.csv
            dados_Data_Frame = analise_dados.AnaliseDados(dados_teste_velocidade).create_dataframe()

            if not os.path.exists('data.csv'):
                dados_Data_Frame.to_csv('data.csv', mode='a', header=True, index=False)
            else:
                dados_Data_Frame.to_csv('data.csv', mode='a', header=False, index=False)

            # lendo data.csv
            leitura_dados = analise_dados.AnaliseDados.view_dados_('data.csv')
            print(leitura_dados)

            print()
            print(f'{contador_teste}° teste finalizado!')
            print(linha_formatacao)

            contador_teste += 1
            sleep(1800)

        # Teste de servidor
        except speedtest.ConfigRetrievalError:
            print("Aguarde um momento... servidor de teste não esta respondendo")
            sleep(120)


thread_teste = Thread(target=inicio_teste, daemon=True)
thread_teste.start()

sys.exit(app.exec())
