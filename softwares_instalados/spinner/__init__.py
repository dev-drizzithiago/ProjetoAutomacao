import itertools
from time import sleep
from subprocess import run


def _run_processo_powershell(self, comando_shell):
    resultado_processo = run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", comando_shell],
        shell=True,
        check=True,
        capture_output=True
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


def _run_spinner(self, comando_str, texto_spinner):
    stop_event = Event()
    _thread = Thread(target=self._spinner, args=(stop_event, texto_spinner), daemon=True)
    _thread.start()
    try:
        result = self._run_processo_powershell(comando_str)
        return result
    finally:
        stop_event.set()
        _thread.join()