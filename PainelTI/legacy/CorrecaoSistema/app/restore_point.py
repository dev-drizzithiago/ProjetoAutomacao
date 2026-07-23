"""Criação de Pontos de Restauração do Windows via PowerShell.

O Windows limita, por padrão, a criação de pontos de restauração a 1 a cada
24 horas quando disparada por script (chave de registro
SystemRestorePointCreationFrequency). Este módulo detecta esse cenário e
oferece uma função explícita para reduzir o intervalo (requer confirmação
do usuário na GUI).
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

_FREQUENCY_REGISTRY_PATH = r"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
_FREQUENCY_VALUE_NAME = "SystemRestorePointCreationFrequency"

_LIMIT_HINT = "since the last successful checkpoint"


@dataclass(frozen=True)
class RestorePointResult:
    success: bool
    message: str
    limited_by_frequency: bool = False


def create_restore_point(description: str = "CorrecaoSistema - Ponto Manual") -> RestorePointResult:
    """Cria um ponto de restauração do sistema. Retorna o resultado da operação,
    identificando quando a falha é causada pela limitação padrão de 24h do Windows."""
    command = (
        f'Checkpoint-Computer -Description "{description}" '
        f'-RestorePointType "MODIFY_SETTINGS"'
    )
    process = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    output = (process.stdout or "") + (process.stderr or "")

    if process.returncode == 0:
        return RestorePointResult(success=True, message="Ponto de restauração criado com sucesso.")

    limited = _LIMIT_HINT.lower() in output.lower()
    if limited:
        return RestorePointResult(
            success=False,
            message=(
                "O Windows permite apenas 1 ponto de restauração a cada 24 horas "
                "quando criado via script. Utilize a opção 'Permitir múltiplos pontos "
                "por dia' se realmente necessário."
            ),
            limited_by_frequency=True,
        )
    return RestorePointResult(success=False, message=output.strip() or "Falha desconhecida ao criar ponto de restauração.")


def allow_frequent_restore_points() -> RestorePointResult:
    """Reduz a frequência mínima entre pontos de restauração para 0 (permite múltiplos
    pontos por dia). Requer privilégios de Administrador. Ação reversível via
    restore_default_restore_point_frequency()."""
    command = (
        f'New-ItemProperty -Path "{_FREQUENCY_REGISTRY_PATH}" '
        f'-Name "{_FREQUENCY_VALUE_NAME}" -Value 0 -PropertyType DWord -Force'
    )
    process = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if process.returncode == 0:
        return RestorePointResult(success=True, message="Restrição de 24h removida para esta sessão.")
    return RestorePointResult(success=False, message=(process.stderr or "Falha ao ajustar o registro.").strip())


def restore_default_restore_point_frequency() -> RestorePointResult:
    """Restaura o comportamento padrão do Windows (remove o valor customizado)."""
    command = (
        f'Remove-ItemProperty -Path "{_FREQUENCY_REGISTRY_PATH}" '
        f'-Name "{_FREQUENCY_VALUE_NAME}" -ErrorAction SilentlyContinue'
    )
    process = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return RestorePointResult(success=process.returncode == 0, message="Comportamento padrão restaurado.")
