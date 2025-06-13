from datetime import datetime
from zoneinfo import ZoneInfo
import calculo_hora



class BuscandoLogsMikrotik:
    date_time = datetime.now()
    DATA_ATUAL = date_time.strftime('%Y-%m-%d %H:%M:%S')

    def __init__(self, obj_principal):
        self.obj_conexao_fw = obj_principal

        self.lista_atribuicao_ip = list()
        self.lista_desatribuicao_ip = list()
        self.lista_ip_on = list()

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
        contador = 0
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
                hora_do_log = str(log[chaves_logs['2']]).split(' ')[-1]
                if 'defconf assigned' in log[chaves_logs['4']]:
                    info_log_on = f'{hora_do_log} - {log[chaves_logs['4']]}'
                    self.lista_atribuicao_ip.append(info_log_on)
                contador += 1

                if 'defconf deassigned' in log[chaves_logs['4']]:
                    info_log_off = f'{hora_do_log} - {log[chaves_logs['4']]}'
                    self.lista_desatribuicao_ip.append(info_log_off)

            print(self.lista_atribuicao_ip)
            print(self.lista_desatribuicao_ip)

            # for item in self.lista_atribuicao_ip:
            #     if item not in self.lista_desatribuicao_ip:
            #         self.lista_ip_on.append(item)

            print(self.lista_ip_on)
