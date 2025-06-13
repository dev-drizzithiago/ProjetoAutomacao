
import subprocess
import socket
import os

class ManipulacaoIcmpHosts:

    LISTA_PING_ON = list()
    LISTA_PING_OFF = list()
    LISTA_HOSTNAME = list()
    HOST = 1

    def __init__(self):
        self.ip_address = None
        ...

    def ping_icmp_redeLocal(self, endereco_rede):
        verificando_host_rede = int(endereco_rede.split('.')[-1])
        prefixo_rede_ = endereco_rede.split('.')[:-1]

        if verificando_host_rede > 0:
            print('Rede invalida.')
            return

        while True:

            endereco_ip = f'{prefixo_rede_[0]}.{prefixo_rede_[1]}.{prefixo_rede_[2]}.{self.HOST}'
            ping_result = subprocess.run(
                'ping ' + f'{endereco_ip} ' + '-n 1 -w 1 ', stdout=subprocess.PIPE, text=True
            )

            if ping_result.returncode == 0:
                self.LISTA_PING_ON.append(endereco_ip)
                self.buscando_host(endereco_ip)
            else:
                self.LISTA_PING_OFF.append(endereco_ip)

            if self.HOST == 254:
                break

        return {'LISTA_HOSTNAME': self.LISTA_HOSTNAME,'LISTA_PING_ON': self.LISTA_PING_ON,}

    def buscando_host(self, endereco_ip):
        try:
            host_name = socket.gethostbyaddr(endereco_ip)
            self.LISTA_HOSTNAME.append(host_name[0])
        except socket.herror:
            ...
            # print(f'Não foi encontrado o hostname dessa do endereço de ip {endereco_ip}')


obj_ping = ManipulacaoIcmpHosts()

if __name__ == '__main__':
    while True:
        entrada_rede_base = input('Digital uma rede base (192.168.0.0): ')
        result = obj_ping.ping_icmp_redeLocal(entrada_rede_base)

        if not result:
            print('Digital uma rede Base...!')
