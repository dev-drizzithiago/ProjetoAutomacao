from datetime import datetime
from zoneinfo import ZoneInfo



class BuscandoLogsMikrotik:
    date_time = datetime.now()
    DATA_ATUAL = date_time.strftime('%Y-%m-%d %H:%M:%S')

    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal

        self.lista_atribuicao_ip = list()
        self.lista_desatribuicao_ip = list()

        self._logs = None
        self.__data_stamp = None

    def log_dhcp(self):
        self._logs = self.obj_conexao_fw.path('log')
        return self._logs

    def log_conexao_internet(self):
        ...

    def log_conxao_bkp_internet(self):
        ...

    def conversao_data_timestamp(self, data_fw):
        data_com_fuso = (
            datetime.strptime(data_fw, "%Y-%m-%d %H:%M:%S"))

        self.__data_stamp = data_com_fuso.timestamp()
        return self.__data_stamp

    def analise_de_logs(self):
        logs = self._logs
        for log in logs:
            chaves_logs = {
                '1': '.id',
                '2': 'time',
                '3': 'topics',
                '4': 'message',
            }
            print(log[chaves_logs['2']])

            # if log[chaves_logs['3']] == 'dhcp,info':
            #
            #     if 'defconf assigned' in log[chaves_logs['4']]:
            #         mac = str(log[chaves_logs['4']]).split('for')[-1].strip()
            #         self.lista_atribuicao_ip.append(mac)
            #
            #     elif 'defconf deassigned' in log[chaves_logs['4']]:
            #         mac = str(log[chaves_logs['4']]).split('for')[-1].strip()
            #         self.lista_desatribuicao_ip.append(mac)

        # for item in self.lista_atribuicao_ip:
        #     print(item)

        for item in self.lista_desatribuicao_ip:
            print(item)
