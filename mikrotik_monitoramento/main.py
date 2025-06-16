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

            print('Conexão realizado com sucesso. ')
            return self.api_mikrotik

        except Exception as error:
            print(f'Erro ao conectar no mikrotik: {error}')
            return None


if __name__ == '__main__':

    MSG_END_IP_ESGOTADO = "defconf: failed to give out IP address: pool <dhcp> is empty"
    iniciando_obj_mikrotik = ConexaoFirewall()
    conexao_fw = iniciando_obj_mikrotik.conexao_fw()
    if conexao_fw is None:
        print()
    else:
        while True:
            print('Processando...')
            # obj_logs = mikrotik_logs.BuscandoLogsMikrotik(conexao_fw)
            # obj_logs.log_dhcp(None)
            # result_ip = obj_logs.analise_de_logs()
            # # print(result_ip)
            # # print('Quantidades de ip: ', len(result_ip))
            #
            #
            # obj_info_ip = mikrotik_ips.InfoEndIp(conexao_fw)
            # quantidade_clientes_dhcp = obj_info_ip.lease_ativas()
            # print(quantidade_clientes_dhcp)

            # obj_icmp = manipulacao_icmp.ManipulacaoIcmpHosts()
            # result = obj_icmp.ping_icmp_redeLocal(result_ip)

            # print("IP's respondendo", len(result_ip))
            # print()
            # for chave, valor in result.items():
            #     print(f'{chave}:')
            #     print('---' * 30)
            #     for item in valor:
            #         print(item)
            #     print()
            #     print()

            sleep(600)

