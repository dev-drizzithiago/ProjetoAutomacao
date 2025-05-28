from librouteros import connect
from dotenv import load_dotenv
import os
load_dotenv('.env')

class BuscandoLogsMikrotik:
    def __init__(self):
        self.api_mikrotik = None

        self.user_fw = os.getenv('mikro_USERNAME', '')
        self.pass_fw = os.getenv('mikro_PASSWORD', '')
        self.host_fw = os.getenv('mikro_HOST_FW', '')
        self.port_fw = os.getenv('mikro_PORT_FW', '')

    def conexao_fw(self):
        self.api_mikrotik = connect(
            username=str(self.user_fw),
            password=str(self.pass_fw),
            host=str(self.host_fw),  # IP do seu MikroTik
            port=str(self.port_fw),  # Porta padrão da API
        )

        return self.api_mikrotik

    def log_dhcp(self):
        self.conexao_fw()
        logs = self.api_mikrotik.path('log')
        return logs