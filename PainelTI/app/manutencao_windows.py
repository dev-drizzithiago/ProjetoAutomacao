"""Diagnóstico do Windows (DISM/SFC), Pontos de Restauração e agendamento no
logon — nativo do PainelTI, substituindo os antigos CorrecaoSistema e
GerarPontoRestauracao (que exigiam Python instalado à parte para rodar como
processo separado).

Os dois legados faziam praticamente a mesma coisa (criar ponto de restauração,
agendar tarefa de logon, gerar PDF) — este módulo consolida numa implementação
só, pegando o melhor de cada: mensagens de bloqueio de 24h mais claras do
GerarPontoRestauracao, o bypass de frequência do CorrecaoSistema, e o
diagnóstico DISM/SFC que só o CorrecaoSistema tinha.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from fpdf import FPDF

from app.constants import RELATORIOS_DIR

TASK_NAME = "PainelTI_LogonCheckpoint"

_FREQUENCY_REGISTRY_PATH = r"HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
_FREQUENCY_VALUE_NAME = "SystemRestorePointCreationFrequency"

_WMI_DATETIME_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})")

_TYPE_LABELS = {
    "0": "Instalação de Aplicativo",
    "1": "Desinstalação de Aplicativo",
    "10": "Instalação de Driver",
    "12": "Alteração de Configurações",
    "13": "Operação Cancelada",
    "14": "Backup do Windows",
}

DARK_BLUE = (30, 58, 138)  # #1e3a8a
ROW_ALT = (235, 240, 249)
WHITE = (255, 255, 255)
TEXT = (20, 20, 20)

OutputCallback = Callable[[str, bool], None]
ProgressCallback = Callable[[int, int, str], None]


@dataclass(frozen=True)
class OperationResult:
    success: bool
    message: str
    throttled: bool = False


# --------------------------------------------------------------- diagnóstico
@dataclass(frozen=True)
class RepairStep:
    name: str
    command: str


STEPS: tuple[RepairStep, ...] = (
    RepairStep("Limpeza de Pontos de Montagem", "Dism /Cleanup-Mountpoints"),
    RepairStep("Verificação da Imagem (ScanHealth)", "Dism /Online /Cleanup-Image /ScanHealth"),
    RepairStep("Restauração da Imagem (RestoreHealth)", "Dism /Online /Cleanup-Image /RestoreHealth"),
    RepairStep("Verificação de Arquivos de Sistema (SFC)", "sfc /scannow"),
)


@dataclass(frozen=True)
class StepResult:
    step: RepairStep
    success: bool
    return_code: int
    output: str


def _run_powershell_streaming(command: str, on_output: OutputCallback) -> tuple[int, str]:
    process = subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    encoding = "cp850"
    collected_lines: list[str] = []
    assert process.stdout is not None

    buffer = bytearray()
    while True:
        chunk = process.stdout.read(1)
        if not chunk:
            break
        if chunk in (b"\r", b"\n"):
            if buffer:
                text = buffer.decode(encoding, errors="replace")
                collected_lines.append(text)
                on_output(text, chunk == b"\r")
                buffer.clear()
            continue
        buffer += chunk

    if buffer:
        text = buffer.decode(encoding, errors="replace")
        collected_lines.append(text)
        on_output(text, False)

    process.wait()
    return process.returncode, "\n".join(collected_lines)


def run_full_diagnostics(on_output: OutputCallback, on_progress: ProgressCallback) -> list[StepResult]:
    """Executa DISM (Cleanup-Mountpoints, ScanHealth, RestoreHealth) e SFC /SCANNOW
    em sequência estrita (não podem rodar concorrentemente)."""
    results: list[StepResult] = []
    total = len(STEPS)
    for index, step in enumerate(STEPS, start=1):
        on_progress(index, total, step.name)
        on_output(f"--- Iniciando: {step.name} ---", False)
        return_code, output = _run_powershell_streaming(step.command, on_output)
        success = return_code == 0
        on_output(f"--- Concluído: {step.name} (código {return_code}) ---", False)
        results.append(StepResult(step=step, success=success, return_code=return_code, output=output))
    return results


# ---------------------------------------------------------- ponto de restauração
def _run_powershell(command: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def create_restore_point(description: str | None = None) -> OperationResult:
    """Cria um ponto de restauração via PowerShell. Requer Administrador. O
    Windows limita, por padrão, a 1 ponto a cada 24h quando criado por script."""
    description = description or f"PainelTI - {datetime.now():%d/%m/%Y %H:%M}"
    command = f"Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'"

    try:
        result = _run_powershell(command)
    except subprocess.TimeoutExpired:
        return OperationResult(False, "Tempo limite excedido ao criar o ponto de restauração.")
    except OSError as error:
        return OperationResult(False, f"Falha ao invocar o PowerShell: {error}")

    if result.returncode == 0:
        return OperationResult(True, "Ponto de restauração criado com sucesso.")

    stderr = result.stderr.strip()
    if "24" in stderr or "frequently" in stderr.lower() or "throttl" in stderr.lower() or "since the last successful checkpoint" in stderr.lower():
        return OperationResult(
            False,
            "Já existe um ponto de restauração criado nas últimas 24 horas "
            "(restrição padrão do Windows). Use 'Permitir múltiplos por dia' se necessário.",
            throttled=True,
        )
    if "acesso negado" in stderr.lower() or "access is denied" in stderr.lower() or "administrator" in stderr.lower():
        return OperationResult(False, "Permissão negada. Execute o PainelTI como Administrador.")

    return OperationResult(False, f"Falha ao criar o ponto de restauração: {stderr or 'erro desconhecido'}")


def allow_frequent_restore_points() -> OperationResult:
    """Reduz a frequência mínima entre pontos de restauração para 0 (permite
    múltiplos pontos por dia). Reversível via restore_default_restore_point_frequency()."""
    command = (
        f'New-ItemProperty -Path "{_FREQUENCY_REGISTRY_PATH}" '
        f'-Name "{_FREQUENCY_VALUE_NAME}" -Value 0 -PropertyType DWord -Force'
    )
    try:
        result = _run_powershell(command, timeout=30)
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao ajustar o registro: {error}")

    if result.returncode == 0:
        return OperationResult(True, "Restrição de 24h removida para esta sessão.")
    return OperationResult(False, (result.stderr or "Falha ao ajustar o registro.").strip())


def restore_default_restore_point_frequency() -> OperationResult:
    """Restaura o comportamento padrão do Windows (remove o valor customizado)."""
    command = (
        f'Remove-ItemProperty -Path "{_FREQUENCY_REGISTRY_PATH}" '
        f'-Name "{_FREQUENCY_VALUE_NAME}" -ErrorAction SilentlyContinue'
    )
    try:
        result = _run_powershell(command, timeout=30)
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao restaurar o registro: {error}")
    return OperationResult(result.returncode == 0, "Comportamento padrão restaurado.")


@dataclass(frozen=True)
class RestorePointInfo:
    sequence_number: int
    description: str
    creation_time: datetime | None
    restore_point_type: str

    @property
    def type_label(self) -> str:
        return _TYPE_LABELS.get(str(self.restore_point_type), f"Tipo {self.restore_point_type}")


def _parse_wmi_datetime(value: str) -> datetime | None:
    if not value:
        return None
    match = _WMI_DATETIME_RE.match(value)
    if not match:
        return None
    year, month, day, hour, minute, second = (int(g) for g in match.groups())
    try:
        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


def list_restore_points() -> list[RestorePointInfo]:
    """Consulta os pontos de restauração já existentes, mais recentes primeiro."""
    import json

    command = (
        "Get-ComputerRestorePoint | "
        "Select-Object SequenceNumber, Description, CreationTime, RestorePointType | "
        "ConvertTo-Json -Compress"
    )
    try:
        result = _run_powershell(command, timeout=30)
    except (subprocess.TimeoutExpired, OSError):
        return []

    if result.returncode != 0 or not result.stdout.strip():
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict):
        data = [data]

    points = [
        RestorePointInfo(
            sequence_number=item.get("SequenceNumber", 0),
            description=item.get("Description") or "(sem descrição)",
            creation_time=_parse_wmi_datetime(item.get("CreationTime", "")),
            restore_point_type=str(item.get("RestorePointType", "")),
        )
        for item in data
    ]
    points.sort(key=lambda p: p.creation_time or datetime.min, reverse=True)
    return points


# --------------------------------------------------------------- agendamento
TASK_NAME_DAILY = "PainelTI_DailyCheckpoint"
TASK_NAME_WEEKLY_DIAGNOSTIC = "PainelTI_DiagnosticoSemanal"

# Rótulo PT-BR exibido na UI -> código de dia esperado por `schtasks /D`.
DIAS_SEMANA: dict[str, str] = {
    "Segunda": "MON",
    "Terça": "TUE",
    "Quarta": "WED",
    "Quinta": "THU",
    "Sexta": "FRI",
    "Sábado": "SAT",
    "Domingo": "SUN",
}


def _target_command(flag: str) -> tuple[str, str]:
    """Retorna (comando, argumentos) apontando pro .exe compilado ou pro
    python + main.py, igual ao padrão já usado em CorrecaoSistema/GerarPontoRestauracao."""
    if getattr(sys, "frozen", False):
        return sys.executable, flag
    main_script = Path(__file__).resolve().parent.parent / "main.py"
    return sys.executable, f'"{main_script}" {flag}'


def _criar_schtask(nome_tarefa: str, flag: str, argumentos_agendamento: list[str]) -> OperationResult:
    """Monta e registra uma tarefa agendada apontando pro PainelTI com `flag`
    (`--silent`/`--diagnostico-silencioso`). `argumentos_agendamento` é a parte
    específica do gatilho (`/SC ONLOGON`, `/SC DAILY /ST 08:00`, etc.)."""
    command, args = _target_command(flag)
    task_run = f'"{command}" {args}'.strip()

    try:
        result = subprocess.run(
            ["schtasks", "/Create", "/TN", nome_tarefa, "/TR", task_run, *argumentos_agendamento, "/RL", "HIGHEST", "/F"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao criar tarefa agendada: {error}")

    if result.returncode == 0:
        return OperationResult(True, f"Tarefa '{nome_tarefa}' agendada com sucesso.")
    return OperationResult(False, (result.stderr or result.stdout).strip())


def _remover_schtask(nome_tarefa: str) -> OperationResult:
    try:
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", nome_tarefa, "/F"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao remover tarefa agendada: {error}")

    if result.returncode == 0:
        return OperationResult(True, f"Tarefa '{nome_tarefa}' removida.")
    return OperationResult(False, (result.stderr or result.stdout).strip())


def _schtask_existe(nome_tarefa: str) -> bool:
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", nome_tarefa],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0


# Ponto de restauração — gatilho por logon (dispara toda vez que alguém loga;
# na prática cria só 1x/dia por causa do limite do próprio Windows).
def create_logon_task() -> OperationResult:
    return _criar_schtask(TASK_NAME, "--silent", ["/SC", "ONLOGON"])


def remove_logon_task() -> OperationResult:
    return _remover_schtask(TASK_NAME)


def task_exists() -> bool:
    return _schtask_existe(TASK_NAME)


# Ponto de restauração — gatilho diário fixo (garante 1x/dia mesmo que a
# máquina fique ligada dias sem novo logon; convive com o gatilho de logon acima).
def create_daily_checkpoint_task(hora: str = "08:00") -> OperationResult:
    return _criar_schtask(TASK_NAME_DAILY, "--silent", ["/SC", "DAILY", "/ST", hora])


def remove_daily_checkpoint_task() -> OperationResult:
    return _remover_schtask(TASK_NAME_DAILY)


def daily_checkpoint_task_exists() -> bool:
    return _schtask_existe(TASK_NAME_DAILY)


# Diagnóstico Dism/SFC — gatilho semanal (dia da semana + horário configuráveis).
def create_weekly_diagnostic_task(dia_semana: str, hora: str) -> OperationResult:
    codigo_dia = DIAS_SEMANA.get(dia_semana)
    if codigo_dia is None:
        return OperationResult(False, f"Dia da semana inválido: '{dia_semana}'.")
    return _criar_schtask(
        TASK_NAME_WEEKLY_DIAGNOSTIC, "--diagnostico-silencioso",
        ["/SC", "WEEKLY", "/D", codigo_dia, "/ST", hora],
    )


def remove_weekly_diagnostic_task() -> OperationResult:
    return _remover_schtask(TASK_NAME_WEEKLY_DIAGNOSTIC)


def weekly_diagnostic_task_exists() -> bool:
    return _schtask_existe(TASK_NAME_WEEKLY_DIAGNOSTIC)


# --------------------------------------------------------------- relatório PDF
class _CorporateReport(FPDF):
    def header(self) -> None:
        self.set_fill_color(*DARK_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 14, "PainelTI - Diagnóstico & Restauração", ln=True, fill=True, align="C")
        self.ln(4)
        self.set_text_color(*TEXT)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def gerar_relatorio_pdf(events: list[dict[str, Any]]) -> Path:
    """Gera um PDF com os pontos de restauração existentes + histórico de
    eventos da sessão (EventLogger), salvo em RELATORIOS_DIR."""
    points = list_restore_points()

    pdf = _CorporateReport(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Gerado em: {datetime.now():%d/%m/%Y %H:%M:%S}", ln=True)
    pdf.cell(0, 6, f"Pontos de restauração encontrados: {len(points)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Pontos de Restauração Existentes", ln=True)

    if points:
        col_widths = (18, 42, 105, 25)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(*DARK_BLUE)
        pdf.set_text_color(*WHITE)
        for width, text in zip(col_widths, ("No.", "Data/Hora", "Descrição", "Tipo")):
            pdf.cell(width, 8, text, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*TEXT)
        for index, point in enumerate(points):
            pdf.set_fill_color(*ROW_ALT) if index % 2 == 0 else pdf.set_fill_color(*WHITE)
            data_str = point.creation_time.strftime("%d/%m/%Y %H:%M:%S") if point.creation_time else "N/D"
            pdf.cell(col_widths[0], 7, str(point.sequence_number), border=1, fill=True, align="C")
            pdf.cell(col_widths[1], 7, data_str, border=1, fill=True)
            pdf.cell(col_widths[2], 7, point.description[:58], border=1, fill=True)
            pdf.cell(col_widths[3], 7, point.type_label[:15], border=1, fill=True)
            pdf.ln()
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 7, "Nenhum ponto de restauração encontrado.", ln=True)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Histórico de Eventos (sessão atual)", ln=True)

    if events:
        col_widths = (32, 22, 136)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(*DARK_BLUE)
        pdf.set_text_color(*WHITE)
        for width, text in zip(col_widths, ("Horário", "Nível", "Mensagem")):
            pdf.cell(width, 8, text, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*TEXT)
        for index, event in enumerate(events):
            pdf.set_fill_color(*ROW_ALT) if index % 2 == 1 else pdf.set_fill_color(*WHITE)
            timestamp = str(event.get("timestamp", ""))[11:19]
            level = str(event.get("level", ""))
            message = str(event.get("message", ""))
            pdf.cell(col_widths[0], 7, timestamp, border=1, fill=True)
            pdf.cell(col_widths[1], 7, level, border=1, fill=True)
            pdf.cell(col_widths[2], 7, message[:95], border=1, fill=True)
            pdf.ln()
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 7, "Nenhum evento registrado nesta sessão.", ln=True)

    output_path = RELATORIOS_DIR / f"diagnostico_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf.output(str(output_path))
    return output_path


# --------------------------------------------------------------- modo --silent
def executar_checkpoint_silencioso() -> None:
    """Chamado pela tarefa agendada no logon (--silent): cria o ponto de
    restauração sem abrir nenhuma janela. Sem diagnóstico DISM/SFC completo
    aqui — seria pesado demais pra rodar em todo logon; fica como ação manual."""
    from app.logger import EventLogger

    logger = EventLogger()
    logger.info("Checkpoint automático (logon) iniciado em modo silencioso.")
    resultado = create_restore_point(description=f"PainelTI - Logon {datetime.now():%d/%m/%Y %H:%M}")
    if resultado.success:
        logger.success(resultado.message)
    elif resultado.throttled:
        logger.info(resultado.message)
    else:
        logger.error(resultado.message)


def executar_diagnostico_silencioso() -> None:
    """Chamado pela tarefa agendada semanal (--diagnostico-silencioso): roda o
    Dism/SFC completo e gera o relatório PDF, sem abrir nenhuma janela — é o
    equivalente ao antigo CorrecaoSistema/app/headless.py."""
    from app.logger import EventLogger

    logger = EventLogger()
    logger.info("Diagnóstico automático (semanal) iniciado em modo silencioso.")

    def on_output(_text: str, _overwrite: bool = False) -> None:
        pass  # sem console em modo silencioso

    def on_progress(current: int, total: int, name: str) -> None:
        logger.info(f"Etapa {current}/{total}: {name}")

    try:
        resultados = run_full_diagnostics(on_output, on_progress)
        for resultado in resultados:
            if resultado.success:
                logger.success(f"{resultado.step.name} concluído com sucesso.")
            else:
                logger.error(f"{resultado.step.name} falhou (código {resultado.return_code}).")
    except Exception as error:  # noqa: BLE001 - garantir que o relatório seja gerado mesmo em falha
        logger.error(f"Falha inesperada no diagnóstico silencioso: {error}")

    try:
        gerar_relatorio_pdf(logger.events)
    except Exception as error:  # noqa: BLE001
        logger.error(f"Falha ao gerar relatório PDF: {error}")
