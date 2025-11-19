from time import sleep


if __name__ == "__main__":
    while True:
        print(
            """
            [ 1 ] Adicionar Redes Wifi.
            [ 2 ] Configurar adaptadores de rede.
            [ 3 ] Desbloquear Visualização no windows.
            [ 0 ] Sair. 
            """
        )
        print('---' * 30)
        try:
            opc = int(input('Escolha uma opção: '))

            if opc == 1:
                ...
            elif opc == 2:
                ...
            elif opc == 3:
                ...
            elif opc == 0:
                print('---' * 30)
                print('Saindo do programa')
                sleep(2)
            else:
                print('Opção não existe.')

        except ValueError:
            print()
            print('---' * 30)
            print('Valor incorreto')


