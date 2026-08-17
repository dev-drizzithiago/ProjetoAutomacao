"""Wrapper sobre alterando_permissao/main.py::AlterarPermissaoReunioes (Exchange Online).

Requer o pacote `cryptography` e um .env com AppId/CertificateThumbprint/
Organization/PATH_CERTIFICADO/PASSWORD já configurados (mesmo esquema do
script original em alterando_permissao/main.py). Sem isso, cada ação retorna
uma mensagem amigável em vez de estourar uma exceção não tratada na GUI.
"""
from __future__ import annotations

from app.modules.common import OperationResult
from app.modules.legacy_loader import import_legacy_main

_instancia = None


def _carregar_instancia():
    global _instancia
    if _instancia is None:
        modulo = import_legacy_main(
            "alterando_permissao", "main.py", "legacy_alterando_permissao_main"
        )
        _instancia = modulo.AlterarPermissaoReunioes()
    return _instancia


def criar_conceder_permissao_shared(grupo: str, email: str) -> OperationResult:
    try:
        instancia = _carregar_instancia()
        resultado = instancia.criar_conceder_permissao_shared(grupo, email)
        return OperationResult(True, str(resultado))
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao criar/conceder permissão do shared '{grupo}': {error}")


def verificar_permissoes(grupo: str) -> OperationResult:
    try:
        instancia = _carregar_instancia()
        resultado = instancia.verificando_permissoes(grupo)
        return OperationResult(True, str(resultado))
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao verificar permissões do grupo '{grupo}': {error}")


def conceder_permissoes_shared(grupo: str, email: str) -> OperationResult:
    try:
        instancia = _carregar_instancia()
        resultado = instancia.concedendo_permissoes_shared(grupo, email)
        return OperationResult(True, str(resultado))
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao conceder permissão para '{email}' em '{grupo}': {error}")


def verificar_calendario(email: str) -> OperationResult:
    try:
        instancia = _carregar_instancia()
        resultado = instancia.verif_calendarios(email)
        return OperationResult(True, str(resultado))
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao verificar calendário de '{email}': {error}")


def compartilhar_calendario(shared: str, usuario: str, permissao: str) -> OperationResult:
    try:
        instancia = _carregar_instancia()
        resultado = instancia.compartilhar_caixa_calendario(shared, usuario, permissao)
        return OperationResult(True, str(resultado))
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao compartilhar calendário de '{shared}' com '{usuario}': {error}")
