

from datetime import datetime

date_now = datetime.now()

data_format_ano = date_now.strftime('%Y-%m-%d %H:%M').split(' ')[0]
data_format_hora = date_now.strftime('%Y-%m-%d %H:%M').split(' ')[-1]
data_format_minu = int(data_format_hora.split(':')[-1]) - 10

data_atualizada = f'{data_format_ano} {data_format_hora[0]}:{data_format_minu}'

print(data_atualizada)

UNIX_DATA_NOW = date_now.timestamp()

DATA =  '2025-06-12 09:18:17'
CONVERSAO_DATA = datetime.strptime(DATA, '%Y-%m-%d %H:%M:%S')
UNIX_DATE = datetime.timestamp(CONVERSAO_DATA)

print(UNIX_DATE)
print(UNIX_DATA_NOW)
