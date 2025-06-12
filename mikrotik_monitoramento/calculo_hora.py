from datetime import datetime


class CalculaHora:
    date_now = datetime.now()
    def __init__(self):
        self.UNIX_DATE_FW = None
        self.horario_log = None
        self.DATA_5_MIN_ATRAS = None

    def converter_hora_atual_stamp(self):
        print('- Convertendo horário atual para UNIX...')
        self.UNIX_DATA_NOW = int(self.date_now.timestamp()) - 600
        self.DATA_10_MIN_ATRAS = datetime.fromtimestamp(self.UNIX_DATA_NOW) # hora formatada
        print(self.DATA_10_MIN_ATRAS)

    def converter_hora_log_stamp(self, entrada_hora_log):
        self.converter_hora_atual_stamp()
        print('- Convertendo horário log para UNIX...')
        self.horario_log = entrada_hora_log
        CONVERSAO_DATA = datetime.strptime(self.horario_log, '%Y-%m-%d %H:%M:%S')
        self.UNIX_DATE_FW = datetime.timestamp(CONVERSAO_DATA)

    def comparacao_data_atual_x_log(self):
        print('- Comparando horário ATUAL com o horário de LOG...')

        if self.UNIX_DATE_FW > self.UNIX_DATA_NOW:
            # print("Data LOG no intervalo de busca")
            return self.UNIX_DATE_FW


if __name__ == "__main__":
    obj_inicio = CalculaHora()
    obj_inicio.converter_hora_log_stamp('2025-06-12 11:35:56')
    obj_inicio.comparacao_data_atual_x_log()
