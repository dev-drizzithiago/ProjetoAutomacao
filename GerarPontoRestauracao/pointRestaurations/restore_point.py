"""Criação de Pontos de Restauração do Windows via PowerShell (Checkpoint-Computer)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime

from pointRestaurations.logger import log_event

# O Windows limita a criação de pontos de restauração via script/API a 1 a cada 24h.
RESTORE_POINT_TYPE = "MODIFY_SETTINGS"


@dataclass
class RestorePointResult:
    success: bool
    message: str
    throttled: bool = False


def _build_description() -> str:
    return f"pointRestaurations - {datetime.now().strftime('%d/%m/%Y %H:%M')}"


def create_restore_point() -> RestorePointResult:
    """Cria um ponto de restauração via PowerShell. Requer privilégios de Administrador."""
    description = _build_description()
    command = (
        f"Checkpoint-Computer -Description '{description}' "
        f"-RestorePointType '{RESTORE_POINT_TYPE}'"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        log_event("ERROR", "Timeout ao executar Checkpoint-Computer.")
        return RestorePointResult(False, "Tempo limite excedido ao criar o ponto de restauração.")
    except OSError as exc:
        log_event("ERROR", "Falha ao invocar o PowerShell.", {"exception": str(exc)})
        return RestorePointResult(False, f"Falha ao invocar o PowerShell: {exc}")

    if result.returncode == 0:
        log_event("SUCCESS", "Ponto de restauração criado com sucesso.", {"description": description})
        return RestorePointResult(True, "Ponto de restauração criado com sucesso.")

    stderr = result.stderr.strip()

    # Restrição padrão do Windows: apenas 1 ponto de restauração por script a cada 24h.
    if "24" in stderr or "frequently" in stderr.lower() or "throttl" in stderr.lower():
        log_event("WARNING", "Criação bloqueada pela restrição de 24h do Windows.", {"stderr": stderr})
        return RestorePointResult(
            False,
            "Já existe um ponto de restauração criado nas últimas 24 horas "
            "(restrição padrão do Windows).",
            throttled=True,
        )

    if "acesso negado" in stderr.lower() or "access is denied" in stderr.lower() or "administrator" in stderr.lower():
        log_event("ERROR", "Permissão insuficiente para criar o ponto de restauração.", {"stderr": stderr})
        return RestorePointResult(False, "Permissão negada. Execute o aplicativo como Administrador.")

    log_event("ERROR", "Falha desconhecida ao criar o ponto de restauração.", {"stderr": stderr})
    return RestorePointResult(False, f"Falha ao criar o ponto de restauração: {stderr or 'erro desconhecido'}")
