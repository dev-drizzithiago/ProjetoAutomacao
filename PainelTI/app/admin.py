"""Validação e elevação de privilégios de Administrador (UAC)."""
from __future__ import annotations

import ctypes
import os
import sys


def is_admin() -> bool:
    """Retorna True se o processo atual já possui privilégios de Administrador."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> bool:
    """Relança o processo atual solicitando elevação via UAC.

    Usa o caminho absoluto do script e define o diretório de trabalho
    explicitamente: sem isso, o processo elevado herda um cwd diferente
    (ex.: System32) e o Python falha ao localizar main.py, fechando a
    janela quase instantaneamente. Retorna True se o UAC foi aceito.
    """
    script_path = os.path.abspath(sys.argv[0])
    work_dir = os.path.dirname(script_path)
    params = " ".join(f'"{arg}"' for arg in [script_path, *sys.argv[1:]])

    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, work_dir, 1
    )
    # ShellExecuteW retorna um valor <= 32 em caso de falha (ex.: UAC cancelado).
    return result > 32
