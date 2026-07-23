"""Wrapper sobre desbloquer_view_explorer/main.py::DesbloqueioViewWindows."""
from __future__ import annotations

from app.modules.common import OperationResult
from app.modules.legacy_loader import import_legacy_main


def _carregar_instancia():
    modulo = import_legacy_main(
        "desbloquer_view_explorer", "main.py", "legacy_desbloquer_view_explorer_main"
    )
    return modulo.DesbloqueioViewWindows()


def desbloquear() -> OperationResult:
    """Remove a Marca da Web (MOTW) dos PDFs do usuário e reinicia o Explorer."""
    try:
        instancia = _carregar_instancia()
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Não foi possível carregar o módulo: {error}")

    try:
        if not instancia.desbloquear_view_windows():
            return OperationResult(False, "Falha ao desbloquear a visualização dos PDFs.")
        instancia.configurar_registro(instancia.comando_powershell_registro_windows_desbloqueio)
        instancia.reiniciar_explorer()
        return OperationResult(True, "Visualização de PDFs desbloqueada e Explorer reiniciado.")
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao desbloquear: {error}")


def bloquear() -> OperationResult:
    """Restaura a Marca da Web (MOTW) nos PDFs do usuário e reinicia o Explorer."""
    try:
        instancia = _carregar_instancia()
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Não foi possível carregar o módulo: {error}")

    try:
        if not instancia.bloquear_view_windows():
            return OperationResult(False, "Falha ao bloquear a visualização dos PDFs.")
        instancia.configurar_registro(instancia.comando_powershell_registro_windows_bloqueio)
        instancia.reiniciar_explorer()
        return OperationResult(True, "Visualização de PDFs bloqueada novamente e Explorer reiniciado.")
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao bloquear: {error}")
