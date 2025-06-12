
import subprocess
import socket

class ManipulacaoIcmpHosts:
    def __init__(self):
        self.ip_address = None
        ...

    def ping_icmp_redeLocal(self, endereco_ip):
        self.ip_address = endereco_ip
        ping_result = subprocess.run('ping ' + '192.168.0.1 ' + '-n 1 -w 1 ', stdout=subprocess.PIPE, text=True)
        print(ping_result.stdout)


    def buscando_host(self, endereco_ip):
        try:
            host_name = socket.gethostbyaddr(endereco_ip)
            print(host_name)
        except socket.herror:
            print(f'Não foi encontrado o hostname dessa do endereço de ip {endereco_ip}')


obj_ping = ManipulacaoIcmpHosts()
obj_ping.ping_icmp_redeLocal('192.168.0.10')
obj_ping.buscando_host('192.168.0.50')