"""Execução sequencial das etapas de reparo do Windows (DISM + SFC).

Cada etapa é executada via PowerShell e aguarda a finalização completa do
processo anterior antes de iniciar a próxima, conforme exigido para estes
comandos (DISM e SFC não podem ser executados concorrentemente).
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable

OutputCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int, str], None]  # (etapa_atual, total_etapas, nome_etapa)


@dataclass(frozen=True)
class RepairStep:
    name: str
    command: str  # comando PowerShell


STEPS: tuple[RepairStep, ...] = (
    RepairStep("Limpeza de Pontos de Montagem", "Dism /Cleanup-Mountpoints"),
    RepairStep("Verificação da Imagem (ScanHealth)", "Dism /Online /Cleanup-Image /ScanHealth"),
    RepairStep("Restauração da Imagem (RestoreHealth)", "Dism /Online /Cleanup-Image /RestoreHealth"),
    RepairStep("Verificação de Arquivos de Sistema (SFC)", "sfc /scannow"),
)


@dataclass(frozen=True)
class StepResult:
    step: RepairStep
    success: bool
    return_code: int
    output: str


def _run_powershell(command: str, on_output: OutputCallback) -> tuple[int, str]:
    """Executa um comando via PowerShell, transmitindo a saída em tempo real."""
    process = subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="cp850",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    collected_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        clean = line.rstrip("\n")
        collected_lines.append(clean)
        on_output(clean)
    process.wait()  # garante que o processo finalizou antes de retornar
    return process.returncode, "\n".join(collected_lines)


def run_full_diagnostics(
    on_output: OutputCallback,
    on_progress: ProgressCallback,
) -> list[StepResult]:
    """Executa DISM (Cleanup-Mountpoints, ScanHealth, RestoreHealth) e SFC /SCANNOW
    em sequência estrita. Retorna o resultado de cada etapa."""
    results: list[StepResult] = []
    total = len(STEPS)
    for index, step in enumerate(STEPS, start=1):
        on_progress(index, total, step.name)
        on_output(f"--- Iniciando: {step.name} ---")
        return_code, output = _run_powershell(step.command, on_output)
        success = return_code == 0
        on_output(f"--- Concluído: {step.name} (código {return_code}) ---")
        results.append(StepResult(step=step, success=success, return_code=return_code, output=output))
    return results
