
import subprocess
import socket

class ManipulacaoIcmpHosts:
    def __init__(self):
        self.ip_address = None
        ...

    def ping_icmp_redeLocal(self, endereco_ip):
        self.ip_address = endereco_ip
        ping_result = subprocess.run(
            [
            'ping', '-c', '1', self.ip_address
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

