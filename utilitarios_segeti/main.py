from time import sleep
import subprocess
import os

import adicionar_redes_wifi
import debloquear_MOTW

import ctypes
import sys

class UtilitariosSegetiDigital:

    def chamar_confi_wifi_segeti(self):
        adicionar_redes_wifi.RedesWifi()

    def chamar_desbloquear(self):
        obj_desbloqueio = debloquear_MOTW.DesbloqueioViewWindows()
        print(
            "[ 1 ] Desbloquear visualização do Windows\n"
            "[ 2 ] Bloquear visualização do Windows\n"
        )

        comando_desbloqueio_registro = obj_desbloqueio.comando_powershell_registro_windows_desbloqueio
        comando_bloqueio_registro = obj_desbloqueio.comando_powershell_registro_windows_bloqueio

        resposta = int(input("Escolha uma opção: "))
        if resposta == 1:
            process_finalizado = obj_desbloqueio.desbloquear_view_windows()
            print(process_finalizado)
            if process_finalizado:
                obj_desbloqueio.configurar_registro(comando_desbloqueio_registro)
                obj_desbloqueio.reiniciar_explorer()
                input('Processo finalizado, aperta Enter para fechar')


        elif resposta == 2:
            process_finalizado = obj_desbloqueio.bloquear_view_windows()
            print(process_finalizado)
            if process_finalizado:
                obj_desbloqueio.configurar_registro(comando_bloqueio_registro)
                obj_desbloqueio.reiniciar_explorer()
                input('Processo finalizado, aperta Enter para fechar')


if __name__ == "__main__":
    obj_utilitario = UtilitariosSegetiDigital()
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    ## Se o app não foi elevado vai abrir a janela para solicita as credinciais de administrador.
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None,  # handle (não usado)
            "runas",  # O verbo que força o UAC
            sys.executable,  # O arquivo a ser executado (o interpretador Python)
            " ".join(sys.argv),  # Os argumentos (o nome do seu script)
            None,  # diretório de trabalho
            1  # mostra a janela
        )
        sys.exit(0)  # Sai do script original

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
                obj_utilitario.chamar_confi_wifi_segeti()
            elif opc == 2:
                ...
            elif opc == 3:
                obj_utilitario.chamar_desbloquear()
            elif opc == 0:
                print('---' * 30)
                print('Saindo do programa')
                sleep(2)
                break
            else:
                print('Opção não existe.')

        except ValueError:
            print()
            print('---' * 30)
            print('Valor incorreto')


