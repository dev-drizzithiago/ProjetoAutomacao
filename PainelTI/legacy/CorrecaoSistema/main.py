"""Ponto de entrada do CorrecaoSistema.

Garante privilégios de Administrador (UAC) antes de iniciar a interface gráfica.
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime

from app.admin import is_admin, relaunch_as_admin
from app.constants import LOGS_DIR


def main() -> None:
    if not is_admin():
        accepted = relaunch_as_admin()
        if not accepted:
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                None,
                "A elevação de Administrador foi cancelada ou falhou.\n"
                "O CorrecaoSistema precisa ser executado como Administrador.",
                "CorrecaoSistema",
                0x10,  # MB_ICONERROR
            )
        sys.exit(0)

    silent = "--silent" in sys.argv[1:]

    try:
        if silent:
            # Disparado pela tarefa agendada no Logon: roda o diagnóstico
            # completo em segundo plano, sem abrir nenhuma janela.
            from app.headless import run_silent_diagnostics

            run_silent_diagnostics()
            return

        from app.gui import run
    except ModuleNotFoundError as exc:
        if silent:
            # Sem GUI para mostrar o erro; grava só no log de falhas.
            raise
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            None,
            f"Dependência ausente: {exc.name}\n\n"
            "As bibliotecas do CorrecaoSistema não estão instaladas neste "
            "interpretador Python. Execute o app usando o arquivo Iniciar.bat "
            "(ele usa o ambiente virtual correto do projeto) em vez de abrir "
            "main.py diretamente.",
            "CorrecaoSistema - Dependência ausente",
            0x10,  # MB_ICONERROR
        )
        sys.exit(1)

    run()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - garantir que falhas fatais fiquem registradas
        crash_file = LOGS_DIR / f"crash_{datetime.now():%Y%m%d_%H%M%S}.txt"
        crash_file.write_text(traceback.format_exc(), encoding="utf-8")
        raise
