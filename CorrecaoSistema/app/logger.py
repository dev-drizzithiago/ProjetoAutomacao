"""Logger estruturado (JSON Lines) gravado em Documents\\CorrecaoSistema\\Logs."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from app.constants import LOGS_DIR

Level = Literal["INFO", "WARNING", "ERROR", "SUCCESS"]


class EventLogger:
    """Acumula eventos da sessão atual (usados também na geração de relatórios PDF)
    e persiste cada evento em disco em formato JSON Lines."""

    def __init__(self) -> None:
        self._session_start = datetime.now()
        self._log_file: Path = LOGS_DIR / f"log_{self._session_start:%Y%m%d_%H%M%S}.jsonl"
        self.events: list[dict[str, Any]] = []

    def log(self, level: Level, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        event = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "level": level,
            "message": message,
            "extra": extra or {},
        }
        self.events.append(event)
        try:
            with self._log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            pass  # falha de gravação em disco não deve derrubar a aplicação
        return event

    def info(self, message: str, **extra: Any) -> None:
        self.log("INFO", message, extra)

    def warning(self, message: str, **extra: Any) -> None:
        self.log("WARNING", message, extra)

    def error(self, message: str, **extra: Any) -> None:
        self.log("ERROR", message, extra)

    def success(self, message: str, **extra: Any) -> None:
        self.log("SUCCESS", message, extra)

    @property
    def log_file(self) -> Path:
        return self._log_file
