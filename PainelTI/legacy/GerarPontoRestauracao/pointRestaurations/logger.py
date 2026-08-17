"""Registro estruturado de execução (JSON lines) na pasta Documents do usuário."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

LogLevel = Literal["INFO", "WARNING", "ERROR", "SUCCESS"]

DOCUMENTS_DIR = Path(os.path.expanduser("~\\Documents"))
LOG_DIR = DOCUMENTS_DIR / "pointRestaurations" / "logs"


def _ensure_log_dir() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR


def _log_file_path() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    return _ensure_log_dir() / f"execucao_{date_str}.jsonl"


def log_event(level: LogLevel, message: str, details: dict | None = None) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "message": message,
        "details": details or {},
    }
    with open(_log_file_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_recent_logs(max_entries: int = 100) -> list[dict]:
    path = _log_file_path()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    entries = [json.loads(line) for line in lines[-max_entries:]]
    return entries
