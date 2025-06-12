from datetime import datetime


class CalculaHora:
    date_now = datetime.now()
    def __init__(self):
        self.horario_log = None
        self.DATA_5_MIN_ATRAS = None

    def _converter_hora_atual_stamp(self):
        print('- Convertendo horário atual para UNIX...')
        self.UNIX_DATA_NOW = int(self.date_now.timestamp()) - 600
        self.DATA_10_MIN_ATRAS = datetime.fromtimestamp(self.UNIX_DATA_NOW) # hora formatada
        print(self.DATA_10_MIN_ATRAS)

    def _converter_hora_log_stamp(self, entrada_hora_log):
        print('- Convertendo horário log para UNIX...')
        self.horario_log = entrada_hora_log
        CONVERSAO_DATA = datetime.strptime(self.horario_log, '%Y-%m-%d %H:%M:%S')
        self.UNIX_DATE_FW = datetime.timestamp(CONVERSAO_DATA)

    def _comparacao_data_atual_x_log(self):
        print('- Comparando horário ATUAL com o horário de LOG...')
        if self.UNIX_DATE_FW > self.UNIX_DATA_NOW:
            return True
        else:
            print('Não pegamos logs abaixo de 10 minutos do horário atual. ')



if __name__ == "__main__":
    obj_inicio = CalculaHora()
    obj_inicio._converter_hora_atual_stamp()
    obj_inicio._converter_hora_log_stamp('2025-06-12 10:50:56')
    obj_inicio._comparacao_data_atual_x_log()
