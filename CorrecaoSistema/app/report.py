"""Geração de relatórios em PDF (padrão corporativo) usando fpdf2.

Fontes Helvetica/Arial, cabeçalhos em azul escuro (#1e3a8a) e tabelas com
zebra striping. Os PDFs são sempre salvos em Documents\\CorrecaoSistema\\Relatorios.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

from app.constants import COLOR_HEADER_BLUE, COLOR_ROW_ALT, COLOR_TEXT, COLOR_WHITE, REPORTS_DIR


class _CorporateReport(FPDF):
    def header(self) -> None:
        self.set_fill_color(*COLOR_HEADER_BLUE)
        self.set_text_color(*COLOR_WHITE)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 14, "CorrecaoSistema - Relatório de Execução", ln=True, fill=True, align="C")
        self.ln(4)
        self.set_text_color(*COLOR_TEXT)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generate_pdf_report(events: list[dict[str, Any]], title: str = "Diagnóstico Completo") -> Path:
    """Gera um PDF corporativo a partir da lista de eventos da sessão e retorna o
    caminho do arquivo salvo em Documents\\CorrecaoSistema\\Relatorios."""
    pdf = _CorporateReport(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M:%S}", ln=True)
    pdf.ln(6)

    col_widths = (32, 22, 136)
    headers = ("Horário", "Nível", "Mensagem")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*COLOR_HEADER_BLUE)
    pdf.set_text_color(*COLOR_WHITE)
    for width, text in zip(col_widths, headers):
        pdf.cell(width, 8, text, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*COLOR_TEXT)
    for index, event in enumerate(events):
        fill = index % 2 == 1
        pdf.set_fill_color(*COLOR_ROW_ALT) if fill else pdf.set_fill_color(*COLOR_WHITE)
        timestamp = str(event.get("timestamp", ""))[11:19]
        level = str(event.get("level", ""))
        message = str(event.get("message", ""))
        pdf.cell(col_widths[0], 7, timestamp, border=1, fill=True)
        pdf.cell(col_widths[1], 7, level, border=1, fill=True)
        pdf.cell(col_widths[2], 7, message[:95], border=1, fill=True)
        pdf.ln()

    output_path = REPORTS_DIR / f"relatorio_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf.output(str(output_path))
    return output_path
