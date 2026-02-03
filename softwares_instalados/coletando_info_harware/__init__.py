import wmi
import itertools
from time import sleep
from threading import Event, Thread


class InfoHardWareScan:
    conn_hardware = wmi.WMI()
    def __init__(self):
        pass


    def scan_hardware(self):
        sleep(10)
        return  self.conn_hardware.classes

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
    result_scan = inicit_obj_scan._run_spinner('Buscando informações sobre o hardware...')

    print(result_scan)

