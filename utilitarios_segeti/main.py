from time import sleep
import subprocess
import os

class UtilitariosSegetiDigital:

    ## -----------------------------------------------------------------------------------------------------------------
    ## Bloco dos parâmetros para o method adicionar redes wifi
    # Redes que estão disponível no ambiente.
    redes_disponiveis = [
        {'nome': 'Segeti-Visitantes', 'senha': '98Ps@visit34'},
        {'nome': 'Staff-Direito', 'senha': 'Sc89#28!54'},
        {'nome': 'Staff-Esquerdo', 'senha': 'Yt87*67Jh'},
        {'nome': 'Sala-Descom', 'senha': '74ou@87ik'},
        {'nome': 'Sala-Treinamento', 'senha': '67Uj$er89'},
    ]
    local_xml_pc_local = r'c:\xml_local'
    arquivo_xml = r"\perfil_wifi.xml"

    try:
        os.makedirs(local_xml_pc_local)
    except FileExistsError:
        ...
    ## -----------------------------------------------------------------------------------------------------------------

    def adicionar_rede_wifi(self):
        """
            Função responsável em adicionar as redes que estão disponivel para os funcionários da segeti.
            :param: perfil_xml - Cria um arquivo xml para que o powershel identifique os parâmtros da rede.
            :return:
            """

        # Serão adicionadas a quantidade de rede que esta na lista.
        for rede in self.redes_disponiveis:

            perfil_xml = f"""
                <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                    <name>{rede['nome']}</name>
                    <SSIDConfig>
                        <SSID>
                            <name>{rede['nome']}</name>
                        </SSID>
                    </SSIDConfig>
                    <connectionType>ESS</connectionType>
                    <connectionMode>auto</connectionMode>
                    <MSM>
                        <security>
                            <authEncryption>
                                <authentication>WPA2PSK</authentication>
                                <encryption>AES</encryption>
                                <useOneX>false</useOneX>
                            </authEncryption>
                            <sharedKey>
                                <keyType>passPhrase</keyType>
                                <protected>false</protected>
                                <keyMaterial>{rede['senha']}</keyMaterial>
                            </sharedKey>
                        </security>
                    </MSM>
                </WLANProfile>
                """

            # Cria o arquivo completo do arquivo xml
            caminho_completo_xml = rf'{local_xml_pc_local}\{arquivo_xml}'

            # Cria o arquivo xml para o powershell conseguir ler.
            with open(caminho_completo_xml, "w") as arquivo:
                arquivo.write(perfil_xml)

            comando_shell_add_wifi = f'netsh wlan add profile filename="{caminho_completo_xml}"'

            try:
                subprocess.run(['powershell', '-Command', comando_shell_add_wifi],
                               capture_output=True, text=True, shell=True)
                print(f' -Rede {rede['nome']} adicionada...')

            except Exception as error:
                print(f'Ocorreu erro na execusão do programa: {error}')
                # Quando ocorrer algum erro, programa sera fechado.
                return (f'Não foi possível adicionar a rede {rede['nome']} \n'
                        f'Entre em contato com o desenvolvedor \n'
                        f'th_grifon@hotmail.com')



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


