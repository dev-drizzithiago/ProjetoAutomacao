"""Registro e remoção de tarefa agendada (disparo no Logon) via schtasks.exe."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from pointRestaurations.logger import log_event

TASK_NAME = "pointRestaurations_LogonCheckpoint"


@dataclass
class TaskResult:
    success: bool
    message: str


def _executable_target() -> tuple[str, str]:
    """Retorna (comando, argumentos) apontando para o .exe compilado ou para python + main.py."""
    if getattr(sys, "frozen", False):
        return sys.executable, "--run-silent"
    main_script = Path(__file__).resolve().parent.parent / "main.py"
    return sys.executable, f'"{main_script}" --run-silent'


def install_logon_task() -> TaskResult:
    """Cria tarefa no Task Scheduler disparada no logon do usuário atual, com privilégio máximo."""
    command, args = _executable_target()
    tr_value = f'"{command}" {args}'.strip()

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", tr_value,
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except OSError as exc:
        log_event("ERROR", "Falha ao criar tarefa agendada.", {"exception": str(exc)})
        return TaskResult(False, f"Falha ao criar tarefa agendada: {exc}")

    if result.returncode == 0:
        log_event("SUCCESS", "Tarefa agendada instalada com sucesso.", {"task_name": TASK_NAME})
        return TaskResult(True, "Tarefa agendada instalada com sucesso (dispara no logon).")

    stderr = result.stderr.strip() or result.stdout.strip()
    log_event("ERROR", "Falha ao instalar tarefa agendada.", {"stderr": stderr})
    return TaskResult(False, f"Falha ao instalar tarefa agendada: {stderr}")


def remove_logon_task() -> TaskResult:
    cmd = ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except OSError as exc:
        log_event("ERROR", "Falha ao remover tarefa agendada.", {"exception": str(exc)})
        return TaskResult(False, f"Falha ao remover tarefa agendada: {exc}")

    if result.returncode == 0:
        log_event("SUCCESS", "Tarefa agendada removida com sucesso.", {"task_name": TASK_NAME})
        return TaskResult(True, "Tarefa agendada removida com sucesso.")

    stderr = result.stderr.strip() or result.stdout.strip()
    log_event("WARNING", "Falha ao remover tarefa agendada (pode não existir).", {"stderr": stderr})
    return TaskResult(False, f"Falha ao remover tarefa agendada: {stderr}")


def task_exists() -> bool:
    cmd = ["schtasks", "/Query", "/TN", TASK_NAME]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0
