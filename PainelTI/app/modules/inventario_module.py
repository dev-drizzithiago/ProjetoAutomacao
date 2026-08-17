"""Wrapper sobre softwares_instalados/ (scan de hardware + software -> planilhas Excel).

Requer os pacotes `wmi`, `psutil` e `pandas` no ambiente do PainelTI (usados
pelos módulos legados `coletando_info_harware`, `app_planilha_excel_hardware` e
`app_planilha_excel_software`). Se algum estiver ausente, a ação falha com uma
mensagem amigável em vez de derrubar o app inteiro.

As classes legadas de planilha salvam por padrão num servidor de rede fixo
(com fallback pra `C:\\PLANILHAS_EXCEL_APPS_LOCAL`) — aqui sobrescrevemos esses
caminhos para `RELATORIOS_DIR`, ao lado do próprio PainelTI, antes de usá-las.
"""
from __future__ import annotations

from app.constants import RELATORIOS_DIR
from app.modules.common import OperationResult
from app.modules.legacy_loader import import_legacy_main


def gerar_relatorio() -> OperationResult:
    """Faz o scan de hardware e software da máquina e gera as planilhas Excel
    correspondentes (mesmo fluxo do softwares_instalados/main.py)."""
    try:
        modulo_main = import_legacy_main(
            "softwares_instalados", "main.py", "legacy_softwares_instalados_main"
        )
    except ImportError as error:
        return OperationResult(
            False,
            "Não foi possível carregar o módulo de Inventário. Verifique se os "
            f"pacotes 'wmi', 'psutil' e 'pandas' estão instalados. Detalhe: {error}",
        )
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha inesperada ao carregar o Inventário: {error}")

    try:
        # Redireciona os dois destinos de arquivo (servidor fixo + fallback local)
        # para a mesma pasta local do PainelTI, evitando depender do servidor de rede.
        modulo_main.CreaterPlanilhaHardware.CAMINHO_ABS_SERVIDOR = str(RELATORIOS_DIR)
        modulo_main.CreaterPlanilhaHardware.LOCAL_PATH_RELATORIO = str(RELATORIOS_DIR)
        modulo_main.CreaterPlanilhaSoftware.CAMINHO_ABS_SERVIDOR = str(RELATORIOS_DIR)
        modulo_main.CreaterPlanilhaSoftware.LOCAL_PATH_RELATORIO = str(RELATORIOS_DIR)

        scan_hardware = modulo_main.InfoHardWareScan()
        dados_hardware = scan_hardware.run_spinner("Buscando informações sobre o hardware...")

        planilha_hardware = modulo_main.CreaterPlanilhaHardware(dados_hardware)
        planilha_hardware.dados_to_pandas()
        planilha_hardware.criar_planilha_dados_app()

        scan_software = modulo_main.RelatorioSoftwareInstalados()
        dados_software = scan_software.scan_software()

        planilha_software = modulo_main.CreaterPlanilhaSoftware()
        planilha_software.dados_to_pandas(dados_software)
        planilha_software.criar_planilha_dados_app()

        return OperationResult(
            True,
            f"Relatório gerado: {planilha_hardware.LOCAL_PATH_RELATORIO} "
            f"({len(dados_hardware)} itens de hardware, {len(dados_software)} softwares).",
        )
    except Exception as error:  # noqa: BLE001
        return OperationResult(False, f"Falha ao gerar o relatório de inventário: {error}")
