from datetime import datetime


class CalculaHora:
    DATA_10_MIN_ATRAS: datetime
    date_now = datetime.now()
    def __init__(self):
        self.UNIX_DATA_DIA = None
        self.UNIX_DATE_FW = None
        self.horario_log = None
        self.DATA_HORA_INICIO_FORMAT = None
        self.DATA_HORA_STAMP = None

    def horario_inicio_trabalho_(self):
        # Pega apenas a data, sem o horário
        data_atual = datetime.now().strftime('%Y-%m-%d')

        # Fixei um horario para o inicio do expediente.
        horario_inicio = '07:00:00'

        # junto a data atual com o horário fixado.
        data_hora_inicio = f'{data_atual} {horario_inicio}'

        # Formatado a data e hora para ficar com o padrão do datetime
        format_data_hora = datetime.strptime(data_hora_inicio, '%Y-%m-%d %H:%M:%S')

        # Transformo a data e hora em stamp, data formatada do UNIX.
        self.DATA_HORA_STAMP = datetime.timestamp(format_data_hora)

        # print para analisar o resultado. 
        print(self.DATA_HORA_STAMP)

    def converter_hora_atual_stamp(self):
        self.horario_inicio_trabalho_()
        SOBRA_CALCULO = int(self.date_now.timestamp()) - int(self.DATA_HORA_STAMP)
        self.UNIX_DATA_DIA =  int(self.date_now.timestamp()) - SOBRA_CALCULO# resultado não bate, verificar
        print(self.UNIX_DATA_DIA)

        self.DATA_HORA_INICIO_FORMAT = datetime.fromtimestamp(self.UNIX_DATA_DIA) # hora formatada para views

        print(self.DATA_HORA_INICIO_FORMAT)

    def converter_hora_log_stamp(self, entrada_hora_log):
        self.converter_hora_atual_stamp()
        self.horario_log = entrada_hora_log
        CONVERSAO_DATA = datetime.strptime(self.horario_log, '%Y-%m-%d %H:%M:%S')
        self.UNIX_DATE_FW = datetime.timestamp(CONVERSAO_DATA)

    def comparacao_data_atual_x_log(self):
        if self.UNIX_DATE_FW >= self.UNIX_DATA_DIA:
            return True


if __name__ == "__main__":
    obj_inicio = CalculaHora()
    obj_inicio.horario_inicio_trabalho_()
    obj_inicio.converter_hora_log_stamp('2025-06-12 07:00:00')
    print(obj_inicio.comparacao_data_atual_x_log())
