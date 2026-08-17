"""Carrega os `main.py` dos módulos legados (em PainelTI/legacy/) como módulos
Python isolados.

Vários módulos legados têm um arquivo chamado `main.py` (anydesk, alterando_permissao,
desbloquer_view_explorer, softwares_instalados, utilitarios_segeti,
mikrotik_monitoramento). Se todos fossem importados como `import main`, o Python
reaproveitaria o mesmo `sys.modules["main"]` para o segundo em diante — por isso
cada um é carregado sob um alias próprio via `importlib`.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _detectar_legacy_dir() -> Path:
    """Localiza `PainelTI/legacy/` (pasta que contém anydesk/, etc.).

    Rodando via `python main.py`, isso é `parents[2]` a partir deste arquivo
    (`app/modules/legacy_loader.py` -> `app/modules` -> `app` -> `PainelTI/`)
    mais `/legacy`. Compilado com PyInstaller, `__file__` aponta para dentro do
    bundle extraído, não para o checkout do repositório — por isso, quando
    frozen, usa `sys._MEIPASS` (onde `--add-data "legacy;legacy"` deposita a
    pasta), mesmo padrão já usado em `app/constants.py::_bundle_dir()` para o
    ícone: é conteúdo empacotado só-leitura, não precisa ficar visível ao lado
    do `.exe` como `config/`/`instaladores/`.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        return base / "legacy"

    return Path(__file__).resolve().parents[2] / "legacy"


LEGACY_DIR = _detectar_legacy_dir()


def import_legacy_main(pasta: str, arquivo: str, alias: str) -> ModuleType:
    """Importa `<LEGACY_DIR>/<pasta>/<arquivo>` como um módulo isolado `alias`.

    Insere `<LEGACY_DIR>/<pasta>` no início do sys.path antes de carregar, para
    que os imports internos do próprio módulo legado (ex.: `from proccess_spinner
    import ProcessoRun`) continuem resolvendo normalmente.
    """
    if alias in sys.modules:
        return sys.modules[alias]

    pasta_modulo = LEGACY_DIR / pasta
    if str(pasta_modulo) not in sys.path:
        sys.path.insert(0, str(pasta_modulo))

    caminho_arquivo = pasta_modulo / arquivo
    spec = importlib.util.spec_from_file_location(alias, caminho_arquivo)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível localizar {caminho_arquivo}")

    modulo = importlib.util.module_from_spec(spec)
    sys.modules[alias] = modulo
    spec.loader.exec_module(modulo)
    return modulo
