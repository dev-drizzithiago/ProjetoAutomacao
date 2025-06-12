
import subprocess
import socket

class ManipulacaoIcmpHosts:
    def __init__(self):
        self.ip_address = None
        ...

    def ping_icmp_redeLocal(self, endereco_ip):
        ping_result = subprocess.run('ping ' + f'192.168.0.{endereco_ip} ' + '-n 1 -w 1 ', stdout=subprocess.PIPE, text=True)
        if ping_result.returncode == 0:
            self.buscando_host(endereco_ip)

    def buscando_host(self, endereco_ip):
        print('Processando hostname...')
        try:
            host_name = socket.gethostbyaddr(endereco_ip)
            print(host_name)
        except socket.herror:
            print(f'Não foi encontrado o hostname dessa do endereço de ip {endereco_ip}')


obj_ping = ManipulacaoIcmpHosts()

range_end_ip = 1
while True:
    obj_ping.ping_icmp_redeLocal(f'192.168.0.{range_end_ip}')
    range_end_ip += 1
    if range_end_ip == 254:
        break