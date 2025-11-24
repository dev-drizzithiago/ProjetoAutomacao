"""
SCRIPT VERSÃO 2
- Realizado algumas correções no portugues e algumas mudanças na ordem que as funções seram executada.

- O obj desse programa resolver o problema de dominio.
- O dominio que foi atribuido na rede interna é o mesmo que o dominio publico;
    1) Interno → segeticonsultoria.com
    2) Externo → www.segeticonsultoria.com
- Explicando o que ocorre.
    * Quando a endereço dns primario esta configurado apotando para o servidor interno, todas as funcionalidades do
    dominio funcionam perfeitamente, mas pelo fato do dominio ser identico ao site www.segeticonsultoria.com,
    deixa todos dentro da rede interna sem acesso ao site.
    * Quando o dns primario é apontado para o ip 8.8.8.8 e o secundário apontado para o servidor 192.168.0.10,
    muitas das vezes ocorre problema com as políticas do AD.
    * Quando um sitema faz solicitação para o dominio segeticonsultoria.com e o dns primário está apontado para o
    servidor, a requisão chega no servidor, se o serviço requerido estiver conforma as políticas o sistema vai
    encaminha a resposta correta para o solicitante. Mas quando o solicitante entrar com uma requição de site, como
    o www.segeticonsultoria.com, como o servidor não possui o serviço de web, o solicitante recebe uma negativa
    não conseguindo acesso o site.
    * Ao contrário tambem ocorre, quando o dns primario esta com o endereço publico, algumas requisições são
    encaminhadas para o servidor de web, como não possui o serviço uma negativa que o utilizador vai receber.
    * Configurando o arquivo vai ajudar a manter o sistema sem esse problema.
    * Como a rede precisa ter comunicação com o servidor, o unico site que apresenta o problema é o da
    propria segeti.
"""
import os
import sys
import socket
import ctypes
import subprocess
from time import sleep

site_segeti = "www.segeticonsultoria.com"
host_local = "192.168.0.10 segeticonsultoria.com"
host_site = "34.149.87.45 www.segeticonsultoria.com"
hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
caminha_wifi_xml = ''

# Get-NetAdapter | Select-Object Name, InterfaceDescription, MediaType | Sort-Object Name
# Get-WinSystemLocale  Para descobrir o idioma do sistema

