"""Entrada da máquina no domínio Active Directory via PowerShell `Add-Computer`.

Credenciais ficam em config/dominio.json, editável pela própria UI — mesmo
princípio de texto simples local já usado em config/wifi_profiles.json (fica
ao lado do app, não em rede, e a equipe de TI atualiza sem mexer em código).
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass

from app.constants import CONFIG_DIR
from app.modules.common import OperationResult

DOMINIO_CONFIG_PATH = CONFIG_DIR / "dominio.json"


@dataclass
class ConfigDominio:
    dominio: str = ""
    usuario: str = ""
    senha: str = ""


def carregar_config() -> ConfigDominio:
    if not DOMINIO_CONFIG_PATH.exists():
        return ConfigDominio()
    try:
        dados = json.loads(DOMINIO_CONFIG_PATH.read_text(encoding="utf-8"))
        return ConfigDominio(
            dominio=dados.get("dominio", ""),
            usuario=dados.get("usuario", ""),
            senha=dados.get("senha", ""),
        )
    except (ValueError, OSError):
        return ConfigDominio()


def salvar_config(config: ConfigDominio) -> None:
    DOMINIO_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOMINIO_CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def entrar_no_dominio(config: ConfigDominio) -> OperationResult:
    """Adiciona esta máquina ao domínio configurado. Requer Administrador e
    reinicialização do Windows para concluir — não reinicia sozinho, quem
    chama decide se oferece isso ao usuário."""
    if not config.dominio or not config.usuario or not config.senha:
        return OperationResult(False, "Preencha domínio, usuário e senha antes de entrar no domínio.")

    comando = rf"""
        $senha = ConvertTo-SecureString '{config.senha}' -AsPlainText -Force
        $credencial = New-Object System.Management.Automation.PSCredential('{config.usuario}', $senha)
        Add-Computer -DomainName '{config.dominio}' -Credential $credencial -Force -ErrorAction Stop
    """

    try:
        resultado = subprocess.run(
            ["powershell", "-NoProfile", "-Command", comando],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        return OperationResult(False, f"Falha ao executar o PowerShell: {error}")

    if resultado.returncode != 0:
        mensagem = (resultado.stderr or resultado.stdout).strip() or "Falha ao entrar no domínio."
        return OperationResult(False, mensagem)

    return OperationResult(
        True, f"Máquina adicionada ao domínio '{config.dominio}' com sucesso. Reinicie o Windows para concluir."
    )


def reiniciar_windows() -> OperationResult:
    try:
        subprocess.run(["shutdown", "/r", "/t", "15"], check=True)
        return OperationResult(True, "Windows vai reiniciar em 15 segundos.")
    except (subprocess.CalledProcessError, OSError) as error:
        return OperationResult(False, f"Falha ao agendar reinicialização: {error}")
