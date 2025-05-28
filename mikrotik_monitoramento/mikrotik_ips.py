import mikrotik_logs


class InfoEndIp:
    def __init__(self):
        self.conexao_firewall = None

    def lease_ativas(self):
        self.conexao_firewall = mikrotik_logs.BuscandoLogsMikrotik()
        fw_conectado = self.conexao_firewall.conexao_fw()
        leases = fw_conectado.path('ip', 'dhcp-server', 'lease')

        return leases

if __name__ == "__main__":
    ...