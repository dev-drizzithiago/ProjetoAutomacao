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

        for listagem in result_busca_processador:

            self.dict_info_hardware['Modelo'] = listagem.Name
            self.dict_info_hardware['Números Cores'] = listagem.NumberOfCores
            self.dict_info_hardware['Número de Threads'] = listagem.NumberOfLogicalProcessors

            self.lista_info_hardware.append({'Processador': self.dict_info_hardware})

        for listagem in result_busca_memoria:

            self.dict_info_hardware['Modelo'] = listagem.Name
            self.dict_info_hardware['Capacidade'] = str(int (listagem.Capacity) / 10243).split('.')[0]
            self.dict_info_hardware['Clock Speed'] = listagem.ConfiguredClockSpeed
            self.dict_info_hardware['Velocidade'] = listagem.Speed
            self.dict_info_hardware['Parte Number'] = listagem.PartNumber
            self.dict_info_hardware['Serial Number'] = listagem.SerialNumber

            self.lista_info_hardware.append({'Memoria': self.dict_info_hardware})

        for listagem in result_busca_placa_mae:

            self.dict_info_hardware['Placa Mae'] = listagem.Name
            self.dict_info_hardware['Fabricante'] = listagem.Manufacturer
            self.dict_info_hardware['Serial Number'] = listagem.SerialNumber
            self.dict_info_hardware['Numero Produto'] = listagem.Product
            self.dict_info_hardware['Versao'] = listagem.Version

            self.lista_info_hardware.append({'MainBoard': self.dict_info_hardware})

        for listagem in result_busca_disk:
            if listagem.DeviceID == "C:":
                porcetangem_espaco_livre = 100*float(listagem.FreeSpace) / float(listagem.Size)
                self.dict_info_hardware['Disco Local'] = listagem.Description
                self.dict_info_hardware['Capacidade'] =  str(int(listagem.Size) / 10243).split('.')[0]
                self.dict_info_hardware['Espaço Livre'] = f"{porcetangem_espaco_livre:.2f}"
                self.dict_info_hardware['Numero de Serie'] = listagem.VolumeSerialNumber

            self.lista_info_hardware.append({'Unidade': self.dict_info_hardware})

        print('\n')
        for item in self.lista_info_hardware:
            print(item)

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
