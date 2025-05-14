from time import sleep
import speedtest
import teste_velocidade

linha_formatacao = '- - ' * 20
contador_teste = 1

while True:

    iniciando_obj = teste_velocidade.TesteVelocidade()

    print(f'{contador_teste}° teste de velocidade')
    print(linha_formatacao)

    try:
        print(f'Teste Download: [{iniciando_obj.testando_conexao_down()}]')
        print(f'Teste Upload: [{iniciando_obj.testando_conexao_up()}]')
        print(f'Tempo de resposta: [{iniciando_obj.teste_conexao_tempo_resposta()}]')

        print(f'Seu endereço de internet: [{iniciando_obj.dados_cliente()["IP"]}]')
        print(f'Sua operadora: [{iniciando_obj.dados_cliente()["Operadora"]}]')

        print(f'{contador_teste}° Finalizado!')
        print(linha_formatacao)
        sleep(120)
    except speedtest.ConfigRetrievalError:
        print('Você tentou várias em um curto periodo, aguarda alguns minutos')
        sleep(120)

    contador_teste += 1

