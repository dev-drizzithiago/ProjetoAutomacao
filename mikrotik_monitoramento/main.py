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
        except Exception as error:
            print(f'Erro ao conectar no mikrotik: {error}')

        return self.api_mikrotik


if __name__ == '__main__':

    iniciando_obj_log = mikrotik_logs.BuscandoLogsMikrotik()
    logs = iniciando_obj_log.log_dhcp()

    iniciando_obj_ip = mikrotik_ips.InfoEndIp()
    active_leases_ips = iniciando_obj_ip.lease_ativas()
    print(active_leases_ips)

    # for log in logs:
    #     print(log)