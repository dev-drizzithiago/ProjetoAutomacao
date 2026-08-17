"""Wrapper sobre anydesk/main.py::GeranciadorDePacotes (reset do AnyDesk)."""
from __future__ import annotations

from app.modules.common import OperationResult
from app.modules.legacy_loader import import_legacy_main


def resetar_anydesk() -> list[OperationResult]:
    """Finaliza, limpa a configuração e reabre o AnyDesk duas vezes (mesmo
    fluxo do CLI original: a segunda abertura garante que o ID seja detectado)."""
    resultados: list[OperationResult] = []
    try:
        modulo = import_legacy_main("anydesk", "main.py", "legacy_anydesk_main")
        pacote = modulo.GeranciadorDePacotes()
    except Exception as error:  # noqa: BLE001 - qualquer falha de import vira mensagem amigável
        return [OperationResult(False, f"Não foi possível carregar o módulo AnyDesk: {error}")]

    etapas = (
        ("Finalizando o AnyDesk...", lambda: pacote.remover_processo("Finalizando o AnyDesk...")),
        ("Removendo configuração antiga...", lambda: pacote.removendo_config_anydesk()),
        ("Reabrindo o AnyDesk...", lambda: pacote.abrir_processo("Reabrindo o AnyDesk...")),
        ("Testando detecção do ID (fechar e reabrir)...", lambda: pacote.remover_processo("Testando AnyDesk...")),
        ("Reabrindo o AnyDesk novamente...", lambda: pacote.abrir_processo("Finalizando...")),
    )

    for descricao, acao in etapas:
        try:
            acao()
            resultados.append(OperationResult(True, descricao))
        except Exception as error:  # noqa: BLE001
            resultados.append(OperationResult(False, f"Falha em '{descricao}': {error}"))
            break

    return resultados
