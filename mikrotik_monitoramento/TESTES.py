from dotenv import load_dotenv
load_dotenv()
from librouteros import connect
import os


# Conectar ao MikroTik
api = connect(
    username=os.getenv('mikro_USERNAME', ''),
    password=os.getenv('mikro_PASSWORD', ''),
    host=os.getenv('mikro_HOST_FW', ''),
    port=os.getenv('mikro_PORT_FW', '')
)

# Obter leases do DHCP
leases = api.path('ip', 'dhcp-server', 'lease')

# Contar quantos IPs estão atribuídos
ativos = [lease for lease in leases if lease.get('status') == 'bound']
print(f"Total de IPs atribuídos: {len(ativos)}")
