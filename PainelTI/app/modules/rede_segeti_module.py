"""Wrapper sobre utilitarios_segeti/config_adp_rede.py::ConfigAdpRedes."""
from __future__ import annotations

from app.modules.common import OperationResult
from app.modules.legacy_loader import import_legacy_main


def _carregar_instancia():
    modulo = import_legacy_main(
        "utilitarios_segeti", "config_adp_rede.py", "legacy_utilitarios_segeti_config_adp_rede"
    )
    return modulo.ConfigAdpRedes()


def detectar_adaptadores() -> tuple[OperationResult, list[dict]]:
    """Lista os adaptadores de rede (nome + tipo: 802.3/802.11)."""
    try:
        instancia = _carregar_instancia()
        interfaces = instancia.buscando__info__adaptadores__()
        return OperationResult(True, f"{len(interfaces)} adaptador(es) encontrado(s)."), interfaces
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao detectar adaptadores: {error}"), []


def configurar_adaptadores(interfaces: list[dict]) -> OperationResult:
    """Renomeia os adaptadores para o padrão SEGETI e configura DHCP em cada um."""
    try:
        instancia = _carregar_instancia()
        instancia.configurando_adaptador_rede(interfaces)
        return OperationResult(True, "Adaptadores configurados com padrão SEGETI (DHCP).")
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao configurar adaptadores: {error}")


def adicionar_entrada_host() -> OperationResult:
    """Adiciona a resolução do domínio da empresa no arquivo hosts."""
    try:
        instancia = _carregar_instancia()
        instancia.add_host_entry()
        return OperationResult(True, "Entrada de host adicionada/verificada.")
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao adicionar entrada de host: {error}")


def testar_conectividade() -> OperationResult:
    """Testa a conectividade (ping) com o site da empresa."""
    try:
        instancia = _carregar_instancia()
        ok = instancia.func_teste_site_empresa()
        if ok:
            return OperationResult(True, "Conectividade com o site da empresa confirmada.")
        return OperationResult(False, "Não foi possível confirmar a conectividade com o site da empresa.")
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao testar conectividade: {error}")
