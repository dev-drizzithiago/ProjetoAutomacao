from datetime import datetime
from zoneinfo import ZoneInfo
import calculo_hora

from time import sleep

class BuscandoLogsMikrotik:
    date_time = datetime.now()
    DATA_ATUAL = date_time.strftime('%Y-%m-%d %H:%M:%S')

    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal

        self.lista_atribuicao_ip = list()
        self.lista_desatribuicao_ip = list()

        self.lista_ip_on = list()
        self.lista_ip_logs = list()

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

            data_log = log[chaves_logs['2']]

            verificado_data = calculo_hora.CalculaHora()
            verificado_data.converter_hora_log_stamp(data_log)
            condicao_hora = verificado_data.comparacao_data_atual_x_log()

            if condicao_hora:

                namehost_assigned = str(log[chaves_logs['4']]).split('for')[-1].strip()
                end_ip_assigned_ = str(log[chaves_logs['4']]).split('for')[0].strip().split(' ')[-1]

                print(end_ip_assigned_, namehost_assigned)

                if 'defconf assigned' in log[chaves_logs['4']]:
                    info_log_on = f'{namehost_assigned}'

                    if info_log_on not in self.lista_atribuicao_ip:
                        print(f'add a lista: {info_log_on}')
                        sleep(3)
                        self.lista_atribuicao_ip.append(end_ip_assigned_)

                if 'defconf deassigned' in log[chaves_logs['4']]:

                    info_log_off = f'{namehost_assigned}'

                    if info_log_off not in self.lista_desatribuicao_ip:
                        self.lista_desatribuicao_ip.append(end_ip_assigned_)

        print()
        print(datetime.now().strftime('%d/%m/%Y - %H:%M'))
        print('---' * 30)

        for item in self.lista_atribuicao_ip:
            if item not in self.lista_desatribuicao_ip:
                self.lista_ip_on.append(item)

        return self.lista_ip_logs


if __name__ == '__main__':
    ...
