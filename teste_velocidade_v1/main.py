from time import sleep
import speedtest
import teste_velocidade

linha_formatacao = '- - ' * 20
contador_teste = 1

while True:

    iniciando_obj = teste_velocidade.TesteVelocidade()

    dados_teste_velocidade = {
        'data_teste': iniciando_obj.data_hora_certa(),
        'teste_download': iniciando_obj.testando_conexao_down(),
        'teste_upload': iniciando_obj.testando_conexao_up(),
        'tempo_resposta': iniciando_obj.teste_conexao_tempo_resposta(),
        'dados_cliente': [iniciando_obj.dados_cliente()["IP"], iniciando_obj.dados_cliente()["Operadora"]],
    }

    print()
    print(f'{contador_teste}° teste de velocidade - {iniciando_obj.data_hora_certa()}')
    print(linha_formatacao)

    try:
        print(f'Teste Download: [{iniciando_obj.testando_conexao_down()}]')
        print(f'Teste Upload: [{iniciando_obj.testando_conexao_up()}]')
        print(f'Tempo de resposta: [{iniciando_obj.teste_conexao_tempo_resposta()}]')

        print(f'Seu endereço de internet: [{iniciando_obj.dados_cliente()["IP"]}]')
        print(f'Sua operadora: [{iniciando_obj.dados_cliente()["Operadora"]}]')

        print(f'{contador_teste}° teste finalizado!')
        print(linha_formatacao)
        sleep(1800)
    except speedtest.ConfigRetrievalError:
        print('Você tentou várias em um curto periodo, aguarda alguns minutos')
        sleep(240)

    contador_teste += 1
