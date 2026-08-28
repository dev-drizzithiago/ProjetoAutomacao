"""Ponto de entrada do PainelTI.

Garante privilégios de Administrador (UAC) antes de iniciar a interface gráfica.
"""
from __future__ import annotations

import sys

from app.admin import is_admin, relaunch_as_admin


def main() -> None:
    if not is_admin():
        accepted = relaunch_as_admin()
        if not accepted:
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                None,
                "A elevação de Administrador foi cancelada ou falhou.\n"
                "O PainelTI precisa ser executado como Administrador.",
                "PainelTI",
                0x10,  # MB_ICONERROR
            )
        sys.exit(0)

    if "--silent" in sys.argv[1:]:
        # Disparado pela tarefa agendada no Logon: cria o ponto de restauração
        # em segundo plano, sem abrir nenhuma janela.
        from app.manutencao_windows import executar_checkpoint_silencioso

        executar_checkpoint_silencioso()
        return

    if "--diagnostico-silencioso" in sys.argv[1:]:
        # Disparado pela tarefa agendada semanal: roda Dism/SFC e gera o PDF,
        # sem abrir nenhuma janela.
        from app.manutencao_windows import executar_diagnostico_silencioso

        executar_diagnostico_silencioso()
        return

    if "--watchdog-silencioso" in sys.argv[1:]:
        # Disparado pela tarefa agendada repetitiva: verifica os apps
        # monitorados e reabre os que não estiverem rodando, sem abrir janela.
        from app.watchdog_manager import executar_watchdog_silencioso

        executar_watchdog_silencioso()
        return

    try:
        from app.gui import run
    except ModuleNotFoundError as exc:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            None,
            f"Dependência ausente: {exc.name}\n\n"
            "Instale as dependências do PainelTI (ex.: pip install customtkinter) "
            "no ambiente Python usado para executar este script.",
            "PainelTI - Dependência ausente",
            0x10,  # MB_ICONERROR
        )
        sys.exit(1)

    run()


if __name__ == "__main__":
    main()
