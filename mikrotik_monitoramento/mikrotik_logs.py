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

        for item in self.lista_desatribuicao_ip:
            print(item)
