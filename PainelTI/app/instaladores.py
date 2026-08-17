"""Instalação silenciosa dos instaladores encontrados em PainelTI/instaladores/.

A pasta fica ao lado do próprio app (mesmo princípio de config/wifi_profiles.json):
tudo que precisa viajar junto com o PainelTI na distribuição para o usuário final
fica dentro da própria pasta do app, não em %LOCALAPPDATA%.

Instaladores não têm um flag silencioso universal (.exe varia por fabricante;
.msi tem um padrão único via msiexec). Por isso o mapeamento arquivo -> argumento
fica em config.json, editável pela equipe de TI sem mexer em código.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Callable

from app.constants import APP_DIR
from app.modules.common import OperationResult

INSTALADORES_DIR = APP_DIR / "instaladores"
CONFIG_PATH = INSTALADORES_DIR / "config.json"

INSTALADORES_DIR.mkdir(parents=True, exist_ok=True)

EXTENSOES_SUPORTADAS = (".exe", ".msi")

ProgressCallback = Callable[[int, int, str], None]


def listar_instaladores() -> list[Path]:
    if not INSTALADORES_DIR.exists():
        return []
    return sorted(
        (p for p in INSTALADORES_DIR.iterdir() if p.is_file() and p.suffix.lower() in EXTENSOES_SUPORTADAS),
        key=lambda p: p.name.lower(),
    )


def carregar_config_silenciosa() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        import json

        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def resolver_argumentos(caminho: Path, config: dict[str, str]) -> list[str] | None:
    """Monta o comando completo para instalar `caminho` silenciosamente.

    Devolve None quando é um .exe sem entrada em config.json — não dá pra
    adivinhar o flag silencioso correto sem essa informação.
    """
    args_configurados = config.get(caminho.name)

    if caminho.suffix.lower() == ".msi":
        args = shlex.split(args_configurados) if args_configurados else ["/quiet", "/norestart"]
        return ["msiexec", "/i", str(caminho), *args]

    if args_configurados is None:
        return None
    return [str(caminho), *shlex.split(args_configurados)]


def instalar_um(caminho: Path, config: dict[str, str]) -> OperationResult:
    comando = resolver_argumentos(caminho, config)
    if comando is None:
        return OperationResult(
            False,
            f"'{caminho.name}' não tem argumento silencioso configurado em "
            f"{CONFIG_PATH.name}. Adicione uma entrada e tente novamente.",
        )

    try:
        resultado = subprocess.run(comando, capture_output=True, text=True)
        if resultado.returncode != 0:
            return OperationResult(
                False,
                f"'{caminho.name}' terminou com código {resultado.returncode}: "
                f"{resultado.stderr.strip() or resultado.stdout.strip()}",
            )
        return OperationResult(True, f"'{caminho.name}' instalado com sucesso.")
    except OSError as error:
        return OperationResult(False, f"Falha ao executar '{caminho.name}': {error}")


def instalar_todos(progress_callback: ProgressCallback | None = None) -> list[OperationResult]:
    """Instala cada instalador encontrado, um de cada vez. Diferente de um
    diagnóstico sequencial, aqui cada instalador é independente: uma falha não
    interrompe os demais, só entra no resumo final."""
    instaladores = listar_instaladores()
    config = carregar_config_silenciosa()
    total = len(instaladores)
    resultados: list[OperationResult] = []

    for indice, caminho in enumerate(instaladores, start=1):
        if progress_callback:
            progress_callback(indice - 1, total, caminho.name)
        resultados.append(instalar_um(caminho, config))
        if progress_callback:
            progress_callback(indice, total, caminho.name)

    return resultados


def instalar_um_visivel(caminho: Path) -> OperationResult:
    """Abre o instalador com a janela normal dele (sem flag silencioso, ignora
    config.json de propósito) e espera terminar antes de devolver — o usuário
    acompanha/clica em cada um, o painel só cuida de abrir o próximo depois."""
    comando = ["msiexec", "/i", str(caminho)] if caminho.suffix.lower() == ".msi" else [str(caminho)]
    try:
        resultado = subprocess.run(comando)
        if resultado.returncode != 0:
            return OperationResult(
                False, f"'{caminho.name}' terminou com código {resultado.returncode}."
            )
        return OperationResult(True, f"'{caminho.name}' concluído.")
    except OSError as error:
        return OperationResult(False, f"Falha ao executar '{caminho.name}': {error}")


def instalar_todos_visivel(progress_callback: ProgressCallback | None = None) -> list[OperationResult]:
    """Mesmo laço sequencial de instalar_todos(), mas abrindo cada instalador
    visível (sem silencioso) e só avançando pro próximo quando o anterior fechar."""
    instaladores = listar_instaladores()
    total = len(instaladores)
    resultados: list[OperationResult] = []

    for indice, caminho in enumerate(instaladores, start=1):
        if progress_callback:
            progress_callback(indice - 1, total, caminho.name)
        resultados.append(instalar_um_visivel(caminho))
        if progress_callback:
            progress_callback(indice, total, caminho.name)

    return resultados
