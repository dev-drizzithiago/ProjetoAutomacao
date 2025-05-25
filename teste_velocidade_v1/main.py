
import os
from time import sleep
import speedtest
import teste_velocidade
import analise_dados
from threading import Thread

linha_formatacao = '- - ' * 20

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


            try:
                # Criando data.csv
                dados_Data_Frame = analise_dados.AnaliseDados(dados_teste_velocidade).create_dataframe()

                # Salvando o arquivo, dentro da pasta do projeto.
                if not os.path.exists('data.csv'):
                    dados_Data_Frame.to_csv('data.csv', mode='a', header=True, index=False)
                else:
                    dados_Data_Frame.to_csv('data.csv', mode='a', header=False, index=False)
            except Exception as error:
                print(f'Ocorreu um erro ao salvar as informações: {error}')

            print()
            print(f'{contador_teste}° teste finalizado!')
            print(linha_formatacao)
            print()

            # Conta cada teste no decorrer do processo.
            contador_teste += 1

            print(f'Aguardado o {contador_teste}° teste')
            sleep(3600)

        # Teste de servidor
        except speedtest.ConfigRetrievalError:
            print("Aguarde um momento... servidor de teste não esta respondendo")
            sleep(120)


def visualizar_dados_do_teste():

    # visualizando o arquivo data.csv
    leitura_dados = analise_dados.AnaliseDados.view_dados_('data.csv').reset_index(drop=True)

    print(leitura_dados.keys())

    for indice in range(len(leitura_dados)):
        print(leitura_dados.iloc[indice])
        print('- -' * 30)


while True:
    try:
        print(
            """
                [1] Iniciar Teste
                [2] Visualizar resultados
                [0] Sair 
            """
        )
        opc = int(input('Escolha uma opção: '))

        if opc == 1:
            inicio_teste()
        elif opc == 2:
            visualizar_dados_do_teste()
        elif opc == 0:
            print('Fechando o processo...')
            sleep(1)
            break
        else:
            print('Opção não existe.')

    except TypeError:
        print('Opção incorreta, tent de novo')

