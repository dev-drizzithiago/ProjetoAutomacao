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

    def log_dhcp(self, info_teste):

        if self.obj_conexao_fw  is None:
            self._logs = info_teste
        else:
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

                if 'defconf assigned' in log[chaves_logs['4']]:
                    info_log_on = f'{namehost_assigned}'
                    if info_log_on not in self.lista_atribuicao_ip:
                        # print(f'add a lista assigned: {end_ip_assigned_, info_log_on}')
                        print(log)
                        self.lista_atribuicao_ip.append(end_ip_assigned_)

                if 'defconf deassigned' in log[chaves_logs['4']]:
                    info_log_off = f'{namehost_assigned}'
                    if info_log_off not in self.lista_desatribuicao_ip:
                        # print(f'add a lista deassigned: {end_ip_assigned_, info_log_off}')
                        print(log)
                        self.lista_desatribuicao_ip.append(end_ip_assigned_)

        print()
        print(datetime.now().strftime('%d/%m/%Y - %H:%M'))
        print('---' * 30)

        for item in self.lista_atribuicao_ip:
            if item not in self.lista_desatribuicao_ip:
                print(f'host adicionado a lista de onlines: {item}')
                self.lista_ip_on.append(item)

        return self.lista_ip_on


lista_teste_logs = [
{'.id': '*20DB', 'time': '2025-06-16 15:45:01', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*20DD', 'time': '2025-06-16 15:46:06', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.213 for 62:29:F9:47:2D:C5 Tab-S6-Lite-de-Patricia-Cristina'},
{'.id': '*20DE', 'time': '2025-06-16 15:49:08', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20DF', 'time': '2025-06-16 15:49:13', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20E4', 'time': '2025-06-16 15:54:51', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*20F2', 'time': '2025-06-16 16:08:53', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20F7', 'time': '2025-06-16 16:10:53', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.205 for 60:C7:27:19:B8:2C lenovo-thabata'},
{'.id': '*20FD', 'time': '2025-06-16 16:12:23', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*20FE', 'time': '2025-06-16 16:12:59', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20FF', 'time': '2025-06-16 16:15:16', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*2104', 'time': '2025-06-16 16:17:58', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*2109', 'time': '2025-06-16 16:19:33', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*210B', 'time': '2025-06-16 16:21:24', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*210D', 'time': '2025-06-16 16:22:23', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*2110', 'time': '2025-06-16 16:25:15', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*2114', 'time': '2025-06-16 16:26:51', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.45 for 4A:02:30:79:54:91 '},
{'.id': '*211B', 'time': '2025-06-16 16:36:30', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*211D', 'time': '2025-06-16 16:39:51', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*211E', 'time': '2025-06-16 16:42:19', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*2120', 'time': '2025-06-16 16:45:05', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*2121', 'time': '2025-06-16 16:45:50', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*2122', 'time': '2025-06-16 16:48:26', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
]

if __name__ == '__main__':
    print('Processando...')
    obj_logs = BuscandoLogsMikrotik(None)
    obj_logs.log_dhcp(lista_teste_logs)
    result_ip = obj_logs.analise_de_logs()
    print(result_ip)
    print('Quantidades de ip: ', len(result_ip))
