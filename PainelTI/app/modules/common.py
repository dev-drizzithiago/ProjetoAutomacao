"""Tipo de retorno compartilhado pelos wrappers de módulos legados."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperationResult:
    success: bool
    message: str
