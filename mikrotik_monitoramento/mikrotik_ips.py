import mikrotik_logs


class InfoEndIp:
    def __init__(self):
        self.conexao_firewall = None

    def lease_ativas(self):
        self.conexao_firewall = mikrotik_logs.BuscandoLogsMikrotik()
        fw_conectado = self.conexao_firewall.conexao_fw()
        leases = fw_conectado.path('ip', 'dhcp-server', 'lease')
        active_leases = [lease for lease in leases if lease.get('status') == ['bound']]

        return active_leases

if __name__ == "__main__":
    iniciando_obj_ip = InfoEndIp()
    ip_activate = iniciando_obj_ip.lease_ativas()
    print(len(ip_activate))