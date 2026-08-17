"""pointRestaurations - ponto de entrada.

Cria automaticamente Pontos de Restauração do Windows, com GUI (customtkinter)
e modo silencioso (--run-silent) para disparo via Agendador de Tarefas no logon.
"""

from __future__ import annotations

import sys

from pointRestaurations.elevation import is_admin, relaunch_as_admin
from pointRestaurations.logger import log_event
from pointRestaurations.restore_point import create_restore_point


def main() -> None:
    if not is_admin():
        relaunch_as_admin()
        return

    if "--run-silent" in sys.argv:
        log_event("INFO", "Execução silenciosa disparada pelo Agendador de Tarefas.")
        result = create_restore_point()
        log_event(
            "SUCCESS" if result.success else "ERROR",
            f"Execução silenciosa finalizada: {result.message}",
        )
        return

    from pointRestaurations.gui import run_gui
    run_gui()


if __name__ == "__main__":
    main()
