"""Caminhos e constantes globais do PainelTI."""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "PainelTI"


def _app_dir() -> Path:
    """Pasta do próprio app: ao lado do .exe quando compilado (PyInstaller),
    ou a raiz do projeto (PainelTI/) quando rodando via `python main.py`.

    Usada para configs que precisam viajar junto com o app na distribuição
    para o usuário final (ex.: wifi_profiles.json), diferente de LOCAL_APPDATA_DIR
    (estado por usuário/máquina, não é enviado com o app).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _bundle_dir() -> Path:
    """Pasta de recursos empacotados só-leitura (ex.: ícone). Compilado com
    PyInstaller (onedir), isso é `sys._MEIPASS` — que na prática é a pasta
    `_internal/` ao lado do .exe, não a mesma pasta do .exe (diferente de
    `APP_DIR`, usada para config editável que precisa ficar visível/acessível
    pra equipe de TI, não escondida dentro de `_internal/`).
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parents[1]


APP_DIR: Path = _app_dir()
CONFIG_DIR: Path = APP_DIR / "config"
RELATORIOS_DIR: Path = APP_DIR / "relatorios"
ICON_PATH: Path = _bundle_dir() / "assets" / "icon.ico"

# Diretório operacional do app (estado interno específico da máquina/usuário)
LOCAL_APPDATA_DIR: Path = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_NAME

# Documentos do usuário: logs estruturados
DOCUMENTS_DIR: Path = Path(os.path.expanduser("~\\Documents")) / APP_NAME
LOGS_DIR: Path = DOCUMENTS_DIR / "Logs"

for _dir in (CONFIG_DIR, RELATORIOS_DIR, LOCAL_APPDATA_DIR, DOCUMENTS_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
