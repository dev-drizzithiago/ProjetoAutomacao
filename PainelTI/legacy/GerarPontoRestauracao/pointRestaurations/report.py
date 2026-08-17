"""Geração de relatório PDF corporativo: pontos de restauração existentes + histórico de execução."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from pointRestaurations.logger import log_event, read_recent_logs
from pointRestaurations.restore_point import RestorePointInfo, list_restore_points

DOCUMENTS_DIR = Path(os.path.expanduser("~\\Documents"))
REPORTS_DIR = DOCUMENTS_DIR / "pointRestaurations" / "relatorios"

DARK_BLUE = (30, 58, 138)  # #1e3a8a
LIGHT_GRAY = (245, 246, 250)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)


class _ReportPDF(FPDF):
    def header(self) -> None:
        self.set_fill_color(*DARK_BLUE)
        self.rect(0, 0, self.w, 22, style="F")
        self.set_xy(10, 6)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "pointRestaurations - Relatorio de Pontos de Restauracao", ln=1)
        self.set_y(26)
        self.set_text_color(*BLACK)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")


def _section_title(pdf: FPDF, text: str) -> None:
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*DARK_BLUE)
    pdf.cell(0, 8, text, ln=1)
    pdf.set_text_color(*BLACK)
    pdf.ln(1)


def _table_header(pdf: FPDF, col_widths: tuple[float, ...], headers: tuple[str, ...]) -> None:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*DARK_BLUE)
    pdf.set_text_color(255, 255, 255)
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(*BLACK)


def _restore_points_table(pdf: FPDF, points: list[RestorePointInfo]) -> None:
    col_widths = (18, 42, 105, 25)
    _table_header(pdf, col_widths, ("No.", "Data/Hora", "Descricao", "Tipo"))

    pdf.set_font("Helvetica", "", 9)
    for i, p in enumerate(points):
        pdf.set_fill_color(*(LIGHT_GRAY if i % 2 == 0 else WHITE))
        dt_str = p.creation_time.strftime("%d/%m/%Y %H:%M:%S") if p.creation_time else "N/D"
        pdf.cell(col_widths[0], 7, str(p.sequence_number), border=1, fill=True, align="C")
        pdf.cell(col_widths[1], 7, dt_str, border=1, fill=True)
        pdf.cell(col_widths[2], 7, p.description[:58], border=1, fill=True)
        pdf.cell(col_widths[3], 7, p.type_label[:15], border=1, fill=True)
        pdf.ln()


def _log_table(pdf: FPDF, entries: list[dict]) -> None:
    col_widths = (36, 24, 130)
    _table_header(pdf, col_widths, ("Timestamp", "Nivel", "Mensagem"))

    pdf.set_font("Helvetica", "", 9)
    for i, e in enumerate(entries):
        pdf.set_fill_color(*(LIGHT_GRAY if i % 2 == 0 else WHITE))
        pdf.cell(col_widths[0], 7, str(e.get("timestamp", "")), border=1, fill=True)
        pdf.cell(col_widths[1], 7, str(e.get("level", "")), border=1, fill=True, align="C")
        pdf.cell(col_widths[2], 7, str(e.get("message", ""))[:82], border=1, fill=True)
        pdf.ln()


def generate_pdf_report() -> Path:
    """Gera o relatório PDF com os pontos de restauração existentes e o histórico de execução."""
    points = list_restore_points()
    entries = read_recent_logs(max_entries=100)

    pdf = _ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=1)
    pdf.cell(0, 6, f"Total de pontos de restauracao encontrados: {len(points)}", ln=1)
    if points and points[0].creation_time:
        pdf.cell(
            0, 6,
            f"Mais recente: {points[0].creation_time.strftime('%d/%m/%Y %H:%M:%S')}",
            ln=1,
        )

    _section_title(pdf, "Pontos de Restauracao Existentes")
    if points:
        _restore_points_table(pdf, points)
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 7, "Nenhum ponto de restauracao encontrado no sistema.", ln=1)

    _section_title(pdf, "Historico de Execucao (mais recentes)")
    if entries:
        _log_table(pdf, entries)
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 7, "Nenhum evento registrado hoje.", ln=1)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"relatorio_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.pdf"
    output_path = REPORTS_DIR / filename
    pdf.output(str(output_path))

    log_event("SUCCESS", "Relatório PDF gerado.", {"path": str(output_path)})
    return output_path
