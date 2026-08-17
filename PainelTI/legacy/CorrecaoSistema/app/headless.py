"""Execução silenciosa do diagnóstico completo, sem interface gráfica.

Usada pela tarefa agendada no Logon (--silent): roda DISM/SFC em sequência,
registra tudo no log estruturado e gera um relatório PDF ao final, sem abrir
nenhuma janela.
"""
from __future__ import annotations

from app.logger import EventLogger
from app.report import generate_pdf_report
from app.system_repair import run_full_diagnostics


def run_silent_diagnostics() -> None:
    logger = EventLogger()
    logger.info("Diagnóstico automático (logon) iniciado em modo silencioso.")

    def on_output(_text: str, _overwrite: bool = False) -> None:
        pass  # sem console em modo silencioso; a saída completa já vai para o log JSON via system_repair

    def on_progress(current: int, total: int, name: str) -> None:
        logger.info(f"Etapa {current}/{total}: {name}")

    try:
        results = run_full_diagnostics(on_output, on_progress)
        for result in results:
            if result.success:
                logger.success(f"{result.step.name} concluído com sucesso.")
            else:
                logger.error(
                    f"{result.step.name} falhou (código {result.return_code}).",
                    output=result.output[-2000:],
                )
    except Exception as exc:  # noqa: BLE001 - garantir que o relatório seja gerado mesmo em falha
        logger.error(f"Falha inesperada no diagnóstico silencioso: {exc}")

    try:
        generate_pdf_report(logger.events, title="Diagnóstico Automático (Logon)")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Falha ao gerar relatório PDF: {exc}")
