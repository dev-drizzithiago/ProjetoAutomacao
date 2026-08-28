"""Auto-restart de aplicativos: monitora processos e reabre se fecharem.

Baseado no manual-watchdog-python.md (raiz do PainelTI), mas adaptado à
arquitetura do app: em vez de um loop Python residente (o PainelTI "não é um
serviço contínuo" — ver CLAUDE.md), a verificação roda como o próprio
PainelTI.exe disparado por uma tarefa agendada repetitiva
(--watchdog-silencioso), igual ao padrão já usado pro checkpoint diário em
manutencao_windows.py.
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil

from app.constants import CONFIG_DIR

WATCHDOG_CONFIG_PATH = CONFIG_DIR / "watchdog_apps.json"
TASK_NAME_WATCHDOG = "PainelTI_Watchdog"

# Nunca listar/monitorar o próprio PainelTI.
_NOMES_IGNORADOS = {"painelti", "python", "pythonw"}


@dataclass(frozen=True)
class OperationResult:
    success: bool
    message: str


@dataclass
class WatchdogApp:
    name: str
    exe_path: str
    enabled: bool = True


def _ler_config() -> dict:
    if not WATCHDOG_CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(WATCHDOG_CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def carregar_apps() -> list[WatchdogApp]:
    try:
        return [WatchdogApp(**item) for item in _ler_config().get("watchdog_apps", [])]
    except TypeError:
        return []


def carregar_intervalo_minutos() -> int:
    try:
        return int(_ler_config().get("check_interval_minutes", 5))
    except (TypeError, ValueError):
        return 5


def salvar_apps(apps: list[WatchdogApp], intervalo_minutos: int | None = None) -> None:
    WATCHDOG_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if intervalo_minutos is None:
        intervalo_minutos = carregar_intervalo_minutos()
    WATCHDOG_CONFIG_PATH.write_text(
        json.dumps(
            {"check_interval_minutes": intervalo_minutos, "watchdog_apps": [asdict(a) for a in apps]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def adicionar_ou_atualizar_app(apps: list[WatchdogApp], name: str, exe_path: str) -> list[WatchdogApp]:
    atualizados = [a for a in apps if a.name != name]
    atualizados.append(WatchdogApp(name=name, exe_path=exe_path, enabled=True))
    return atualizados


def remover_app(apps: list[WatchdogApp], name: str) -> list[WatchdogApp]:
    return [a for a in apps if a.name != name]


def alternar_app(apps: list[WatchdogApp], name: str) -> list[WatchdogApp]:
    return [WatchdogApp(a.name, a.exe_path, not a.enabled) if a.name == name else a for a in apps]


def listar_processos_em_execucao() -> list[tuple[str, str]]:
    """Programas com processo em execução agora, pra escolher qual monitorar
    sem precisar digitar o caminho do executável na mão."""
    encontrados: dict[str, str] = {}
    for proc in psutil.process_iter(["name", "exe"]):
        try:
            nome = proc.info["name"]
            caminho = proc.info["exe"]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        if not nome or not caminho:
            continue
        nome_base = nome[:-4] if nome.lower().endswith(".exe") else nome
        if nome_base.lower() in _NOMES_IGNORADOS:
            continue
        encontrados.setdefault(nome_base, caminho)
    return sorted(encontrados.items(), key=lambda item: item[0].lower())


def is_running(process_name: str) -> bool:
    for proc in psutil.process_iter(["name"]):
        try:
            nome = proc.info["name"]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        if nome and process_name.lower() in nome.lower():
            return True
    return False


def _restart_app(exe_path: str) -> OperationResult:
    try:
        subprocess.Popen([exe_path], shell=False)
        return OperationResult(True, f"App reiniciado: {exe_path}")
    except OSError as error:
        return OperationResult(False, f"Falha ao reiniciar {exe_path}: {error}")


def checar_e_reiniciar() -> list[OperationResult]:
    """Uma passada: reinicia todo app habilitado que não estiver rodando."""
    resultados: list[OperationResult] = []
    for app in carregar_apps():
        if app.enabled and not is_running(app.name):
            resultados.append(_restart_app(app.exe_path))
    return resultados


def executar_watchdog_silencioso() -> None:
    """Disparado pela tarefa agendada repetitiva (--watchdog-silencioso)."""
    checar_e_reiniciar()


# --------------------------------------------------------------- agendamento
def _target_command(flag: str) -> tuple[str, str]:
    """Igual ao padrão de manutencao_windows.py: aponta pro .exe compilado ou
    pro python + main.py."""
    if getattr(sys, "frozen", False):
        return sys.executable, flag
    main_script = Path(__file__).resolve().parent.parent / "main.py"
    return sys.executable, f'"{main_script}" {flag}'


def criar_tarefa_watchdog(intervalo_minutos: int) -> OperationResult:
    command, args = _target_command("--watchdog-silencioso")
    task_run = f'"{command}" {args}'.strip()

    try:
        result = subprocess.run(
            [
                "schtasks", "/Create", "/TN", TASK_NAME_WATCHDOG, "/TR", task_run,
                "/SC", "MINUTE", "/MO", str(intervalo_minutos), "/RL", "HIGHEST", "/F",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao criar tarefa agendada: {error}")

    if result.returncode == 0:
        return OperationResult(True, f"Watchdog ativado: verificação a cada {intervalo_minutos} minuto(s).")
    return OperationResult(False, (result.stderr or result.stdout).strip())


def remover_tarefa_watchdog() -> OperationResult:
    try:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", TASK_NAME_WATCHDOG, "/F"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao remover tarefa agendada: {error}")

    if result.returncode == 0:
        return OperationResult(True, "Watchdog desativado.")
    return OperationResult(False, (result.stderr or result.stdout).strip())


def tarefa_watchdog_existe() -> bool:
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME_WATCHDOG],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0
