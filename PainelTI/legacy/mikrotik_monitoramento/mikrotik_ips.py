
class InfoEndIp:
    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal

    def lease_ativas(self):

        leases = self.obj_conexao_fw.path('ip', 'dhcp-server', 'lease')
        active_leases = [lease for lease in leases if lease.get('status') == 'bound']

        return len(active_leases)
