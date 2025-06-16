
import subprocess
import socket
import os

class ManipulacaoIcmpHosts:

    LISTA_PING_ON = list()
    LISTA_HOSTNAME = list()

    def __init__(self):
        self.ip_address = None
        ...

    def ping_icmp_redeLocal(self, list_ip_hosts):

        print('Processando icmp...')
        for ip_host_ in list_ip_hosts:


            ping_result = subprocess.run(
                'ping ' + f'{ip_host_} ' + '-n 2 -w 1 ', stdout=subprocess.PIPE, text=True
            )

            if ping_result.returncode == 0:
                print(f'Sucesso para o ip: {ip_host_}')
                self.LISTA_PING_ON.append(ip_host_)
                self.buscando_host(ip_host_)

        return {'LISTA_HOSTNAME': self.LISTA_HOSTNAME, 'LISTA_PING_ON': self.LISTA_PING_ON,}

    def buscando_host(self, ip_host_):
        try:
            host_name = socket.gethostbyaddr(ip_host_)
            self.LISTA_HOSTNAME.append(host_name[0])
        except socket.herror:
            ...

obj_ping = ManipulacaoIcmpHosts()


if __name__ == '__main__':
    lista_end_hosts = '192.168.0.250', '192.168.0.25'
    result = obj_ping.ping_icmp_redeLocal(lista_end_hosts)

    print()
    for chave, valor in result.items():
        print(f'{chave}:')
        print('---' * 30)
        for item in valor:
            print(item)
        print()
        print()