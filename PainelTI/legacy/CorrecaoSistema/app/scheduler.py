"""Integração com o Agendador de Tarefas do Windows (schtasks) para disparo no Logon."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from app.constants import SCHEDULED_TASK_NAME


@dataclass(frozen=True)
class SchedulerResult:
    success: bool
    message: str


def create_logon_task(target_path: str, args: str = "") -> SchedulerResult:
    """Cria/atualiza uma tarefa agendada disparada no Logon do usuário, executando
    com o nível de privilégio mais alto (Administrador). Requer privilégios de Admin."""
    task_run = f'"{target_path}" {args}'.strip()
    process = subprocess.run(
        [
            "schtasks", "/Create",
            "/TN", SCHEDULED_TASK_NAME,
            "/TR", task_run,
            "/SC", "ONLOGON",
            "/RL", "HIGHEST",
            "/F",
        ],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if process.returncode == 0:
        return SchedulerResult(success=True, message=f"Tarefa '{SCHEDULED_TASK_NAME}' agendada para logon.")
    return SchedulerResult(success=False, message=(process.stderr or process.stdout).strip())


def remove_logon_task() -> SchedulerResult:
    """Remove a tarefa agendada no Logon, se existir."""
    process = subprocess.run(
        ["schtasks", "/Delete", "/TN", SCHEDULED_TASK_NAME, "/F"],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if process.returncode == 0:
        return SchedulerResult(success=True, message=f"Tarefa '{SCHEDULED_TASK_NAME}' removida.")
    return SchedulerResult(success=False, message=(process.stderr or process.stdout).strip())


def task_exists() -> bool:
    """Verifica se a tarefa agendada já está registrada no Windows."""
    process = subprocess.run(
        ["schtasks", "/Query", "/TN", SCHEDULED_TASK_NAME],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return process.returncode == 0
