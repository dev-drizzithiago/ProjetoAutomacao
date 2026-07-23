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

    def converter_para_stamp(self, data_entrada):
        """
        Converte qualquer data para o formata de strstamp, data UNIX.
        :param data_entrada: valor de entrar no formato: ('2025-06-12 07:00:00')
        :return: Retorno o valor com o formato: ("1749722400.0 segundos")
        """
        return datetime.strptime(data_entrada, '%Y-%m-%d %H:%M:%S')

    def horario_inicio_trabalho_(self):
        # Pega apenas a data, sem o horário
        data_atual = datetime.now().strftime('%Y-%m-%d')

        # Fixei um horario para o inicio do expediente.
        horario_inicio = '07:00:00'

        # junto a data atual com o horário fixado.
        data_hora_inicio = f'{data_atual} {horario_inicio}'

        # Formatado a data e hora para ficar com o padrão do datetime
        format_data_hora = self.converter_para_stamp(data_hora_inicio)

        # Transformo a data e hora em stamp, data formatada do UNIX.
        self.DATA_HORA_STAMP = datetime.timestamp(format_data_hora)

        # print('Formatação stamp inicio trabalho: ', self.DATA_HORA_STAMP)

    def converter_hora_atual_stamp(self):

        # chama o metodo para solicitar a data e horario de início de trabalho.
        self.horario_inicio_trabalho_()

        # Subtrai o valor stamp da hora atual com a hora de início do trabalho, pegando a sobra.
        SOBRA_CALCULO = int(self.date_now.timestamp()) - int(self.DATA_HORA_STAMP)

        # Com a sobra da subtração, é subtraido mais uma vez, mas apenas com a data do dia. Ai fica com a data do dia
        # e o horario das 07:00:00
        self.UNIX_DATA_DIA =  int(self.date_now.timestamp()) - SOBRA_CALCULO

        # Para saber se esta tudo cereto, eu transformei o stamp no formata de horario padrão
        self.DATA_HORA_INICIO_FORMAT = datetime.fromtimestamp(self.UNIX_DATA_DIA)

        # print('Formatação decimal inicio trabalho: ', self.DATA_HORA_INICIO_FORMAT)

    def converter_hora_log_stamp(self, entrada_hora_log):

        # Chama o metodo para formatar a data em stamp.
        self.converter_hora_atual_stamp()
        self.horario_log = entrada_hora_log
        CONVERSAO_DATA = self.converter_para_stamp(self.horario_log)
        self.UNIX_DATE_FW = datetime.timestamp(CONVERSAO_DATA)

    def comparacao_data_atual_x_log(self):
        if self.UNIX_DATE_FW >= self.UNIX_DATA_DIA:
            return True


if __name__ == "__main__":
    obj_inicio = CalculaHora()
    obj_inicio.converter_hora_log_stamp('2025-06-12 07:00:00')
    print(obj_inicio.comparacao_data_atual_x_log())
