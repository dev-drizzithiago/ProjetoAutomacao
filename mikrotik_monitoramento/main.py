from librouteros import connect
from dotenv import load_dotenv
import os
load_dotenv()


api_mikrotik = connect(
    username=str(os.getenv('USERNAME')),
    password=str(os.getenv('PASSWORD')),
    host=str(os.getenv('HOST_FW')), # IP do seu MikroTik
    port=str(os.getenv('PORT_FW')), # Porta padrão da API
)

logs = api_mikrotik.path('log')

for log in logs:
    print(log)
    