class ConfigAdpRedes:
    # Verifica se o programa foi executado com privilégios de administrator
    def add_host_entry(self):
        """
        - Função ficará responsável em adicionar duas linhas ao arquivo de hosts, que fica na pasta do system32.
        O obj é fazer com que os sistemas da rede estabeleça o endereço dns primario apontando para o servidor, com o ip
        192.168.0.10 e o secundário apontado para o dns public 8.8.8.8.
        """
        print()
        print('Adicionando a resolução da url www.segeticonsultoria.com, aguarde!')

        # Ler o conteúdo atual do arquivo hosts
        with open(hosts_file, 'r') as file:
            linhas = file.readlines()

        # Corrige linha por linha, removendo os espaços e o carectere para pular linha: "\n"
        linhas = [linha.strip().replace('\n', '') for linha in linhas]

        # Verificar se a entrada já existe
        if host_site in linhas:
            print('O sistema consegue resolver o nome do dominío "www.segeticonsultoria.com"')
            sleep(5)
        else:
            # Adicionar a entrada ao arquivo hosts
            try:
                with open(hosts_file, 'a') as file:
                    file.write(f"\n{host_site}\n{host_local}\n")
                print(f"Entrada adicionada: {host_site} e {host_local}")
            except PermissionError:
                print('Você não tem autorização para realizar esse processo')
                print('Contate o suporte.')
                sleep(10)

    def validate_ip(self):
        print()
        print('Validando endereço de IPV4:')
        print('----' * 20)

        site_segeti = "www.segeticonsultoria.com"
        with open(hosts_file) as arquivo:
            linhas_verificacao = arquivo.readlines()

        valor_end_ip = str([linha.split()[0] for linha in linhas_verificacao if site_segeti in linha])
        endIP_reg = valor_end_ip.replace('[', '').replace(']', '').replace("'", '')

        try:
            ip_address = socket.gethostbyname(site_segeti)
            if ip_address == endIP_reg:
                print('Endereço não foi modificado')
                return False
            else:
                print(f"O endereço de IP foi modificado: {ip_address}")
                return True
        except socket.gaierror:
            print("nome do dominio não foi resolvido")

    def configurando_adaptador_rede(self, valor_de_entrada):
        """
        Função vai ser responsável por modificar o nome do adaptador para um padrão e configurar todos os
        adaptadores de rede como DHCP.
        :param valor_de_entrada: Vai receber o nome e o tipo do adaptador, se é cabo ou wifi
        :return: Configura um novo nome nos adaptadores e todoas as conexões vai ficar com DHCP.
        """
        print()
        print("Configurando seus adaptadores de rede, aguarde...")
        print('----' * 20)

        # ------------------------------------------------------------------------------------------------------------------
        # Define o nome dos adaptadores.
        nome_tipo_conexao_cabo = '_SEGETI_CABO_802_3'
        nome_tipo_conexao_wifi = '_SEGETI_WIFI_802.11'

        # Como existe varios adaptadores é preciso fazer um loop para cada processo.
        indice = 1

        for lista in valor_de_entrada:

            # A linha a baixo, pega a lista e transforma em dicionario, pegando apenas os valores, nome e tipo do adp.
            valor_dict_adp = dict(lista).values()

            # A proxima lista, apor pega o nome e tipo, é transformado novamente em lista para buscar por indices.
            valor_tipo_adp = list(valor_dict_adp)

            # Com a nova lista, é iterado os valore, nome e tipo e colocado na suas respetivas variaveis.
            nome_adp = str(valor_tipo_adp[0]).strip()
            tipo_adp = str(valor_tipo_adp[1]).strip()

            # Conforme for a tecnologia, é realizado um filtro para definir se é conexão por cabo ou wifi.
            if tipo_adp == '802.3':
                novo_nome_interface = nome_tipo_conexao_cabo
            elif tipo_adp == '802.11':
                novo_nome_interface = nome_tipo_conexao_wifi
            nome_novo_adp = f'{indice}{novo_nome_interface}'

            if nome_adp != str(f'{indice}{novo_nome_interface}'):
                # A linha abaixo, os nomes dos adp serão renomeados para o nome padrão.
                subprocess.run([
                    'netsh', 'interface', 'set', 'interface',
                    f'name="{nome_adp}"', f'newname={nome_novo_adp}'
                ])
                print()
                print(f"Configurando o adaptador {nome_novo_adp}")

                # Depois que for renomeada será realizada a configuração de rede em DHCP
                # Lembrando que para realizar esse processo, é preciso executar o código com privilégios de adm.
                comando_shell_dhcp = f'netsh interface ip set address name="{novo_nome_interface}" source=dhcp'
                subprocess.run(["powershell", "-Command", comando_shell_dhcp], shell=True)
            else:
                print()
                print(f"Configurando o adaptador {nome_novo_adp}")
                # Depois que for renomeada será realizada a configuração de rede em DHCP
                # Lembrando que para realizar esse processo, é preciso executar o código com privilégios de adm.
                print(f'Configurando adaptador de rede {nome_novo_adp} com IP dinamico (DHCP)')
                sleep(1)
                subprocess.run([
                    'netsh', 'interface', 'ip', 'set', 'address', 'name=' + nome_novo_adp, 'source=dhcp'
                ])
                print(f'Configurando adaptador de rede {nome_novo_adp} com DNS dinamico (DHCP)')
                sleep(1)
                subprocess.run([
                    'netsh', 'interface', 'ip', 'set', 'dnsservers', 'name=' + nome_novo_adp, 'source=dhcp'
                ])
            indice += 1
        print('Configuração dos adaptadores concluida')
        # ------------------------------------------------------------------------------------------------------------------

    def buscando__info__adaptadores__(self):
        """
        Função será responsável em busca o nome das ‘interfaces’ de rede.
        :return: Os valores serão o nome completo de cada "interface" e o tipo de conexão, que vai se representado com
        o padrão:
        - IEEE 802.3: que é um padrão referente a conexão cabeado e;
        - IEEE 802.11: referencia as conexões de WI-FI.
        - O Bluetooth segue as normas do padrão 802.15.1, que também usa conexão de rádio
        """
        print()
        print('Buscando informações dos adaptadores, aguarde...!')
        print('----' * 20)
        #
        # Comando que busca as informações dos acaptadores de rede:
        #
        comando_power_shell = "Get-NetAdapter | Select-Object Name, MediaType"
        resultado_info = subprocess.run(
            ['powershell', '-Command', comando_power_shell],
            capture_output=True, text=True
        )
        #
        # Após busca as informações, os dados são transferidos para uma variável
        valor_info_adptadores = resultado_info.stdout
        #
        # Uma lista é criada para amarzenar o dicionario que vai conter os nomes e tecnologia dos adaptadores.
        lista_interfaces = []
        dict_valores_interfaces = {}
        #
        # É gerado um loop com as informações que possui na lista. Com o comando "splitlines()"
        # os dados são pegos linha/linha
        for valor_interfaces in valor_info_adptadores.splitlines():
            #
            # Filtro criado para pega apenas as informações do padrão IEEE.
            if '802.3' in valor_interfaces or '802.11' in valor_interfaces:
                #
                # Fatiamento das informações pertinentes.
                # Na primeira linha pega o último valor o padrão que define o tipo da conexão.
                # Na segunda linha é pego apenas o nome do adaptador.
                #
                # 1) As informações são primeiro separada por espaço, que construido uma 'lista'
                # 2) O metodo strip() remove os espaços do começo e final dos dados.
                tipo_conexao = valor_interfaces.strip().split(' ')[-1]
                nome_conexao = valor_interfaces.strip().split(' ')[:-2]
                #
                # Depois que todos os dados separadores, é feito a formatação para inserir dentro da lista.
                valor_nome_interfaces = ' '.join(nome_conexao)
                dict_valores_interfaces['nome'] = valor_nome_interfaces.strip()
                dict_valores_interfaces['tipo'] = tipo_conexao.strip()
                #
                # Lista que recebe os dicionários
                lista_interfaces.append(dict_valores_interfaces.copy())
        print()
        print('Busca concluida!')
        return lista_interfaces

    def func_teste_site_empresa(self):
        """
        Função ira realizar um teste de ping no site www.segeticonsultoria.com
        :return: vai ser encaminha o valor True e o programa será finalizado.
        """
        print()
        print('Obtendo resposta do domínio externo, aguarde...!')
        print('----' * 20)

        # Guarda o comando de ping na variavel "comando_ping"
        comando_ping = f'ping {site_segeti} -4'

        # É executado o "comando_ping" usando o powershell
        valor_icmp = subprocess.run(
            ['powershell', '-Command', comando_ping],
            capture_output=True, text=True
        )

        # Os valores da busca é guardado na variavel "valor_texto_ping"
        valor_texto_ping = valor_icmp.stdout

        # Loop que vai ser reposavel em pegar linha por linha para ser tratado.
        for result_ping in valor_texto_ping.splitlines():

            # Busca as linhas que possui o valor "Pacotes"
            if 'Pacotes' in result_ping:

                # Fatia as linhas que foram encontrada e colocar na variavel apenas o valor numerico
                resultado_pacotes_enviados = result_ping.strip().split(',')[0].split('=')[-1]
                resultado_pacotes_recebidos = result_ping.strip().split(',')[1].split('=')[-1]

                # Se o valor for "0" mostra que no ping nenhum pacote voltou então é validado para adicionar a linha no
                # arquivo hosts
                # Caso o valor seja difente, mas positivo, quer dizer que o sistema resolve,
                # nesse caso não é necessário adicionar a linha no arquivo hosts.
                if resultado_pacotes_recebidos == 0:
                    print(f'Foram enviados [{resultado_pacotes_enviados}], [{site_segeti}], '
                          f'[{resultado_pacotes_recebidos}] pacotes responderam')
                else:
                    print(f'Foram enviados [{resultado_pacotes_enviados}], [{site_segeti}], '
                          f'[{resultado_pacotes_recebidos}] pacotes responderam com sucesso.')
                    return True

    # O script só vai continuar depois for executador como administrador.
    """
    if is_admin():
    
        if func_teste_site_empresa():
    
            print()
            print('------' * 20)
            print('Site www.segeticonsultoria.com esta respondendo, não é preciso adicionar uma regra dentro do \n'
                  'arquivo hosts. Mas vamos configurar seus adaptadores para que fique no padrão Segeti. \n'
                  'Para a configuração funcionar corretamente é preciso executar o programa como Administrador')
            sleep(10)
    
            # 1) Busca as informações sobre os adaptadores, como nome, o tipo de tecnologia que possui.
            resultado_busca_info_adaptadores = buscando__info__adaptadores__()
    
            # 2) Com as informações os dados são levados para que os
            # adaptadores sejam configurados com novos parametros.
            configurando_adaptador_rede(resultado_busca_info_adaptadores)
    
        else:
    
            # 3) Caso o site não responde, após os adaptadores serem configurados,
            # é adicionado a regra dentro do arquivo hosts
            add_host_entry()
    
            # 4) Função vai verificar se o endereço de ip do site "www.segeticonsultoria.com" continua o mesmo,
            # caso tenha sido alterado é add uma nova entrada. Esse processo precisa
            # ser inserido na inicialização do win.
    
            if validate_ip():
                add_host_entry()
    
            func_teste_site_empresa()
    
    else:
    
        print()
        print()
        print("A execusão requer elevação.")
    
    # ---------------------------------------------------------------------------------------------------------------------
    # Finalizando o script
    print()
    print()
    print('------' * 20)
    input('Aperte "Enter" para finalizar.')
    """