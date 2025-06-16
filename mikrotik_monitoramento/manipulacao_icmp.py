
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
                self.LISTA_PING_ON.append(ip_host_)
                self.buscando_host(ip_host_)

        return {'LISTA_HOSTNAME': self.LISTA_HOSTNAME,'LISTA_PING_ON': self.LISTA_PING_ON,}

    def buscando_host(self, ip_host_):
        try:
            host_name = socket.gethostbyaddr(ip_host_)
            self.LISTA_HOSTNAME.append(host_name[0])
        except socket.herror:
            ...

obj_ping = ManipulacaoIcmpHosts()


if __name__ == '__main__':
    lista_end_hosts = '192.168.0.250', '192.168.0.10'
    result = obj_ping.ping_icmp_redeLocal(lista_end_hosts)

    if not result:
        print('Digital uma rede Base...!')

    nome_host = result['LISTA_HOSTNAME']
    ip_host = result['LISTA_PING_ON']

    for item in nome_host:
        print(item)

    for item in ip_host:
        print(item)
