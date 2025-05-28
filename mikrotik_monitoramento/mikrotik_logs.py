


class BuscandoLogsMikrotik:
    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal

    def log_dhcp(self):
        logs = self.obj_conexao_fw.path('log')
        return logs

    def log_conexao_internet(self):
        ...

    def log_conxao_bkp_internet(self):
        ...