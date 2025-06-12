

from datetime import datetime

date_now = datetime.now()
UNIX_DATA_NOW = int(date_now.timestamp()) - 300
DATA_5_MIN_ATRAS = datetime.fromtimestamp(UNIX_DATA_NOW)


DATA =  '2025-06-12 09:18:17'
CONVERSAO_DATA = datetime.strptime(DATA, '%Y-%m-%d %H:%M:%S')
UNIX_DATE_FW = datetime.timestamp(CONVERSAO_DATA)


if UNIX_DATE_FW > UNIX_DATA_NOW:
    print(UNIX_DATE_FW)
    print(UNIX_DATA_NOW)