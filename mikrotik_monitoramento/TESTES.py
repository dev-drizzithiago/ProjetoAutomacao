

from datetime import datetime

date_now = datetime.now()
UNIX_DATA_NOW = date_now.timestamp()

DATA =  '2025-06-12 09:18:17'
CONVERSAO_DATA = datetime.strptime(DATA, '%Y-%m-%d %H:%M:%S')
UNIX_DATE = datetime.timestamp(CONVERSAO_DATA)

print(UNIX_DATE)
print(UNIX_DATA_NOW)
