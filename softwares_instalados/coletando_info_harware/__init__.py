import wmi
import psutil
import itertools
from time import sleep
from threading import Event, Thread


class InfoHardWareScan:

    conn_hardware = wmi.WMI()

    conn_disk_local = psutil.disk_partitions()

    def __init__(self):
        self.lista_info_hardware = []
        self.dict_info_hardware = {}
        self.dict_geral_hardware = {}


    def scan_hardware(self):

        result_busca_processador = self.conn_hardware.Win32_Processor()
        result_busca_memoria = self.conn_hardware.Win32_PhysicalMemory()
        result_busca_placa_mae = self.conn_hardware.Win32_BaseBoard()
        result_busca_disk = self.conn_hardware.Win32_LogicalDisk()

        for listagem in result_busca_placa_mae:

            self.lista_info_hardware.append({'MainBoard': {
                'Placa Mae': listagem.Name,
                'Fabricante': listagem.Manufacturer,
                'Serial Number': listagem.SerialNumber,
                'Numero Produto': listagem.Product,
                'Versao': listagem.Version,
            }})

        for listagem in result_busca_processador:
            self.lista_info_hardware.append({'Processador': {
                'Modelo': listagem.Name,
                'Números Cores': listagem.NumberOfCores,
                'Número de Threads': listagem.NumberOfLogicalProcessors,
            }})

        for listagem in result_busca_memoria:

            self.lista_info_hardware.append({'Memoria': {
                'Modelo':  listagem.Name,
                'Capacidade':  f'{self._to_gib(listagem.Capacity)}GB',
                'Clock Speed':  listagem.ConfiguredClockSpeed,
                'Velocidade':  listagem.Speed,
                'Parte Number':  listagem.PartNumber,
                'Serial Number':  listagem.SerialNumber,
            }})

        for listagem in result_busca_disk:

            if listagem.DeviceID == "C:":
                porcetangem_espaco_livre = 100 * float(listagem.FreeSpace) / float(listagem.Size)

                self.lista_info_hardware.append({'HDD_SSD': {
                    'Disco Local': listagem.Description,
                    'Capacidade': f'{self._to_gib(listagem.Size)}GB',
                    'Espaço Livre': f"{porcetangem_espaco_livre:.2f}%",
                    'Numero de Serie': listagem.VolumeSerialNumber,
                    'Nome do Sistema': listagem.SystemName,
                }})

        return self.lista_info_hardware

    def _spinner(self, stop_event, prefix='Processando... '):
        ciclo = itertools.cycle(['|', '/', '-', '\\'])

        while not stop_event.is_set():
            # \r volta o cursor para início da linha
            print(f"\r{prefix} {next(ciclo)}", end='', flush=True)
            sleep(0.1)

        # limpa linha ao finalizar
        print('\n' + ' ' * 60 + '\r', end='', flush=True)

    @staticmethod
    def _to_gib(value):
        try:
            return int(int(value) / (1024 ** 3))
        except:
            return None


    def run_spinner(self, texto_spinner):
        stop_event = Event()
        _thread = Thread(target=self._spinner, args=(stop_event, texto_spinner), daemon=True)
        _thread.start()
        try:
            result = self.scan_hardware()
            return result
        finally:
            stop_event.set()
            _thread.join()

if __name__ == '__main__':
    inicit_obj_scan = InfoHardWareScan()
    result_scan = inicit_obj_scan.run_spinner('Buscando informações sobre o hardware...')
