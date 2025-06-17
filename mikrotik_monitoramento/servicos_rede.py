from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

servico = "_services._dns-sd._udp.local."

class DescobertaRede(ServiceListener):
    def adicionar_servicos(self, zeroconf, tipo_servico, nome):
        info = zeroconf.get_service_info(tipo_servico, nome)
        if info:
            print(f'Servicos encontrados: {nome}')

    def remove_servicos(self, zeroconf, tipo, nome):
        print(f'[-] Servico removido: {nome}')

    def atualiza_servico(self, zeroconf, tipo, nome):
        print(f'[-] Servico atualizado: {nome}')

zeroconf = Zeroconf()
listener = DescobertaRede()

Browser = ServiceBrowser(zeroconf, servico, listener)
