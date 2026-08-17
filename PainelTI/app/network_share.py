"""Pasta de digitalização, compartilhamento SMB e permissões do usuário 'ti'.

Cria a pasta C:\\Digitalização, compartilha na rede para uso da impressora e
garante Acesso Total (Full Control) para o usuário local 'ti', tanto no nível
de compartilhamento (SMB) quanto no nível do sistema de arquivos (NTFS) — os
dois são independentes: liberar o compartilhamento sem liberar a ACL NTFS
ainda bloquearia o acesso.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

CAMINHO_PADRAO = r"C:\Digitalização"
NOME_COMPARTILHAMENTO_PADRAO = "Digitalização"

# Precisa ser a conta LOCAL da máquina, não uma conta de domínio "ti" (se
# existir uma). O atalho ".\ti" deveria bastar, mas na prática não resolveu de
# forma confiável em testes (icacls e o .NET NTAccount.Translate() falharam
# com "Não foi possível converter algumas ou todas as referências de
# identidade" mesmo com o usuário local existindo) — então usamos o nome do
# computador explícito, que resolveu certo nos mesmos testes.
USUARIO_PADRAO = rf"{os.environ.get('COMPUTERNAME', '.')}\ti"


@dataclass(frozen=True)
class OperationResult:
    success: bool
    message: str


def _run_powershell(comando: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["powershell", "-NoProfile", "-Command", comando],
        capture_output=True,
        text=True,
    )


def criar_pasta_digitalizacao(caminho: str = CAMINHO_PADRAO) -> OperationResult:
    try:
        Path(caminho).mkdir(parents=True, exist_ok=True)
        return OperationResult(True, f"Pasta '{caminho}' pronta.")
    except (PermissionError, OSError) as error:
        return OperationResult(False, f"Falha ao criar a pasta '{caminho}': {error}")


def compartilhar_pasta(
    caminho: str = CAMINHO_PADRAO,
    nome_compartilhamento: str = NOME_COMPARTILHAMENTO_PADRAO,
    usuario: str = USUARIO_PADRAO,
) -> OperationResult:
    comando_shell = rf"""
        $share = Get-SmbShare -Name "{nome_compartilhamento}" -ErrorAction SilentlyContinue
        if (-not $share) {{
            New-SmbShare -Name "{nome_compartilhamento}" -Path "{caminho}" -FullAccess "{usuario}" -ErrorAction Stop | Out-Null
            Write-Output "Compartilhamento '{nome_compartilhamento}' criado."
        }} else {{
            Grant-SmbShareAccess -Name "{nome_compartilhamento}" -AccountName "{usuario}" -AccessRight Full -Force -ErrorAction Stop | Out-Null
            Write-Output "Compartilhamento '{nome_compartilhamento}' já existia; permissão de '{usuario}' garantida."
        }}
    """

    try:
        resultado = _run_powershell(comando_shell)
        if resultado.returncode != 0:
            return OperationResult(False, f"Falha ao compartilhar a pasta: {resultado.stderr.strip()}")
        return OperationResult(True, resultado.stdout.strip() or "Compartilhamento configurado.")
    except OSError as error:
        return OperationResult(False, f"Falha ao executar o PowerShell: {error}")


def conceder_permissao_ntfs(caminho: str = CAMINHO_PADRAO, usuario: str = USUARIO_PADRAO) -> OperationResult:
    try:
        resultado = subprocess.run(
            ["icacls", caminho, "/grant", f"{usuario}:(OI)(CI)F"],
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            return OperationResult(False, f"Falha ao ajustar permissão NTFS: {resultado.stderr.strip() or resultado.stdout.strip()}")
        return OperationResult(True, f"Permissão NTFS Full Control concedida a '{usuario}' em '{caminho}'.")
    except OSError as error:
        return OperationResult(False, f"Falha ao executar icacls: {error}")


def configurar_pasta_compartilhada(
    caminho: str = CAMINHO_PADRAO,
    nome_compartilhamento: str = NOME_COMPARTILHAMENTO_PADRAO,
    usuario: str = USUARIO_PADRAO,
) -> list[OperationResult]:
    """Executa em sequência: criar pasta -> compartilhar -> permissão NTFS.

    Para a execução (sem seguir para a próxima etapa) assim que uma falhar,
    já que cada passo depende do sucesso do anterior.
    """
    resultados: list[OperationResult] = []

    passo_pasta = criar_pasta_digitalizacao(caminho)
    resultados.append(passo_pasta)
    if not passo_pasta.success:
        return resultados

    passo_share = compartilhar_pasta(caminho, nome_compartilhamento, usuario)
    resultados.append(passo_share)
    if not passo_share.success:
        return resultados

    passo_ntfs = conceder_permissao_ntfs(caminho, usuario)
    resultados.append(passo_ntfs)
    return resultados
