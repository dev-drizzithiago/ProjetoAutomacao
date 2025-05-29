from datetime import datetime


class BuscandoLogsMikrotik:
    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal

        self.lista_atribuicao_ip = list()
        self.lista_desatribuicao_ip = list()

        self._logs = None

    def log_dhcp(self):
        self._logs = self.obj_conexao_fw.path('log')
        return self._logs

    def log_conexao_internet(self):
        ...

    def log_conxao_bkp_internet(self):
        ...

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
                    divisao_itens = mac.split(' ')
                    horario_unix = datetime.timestamp(str(log[chaves_logs['2']]))

                    if len(divisao_itens) == 2:
                        host_name = divisao_itens[-1]

                        if 'note' in divisao_itens[-1]:
                            print(f'A: {horario_unix} - {host_name}')

                    self.lista_atribuicao_ip.append(mac)

                elif 'defconf deassigned' in log[chaves_logs['4']]:
                    mac = str(log[chaves_logs['4']]).split('for')[-1].strip()
                    self.lista_desatribuicao_ip.append(mac)
