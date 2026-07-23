"""Criação e consulta de Pontos de Restauração do Windows via PowerShell."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime

from pointRestaurations.logger import log_event

# O Windows limita a criação de pontos de restauração via script/API a 1 a cada 24h.
RESTORE_POINT_TYPE = "MODIFY_SETTINGS"

_TYPE_LABELS = {
    "0": "Instalação de Aplicativo",
    "1": "Desinstalação de Aplicativo",
    "10": "Instalação de Driver",
    "12": "Alteração de Configurações",
    "13": "Operação Cancelada",
    "14": "Backup do Windows",
}

_WMI_DATETIME_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})")


def _type_label(code: str) -> str:
    return _TYPE_LABELS.get(str(code), f"Tipo {code}")


def _parse_wmi_datetime(value: str) -> datetime | None:
    """Converte o formato de data WMI (ex.: 20260710143022.000000-180) para datetime."""
    if not value:
        return None
    match = _WMI_DATETIME_RE.match(value)
    if not match:
        return None
    year, month, day, hour, minute, second = (int(g) for g in match.groups())
    try:
        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


@dataclass
class RestorePointResult:
    success: bool
    message: str
    throttled: bool = False


@dataclass
class RestorePointInfo:
    sequence_number: int
    description: str
    creation_time: datetime | None
    restore_point_type: str

    @property
    def type_label(self) -> str:
        return _type_label(self.restore_point_type)


def list_restore_points() -> list[RestorePointInfo]:
    """Consulta os pontos de restauração já existentes no sistema, mais recentes primeiro."""
    command = (
        "Get-ComputerRestorePoint | "
        "Select-Object SequenceNumber, Description, CreationTime, RestorePointType | "
        "ConvertTo-Json -Compress"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        log_event("ERROR", "Falha ao consultar pontos de restauração existentes.", {"exception": str(exc)})
        return []

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "acesso negado" in stderr.lower() or "access is denied" in stderr.lower():
            log_event("WARNING", "Permissão insuficiente para consultar pontos de restauração.", {"stderr": stderr})
        else:
            log_event("ERROR", "Falha ao consultar pontos de restauração existentes.", {"stderr": stderr})
        return []

    if not result.stdout.strip():
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        log_event("WARNING", "Resposta inesperada do PowerShell ao listar pontos de restauração.")
        return []

    if isinstance(data, dict):
        data = [data]

    points = [
        RestorePointInfo(
            sequence_number=item.get("SequenceNumber", 0),
            description=item.get("Description") or "(sem descrição)",
            creation_time=_parse_wmi_datetime(item.get("CreationTime", "")),
            restore_point_type=str(item.get("RestorePointType", "")),
        )
        for item in data
    ]
    points.sort(key=lambda p: p.creation_time or datetime.min, reverse=True)
    return points


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
