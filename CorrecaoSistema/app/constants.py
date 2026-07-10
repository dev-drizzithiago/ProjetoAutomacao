"""Caminhos e constantes globais do CorrecaoSistema."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "CorrecaoSistema"

# Diretório operacional do app (scripts/executável/estado interno)
LOCAL_APPDATA_DIR: Path = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_NAME

# Documentos do usuário: logs estruturados e relatórios em PDF
DOCUMENTS_DIR: Path = Path(os.path.expanduser("~\\Documents")) / APP_NAME
LOGS_DIR: Path = DOCUMENTS_DIR / "Logs"
REPORTS_DIR: Path = DOCUMENTS_DIR / "Relatorios"

for _dir in (LOCAL_APPDATA_DIR, DOCUMENTS_DIR, LOGS_DIR, REPORTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Cores do padrão corporativo (relatórios PDF)
COLOR_HEADER_BLUE = (30, 58, 138)  # #1e3a8a
COLOR_ROW_ALT = (235, 240, 249)
COLOR_WHITE = (255, 255, 255)
COLOR_TEXT = (20, 20, 20)

# Agendador de Tarefas
SCHEDULED_TASK_NAME = APP_NAME
