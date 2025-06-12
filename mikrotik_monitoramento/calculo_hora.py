from datetime import datetime


class CalculaHora:
    def __init__(self):
        self.horario_log = None

    def _converter_hora_atual_stamp(self):
        date_now = datetime.now()
        UNIX_DATA_NOW = int(date_now.timestamp()) - 300
        DATA_5_MIN_ATRAS = datetime.fromtimestamp(UNIX_DATA_NOW)

    def _converter_hora_log_stamp(self, entrada_hora_log):
        self.horario_log =  '2025-06-12 09:18:17'
        CONVERSAO_DATA = datetime.strptime(DATA, '%Y-%m-%d %H:%M:%S')
        UNIX_DATE_FW = datetime.timestamp(CONVERSAO_DATA)

        if UNIX_DATE_FW > UNIX_DATA_NOW:
            print(UNIX_DATE_FW)
            print(UNIX_DATA_NOW)