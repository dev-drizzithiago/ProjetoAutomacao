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
        relaunch_as_admin()
        sys.exit(0)

    from app.gui import run

    run()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - garantir que falhas fatais fiquem registradas
        crash_file = LOGS_DIR / f"crash_{datetime.now():%Y%m%d_%H%M%S}.txt"
        crash_file.write_text(traceback.format_exc(), encoding="utf-8")
        raise
