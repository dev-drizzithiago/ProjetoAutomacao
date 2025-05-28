
class BuscandoLogsMikrotik:
    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal
        self.lista_atribuicao_ip = list()
        self.lista_desatribuicao_ip = list()
        self._logs = None

    def log_dhcp(self):
        self._logs = self.obj_conexao_fw.path('log')
        return self._logs

    def analise_de_logs(self):
        logs = self._logs
        for log in logs:

            chaves_logs = {
                '1': '.id',
                '2': 'time',
                '3': 'topics',
                '4': 'message',
            }
            if log[chaves_logs['3']] == 'dhcp,info':
                if 'defconf assigned' in log[chaves_logs['4']]:
                    mac = str(log[chaves_logs['4']]).split('for')[-1].strip()
                    print('a', mac)
                    self.lista_atribuicao_ip.append(mac)
                elif 'defconf deassigned' in log[chaves_logs['4']]:
                    mac = str(log[chaves_logs['4']]).split('for')[-1].strip()
                    print('d', mac)
                    self.lista_desatribuicao_ip.append(mac)


    def log_conexao_internet(self):
        ...

    def log_conxao_bkp_internet(self):
        ...