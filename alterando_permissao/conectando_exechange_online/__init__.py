from subprocess import run, PIPE
import itertools
from time import sleep
from threading import Event, Thread

class ConexaoExchangeOnline:
    def __init__(self):
        self.init_obj_spinner = ProcessoRun()
        self.resultado_processo = None

    def conectando(self, *credenciais):
        print(credenciais)

    def processando_modulo_exchange(self, COMANDO_SHELL, texto_processo):

        result_comando = self.init_obj_spinner.run_spinner(COMANDO_SHELL, texto_processo)

class ProcessoRun:

    def _run_processo_powershell(self, comando_shell):
        resultado_processo = run(
            ["powershell", "-NoExit", "-Command", comando_shell],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            text=True
        )

        return resultado_processo

    def _spinner(self, stop_event, prefix='Processando... '):
        ciclo = itertools.cycle(['|', '/', '-', '\\'])

        while not stop_event.is_set():
            # \r volta o cursor para início da linha
            print(f"\r{prefix} {next(ciclo)}", end='', flush=True)
            sleep(0.1)

        # limpa linha ao finalizar
        print('\n' + ' ' * 60 + '\r', end='', flush=True)

    def run_spinner(self, comando_str, texto_spinner):
        stop_event = Event()
        _thread = Thread(target=self._spinner, args=(stop_event, texto_spinner), daemon=True)
        _thread.start()
        try:
            result = self._run_processo_powershell(comando_str)
            return result
        finally:
            stop_event.set()
            _thread.join()

if __name__ == '__main__':
    init_obj_conexao_exchange_online = ConexaoExchangeOnline()
    init_obj_conexao_exchange_online.conectando('thiago', '123')
