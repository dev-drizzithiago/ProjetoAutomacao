"""Validação e elevação de privilégios de Administrador (UAC)."""
from __future__ import annotations

import ctypes
import sys


def is_admin() -> bool:
    """Retorna True se o processo atual já possui privilégios de Administrador."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> None:
    """Relança o processo atual solicitando elevação via UAC e encerra o processo atual."""
    params = " ".join(f'"{arg}"' for arg in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
