from datetime import datetime
from zoneinfo import ZoneInfo
import calculo_hora
import manipulacao_icmp

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
                        print('ip adicionado', end_ip_assigned_)
                        self.lista_atribuicao_ip.append(end_ip_assigned_)

                if 'defconf deassigned' in log[chaves_logs['4']]:
                    end_ip_deassigned_ = str(log[chaves_logs['4']]).split('for')[0].strip().split(' ')[-1]
                    print('ip removido',end_ip_deassigned_ )
                    self.lista_atribuicao_ip.remove(end_ip_deassigned_)

        print(self.lista_atribuicao_ip)
        print()
        print(datetime.now().strftime('%d/%m/%Y - %H:%M'))
        print('---' * 30)

        print(len(self.lista_atribuicao_ip), self.lista_atribuicao_ip)
        return self.lista_atribuicao_ip

dia = '17'
mes = '06'

lista_teste_logs = [
{'.id': '*1FD6', 'time': f'2025-{mes}-{dia} 07:25:10', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.121 for 5C:CD:5B:D3:0F:E0 note-giselle'},
{'.id': '*1FD7', 'time': f'2025-{mes}-{dia} 07:31:02', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*1FD8', 'time': f'2025-{mes}-{dia} 07:31:55', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*1FD9', 'time': f'2025-{mes}-{dia} 07:31:55', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*1FDA', 'time': f'2025-{mes}-{dia} 07:35:20', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*1FDB', 'time': f'2025-{mes}-{dia} 07:37:20', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.64 for 5C:CD:5B:D3:0F:D6 note-erica'},
{'.id': '*1FDC', 'time': f'2025-{mes}-{dia} 07:37:20', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.41 for B0:7B:25:64:BF:EA note-erica'},
{'.id': '*1FDD', 'time': f'2025-{mes}-{dia} 07:39:47', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.104 for 84:7B:EB:FE:EB:8B note-bruna'},
{'.id': '*1FDE', 'time': f'2025-{mes}-{dia} 07:39:56', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.227 for 54:13:79:7B:FA:63 note-bruna'},
{'.id': '*1FDF', 'time': f'2025-{mes}-{dia} 07:41:26', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.150 for 5C:CD:5B:D3:06:7B ntb-gabrielly'},
{'.id': '*1FE0', 'time': f'2025-{mes}-{dia} 07:43:42', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*1FE1', 'time': f'2025-{mes}-{dia} 07:43:42', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*1FE2', 'time': f'2025-{mes}-{dia} 07:47:20', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.64 for 5C:CD:5B:D3:0F:D6 note-erica'},
{'.id': '*1FE3', 'time': f'2025-{mes}-{dia} 07:49:51', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.65 for 5C:CD:5B:D3:06:58 ntb-df-andressa'},
{'.id': '*1FE4', 'time': f'2025-{mes}-{dia} 07:49:56', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.227 for 54:13:79:7B:FA:63 note-bruna'},
{'.id': '*1FE5', 'time': f'2025-{mes}-{dia} 07:50:00', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*1FE6', 'time': f'2025-{mes}-{dia} 07:50:16', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*1FE7', 'time': f'2025-{mes}-{dia} 07:50:16', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*1FE8', 'time': f'2025-{mes}-{dia} 07:51:50', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*1FE9', 'time': f'2025-{mes}-{dia} 07:59:13', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*1FEA', 'time': f'2025-{mes}-{dia} 08:01:35', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*1FEB', 'time': f'2025-{mes}-{dia} 08:02:17', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.172 for F2:FB:53:C9:D0:09 S24-de-GRAZIELE'},
{'.id': '*1FEC', 'time': f'2025-{mes}-{dia} 08:04:12', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.172 for F2:FB:53:C9:D0:09 S24-de-GRAZIELE'},
{'.id': '*1FED', 'time': f'2025-{mes}-{dia} 08:04:12', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.172 for F2:FB:53:C9:D0:09 S24-de-GRAZIELE'},
{'.id': '*1FEE', 'time': f'2025-{mes}-{dia} 08:11:35', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*1FEF', 'time': f'2025-{mes}-{dia} 08:13:03', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.53 for B2:74:80:17:65:7A iPhone'},
{'.id': '*1FF0', 'time': f'2025-{mes}-{dia} 08:14:51', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.115 for 30:E3:A4:B0:68:AA note-graziele'},
{'.id': '*1FF1', 'time': f'2025-{mes}-{dia} 08:17:33', 'topics': 'dhcp,warning', 'message': 'defconf offering lease 192.168.0.226 for 18:66:DA:86:16:C5 without success'},
{'.id': '*1FF2', 'time': f'2025-{mes}-{dia} 08:17:54', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.143 for 30:E3:A4:B0:84:25 note-amanda-dp'},
{'.id': '*1FF3', 'time': f'2025-{mes}-{dia} 08:18:59', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.148 for FA:29:90:F1:6E:F5 iPhone'},
{'.id': '*1FF4', 'time': f'2025-{mes}-{dia} 08:19:32', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.152 for 42:E7:C7:B3:F1:7F iPhone'},
{'.id': '*1FF5', 'time': f'2025-{mes}-{dia} 08:20:12', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*1FF6', 'time': f'2025-{mes}-{dia} 08:20:36', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.85 for 5C:CD:5B:D3:06:80 note-fernanda'},
{'.id': '*1FF7', 'time': f'2025-{mes}-{dia} 08:21:18', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.170 for FA:01:64:91:B5:DC S23-de-Eumi'},
{'.id': '*1FF8', 'time': f'2025-{mes}-{dia} 08:22:02', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.123 for 5C:CD:5B:71:C6:F4 ntb-eumi'},
{'.id': '*1FF9', 'time': f'2025-{mes}-{dia} 08:23:00', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.93 for B0:7B:25:64:B9:5E note-fernanda'},
{'.id': '*1FFA', 'time': f'2025-{mes}-{dia} 08:23:40', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.228 for 5C:CD:5B:D3:08:47 note-renata'},
{'.id': '*1FFB', 'time': f'2025-{mes}-{dia} 08:25:19', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*1FFC', 'time': f'2025-{mes}-{dia} 08:28:08', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*1FFD', 'time': f'2025-{mes}-{dia} 08:28:41', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.154 for 60:C7:27:2B:91:4C note-jessica'},
{'.id': '*1FFE', 'time': f'2025-{mes}-{dia} 08:28:59', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.148 for FA:29:90:F1:6E:F5 iPhone'},
{'.id': '*1FFF', 'time': f'2025-{mes}-{dia} 08:30:18', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.34 for 3E:33:E4:2B:33:B0 iPhone'},
{'.id': '*2000', 'time': f'2025-{mes}-{dia} 08:30:46', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2001', 'time': f'2025-{mes}-{dia} 08:34:51', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.220 for 0E:DB:EF:06:A3:99 '},
{'.id': '*2002', 'time': f'2025-{mes}-{dia} 08:38:08', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*2003', 'time': f'2025-{mes}-{dia} 08:38:45', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.85 for 5C:CD:5B:D3:06:80 note-fernanda'},
{'.id': '*2004', 'time': f'2025-{mes}-{dia} 08:40:08', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*2005', 'time': f'2025-{mes}-{dia} 08:40:16', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*2006', 'time': f'2025-{mes}-{dia} 08:41:18', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*2007', 'time': f'2025-{mes}-{dia} 08:41:42', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*2008', 'time': f'2025-{mes}-{dia} 08:44:57', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*2009', 'time': f'2025-{mes}-{dia} 08:47:08', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.1{dia} for 5C:CD:5B:D3:0F:EF note-beatriz'},
{'.id': '*200A', 'time': f'2025-{mes}-{dia} 08:48:01', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.29 for 6C:2F:80:58:AA:57 note-pedro'},
{'.id': '*200B', 'time': f'2025-{mes}-{dia} 08:48:01', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.110 for 60:C7:27:1B:A5:E3 note-pedro'},
{'.id': '*200C', 'time': f'2025-{mes}-{dia} 08:48:02', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*200D', 'time': f'2025-{mes}-{dia} 08:48:46', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.73 for AE:01:DC:28:83:EC S21-FE-de-Sarah'},
{'.id': '*200E', 'time': f'2025-{mes}-{dia} 08:48:49', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.155 for D0:D0:03:CC:12:2D TIZEN'},
{'.id': '*200F', 'time': f'2025-{mes}-{dia} 08:48:55', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.186 for 56:5D:BE:AB:2A:66 S23-de-Patricia-Cristina'},
{'.id': '*2010', 'time': f'2025-{mes}-{dia} 08:49:00', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*2011', 'time': f'2025-{mes}-{dia} 08:49:05', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.205 for 60:C7:27:19:B8:2C lenovo-thabata'},
{'.id': '*2012', 'time': f'2025-{mes}-{dia} 08:49:17', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*2013', 'time': f'2025-{mes}-{dia} 08:49:17', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*2014', 'time': f'2025-{mes}-{dia} 08:51:03', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.34 for 3E:33:E4:2B:33:B0 iPhone'},
{'.id': '*2015', 'time': f'2025-{mes}-{dia} 08:51:18', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*2016', 'time': f'2025-{mes}-{dia} 08:51:54', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2017', 'time': f'2025-{mes}-{dia} 08:51:57', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.97 for 4E:CE:FA:9F:57:43 Tab-S6-Lite-de-Jorge'},
{'.id': '*2018', 'time': f'2025-{mes}-{dia} 08:52:01', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.103 for 60:45:2E:2C:C6:94 note-jorge'},
{'.id': '*2019', 'time': f'2025-{mes}-{dia} 08:52:33', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*201A', 'time': f'2025-{mes}-{dia} 08:52:52', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*201B', 'time': f'2025-{mes}-{dia} 08:54:49', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.213 for 62:29:F9:47:2D:C5 Tab-S6-Lite-de-Patricia-Cristina'},
{'.id': '*201C', 'time': f'2025-{mes}-{dia} 08:58:01', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.29 for 6C:2F:80:58:AA:57 note-pedro'},
{'.id': '*201D', 'time': f'2025-{mes}-{dia} 08:58:58', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*201E', 'time': f'2025-{mes}-{dia} 08:59:00', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*201F', 'time': f'2025-{mes}-{dia} 08:59:17', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*2020', 'time': f'2025-{mes}-{dia} 08:59:27', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*2021', 'time': f'2025-{mes}-{dia} 08:59:29', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2022', 'time': f'2025-{mes}-{dia} 08:59:29', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2023', 'time': f'2025-{mes}-{dia} 08:59:44', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*2024', 'time': f'2025-{mes}-{dia} 09:00:36', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*2025', 'time': f'2025-{mes}-{dia} 09:02:47', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*2026', 'time': f'2025-{mes}-{dia} 09:03:30', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*2027', 'time': f'2025-{mes}-{dia} 09:04:15', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.205 for 60:C7:27:19:B8:2C lenovo-thabata'},
{'.id': '*2028', 'time': f'2025-{mes}-{dia} 09:04:25', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*2029', 'time': f'2025-{mes}-{dia} 09:04:52', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.220 for 0E:DB:EF:06:A3:99 '},
{'.id': '*202A', 'time': f'2025-{mes}-{dia} 09:08:23', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.193 for 4A:65:C3:E0:9C:24 Jeeh'},
{'.id': '*202B', 'time': f'2025-{mes}-{dia} 09:08:56', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*202C', 'time': f'2025-{mes}-{dia} 09:09:47', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*202D', 'time': f'2025-{mes}-{dia} 09:19:23', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.208 for 76:D1:3E:18:2F:4E S21-FE-de-Sarah'},
{'.id': '*202E', 'time': f'2025-{mes}-{dia} 09:27:46', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*202F', 'time': f'2025-{mes}-{dia} 09:28:33', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*2030', 'time': f'2025-{mes}-{dia} 09:30:31', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.171 for 52:8B:5D:98:8F:BE S23-de-Patricia-Cristina'},
{'.id': '*2031', 'time': f'2025-{mes}-{dia} 09:32:05', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*2032', 'time': f'2025-{mes}-{dia} 09:34:24', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.208 for 76:D1:3E:18:2F:4E S21-FE-de-Sarah'},
{'.id': '*2033', 'time': f'2025-{mes}-{dia} 09:35:56', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.190 for 6A:01:EF:F8:B7:1D '},
{'.id': '*2034', 'time': f'2025-{mes}-{dia} 09:39:00', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.186 for 56:5D:BE:AB:2A:66 S23-de-Patricia-Cristina'},
{'.id': '*2035', 'time': f'2025-{mes}-{dia} 09:43:56', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*2036', 'time': f'2025-{mes}-{dia} 09:44:38', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2037', 'time': f'2025-{mes}-{dia} 09:50:53', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*2038', 'time': f'2025-{mes}-{dia} 09:50:58', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*2039', 'time': f'2025-{mes}-{dia} 09:56:22', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*203A', 'time': f'2025-{mes}-{dia} 10:02:04', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.190 for 6A:01:EF:F8:B7:1D '},
{'.id': '*203B', 'time': f'2025-{mes}-{dia} 10:05:21', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*203C', 'time': f'2025-{mes}-{dia} 10:06:04', 'topics': 'dhcp,warning', 'message': 'defconf offering lease 192.168.0.192 for D2:6B:44:8B:B5:68 without success'},
{'.id': '*203D', 'time': f'2025-{mes}-{dia} 10:06:28', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*203E', 'time': f'2025-{mes}-{dia} 10:11:08', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*203F', 'time': f'2025-{mes}-{dia} 10:13:23', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.185 for 70:32:17:3C:C3:3C katiaNogueira'},
{'.id': '*2040', 'time': f'2025-{mes}-{dia} 10:20:52', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2041', 'time': f'2025-{mes}-{dia} 10:21:10', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2042', 'time': f'2025-{mes}-{dia} 10:21:34', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2043', 'time': f'2025-{mes}-{dia} 10:21:40', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2044', 'time': f'2025-{mes}-{dia} 10:22:01', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2045', 'time': f'2025-{mes}-{dia} 10:26:25', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2046', 'time': f'2025-{mes}-{dia} 10:26:40', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2047', 'time': f'2025-{mes}-{dia} 10:27:19', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2048', 'time': f'2025-{mes}-{dia} 10:27:40', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2049', 'time': f'2025-{mes}-{dia} 10:32:01', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*204A', 'time': f'2025-{mes}-{dia} 10:34:59', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*204B', 'time': f'2025-{mes}-{dia} 10:35:08', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*204C', 'time': f'2025-{mes}-{dia} 10:37:26', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.220 for 0E:DB:EF:06:A3:99 '},
{'.id': '*204D', 'time': f'2025-{mes}-{dia} 10:42:08', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.194 for C2:A8:12:70:98:66 '},
{'.id': '*204E', 'time': f'2025-{mes}-{dia} 10:42:08', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.194 for C2:A8:12:70:98:66 '},
{'.id': '*204F', 'time': f'2025-{mes}-{dia} 10:42:09', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.194 for C2:A8:12:70:98:66 '},
{'.id': '*2050', 'time': f'2025-{mes}-{dia} 10:42:12', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*2051', 'time': f'2025-{mes}-{dia} 10:44:03', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*2052', 'time': f'2025-{mes}-{dia} 10:46:34', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2053', 'time': f'2025-{mes}-{dia} 10:46:34', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2054', 'time': f'2025-{mes}-{dia} 10:50:10', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*2055', 'time': f'2025-{mes}-{dia} 10:54:28', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.170 for FA:01:64:91:B5:DC S23-de-Eumi'},
{'.id': '*2056', 'time': f'2025-{mes}-{dia} 10:57:11', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2057', 'time': f'2025-{mes}-{dia} 10:57:12', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2058', 'time': f'2025-{mes}-{dia} 10:57:28', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.220 for 0E:DB:EF:06:A3:99 '},
{'.id': '*2059', 'time': f'2025-{mes}-{dia} 11:02:52', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*205A', 'time': f'2025-{mes}-{dia} 11:03:03', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*205B', 'time': f'2025-{mes}-{dia} 11:05:33', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.192 for D2:6B:44:8B:B5:68 '},
{'.id': '*205C', 'time': f'2025-{mes}-{dia} 11:13:01', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*205D', 'time': f'2025-{mes}-{dia} 11:14:13', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*205E', 'time': f'2025-{mes}-{dia} 11:14:32', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*205F', 'time': f'2025-{mes}-{dia} 11:14:41', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2060', 'time': f'2025-{mes}-{dia} 11:21:08', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2061', 'time': f'2025-{mes}-{dia} 11:21:21', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2062', 'time': f'2025-{mes}-{dia} 11:21:30', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2063', 'time': f'2025-{mes}-{dia} 11:21:38', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2064', 'time': f'2025-{mes}-{dia} 11:22:17', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2065', 'time': f'2025-{mes}-{dia} 11:22:28', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2066', 'time': f'2025-{mes}-{dia} 11:25:52', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2067', 'time': f'2025-{mes}-{dia} 11:29:50', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*2068', 'time': f'2025-{mes}-{dia} 11:32:36', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2069', 'time': f'2025-{mes}-{dia} 11:33:06', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.121 for 5C:CD:5B:D3:0F:E0 note-giselle'},
{'.id': '*206A', 'time': f'2025-{mes}-{dia} 11:33:11', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.121 for 5C:CD:5B:D3:0F:E0 note-giselle'},
{'.id': '*206B', 'time': f'2025-{mes}-{dia} 11:34:28', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*206C', 'time': f'2025-{mes}-{dia} 11:34:28', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*206D', 'time': f'2025-{mes}-{dia} 11:38:27', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*206E', 'time': f'2025-{mes}-{dia} 11:38:38', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*206F', 'time': f'2025-{mes}-{dia} 11:40:15', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.194 for C2:A8:12:70:98:66 '},
{'.id': '*2070', 'time': f'2025-{mes}-{dia} 11:43:05', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*2071', 'time': f'2025-{mes}-{dia} 11:43:05', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*2072', 'time': f'2025-{mes}-{dia} 11:47:24', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*2073', 'time': f'2025-{mes}-{dia} 11:47:56', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*2074', 'time': f'2025-{mes}-{dia} 11:57:06', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*2075', 'time': f'2025-{mes}-{dia} 11:57:06', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*2076', 'time': f'2025-{mes}-{dia} 11:58:28', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*2077', 'time': f'2025-{mes}-{dia} 12:00:11', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*2078', 'time': f'2025-{mes}-{dia} 12:01:06', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*2079', 'time': f'2025-{mes}-{dia} 12:05:38', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*207A', 'time': f'2025-{mes}-{dia} 12:13:29', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*207B', 'time': f'2025-{mes}-{dia} 12:14:30', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.181 for 30:E3:A4:B0:B9:7C note-jessica'},
{'.id': '*207C', 'time': f'2025-{mes}-{dia} 12:19:59', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*207D', 'time': f'2025-{mes}-{dia} 12:20:40', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.154 for 60:C7:27:2B:91:4C note-jessica'},
{'.id': '*207E', 'time': f'2025-{mes}-{dia} 12:22:54', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.152 for 42:E7:C7:B3:F1:7F iPhone'},
{'.id': '*207F', 'time': f'2025-{mes}-{dia} 12:23:33', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.193 for 4A:65:C3:E0:9C:24 Jeeh'},
{'.id': '*2080', 'time': f'2025-{mes}-{dia} 12:24:30', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.181 for 30:E3:A4:B0:B9:7C note-jessica'},
{'.id': '*2081', 'time': f'2025-{mes}-{dia} 12:27:18', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*2082', 'time': f'2025-{mes}-{dia} 12:29:39', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.22 for F2:96:5B:B4:A0:9B '},
{'.id': '*2083', 'time': f'2025-{mes}-{dia} 12:30:31', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*2084', 'time': f'2025-{mes}-{dia} 12:32:39', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*2085', 'time': f'2025-{mes}-{dia} 12:34:04', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*2086', 'time': f'2025-{mes}-{dia} 12:34:04', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*2087', 'time': f'2025-{mes}-{dia} 12:35:12', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*2088', 'time': f'2025-{mes}-{dia} 12:35:45', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.186 for 56:5D:BE:AB:2A:66 S23-de-Patricia-Cristina'},
{'.id': '*2089', 'time': f'2025-{mes}-{dia} 12:35:53', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*208A', 'time': f'2025-{mes}-{dia} 12:37:18', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*208B', 'time': f'2025-{mes}-{dia} 12:38:30', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*208C', 'time': f'2025-{mes}-{dia} 12:38:46', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.172 for F2:FB:53:C9:D0:09 S24-de-GRAZIELE'},
{'.id': '*208D', 'time': f'2025-{mes}-{dia} 12:39:16', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.53 for B2:74:80:17:65:7A iPhone'},
{'.id': '*208E', 'time': f'2025-{mes}-{dia} 12:39:39', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.22 for F2:96:5B:B4:A0:9B '},
{'.id': '*208F', 'time': f'2025-{mes}-{dia} 12:40:51', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.171 for 52:8B:5D:98:8F:BE S23-de-Patricia-Cristina'},
{'.id': '*2090', 'time': f'2025-{mes}-{dia} 12:40:51', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2091', 'time': f'2025-{mes}-{dia} 12:40:51', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2092', 'time': f'2025-{mes}-{dia} 12:42:47', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2093', 'time': f'2025-{mes}-{dia} 12:42:47', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2094', 'time': f'2025-{mes}-{dia} 12:42:49', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*2095', 'time': f'2025-{mes}-{dia} 12:43:09', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*2096', 'time': f'2025-{mes}-{dia} 12:43:13', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2097', 'time': f'2025-{mes}-{dia} 12:43:13', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*2098', 'time': f'2025-{mes}-{dia} 12:44:04', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*2099', 'time': f'2025-{mes}-{dia} 12:45:45', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.186 for 56:5D:BE:AB:2A:66 S23-de-Patricia-Cristina'},
{'.id': '*209A', 'time': f'2025-{mes}-{dia} 12:57:11', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*209B', 'time': f'2025-{mes}-{dia} 12:57:55', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.229 for 5A:3B:B8:87:44:B1 M53-de-Renata'},
{'.id': '*209C', 'time': f'2025-{mes}-{dia} 13:02:11', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*209D', 'time': f'2025-{mes}-{dia} 13:08:14', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*209E', 'time': f'2025-{mes}-{dia} 13:12:16', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*209F', 'time': f'2025-{mes}-{dia} 13:12:39', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*20A0', 'time': f'2025-{mes}-{dia} 13:12:46', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.195 for A6:DA:0E:18:B5:46 S24-de-GRAZIELE'},
{'.id': '*20A1', 'time': f'2025-{mes}-{dia} 13:12:47', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*20A2', 'time': f'2025-{mes}-{dia} 13:12:50', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.196 for 92:50:AD:12:D6:10 '},
{'.id': '*20A3', 'time': f'2025-{mes}-{dia} 13:13:07', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.53 for B2:74:80:17:65:7A iPhone'},
{'.id': '*20A4', 'time': f'2025-{mes}-{dia} 13:13:17', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.172 for F2:FB:53:C9:D0:09 S24-de-GRAZIELE'},
{'.id': '*20A5', 'time': f'2025-{mes}-{dia} 13:17:34', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*20A6', 'time': f'2025-{mes}-{dia} 13:18:01', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*20A7', 'time': f'2025-{mes}-{dia} 13:18:17', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*20A8', 'time': f'2025-{mes}-{dia} 13:18:18', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*20A9', 'time': f'2025-{mes}-{dia} 13:22:46', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.195 for A6:DA:0E:18:B5:46 S24-de-GRAZIELE'},
{'.id': '*20AA', 'time': f'2025-{mes}-{dia} 13:22:50', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.196 for 92:50:AD:12:D6:10 '},
{'.id': '*20AB', 'time': f'2025-{mes}-{dia} 13:24:08', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.94 for 92:AC:EF:1C:0F:79 POCO-X6-5G'},
{'.id': '*20AC', 'time': f'2025-{mes}-{dia} 13:27:29', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.208 for 76:D1:3E:18:2F:4E S21-FE-de-Sarah'},
{'.id': '*20AD', 'time': f'2025-{mes}-{dia} 13:27:35', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*20AE', 'time': f'2025-{mes}-{dia} 13:30:01', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.171 for 52:8B:5D:98:8F:BE S23-de-Patricia-Cristina'},
{'.id': '*20AF', 'time': f'2025-{mes}-{dia} 13:30:59', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*20B0', 'time': f'2025-{mes}-{dia} 13:31:29', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.99 for 22:9B:16:D5:D1:94 POCO-X6-5G'},
{'.id': '*20B1', 'time': f'2025-{mes}-{dia} 13:31:41', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.189 for E6:F7:27:6F:E9:C2 '},
{'.id': '*20B2', 'time': f'2025-{mes}-{dia} 13:33:08', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*20B3', 'time': f'2025-{mes}-{dia} 13:33:49', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.155 for D0:D0:03:CC:12:2D TIZEN'},
{'.id': '*20B4', 'time': f'2025-{mes}-{dia} 13:34:08', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.94 for 92:AC:EF:1C:0F:79 POCO-X6-5G'},
{'.id': '*20B5', 'time': f'2025-{mes}-{dia} 13:34:37', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.171 for 52:8B:5D:98:8F:BE S23-de-Patricia-Cristina'},
{'.id': '*20B6', 'time': f'2025-{mes}-{dia} 13:34:37', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.171 for 52:8B:5D:98:8F:BE S23-de-Patricia-Cristina'},
{'.id': '*20B7', 'time': f'2025-{mes}-{dia} 13:36:34', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*20B8', 'time': f'2025-{mes}-{dia} 13:36:35', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.119 for 5A:8E:19:EE:90:A0 iPhone'},
{'.id': '*20B9', 'time': f'2025-{mes}-{dia} 13:37:29', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.208 for 76:D1:3E:18:2F:4E S21-FE-de-Sarah'},
{'.id': '*20BA', 'time': f'2025-{mes}-{dia} 13:43:15', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.220 for 0E:DB:EF:06:A3:99 '},
{'.id': '*20BB', 'time': f'2025-{mes}-{dia} 13:50:00', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*20BC', 'time': f'2025-{mes}-{dia} 13:50:59', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.66 for B8:7E:39:16:E2:10 '},
{'.id': '*20BD', 'time': f'2025-{mes}-{dia} 13:56:45', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*20BE', 'time': f'2025-{mes}-{dia} 14:13:15', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.220 for 0E:DB:EF:06:A3:99 '},
{'.id': '*20BF', 'time': f'2025-{mes}-{dia} 14:21:27', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*20C0', 'time': f'2025-{mes}-{dia} 14:28:37', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*20C1', 'time': f'2025-{mes}-{dia} 14:34:55', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.103 for 60:45:2E:2C:C6:94 note-jorge'},
{'.id': '*20C2', 'time': f'2025-{mes}-{dia} 14:36:25', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.99 for 22:9B:16:D5:D1:94 POCO-X6-5G'},
{'.id': '*20C3', 'time': f'2025-{mes}-{dia} 14:45:40', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20C4', 'time': f'2025-{mes}-{dia} 14:45:52', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20C5', 'time': f'2025-{mes}-{dia} 14:47:24', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.45 for 4A:02:30:79:54:91 '},
{'.id': '*20C6', 'time': f'2025-{mes}-{dia} 14:48:38', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*20C7', 'time': f'2025-{mes}-{dia} 14:53:54', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*20C8', 'time': f'2025-{mes}-{dia} 14:56:32', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20C9', 'time': f'2025-{mes}-{dia} 14:56:37', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20CA', 'time': f'2025-{mes}-{dia} 14:57:11', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20CB', 'time': f'2025-{mes}-{dia} 14:57:46', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20CC', 'time': f'2025-{mes}-{dia} 15:01:45', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*20CD', 'time': f'2025-{mes}-{dia} 15:02:13', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*20CE', 'time': f'2025-{mes}-{dia} 15:02:13', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.59 for 06:9F:7B:7E:5E:3E Galaxy-M30'},
{'.id': '*20CF', 'time': f'2025-{mes}-{dia} 15:05:16', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*20D0', 'time': f'2025-{mes}-{dia} 15:07:34', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.45 for 4A:02:30:79:54:91 '},
{'.id': '*20D1', 'time': f'2025-{mes}-{dia} 15:11:46', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.45 for 4A:02:30:79:54:91 '},
{'.id': '*20D2', 'time': f'2025-{mes}-{dia} 15:14:48', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.20 for 64:1C:67:F4:1C:C5 Sarah-note'},
{'.id': '*20D3', 'time': f'2025-{mes}-{dia} 15:19:34', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*20D4', 'time': f'2025-{mes}-{dia} 15:23:27', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.180 for AC:5A:FC:C8:E8:80 Sarah-note'},
{'.id': '*20D5', 'time': f'2025-{mes}-{dia} 15:34:25', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.88 for D0:57:7E:F6:A0:1D ntb-df-marcelo'},
{'.id': '*20D6', 'time': f'2025-{mes}-{dia} 15:43:10', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20D7', 'time': f'2025-{mes}-{dia} 15:43:10', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20D8', 'time': f'2025-{mes}-{dia} 15:44:13', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20D9', 'time': f'2025-{mes}-{dia} 15:44:13', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20DA', 'time': f'2025-{mes}-{dia} 15:44:57', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.171 for 52:8B:5D:98:8F:BE S23-de-Patricia-Cristina'},
{'.id': '*20DB', 'time': f'2025-{mes}-{dia} 15:45:01', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.147 for 20:15:DE:D7:F5:C6 Samsung'},
{'.id': '*20DC', 'time': f'2025-{mes}-{dia} 15:45:51', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20DD', 'time': f'2025-{mes}-{dia} 15:46:06', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.213 for 62:29:F9:47:2D:C5 Tab-S6-Lite-de-Patricia-Cristina'},
{'.id': '*20DE', 'time': f'2025-{mes}-{dia} 15:49:08', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20DF', 'time': f'2025-{mes}-{dia} 15:49:13', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20E0', 'time': f'2025-{mes}-{dia} 15:51:33', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20E1', 'time': f'2025-{mes}-{dia} 15:51:35', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20E2', 'time': f'2025-{mes}-{dia} 15:54:25', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20E3', 'time': f'2025-{mes}-{dia} 15:54:44', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20E4', 'time': f'2025-{mes}-{dia} 15:54:51', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*20E5', 'time': f'2025-{mes}-{dia} 15:54:57', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20E6', 'time': f'2025-{mes}-{dia} 15:56:27', 'topics': 'netwatch,info', 'message': 'event down [ type: simple, host: 192.168.0.15 ]'},
{'.id': '*20E7', 'time': f'2025-{mes}-{dia} 15:56:27', 'topics': 'script,info', 'message': 'Servidor LINUX: Desativado'},
{'.id': '*20E8', 'time': f'2025-{mes}-{dia} 15:56:52', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20E9', 'time': f'2025-{mes}-{dia} 15:57:05', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20EA', 'time': f'2025-{mes}-{dia} 15:57:24', 'topics': 'netwatch,info', 'message': 'event up [ type: simple, host: 192.168.0.15 ]'},
{'.id': '*20EB', 'time': f'2025-{mes}-{dia} 15:57:24', 'topics': 'script,info', 'message': 'Servidor LINUX: Ativado'},
{'.id': '*20EC', 'time': f'2025-{mes}-{dia} 15:57:26', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via web'},
{'.id': '*20ED', 'time': f'2025-{mes}-{dia} 15:57:40', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20EE', 'time': f'2025-{mes}-{dia} 16:00:42', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20EF', 'time': f'2025-{mes}-{dia} 16:02:51', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20F0', 'time': f'2025-{mes}-{dia} 16:07:37', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20F1', 'time': f'2025-{mes}-{dia} 16:08:21', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20F2', 'time': f'2025-{mes}-{dia} 16:08:53', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20F3', 'time': f'2025-{mes}-{dia} 16:09:32', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20F4', 'time': f'2025-{mes}-{dia} 16:09:54', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20F5', 'time': f'2025-{mes}-{dia} 16:10:48', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20F6', 'time': f'2025-{mes}-{dia} 16:10:51', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20F7', 'time': f'2025-{mes}-{dia} 16:10:53', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.205 for 60:C7:27:19:B8:2C lenovo-thabata'},
{'.id': '*20F8', 'time': f'2025-{mes}-{dia} 16:11:29', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20F9', 'time': f'2025-{mes}-{dia} 16:11:32', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20FA', 'time': f'2025-{mes}-{dia} 16:11:32', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20FB', 'time': f'2025-{mes}-{dia} 16:11:49', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*20FC', 'time': f'2025-{mes}-{dia} 16:12:08', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*20FD', 'time': f'2025-{mes}-{dia} 16:12:23', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*20FE', 'time': f'2025-{mes}-{dia} 16:12:59', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*20FF', 'time': f'2025-{mes}-{dia} 16:15:16', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.50 for D0:D0:03:CC:12:77 TIZEN'},
{'.id': '*2100', 'time': f'2025-{mes}-{dia} 16:15:18', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2101', 'time': f'2025-{mes}-{dia} 16:15:26', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2102', 'time': f'2025-{mes}-{dia} 16:17:14', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2103', 'time': f'2025-{mes}-{dia} 16:17:19', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2104', 'time': f'2025-{mes}-{dia} 16:17:58', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.101 for A0:D3:65:A3:08:4F lenovo-thabata'},
{'.id': '*2105', 'time': f'2025-{mes}-{dia} 16:18:00', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2106', 'time': f'2025-{mes}-{dia} 16:18:01', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2107', 'time': f'2025-{mes}-{dia} 16:18:43', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2108', 'time': f'2025-{mes}-{dia} 16:18:50', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2109', 'time': f'2025-{mes}-{dia} 16:19:33', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*210A', 'time': f'2025-{mes}-{dia} 16:21:18', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*210B', 'time': f'2025-{mes}-{dia} 16:21:24', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*210C', 'time': f'2025-{mes}-{dia} 16:21:30', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*210D', 'time': f'2025-{mes}-{dia} 16:22:23', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*210E', 'time': f'2025-{mes}-{dia} 16:23:18', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*210F', 'time': f'2025-{mes}-{dia} 16:23:59', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2110', 'time': f'2025-{mes}-{dia} 16:25:15', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*2111', 'time': f'2025-{mes}-{dia} 16:26:04', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2112', 'time': f'2025-{mes}-{dia} 16:26:15', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2113', 'time': f'2025-{mes}-{dia} 16:26:26', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2114', 'time': f'2025-{mes}-{dia} 16:26:51', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.45 for 4A:02:30:79:54:91 '},
{'.id': '*2115', 'time': f'2025-{mes}-{dia} 16:32:18', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2116', 'time': f'2025-{mes}-{dia} 16:32:21', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2117', 'time': f'2025-{mes}-{dia} 16:33:48', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2118', 'time': f'2025-{mes}-{dia} 16:33:51', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2119', 'time': f'2025-{mes}-{dia} 16:36:11', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*211A', 'time': f'2025-{mes}-{dia} 16:36:13', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*211B', 'time': f'2025-{mes}-{dia} 16:36:30', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*211C', 'time': f'2025-{mes}-{dia} 16:39:12', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*211D', 'time': f'2025-{mes}-{dia} 16:39:51', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.130 for B6:10:7B:E3:01:CE '},
{'.id': '*211E', 'time': f'2025-{mes}-{dia} 16:42:19', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.160 for 60:45:2E:2C:ED:F9 note-patricia'},
{'.id': '*211F', 'time': f'2025-{mes}-{dia} 16:44:33', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2120', 'time': f'2025-{mes}-{dia} 16:45:05', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*2121', 'time': f'2025-{mes}-{dia} 16:45:50', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.142 for 3E:5B:8F:EF:4B:50 iPhone'},
{'.id': '*2122', 'time': f'2025-{mes}-{dia} 16:48:26', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*2123', 'time': f'2025-{mes}-{dia} 16:49:58', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2124', 'time': f'2025-{mes}-{dia} 16:50:01', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2125', 'time': f'2025-{mes}-{dia} 16:53:02', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2126', 'time': f'2025-{mes}-{dia} 16:54:35', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*2127', 'time': f'2025-{mes}-{dia} 16:57:33', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*2128', 'time': f'2025-{mes}-{dia} 16:57:34', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.105 for 16:62:5E:0F:EA:FB iPhone'},
{'.id': '*2129', 'time': f'2025-{mes}-{dia} 17:03:25', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*212A', 'time': f'2025-{mes}-{dia} 17:04:35', 'topics': 'dhcp,info', 'message': 'defconf deassigned 192.168.0.38 for 02:8C:AE:2F:50:51 iPhone'},
{'.id': '*212B', 'time': f'2025-{mes}-{dia} 17:04:50', 'topics': 'dhcp,info', 'message': 'defconf assigned 192.168.0.42 for 9A:5C:CC:AB:86:9C iPhone'},
{'.id': '*212C', 'time': f'2025-{mes}-{dia} 17:07:58', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*212D', 'time': f'2025-{mes}-{dia} 17:08:07', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*212E', 'time': f'2025-{mes}-{dia} 17:08:22', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*212F', 'time': f'2025-{mes}-{dia} 17:08:34', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2130', 'time': f'2025-{mes}-{dia} 17:08:36', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
{'.id': '*2131', 'time': f'2025-{mes}-{dia} 17:09:24', 'topics': 'system,info,account', 'message': 'user admin logged out from 192.168.0.250 via api'},
{'.id': '*2132', 'time': f'2025-{mes}-{dia} 17:09:26', 'topics': 'system,info,account', 'message': 'user admin logged in from 192.168.0.250 via api'},
]

if __name__ == '__main__':
    print('Processando...')
    obj_logs = BuscandoLogsMikrotik(None)
    obj_logs.log_dhcp(lista_teste_logs)
    result_ip = obj_logs.analise_de_logs()

    obj_icmp = manipulacao_icmp.ManipulacaoIcmpHosts()
    informacoes_icmp = obj_icmp.ping_icmp_redeLocal(result_ip)

    print()
    print(f'Quantidade IP: {len(informacoes_icmp['LISTA_PING_ON'])}')
    print(f'Quantidade HostName: {len(informacoes_icmp['LISTA_HOSTNAME'])}')
    print()
    for chave, valor in informacoes_icmp.items():
        print(f'{chave}:')
        print('---' * 30)
        for item in valor:
            print(item)
        print()
        print()

    # print('Quantidades de ip: ', len(result_ip))
