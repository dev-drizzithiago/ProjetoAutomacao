from wsgiref.util import request_uri

from librouteros import connect
from dotenv import load_dotenv
from time import sleep
import mikrotik_logs
import mikrotik_ips
import manipulacao_icmp
import os

load_dotenv()

class ConexaoFirewall:
    def __init__(self):

        self.api_mikrotik = None

        self.user_fw = os.getenv('mikro_USERNAME', '')
        self.pass_fw = os.getenv('mikro_PASSWORD', '')
        self.host_fw = os.getenv('mikro_HOST_FW', '')
        self.port_fw = os.getenv('mikro_PORT_FW', '')

    def conexao_fw(self):
        try:
            self.api_mikrotik = connect(
                username=str(self.user_fw),
                password=str(self.pass_fw),
                host=str(self.host_fw),  # IP do seu MikroTik
                port=str(self.port_fw),  # Porta padrão da API
            )
            print()
            print('---' * 30)
            print('Conexão com o mikrotik realizado com sucesso. ')
            return self.api_mikrotik

        except Exception as error:
            print(f'Erro ao conectar ao mikrotik: {error}')
            return None


if __name__ == '__main__':

    MSG_END_IP_ESGOTADO = "defconf: failed to give out IP address: pool <dhcp> is empty"

    # Iniciando o obj
    iniciando_obj_mikrotik = ConexaoFirewall()

    # conectando ao mikrotik
    conexao_fw = iniciando_obj_mikrotik.conexao_fw()

    if conexao_fw is None:
        ...
    else:
        while True:
            print('Processando...')

            # Buscando os logs dentro do mikrotik.
            obj_logs = mikrotik_logs.BuscandoLogsMikrotik(conexao_fw)

            # Filtrando apenas os logs de DHCP
            obj_logs.log_dhcp(None)

            # Após analisados e formatado as informações chegam em forma de lista.
            result_ip = obj_logs.analise_de_logs()

            # Abrindo o obj para imcp.
            obj_icmp = manipulacao_icmp.ManipulacaoIcmpHosts()

            # Processa a lista de ip que chegaram dos logs.
            informacoes_icmp = obj_icmp.ping_icmp_redeLocal(result_ip)

            # Mostra o resultado do icmp.
            print()
            print(f'Quantidade IP: {len(informacoes_icmp['LISTA_PING_ON'])}')
            print(f'Quantidade HostName: {len(informacoes_icmp['LISTA_HOSTNAME'])}')
            print()
            for chave, valor in informacoes_icmp.items():
                print(f'{chave}:')
                print('---' * 30)
                for item in valor:
                    print(item)
                print()
                print()

            sleep(600)

