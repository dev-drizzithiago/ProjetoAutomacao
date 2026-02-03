import wmi
import itertools
from time import sleep
from threading import Event, Thread


class InfoHardWareScan:
    conn_hardware = wmi.WMI()
    def __init__(self):
        self.lista_info_hardware = []


    def scan_hardware(self):

        result_busca_processador = self.conn_hardware.Win32_Processor()
        result_busca_memoria = self.conn_hardware.Win32_PhysicalMemory()
        # for listagem in result_busca_processador:
        #     self.lista_info_hardware.append({
        #         'Processador': listagem.Name,
        #         'Números Cores': listagem.NumberOfCores,
        #         'Número de Threads': listagem.NumberOfLogicalProcessors,
        #     })

        for listagem in result_busca_memoria:
            print(listagem.Name)
            print(int (listagem.Capacity) / 10243, 'GB')
            print(listagem.ConfiguredClockSpeed)
            print(listagem.Speed)
            print(listagem.PartNumber)
            print(listagem.SerialNumber)

    def _spinner(self, stop_event, prefix='Processando... '):
        ciclo = itertools.cycle(['|', '/', '-', '\\'])

        while not stop_event.is_set():
            # \r volta o cursor para início da linha
            print(f"\r{prefix} {next(ciclo)}", end='', flush=True)
            sleep(0.1)

        # limpa linha ao finalizar
        print('\n' + ' ' * 60 + '\r', end='', flush=True)

    def _run_spinner(self, texto_spinner):
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
    inicit_obj_scan._run_spinner('Buscando informações sobre o hardware...')
