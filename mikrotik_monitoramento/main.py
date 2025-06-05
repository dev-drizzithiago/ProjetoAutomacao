from librouteros import connect
from dotenv import load_dotenv
import mikrotik_logs
import mikrotik_ips
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


if __name__ == '__main__':
    MSG_END_IP_ESGOTADO = "defconf: failed to give out IP address: pool <dhcp> is empty"
    iniciando_obj_mikrotik = ConexaoFirewall()
    conexao_fw = iniciando_obj_mikrotik.conexao_fw()

    obj_logs = mikrotik_logs.BuscandoLogsMikrotik(conexao_fw)
    obj_logs.log_dhcp()
    obj_logs.analise_de_logs()

    obj_info_ip = mikrotik_ips.InfoEndIp(conexao_fw)
    quantidade_clientes_dhcp = obj_info_ip.lease_ativas()
    print(quantidade_clientes_dhcp)
