"""Cadastro de redes Wi-Fi corporativas e aplicação via netsh.

Substitui o antigo utilitarios_segeti/adicionar_redes_wifi.py, que dependia de
uma lista `redes_disponiveis` com senhas hardcoded (removida do arquivo em
algum momento). Aqui a lista de redes fica num JSON editável pela própria UI,
para que a equipe de TI atualize senhas sem tocar em código.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass

from app.constants import CONFIG_DIR

WIFI_CONFIG_PATH = CONFIG_DIR / "wifi_profiles.json"

_PERFIL_XML = """<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{nome}</name>
    <SSIDConfig>
        <SSID>
            <name>{nome}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{senha}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
"""


@dataclass(frozen=True)
class OperationResult:
    success: bool
    message: str


@dataclass
class WifiProfile:
    nome: str
    senha: str


def carregar_perfis() -> list[WifiProfile]:
    if not WIFI_CONFIG_PATH.exists():
        return []
    try:
        dados = json.loads(WIFI_CONFIG_PATH.read_text(encoding="utf-8"))
        return [WifiProfile(**item) for item in dados]
    except (json.JSONDecodeError, OSError, TypeError):
        return []


def salvar_perfis(perfis: list[WifiProfile]) -> None:
    WIFI_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    WIFI_CONFIG_PATH.write_text(
        json.dumps([asdict(p) for p in perfis], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def adicionar_ou_atualizar_perfil(perfis: list[WifiProfile], nome: str, senha: str) -> list[WifiProfile]:
    atualizados = [p for p in perfis if p.nome != nome]
    atualizados.append(WifiProfile(nome=nome, senha=senha))
    return atualizados


def remover_perfil(perfis: list[WifiProfile], nome: str) -> list[WifiProfile]:
    return [p for p in perfis if p.nome != nome]


def aplicar_perfil(perfil: WifiProfile) -> OperationResult:
    xml_content = _PERFIL_XML.format(nome=perfil.nome, senha=perfil.senha)

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xml", encoding="utf-8", delete=False
        ) as tmp_file:
            tmp_file.write(xml_content)
            tmp_path = tmp_file.name

        resultado = subprocess.run(
            ["netsh", "wlan", "add", "profile", f"filename={tmp_path}"],
            capture_output=True,
            text=True,
        )

        if resultado.returncode != 0:
            return OperationResult(
                False, f"Falha ao aplicar o perfil '{perfil.nome}': {resultado.stdout.strip() or resultado.stderr.strip()}"
            )
        return OperationResult(True, f"Rede '{perfil.nome}' aplicada com sucesso.")
    except OSError as error:
        return OperationResult(False, f"Falha ao executar netsh: {error}")
    finally:
        if tmp_path is not None:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
