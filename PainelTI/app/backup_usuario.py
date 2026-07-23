"""Backup compactado do perfil do usuário atual (Desktop/Downloads/Documents +
pastas extras configuráveis) para o servidor, ao desligar um colaborador.

O zip é montado localmente num temporário primeiro e só depois copiado para o
servidor — assim uma queda de rede no meio do processo não deixa um arquivo
corrompido/parcial no destino final.
"""
from __future__ import annotations

import getpass
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Callable

from app.constants import CONFIG_DIR
from app.modules.common import OperationResult

DESTINO_PADRAO = r"\\192.168.0.10\Backup Usuários\BKP - Ex Funcionários"
PASTAS_EXTRAS_CONFIG_PATH = CONFIG_DIR / "backup_pastas_extras.json"

ProgressCallback = Callable[[int, int, str], None]


def carregar_pastas_extras() -> list[str]:
    if not PASTAS_EXTRAS_CONFIG_PATH.exists():
        return []
    try:
        return json.loads(PASTAS_EXTRAS_CONFIG_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []


def salvar_pastas_extras(pastas: list[str]) -> None:
    PASTAS_EXTRAS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    PASTAS_EXTRAS_CONFIG_PATH.write_text(
        json.dumps(pastas, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def adicionar_pasta_extra(pastas: list[str], caminho: str) -> list[str]:
    if caminho in pastas:
        return pastas
    return [*pastas, caminho]


def remover_pasta_extra(pastas: list[str], caminho: str) -> list[str]:
    return [p for p in pastas if p != caminho]


def pastas_padrao_usuario() -> list[Path]:
    home = Path.home()
    candidatas = [home / "Desktop", home / "Downloads", home / "Documents"]
    return [p for p in candidatas if p.exists()]


def pastas_para_backup() -> list[Path]:
    pastas = pastas_padrao_usuario()
    for caminho_str in carregar_pastas_extras():
        caminho = Path(caminho_str)
        if caminho.exists():
            pastas.append(caminho)
    return pastas


def _contar_arquivos(pastas: list[Path]) -> int:
    total = 0
    for pasta in pastas:
        total += sum(1 for _ in pasta.rglob("*") if _.is_file())
    return total


def _nome_zip_disponivel(usuario: str) -> str:
    candidato = f"{usuario}.zip"
    if not (Path(DESTINO_PADRAO) / candidato).exists():
        return candidato
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{usuario}_{timestamp}.zip"


def gerar_backup(progress_callback: ProgressCallback | None = None) -> OperationResult:
    usuario = getpass.getuser()
    pastas = pastas_para_backup()

    if not pastas:
        return OperationResult(
            False,
            "Nenhuma pasta encontrada para backup (Desktop/Downloads/Documents "
            "ausentes e nenhuma pasta extra configurada).",
        )

    total = _contar_arquivos(pastas)
    processados = 0
    tmp_zip_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_zip_path = tmp_file.name

        with zipfile.ZipFile(tmp_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zip_arquivo:
            for pasta in pastas:
                prefixo = pasta.name
                for arquivo in pasta.rglob("*"):
                    if arquivo.is_file():
                        arcname = f"{prefixo}/{arquivo.relative_to(pasta)}"
                        try:
                            zip_arquivo.write(arquivo, arcname)
                        except OSError:
                            pass  # arquivo bloqueado/inacessível: pula, não interrompe o backup
                        processados += 1
                        if progress_callback:
                            progress_callback(processados, total, arquivo.name)

        try:
            Path(DESTINO_PADRAO).mkdir(parents=True, exist_ok=True)
        except OSError as error:
            return OperationResult(False, f"Não foi possível acessar o servidor de destino: {error}")

        nome_final = _nome_zip_disponivel(usuario)
        destino_final = Path(DESTINO_PADRAO) / nome_final
        shutil.copy2(tmp_zip_path, destino_final)

        return OperationResult(
            True,
            f"Backup de '{usuario}' salvo em '{destino_final}' ({processados} arquivo(s), {total} no total).",
        )
    except (OSError, PermissionError) as error:
        return OperationResult(False, f"Falha ao gerar/copiar o backup de '{usuario}': {error}")
    finally:
        if tmp_zip_path is not None:
            try:
                Path(tmp_zip_path).unlink(missing_ok=True)
            except OSError:
                pass
