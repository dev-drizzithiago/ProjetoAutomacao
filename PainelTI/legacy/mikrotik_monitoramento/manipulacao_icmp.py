
import subprocess
import socket
import os
from os import times_result
from threading import Thread, Event
from time import sleep


# Evento para sinalizar cancelamento
cancelar_processo = Event()

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
            host_name = socket.gethostbyaddr(ip_host_)[0]

            if len(host_name) == 0:
                host_name = '<desconhecido>'

            self.LISTA_HOSTNAME.append(host_name)
        except socket.herror:
            ...

    def icmp_ip_online(self, ip_host_):

        resposta_icmp = subprocess.run(
                'ping ' + f'{ip_host_} ' + '-n 2 -w 1 ', stdout=subprocess.PIPE, text=True
            )
        if resposta_icmp.returncode == 0:
            print(f'{ip_host_} [✓]')
        else:
            print(f'{ip_host_} [✗]')


def escutar_cancelamento():
    opc = input('[0] para cancelar: ')
    if opc == '0':
        cancelar_processo.set()

lista_ip_host = [
    '192.168.0.10',
    '192.168.0.15',
    '192.168.0.16',
    '192.168.0.250',
]

# Criando obj
obj_ping = ManipulacaoIcmpHosts()

if __name__ == '__main__':
    # lista_end_hosts = '192.168.0.250', '192.168.0.25'
    # result = obj_ping.ping_icmp_redeLocal(lista_end_hosts)

    while not cancelar_processo.is_set():
        threads = list()
        for ip in lista_ip_host:
            processo = Thread(target=obj_ping.icmp_ip_online, args=(ip,))
            processo.start()
            threads.append(processo)

        for thread in threads:
            thread.join()

        print('---' * 30)
        print('Repetindo processo...')
        sleep(10)

        # Inicia thread de escuta de cancelamento
        Thread(target=escutar_cancelamento, daemon=True).start()

        # print()
    # for chave, valor in result.items():
    #     print(f'{chave}:')
    #     print('---' * 30)
    #     for item in valor:
    #         print(item)
    #     print()
    #     print()