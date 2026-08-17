"""Wrapper sobre mikrotik_monitoramento/ (conectar + 1 busca de logs sob demanda).

Requer o pacote `librouteros` e as variáveis de ambiente mikro_USERNAME/
mikro_PASSWORD/mikro_HOST_FW/mikro_PORT_FW (via .env, mesmo esquema do script
original). Diferente do main.py original (loop infinito com sleep(600)), aqui
a busca é uma ação pontual: o usuário clica em "Buscar Agora" quando quiser
atualizar os dados.
"""
from __future__ import annotations

from app.modules.common import OperationResult
from app.modules.legacy_loader import import_legacy_main


def conectar_e_buscar_logs() -> tuple[OperationResult, dict]:
    try:
        modulo_main = import_legacy_main(
            "mikrotik_monitoramento", "main.py", "legacy_mikrotik_monitoramento_main"
        )
        modulo_logs = import_legacy_main(
            "mikrotik_monitoramento", "mikrotik_logs.py", "legacy_mikrotik_monitoramento_logs"
        )
        modulo_icmp = import_legacy_main(
            "mikrotik_monitoramento", "manipulacao_icmp.py", "legacy_mikrotik_monitoramento_icmp"
        )
    except ImportError as error:
        return (
            OperationResult(
                False,
                "Não foi possível carregar o módulo Mikrotik. Verifique se o pacote "
                f"'librouteros' está instalado. Detalhe: {error}",
            ),
            {},
        )
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha inesperada ao carregar o módulo Mikrotik: {error}"), {}

    try:
        conexao = modulo_main.ConexaoFirewall()
        api = conexao.conexao_fw()
        if api is None:
            return (
                OperationResult(
                    False,
                    "Não foi possível conectar ao Mikrotik. Verifique as variáveis "
                    "mikro_USERNAME/mikro_PASSWORD/mikro_HOST_FW/mikro_PORT_FW no .env.",
                ),
                {},
            )

        obj_logs = modulo_logs.BuscandoLogsMikrotik(api)
        obj_logs.log_dhcp(None)
        resultado_ip = obj_logs.analise_de_logs()

        obj_icmp = modulo_icmp.ManipulacaoIcmpHosts()
        informacoes_icmp = obj_icmp.ping_icmp_redeLocal(resultado_ip)

        qtd_ip = len(informacoes_icmp.get("LISTA_PING_ON", []))
        qtd_host = len(informacoes_icmp.get("LISTA_HOSTNAME", []))
        return (
            OperationResult(True, f"Busca concluída: {qtd_ip} IP(s) ativo(s), {qtd_host} hostname(s)."),
            informacoes_icmp,
        )
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao buscar logs do Mikrotik: {error}"), {}
