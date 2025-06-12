
import subprocess
import socket

class ManipulacaoIcmpHosts:

    LISTA_PING_ON = list()
    LISTA_PING_OFF = list()
    LISTA_HOSTNAME = list()


    def __init__(self):
        self.ip_address = None
        ...

    def ping_icmp_redeLocal(self, endereco_ip):

        ping_result = subprocess.run(
            'ping ' + f'{endereco_ip} ' + '-n 1 -w 1 ', stdout=subprocess.PIPE, text=True
        )

        if ping_result.returncode == 0:
            self.LISTA_PING_ON.append(endereco_ip)
            self.buscando_host(endereco_ip)
        else:
            self.LISTA_PING_OFF.append(endereco_ip)

    def buscando_host(self, endereco_ip):
        print('Processando hostname...')
        try:
            host_name = socket.gethostbyaddr(endereco_ip)
            self.LISTA_HOSTNAME.append(host_name)
        except socket.herror:
            ...
            # print(f'Não foi encontrado o hostname dessa do endereço de ip {endereco_ip}')


obj_ping = ManipulacaoIcmpHosts()

range_end_ip = 1
while True:
    obj_ping.ping_icmp_redeLocal(f'192.168.0.{range_end_ip}')
    range_end_ip += 1
    if range_end_ip == 254:
        break

for item in obj_ping.LISTA_PING_ON:
    print(f'Lista de IPs Ativos: {item}')

for item in obj_ping.LISTA_HOSTNAME:
    print(f'Lista de HostNames: {item}')