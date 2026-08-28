"""Janela principal do PainelTI (customtkinter)."""
from __future__ import annotations

import getpass
import threading
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app import backup_usuario, dominio, instaladores, manutencao_windows, network_share, watchdog_manager, wifi_manager
from app.constants import ICON_PATH, RELATORIOS_DIR
from app.logger import EventLogger
from app.modules import (
    anydesk_module,
    exchange_module,
    explorer_module,
    inventario_module,
    mikrotik_module,
    rede_segeti_module,
)
from app.tooltip import CTkToolTip

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PainelTI")
        self.geometry("980x720")
        self.minsize(880, 640)
        if ICON_PATH.exists():
            self.iconbitmap(str(ICON_PATH))

        self.logger = EventLogger()
        self._busy = False
        self._botoes_para_bloquear: list[ctk.CTkButton] = []
        self._perfis: list[wifi_manager.WifiProfile] = wifi_manager.carregar_perfis()
        self._interfaces_detectadas: list[dict] = []
        self._instaladores_encontrados: list = []
        self._pastas_extras_backup: list[str] = backup_usuario.carregar_pastas_extras()
        self._apps_watchdog: list[watchdog_manager.WatchdogApp] = watchdog_manager.carregar_apps()
        self._intervalo_watchdog: int = watchdog_manager.carregar_intervalo_minutos()
        self._processos_disponiveis_watchdog: list[tuple[str, str]] = []

        self._build_layout()
        self.logger.info("Aplicação iniciada.")
        self._log_to_console("Bem-vindo ao PainelTI.")
        self._garantir_agendamento_logon()

    # ---------------------------------------------------------------- layout
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_bar()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 4))

        aba_rede = self.tabview.add("Rede")
        aba_dominio = self.tabview.add("Domínio")
        aba_manutencao = self.tabview.add("Manutenção")
        aba_diagnostico = self.tabview.add("Diagnóstico & Restauração")
        aba_instalacao = self.tabview.add("Instalação de Apps")
        aba_backup = self.tabview.add("Backup de Usuário")
        aba_inventario = self.tabview.add("Inventário")
        aba_rede_segeti = self.tabview.add("Rede SEGETI")
        aba_exchange = self.tabview.add("Exchange Online")
        aba_mikrotik = self.tabview.add("Mikrotik")
        aba_watchdog = self.tabview.add("Watchdog")

        self._build_rede_tab(aba_rede)
        self._build_dominio_tab(aba_dominio)
        self._build_manutencao_tab(aba_manutencao)
        self._build_diagnostico_tab(aba_diagnostico)
        self._build_instalacao_tab(aba_instalacao)
        self._build_backup_tab(aba_backup)
        self._build_inventario_tab(aba_inventario)
        self._build_rede_segeti_tab(aba_rede_segeti)
        self._build_exchange_tab(aba_exchange)
        self._build_mikrotik_tab(aba_mikrotik)
        self._build_watchdog_tab(aba_watchdog)

        self._build_console()

    def _build_top_bar(self) -> None:
        top = ctk.CTkFrame(self, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(top, text="PainelTI", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=16, pady=12, sticky="w")

        appearance_switch = ctk.CTkSegmentedButton(
            top, values=["System", "Light", "Dark"], command=self._on_appearance_change
        )
        appearance_switch.set("System")
        appearance_switch.grid(row=0, column=1, padx=16, pady=12, sticky="e")
        CTkToolTip(appearance_switch, "Alterna entre tema claro, escuro ou o padrão do Windows.")

    # ------------------------------------------------------------- aba: Rede
    def _build_rede_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame_share = ctk.CTkFrame(aba)
        frame_share.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame_share.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(frame_share, text="Rede & Compartilhamento", font=ctk.CTkFont(size=15, weight="bold"))
        label.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        btn_compartilhar = self._botao_acao(
            frame_share, "Configurar Pasta e Compartilhamento", self._configurar_compartilhamento
        )
        btn_compartilhar.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")
        CTkToolTip(
            btn_compartilhar,
            f"Cria a pasta {network_share.CAMINHO_PADRAO}, compartilha na rede "
            f"como '{network_share.NOME_COMPARTILHAMENTO_PADRAO}' (para uso da impressora) "
            f"e concede Acesso Total (Full Control) ao usuário local '{network_share.USUARIO_PADRAO}', "
            "tanto no compartilhamento quanto no sistema de arquivos.",
        )

        frame_wifi = ctk.CTkFrame(aba)
        frame_wifi.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        frame_wifi.grid_columnconfigure(0, weight=1)

        label_wifi = ctk.CTkLabel(frame_wifi, text="Wi-Fi Corporativo", font=ctk.CTkFont(size=15, weight="bold"))
        label_wifi.grid(row=0, column=0, columnspan=3, padx=12, pady=(10, 4), sticky="w")

        form = ctk.CTkFrame(frame_wifi, fg_color="transparent")
        form.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew")
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        self.entry_nome = ctk.CTkEntry(form, placeholder_text="Nome da rede (SSID)")
        self.entry_nome.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")
        CTkToolTip(self.entry_nome, "Nome (SSID) da rede Wi-Fi corporativa.")

        self.entry_senha = ctk.CTkEntry(form, placeholder_text="Senha", show="*")
        self.entry_senha.grid(row=0, column=1, padx=(6, 0), pady=4, sticky="ew")
        CTkToolTip(self.entry_senha, "Senha da rede Wi-Fi (armazenada localmente em texto simples).")

        btn_salvar_perfil = ctk.CTkButton(form, text="Adicionar/Atualizar", command=self._salvar_perfil_form)
        btn_salvar_perfil.grid(row=0, column=2, padx=(6, 0), pady=4)
        CTkToolTip(btn_salvar_perfil, "Adiciona a rede à lista ou atualiza a senha se o nome já existir.")

        self.btn_aplicar_todas = self._botao_acao(frame_wifi, "Aplicar Todas", self._aplicar_todos_perfis)
        self.btn_aplicar_todas.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="e")
        CTkToolTip(self.btn_aplicar_todas, "Aplica todas as redes salvas nesta máquina, uma após a outra, via netsh.")

        self.lista_perfis_frame = ctk.CTkScrollableFrame(frame_wifi, height=140)
        self.lista_perfis_frame.grid(row=3, column=0, columnspan=3, padx=12, pady=(0, 12), sticky="ew")
        self.lista_perfis_frame.grid_columnconfigure(0, weight=1)

        self._render_lista_perfis()

    def _render_lista_perfis(self) -> None:
        for child in self.lista_perfis_frame.winfo_children():
            child.destroy()

        if not self._perfis:
            vazio = ctk.CTkLabel(self.lista_perfis_frame, text="Nenhuma rede cadastrada ainda.")
            vazio.grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for i, perfil in enumerate(self._perfis):
            row = ctk.CTkFrame(self.lista_perfis_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            nome_label = ctk.CTkLabel(row, text=perfil.nome, anchor="w")
            nome_label.grid(row=0, column=0, padx=(4, 8), sticky="ew")

            btn_aplicar = ctk.CTkButton(row, text="Aplicar", width=70, command=lambda p=perfil: self._aplicar_perfil(p))
            btn_aplicar.grid(row=0, column=1, padx=2)
            CTkToolTip(btn_aplicar, f"Aplica o perfil Wi-Fi '{perfil.nome}' nesta máquina via netsh.")

            btn_editar = ctk.CTkButton(row, text="Editar", width=70, command=lambda p=perfil: self._editar_perfil(p))
            btn_editar.grid(row=0, column=2, padx=2)
            CTkToolTip(btn_editar, "Carrega esta rede nos campos acima para edição.")

            btn_remover = ctk.CTkButton(
                row, text="Remover", width=70, fg_color="transparent", border_width=1,
                command=lambda p=perfil: self._remover_perfil(p),
            )
            btn_remover.grid(row=0, column=3, padx=2)
            CTkToolTip(btn_remover, "Remove esta rede da lista salva (não desconecta a rede no Windows).")

    # ---------------------------------------------------------- aba: Domínio
    def _build_dominio_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(aba)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame, text="Entrada no Domínio", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )
        ctk.CTkLabel(
            frame,
            text="Configure uma vez; depois é só clicar em 'Entrar no Domínio' em cada máquina nova.",
            text_color=("gray40", "gray70"),
        ).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="w")

        config_atual = dominio.carregar_config()

        self.entry_dominio_nome = ctk.CTkEntry(frame, placeholder_text="Domínio (ex.: empresa.local)")
        self.entry_dominio_nome.insert(0, config_atual.dominio)
        self.entry_dominio_nome.grid(row=2, column=0, columnspan=2, padx=12, pady=4, sticky="ew")
        CTkToolTip(self.entry_dominio_nome, "Nome do domínio Active Directory (ex.: empresa.local).")

        self.entry_dominio_usuario = ctk.CTkEntry(frame, placeholder_text="Usuário (ex.: DOMINIO\\ti)")
        self.entry_dominio_usuario.insert(0, config_atual.usuario)
        self.entry_dominio_usuario.grid(row=3, column=0, padx=(12, 6), pady=4, sticky="ew")
        CTkToolTip(self.entry_dominio_usuario, "Usuário com permissão de adicionar computadores ao domínio.")

        self.entry_dominio_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*")
        self.entry_dominio_senha.insert(0, config_atual.senha)
        self.entry_dominio_senha.grid(row=3, column=1, padx=(6, 12), pady=4, sticky="ew")
        CTkToolTip(self.entry_dominio_senha, "Senha do usuário acima (armazenada localmente em texto simples, em config/dominio.json).")

        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.grid(row=4, column=0, columnspan=2, padx=12, pady=(8, 12), sticky="w")

        btn_salvar = ctk.CTkButton(botoes, text="Salvar Configuração", command=self._salvar_config_dominio)
        btn_salvar.grid(row=0, column=0, padx=(0, 6))

        self.btn_entrar_dominio = self._botao_acao(botoes, "Entrar no Domínio", self._entrar_no_dominio)
        self.btn_entrar_dominio.grid(row=0, column=1, padx=6)
        CTkToolTip(
            self.btn_entrar_dominio,
            "Adiciona esta máquina ao domínio configurado (Add-Computer). Requer "
            "Administrador. Ao concluir, pede pra reiniciar o Windows.",
        )

    # ------------------------------------------------------- aba: Manutenção
    def _build_manutencao_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame_anydesk = ctk.CTkFrame(aba)
        frame_anydesk.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        ctk.CTkLabel(frame_anydesk, text="AnyDesk", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        btn_anydesk = self._botao_acao(frame_anydesk, "Resetar AnyDesk", self._resetar_anydesk)
        btn_anydesk.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")
        CTkToolTip(btn_anydesk, "Finaliza o processo, limpa a configuração e reabre o AnyDesk (duas vezes, para garantir a detecção do ID).")

        frame_explorer = ctk.CTkFrame(aba)
        frame_explorer.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        ctk.CTkLabel(frame_explorer, text="Visualização de PDFs (MOTW)", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )
        btn_desbloquear = self._botao_acao(frame_explorer, "Desbloquear Visualização", self._desbloquear_explorer)
        btn_desbloquear.grid(row=1, column=0, padx=(12, 6), pady=(0, 12), sticky="w")
        CTkToolTip(btn_desbloquear, "Remove a Marca da Web (MOTW) dos PDFs do usuário e reinicia o Explorer.")

        btn_bloquear = self._botao_acao(frame_explorer, "Bloquear Visualização", self._bloquear_explorer)
        btn_bloquear.grid(row=1, column=1, padx=(6, 12), pady=(0, 12), sticky="w")
        CTkToolTip(btn_bloquear, "Restaura a Marca da Web (MOTW) nos PDFs do usuário e reinicia o Explorer.")

    # ------------------------------------------------ aba: Diagnóstico & Restauração
    def _build_diagnostico_tab(self, aba_externa: ctk.CTkFrame) -> None:
        aba_externa.grid_columnconfigure(0, weight=1)
        aba_externa.grid_rowconfigure(0, weight=1)

        # A aba precisa rolar: Diagnóstico + Ponto de Restauração (com lista) +
        # Agendamento juntos não cabem na altura da janela em telas menores —
        # sem isso, a seção de agendamento fica invisível abaixo da dobra.
        aba = ctk.CTkScrollableFrame(aba_externa, fg_color="transparent")
        aba.grid(row=0, column=0, sticky="nsew")
        aba.grid_columnconfigure(0, weight=1)

        frame_diag = ctk.CTkFrame(aba)
        frame_diag.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame_diag.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_diag, text="Diagnóstico do Windows", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        self.btn_diagnostico = self._botao_acao(frame_diag, "Diagnóstico Completo (Dism/SFC)", self._executar_diagnostico)
        self.btn_diagnostico.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")
        CTkToolTip(
            self.btn_diagnostico,
            "Executa em sequência: Dism /Cleanup-Mountpoints, Dism /ScanHealth, "
            "Dism /RestoreHealth e SFC /SCANNOW. Pode levar vários minutos.",
        )

        progresso_diag = ctk.CTkFrame(frame_diag, fg_color="transparent")
        progresso_diag.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        progresso_diag.grid_columnconfigure(0, weight=1)

        self.progress_bar_diagnostico = ctk.CTkProgressBar(progresso_diag)
        self.progress_bar_diagnostico.set(0)
        self.progress_bar_diagnostico.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.progress_label_diagnostico = ctk.CTkLabel(progresso_diag, text="0%", width=50)
        self.progress_label_diagnostico.grid(row=0, column=1)

        agendamento_diag = ctk.CTkFrame(frame_diag, fg_color="transparent")
        agendamento_diag.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="w")

        ctk.CTkLabel(agendamento_diag, text="Repetir toda:").grid(row=0, column=0, padx=(0, 6))

        self.option_dia_semana_diagnostico = ctk.CTkOptionMenu(
            agendamento_diag, values=list(manutencao_windows.DIAS_SEMANA.keys())
        )
        self.option_dia_semana_diagnostico.set("Sexta")
        self.option_dia_semana_diagnostico.grid(row=0, column=1, padx=6)

        self.entry_hora_diagnostico = ctk.CTkEntry(agendamento_diag, placeholder_text="HH:MM", width=70)
        self.entry_hora_diagnostico.insert(0, "18:00")
        self.entry_hora_diagnostico.grid(row=0, column=2, padx=6)

        btn_agendar_diagnostico = ctk.CTkButton(
            agendamento_diag, text="Agendar Diagnóstico Semanal", command=self._agendar_diagnostico_semanal
        )
        btn_agendar_diagnostico.grid(row=0, column=3, padx=6)
        CTkToolTip(
            btn_agendar_diagnostico,
            f"Registra a tarefa '{manutencao_windows.TASK_NAME_WEEKLY_DIAGNOSTIC}', rodando o "
            "diagnóstico completo automaticamente no dia/horário escolhidos, sem abrir janela.",
        )

        btn_remover_diagnostico = ctk.CTkButton(
            agendamento_diag, text="Remover Agendamento", fg_color="transparent", border_width=1,
            command=self._remover_agendamento_diagnostico,
        )
        btn_remover_diagnostico.grid(row=0, column=4, padx=6)

        frame_restore = ctk.CTkFrame(aba)
        frame_restore.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        frame_restore.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_restore, text="Ponto de Restauração", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=12, pady=(10, 4), sticky="w"
        )

        botoes_restore = ctk.CTkFrame(frame_restore, fg_color="transparent")
        botoes_restore.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="w")

        btn_criar_restore = self._botao_acao(botoes_restore, "Criar Ponto de Restauração", self._criar_ponto_restauracao)
        btn_criar_restore.grid(row=0, column=0, padx=(0, 6))
        CTkToolTip(btn_criar_restore, "Cria um ponto de restauração do Windows. Limitado a 1 a cada 24h pelo próprio Windows quando criado via script.")

        btn_listar_restore = self._botao_acao(botoes_restore, "Listar Pontos Existentes", self._listar_pontos_restauracao)
        btn_listar_restore.grid(row=0, column=1, padx=6)

        btn_relatorio_pdf = self._botao_acao(botoes_restore, "Gerar Relatório PDF", self._gerar_relatorio_diagnostico)
        btn_relatorio_pdf.grid(row=0, column=2, padx=6)
        CTkToolTip(btn_relatorio_pdf, f"Gera um PDF com os pontos de restauração existentes e o histórico da sessão, salvo em {RELATORIOS_DIR}.")

        self.lista_pontos_restauracao_frame = ctk.CTkScrollableFrame(frame_restore, height=120)
        self.lista_pontos_restauracao_frame.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 12), sticky="ew")
        self.lista_pontos_restauracao_frame.grid_columnconfigure(0, weight=1)

        frame_agendamento = ctk.CTkFrame(aba)
        frame_agendamento.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        ctk.CTkLabel(frame_agendamento, text="Agendamento do Ponto de Restauração", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )

        btn_agendar = self._botao_acao(frame_agendamento, "Agendar no Logon", self._agendar_logon)
        btn_agendar.grid(row=1, column=0, padx=(12, 6), pady=(0, 8), sticky="w")
        CTkToolTip(
            btn_agendar,
            f"Registra a tarefa '{manutencao_windows.TASK_NAME}' no Agendador de Tarefas, "
            "disparada no logon com privilégio máximo: cria um ponto de restauração "
            "automaticamente, sem abrir nenhuma janela.",
        )

        btn_remover_agendamento = ctk.CTkButton(
            frame_agendamento, text="Remover", fg_color="transparent", border_width=1,
            command=self._remover_agendamento_logon,
        )
        btn_remover_agendamento.grid(row=1, column=1, padx=(6, 12), pady=(0, 8), sticky="w")

        linha_diaria = ctk.CTkFrame(frame_agendamento, fg_color="transparent")
        linha_diaria.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="w")

        ctk.CTkLabel(linha_diaria, text="Ou todo dia às:").grid(row=0, column=0, padx=(0, 6))

        self.entry_hora_checkpoint_diario = ctk.CTkEntry(linha_diaria, placeholder_text="HH:MM", width=70)
        self.entry_hora_checkpoint_diario.insert(0, "08:00")
        self.entry_hora_checkpoint_diario.grid(row=0, column=1, padx=6)

        btn_agendar_diario = ctk.CTkButton(linha_diaria, text="Agendar Diário", command=self._agendar_checkpoint_diario)
        btn_agendar_diario.grid(row=0, column=2, padx=6)
        CTkToolTip(
            btn_agendar_diario,
            f"Registra a tarefa '{manutencao_windows.TASK_NAME_DAILY}' num horário fixo todo "
            "dia — garante o ponto de restauração mesmo se a máquina ficar ligada dias sem "
            "novo logon. Convive com o agendamento por logon acima (os dois podem estar ativos).",
        )

        btn_remover_diario = ctk.CTkButton(
            linha_diaria, text="Remover", fg_color="transparent", border_width=1,
            command=self._remover_checkpoint_diario,
        )
        btn_remover_diario.grid(row=0, column=3, padx=6)

    # ------------------------------------------------------- aba: Instalação
    def _build_instalacao_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(aba)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Instalação de Apps Básicos", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )

        botoes = ctk.CTkFrame(frame, fg_color="transparent")
        botoes.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="w")

        btn_atualizar = ctk.CTkButton(botoes, text="Atualizar Lista", command=self._atualizar_lista_instaladores)
        btn_atualizar.grid(row=0, column=0, padx=(0, 6))
        CTkToolTip(
            btn_atualizar,
            f"Relê a pasta '{instaladores.INSTALADORES_DIR}' em busca de instaladores "
            "(.exe/.msi) e do config.json com os argumentos silenciosos de cada um.",
        )

        self.btn_instalar_todos = self._botao_acao(botoes, "Instalar Todos em Segundo Plano", self._instalar_todos)
        self.btn_instalar_todos.grid(row=0, column=1, padx=(6, 0))
        CTkToolTip(
            self.btn_instalar_todos,
            "Instala cada aplicativo encontrado, um de cada vez, silenciosamente "
            "(sem abrir janelas de instalação, usa os argumentos de instaladores/config.json). "
            "Já roda com privilégio de administrador, pois o próprio PainelTI já foi aberto elevado.",
        )

        self.btn_instalar_visivel = self._botao_acao(botoes, "Instalar Sequencialmente (Visível)", self._instalar_todos_visivel)
        self.btn_instalar_visivel.grid(row=0, column=2, padx=(6, 0))
        CTkToolTip(
            self.btn_instalar_visivel,
            "Abre cada instalador com a janela normal dele (ignora config.json de propósito) "
            "e só passa pro próximo da lista quando você fechar/concluir o atual — dá controle "
            "visual sobre cada instalação, sem precisar abrir manualmente um por um.",
        )

        self.lista_instaladores_frame = ctk.CTkScrollableFrame(frame, height=160)
        self.lista_instaladores_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="ew")
        self.lista_instaladores_frame.grid_columnconfigure(0, weight=1)

        progresso = ctk.CTkFrame(frame, fg_color="transparent")
        progresso.grid(row=3, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")
        progresso.grid_columnconfigure(0, weight=1)

        self.progress_bar_instaladores = ctk.CTkProgressBar(progresso)
        self.progress_bar_instaladores.set(0)
        self.progress_bar_instaladores.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.progress_label_instaladores = ctk.CTkLabel(progresso, text="0%", width=50)
        self.progress_label_instaladores.grid(row=0, column=1)

        self._atualizar_lista_instaladores()

    def _atualizar_lista_instaladores(self) -> None:
        self._instaladores_encontrados = instaladores.listar_instaladores()
        config = instaladores.carregar_config_silenciosa()

        for child in self.lista_instaladores_frame.winfo_children():
            child.destroy()

        if not self._instaladores_encontrados:
            vazio = ctk.CTkLabel(
                self.lista_instaladores_frame,
                text=f"Nenhum instalador encontrado em {instaladores.INSTALADORES_DIR}",
            )
            vazio.grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for i, caminho in enumerate(self._instaladores_encontrados):
            args = instaladores.resolver_argumentos(caminho, config)
            if args is None:
                status = "⚠ sem config (.exe sem argumento silencioso definido)"
            elif caminho.suffix.lower() == ".msi":
                status = f"msiexec {' '.join(args[1:])}"
            else:
                status = " ".join(args)

            row = ctk.CTkFrame(self.lista_instaladores_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=caminho.name, anchor="w", font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=0, padx=(4, 8), sticky="ew"
            )
            ctk.CTkLabel(row, text=status, anchor="w", text_color=("gray40", "gray70")).grid(
                row=1, column=0, padx=(4, 8), sticky="ew"
            )

    def _set_progress_instaladores(self, current: int, total: int) -> None:
        fraction = 0.0 if total == 0 else current / total
        self.progress_bar_instaladores.set(fraction)
        self.progress_label_instaladores.configure(text=f"{int(fraction * 100)}%")

    def _instalar_todos(self) -> None:
        if not self._instaladores_encontrados:
            messagebox.showinfo("PainelTI", "Nenhum instalador encontrado para instalar.")
            return

        def task() -> None:
            self.logger.info(f"Instalação de {len(self._instaladores_encontrados)} app(s) solicitada.")

            def on_progress(current: int, total: int, nome: str) -> None:
                self.after(0, self._set_progress_instaladores, current, total)
                if current > 0:
                    self.after(0, self._log_to_console, f"[{current}/{total}] {nome} concluído.")

            resultados = instaladores.instalar_todos(on_progress)
            falhas = 0
            for resultado in resultados:
                self._registrar_resultado(resultado)
                if not resultado.success:
                    falhas += 1

            total = len(resultados)
            if falhas == 0:
                self.after(0, messagebox.showinfo, "PainelTI", f"{total} app(s) instalado(s) com sucesso.")
            else:
                self.after(
                    0, messagebox.showwarning, "PainelTI",
                    f"{total - falhas} de {total} app(s) instalado(s). {falhas} falharam — veja o console.",
                )
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _instalar_todos_visivel(self) -> None:
        if not self._instaladores_encontrados:
            messagebox.showinfo("PainelTI", "Nenhum instalador encontrado para instalar.")
            return

        def task() -> None:
            self.logger.info(
                f"Instalação sequencial visível de {len(self._instaladores_encontrados)} app(s) solicitada."
            )

            def on_progress(current: int, total: int, nome: str) -> None:
                self.after(0, self._set_progress_instaladores, current, total)
                if current > 0:
                    self.after(0, self._log_to_console, f"[{current}/{total}] {nome} concluído.")

            resultados = instaladores.instalar_todos_visivel(on_progress)
            falhas = 0
            for resultado in resultados:
                self._registrar_resultado(resultado)
                if not resultado.success:
                    falhas += 1

            total = len(resultados)
            if falhas == 0:
                self.after(0, messagebox.showinfo, "PainelTI", f"{total} app(s) instalado(s).")
            else:
                self.after(
                    0, messagebox.showwarning, "PainelTI",
                    f"{total - falhas} de {total} app(s) concluído(s) sem erro. {falhas} com código de saída diferente de 0 — veja o console.",
                )
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # ------------------------------------------------------------ aba: Backup
    def _build_backup_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame_info = ctk.CTkFrame(aba)
        frame_info.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame_info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_info, text="Backup de Colaborador Desligado", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        ctk.CTkLabel(frame_info, text=f"Usuário atual: {getpass.getuser()}").grid(
            row=1, column=0, padx=12, sticky="w"
        )
        ctk.CTkLabel(frame_info, text=f"Destino: {backup_usuario.DESTINO_PADRAO}").grid(
            row=2, column=0, padx=12, pady=(0, 4), sticky="w"
        )
        ctk.CTkLabel(
            frame_info,
            text="Faz um único .zip com Desktop, Downloads, Documents e as pastas extras abaixo.",
            text_color=("gray40", "gray70"),
        ).grid(row=3, column=0, padx=12, pady=(0, 10), sticky="w")

        frame_extras = ctk.CTkFrame(aba)
        frame_extras.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        frame_extras.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_extras, text="Pastas Extras (Apps do Governo)", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=12, pady=(10, 4), sticky="w"
        )

        form_extras = ctk.CTkFrame(frame_extras, fg_color="transparent")
        form_extras.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew")
        form_extras.grid_columnconfigure(0, weight=1)

        self.entry_pasta_extra = ctk.CTkEntry(form_extras, placeholder_text="Caminho da pasta (ex.: C:\\Receitanet)")
        self.entry_pasta_extra.grid(row=0, column=0, padx=(0, 6), pady=4, sticky="ew")
        CTkToolTip(self.entry_pasta_extra, "Caminho absoluto de uma pasta em C: que também deve entrar no backup.")

        btn_procurar = ctk.CTkButton(form_extras, text="Procurar...", width=90, command=self._procurar_pasta_extra)
        btn_procurar.grid(row=0, column=1, padx=(6, 0), pady=4)

        btn_adicionar_extra = ctk.CTkButton(form_extras, text="Adicionar", command=self._adicionar_pasta_extra_backup)
        btn_adicionar_extra.grid(row=0, column=2, padx=(6, 0), pady=4)
        CTkToolTip(btn_adicionar_extra, "Adiciona a pasta à lista de pastas extras incluídas em todo backup.")

        self.lista_pastas_extras_frame = ctk.CTkScrollableFrame(frame_extras, height=100)
        self.lista_pastas_extras_frame.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 12), sticky="ew")
        self.lista_pastas_extras_frame.grid_columnconfigure(0, weight=1)

        self._render_lista_pastas_extras()

        frame_acao = ctk.CTkFrame(aba)
        frame_acao.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        frame_acao.grid_columnconfigure(0, weight=1)

        self.btn_fazer_backup = self._botao_acao(frame_acao, "Fazer Backup Agora", self._fazer_backup)
        self.btn_fazer_backup.grid(row=0, column=0, padx=12, pady=(10, 8), sticky="w")
        CTkToolTip(
            self.btn_fazer_backup,
            "Compacta Desktop, Downloads, Documents e as pastas extras num único "
            ".zip e copia para o servidor de backup.",
        )

        progresso = ctk.CTkFrame(frame_acao, fg_color="transparent")
        progresso.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        progresso.grid_columnconfigure(0, weight=1)

        self.progress_bar_backup = ctk.CTkProgressBar(progresso)
        self.progress_bar_backup.set(0)
        self.progress_bar_backup.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.progress_label_backup = ctk.CTkLabel(progresso, text="0%", width=50)
        self.progress_label_backup.grid(row=0, column=1)

    def _render_lista_pastas_extras(self) -> None:
        for child in self.lista_pastas_extras_frame.winfo_children():
            child.destroy()

        if not self._pastas_extras_backup:
            vazio = ctk.CTkLabel(self.lista_pastas_extras_frame, text="Nenhuma pasta extra configurada.")
            vazio.grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for i, caminho in enumerate(self._pastas_extras_backup):
            row = ctk.CTkFrame(self.lista_pastas_extras_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=caminho, anchor="w").grid(row=0, column=0, padx=(4, 8), sticky="ew")

            btn_remover = ctk.CTkButton(
                row, text="Remover", width=70, fg_color="transparent", border_width=1,
                command=lambda c=caminho: self._remover_pasta_extra_backup(c),
            )
            btn_remover.grid(row=0, column=1, padx=2)

    def _procurar_pasta_extra(self) -> None:
        caminho = filedialog.askdirectory()
        if caminho:
            self.entry_pasta_extra.delete(0, "end")
            self.entry_pasta_extra.insert(0, caminho)

    def _adicionar_pasta_extra_backup(self) -> None:
        caminho = self.entry_pasta_extra.get().strip()
        if not caminho:
            messagebox.showwarning("PainelTI", "Informe ou selecione um caminho de pasta.")
            return

        self._pastas_extras_backup = backup_usuario.adicionar_pasta_extra(self._pastas_extras_backup, caminho)
        backup_usuario.salvar_pastas_extras(self._pastas_extras_backup)
        self._log_to_console(f"Pasta extra '{caminho}' adicionada ao backup.")
        self.entry_pasta_extra.delete(0, "end")
        self._render_lista_pastas_extras()

    def _remover_pasta_extra_backup(self, caminho: str) -> None:
        self._pastas_extras_backup = backup_usuario.remover_pasta_extra(self._pastas_extras_backup, caminho)
        backup_usuario.salvar_pastas_extras(self._pastas_extras_backup)
        self._log_to_console(f"Pasta extra '{caminho}' removida do backup.")
        self._render_lista_pastas_extras()

    def _set_progress_backup(self, current: int, total: int) -> None:
        fraction = 0.0 if total == 0 else current / total
        self.progress_bar_backup.set(fraction)
        self.progress_label_backup.configure(text=f"{int(fraction * 100)}%")

    def _fazer_backup(self) -> None:
        def task() -> None:
            self.logger.info("Backup de usuário solicitado.")

            def on_progress(current: int, total: int, nome_arquivo: str) -> None:
                self.after(0, self._set_progress_backup, current, total)

            resultado = backup_usuario.gerar_backup(on_progress)
            self._registrar_resultado(resultado)
            if resultado.success:
                self.after(0, messagebox.showinfo, "PainelTI", resultado.message)
            else:
                self.after(0, messagebox.showerror, "PainelTI", resultado.message)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # ------------------------------------------------------- aba: Inventário
    def _build_inventario_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(aba)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(frame, text="Inventário de Máquina", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        btn_relatorio = self._botao_acao(frame, "Gerar Relatório de Hardware e Software", self._gerar_relatorio_inventario)
        btn_relatorio.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")
        CTkToolTip(
            btn_relatorio,
            "Faz o scan de hardware (placa-mãe, disco, processador, memória) e dos "
            "softwares instalados, gerando planilhas Excel. Requer os pacotes "
            "'wmi', 'psutil' e 'pandas' instalados.",
        )

    # ------------------------------------------------------ aba: Rede SEGETI
    def _build_rede_segeti_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(aba)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(frame, text="Configuração de Rede SEGETI", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )

        btn_detectar = self._botao_acao(frame, "Detectar Adaptadores", self._detectar_adaptadores)
        btn_detectar.grid(row=1, column=0, padx=(12, 6), pady=(0, 8), sticky="w")
        CTkToolTip(btn_detectar, "Lista os adaptadores de rede (cabo/Wi-Fi) desta máquina.")

        btn_configurar = self._botao_acao(frame, "Configurar Adaptadores (DHCP)", self._configurar_adaptadores)
        btn_configurar.grid(row=1, column=1, padx=(6, 12), pady=(0, 8), sticky="w")
        CTkToolTip(
            btn_configurar,
            "Renomeia os adaptadores detectados para o padrão SEGETI e configura "
            "todos como DHCP. Clique em 'Detectar Adaptadores' primeiro.",
        )

        btn_host = self._botao_acao(frame, "Adicionar Entrada de Host/DNS", self._adicionar_entrada_host)
        btn_host.grid(row=2, column=0, padx=(12, 6), pady=(0, 12), sticky="w")
        CTkToolTip(btn_host, "Adiciona a resolução do domínio da empresa no arquivo hosts do Windows.")

        btn_teste = self._botao_acao(frame, "Testar Conectividade", self._testar_conectividade)
        btn_teste.grid(row=2, column=1, padx=(6, 12), pady=(0, 12), sticky="w")
        CTkToolTip(btn_teste, "Testa (ping) a conectividade com o site da empresa.")

    # ----------------------------------------------------- aba: Exchange Online
    def _build_exchange_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(aba)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame, text="Exchange Online (Shared Mailbox / Calendário)", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w"
        )

        self.entry_exchange_grupo = ctk.CTkEntry(frame, placeholder_text="Grupo / shared mailbox")
        self.entry_exchange_grupo.grid(row=1, column=0, padx=(12, 6), pady=4, sticky="ew")
        CTkToolTip(self.entry_exchange_grupo, "Endereço do shared mailbox/calendário (ex.: financeiro@empresa.com).")

        self.entry_exchange_email = ctk.CTkEntry(frame, placeholder_text="E-mail do usuário")
        self.entry_exchange_email.grid(row=1, column=1, padx=(6, 12), pady=4, sticky="ew")
        CTkToolTip(self.entry_exchange_email, "E-mail do usuário que vai receber a permissão.")

        self.entry_exchange_permissao = ctk.CTkEntry(frame, placeholder_text="Permissão (ex.: Editor, Reviewer)")
        self.entry_exchange_permissao.grid(row=2, column=0, columnspan=2, padx=12, pady=4, sticky="ew")
        CTkToolTip(self.entry_exchange_permissao, "Usada só na ação 'Compartilhar Calendário' (Owner/PublishingEditor/Editor/Reviewer).")

        btn_criar_shared = self._botao_acao(frame, "Criar/Conceder Shared Mailbox", self._exchange_criar_conceder_shared)
        btn_criar_shared.grid(row=3, column=0, padx=(12, 6), pady=(8, 4), sticky="ew")

        btn_verificar_perm = self._botao_acao(frame, "Verificar Permissões do Grupo", self._exchange_verificar_permissoes)
        btn_verificar_perm.grid(row=3, column=1, padx=(6, 12), pady=(8, 4), sticky="ew")

        btn_conceder = self._botao_acao(frame, "Conceder Permissão ao Usuário", self._exchange_conceder_permissao)
        btn_conceder.grid(row=4, column=0, padx=(12, 6), pady=4, sticky="ew")

        btn_calendario = self._botao_acao(frame, "Verificar Calendário do Usuário", self._exchange_verificar_calendario)
        btn_calendario.grid(row=4, column=1, padx=(6, 12), pady=4, sticky="ew")

        btn_compartilhar_cal = self._botao_acao(frame, "Compartilhar Calendário", self._exchange_compartilhar_calendario)
        btn_compartilhar_cal.grid(row=5, column=0, columnspan=2, padx=12, pady=(4, 12), sticky="ew")
        CTkToolTip(
            btn_compartilhar_cal,
            "Requer o pacote 'cryptography' e o .env do Exchange Online configurado "
            "(AppId/CertificateThumbprint/Organization/PATH_CERTIFICADO/PASSWORD).",
        )

    # ---------------------------------------------------------- aba: Mikrotik
    def _build_mikrotik_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(aba)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(frame, text="Monitoramento MikroTik", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        btn_buscar = self._botao_acao(frame, "Buscar Logs Agora", self._mikrotik_buscar_logs)
        btn_buscar.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")
        CTkToolTip(
            btn_buscar,
            "Conecta ao MikroTik, busca os logs de DHCP recentes e testa (ping) os "
            "IPs encontrados. Requer o pacote 'librouteros' e o .env "
            "(mikro_USERNAME/mikro_PASSWORD/mikro_HOST_FW/mikro_PORT_FW) configurados.",
        )

    # ---------------------------------------------------------- aba: Watchdog
    def _build_watchdog_tab(self, aba: ctk.CTkFrame) -> None:
        aba.grid_columnconfigure(0, weight=1)

        frame_processos = ctk.CTkFrame(aba)
        frame_processos.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame_processos.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_processos, text="Programas em Execução", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        ctk.CTkLabel(
            frame_processos,
            text="Abra o programa desejado antes de atualizar a lista, depois clique em 'Monitorar'.",
            text_color=("gray40", "gray70"),
        ).grid(row=1, column=0, padx=12, pady=(0, 4), sticky="w")

        btn_atualizar_processos = ctk.CTkButton(
            frame_processos, text="Atualizar Lista de Programas", command=self._atualizar_lista_processos_watchdog
        )
        btn_atualizar_processos.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="w")
        CTkToolTip(btn_atualizar_processos, "Lista os programas com processo em execução nesta máquina agora.")

        self.lista_processos_watchdog_frame = ctk.CTkScrollableFrame(frame_processos, height=160)
        self.lista_processos_watchdog_frame.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.lista_processos_watchdog_frame.grid_columnconfigure(0, weight=1)

        frame_monitorados = ctk.CTkFrame(aba)
        frame_monitorados.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        frame_monitorados.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame_monitorados, text="Apps Monitorados (Auto-Restart)", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )

        self.lista_apps_watchdog_frame = ctk.CTkScrollableFrame(frame_monitorados, height=140)
        self.lista_apps_watchdog_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.lista_apps_watchdog_frame.grid_columnconfigure(0, weight=1)

        frame_ativacao = ctk.CTkFrame(aba)
        frame_ativacao.grid(row=2, column=0, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(frame_ativacao, text="Ativação", font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=12, pady=(10, 4), sticky="w"
        )

        ctk.CTkLabel(frame_ativacao, text="Verificar a cada (minutos):").grid(
            row=1, column=0, padx=(12, 6), pady=(0, 12), sticky="w"
        )

        self.entry_intervalo_watchdog = ctk.CTkEntry(frame_ativacao, width=60)
        self.entry_intervalo_watchdog.insert(0, str(self._intervalo_watchdog))
        self.entry_intervalo_watchdog.grid(row=1, column=1, padx=6, pady=(0, 12))

        self.btn_ativar_watchdog = self._botao_acao(frame_ativacao, "Ativar Watchdog", self._ativar_watchdog)
        self.btn_ativar_watchdog.grid(row=1, column=2, padx=6, pady=(0, 12))
        CTkToolTip(
            self.btn_ativar_watchdog,
            f"Registra a tarefa '{watchdog_manager.TASK_NAME_WATCHDOG}', que verifica os apps "
            "monitorados no intervalo escolhido e reabre qualquer um que tenha fechado.",
        )

        btn_desativar_watchdog = ctk.CTkButton(
            frame_ativacao, text="Desativar", fg_color="transparent", border_width=1,
            command=self._desativar_watchdog,
        )
        btn_desativar_watchdog.grid(row=1, column=3, padx=(6, 12), pady=(0, 12))
        CTkToolTip(btn_desativar_watchdog, f"Remove a tarefa agendada '{watchdog_manager.TASK_NAME_WATCHDOG}'.")

        self.label_status_watchdog = ctk.CTkLabel(frame_ativacao, text="")
        self.label_status_watchdog.grid(row=2, column=0, columnspan=4, padx=12, pady=(0, 10), sticky="w")

        self._render_lista_apps_watchdog()
        self._atualizar_status_watchdog()

    def _atualizar_lista_processos_watchdog(self) -> None:
        self._processos_disponiveis_watchdog = watchdog_manager.listar_processos_em_execucao()

        for child in self.lista_processos_watchdog_frame.winfo_children():
            child.destroy()

        if not self._processos_disponiveis_watchdog:
            vazio = ctk.CTkLabel(self.lista_processos_watchdog_frame, text="Nenhum programa encontrado.")
            vazio.grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        nomes_monitorados = {a.name for a in self._apps_watchdog}

        for i, (nome, caminho) in enumerate(self._processos_disponiveis_watchdog):
            row = ctk.CTkFrame(self.lista_processos_watchdog_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=f"{nome}   —   {caminho}", anchor="w").grid(
                row=0, column=0, padx=(4, 8), sticky="ew"
            )

            if nome in nomes_monitorados:
                ctk.CTkLabel(row, text="já monitorado", text_color=("gray40", "gray70")).grid(row=0, column=1, padx=6)
            else:
                btn_monitorar = ctk.CTkButton(
                    row, text="Monitorar", width=90,
                    command=lambda n=nome, c=caminho: self._adicionar_app_watchdog(n, c),
                )
                btn_monitorar.grid(row=0, column=1, padx=6)

    def _adicionar_app_watchdog(self, nome: str, caminho: str) -> None:
        self._apps_watchdog = watchdog_manager.adicionar_ou_atualizar_app(self._apps_watchdog, nome, caminho)
        watchdog_manager.salvar_apps(self._apps_watchdog)
        self._log_to_console(f"'{nome}' adicionado ao Watchdog ({caminho}).")
        self._render_lista_apps_watchdog()
        self._atualizar_lista_processos_watchdog()
        self._atualizar_status_watchdog()

    def _render_lista_apps_watchdog(self) -> None:
        for child in self.lista_apps_watchdog_frame.winfo_children():
            child.destroy()

        if not self._apps_watchdog:
            vazio = ctk.CTkLabel(self.lista_apps_watchdog_frame, text="Nenhum app monitorado ainda.")
            vazio.grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for i, app in enumerate(self._apps_watchdog):
            row = ctk.CTkFrame(self.lista_apps_watchdog_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=app.name, anchor="w").grid(row=0, column=0, padx=(4, 8), sticky="ew")

            switch = ctk.CTkSwitch(
                row, text="Ativo" if app.enabled else "Pausado", width=80,
                command=lambda a=app: self._alternar_app_watchdog(a),
            )
            (switch.select if app.enabled else switch.deselect)()
            switch.grid(row=0, column=1, padx=6)

            btn_remover = ctk.CTkButton(
                row, text="Remover", width=70, fg_color="transparent", border_width=1,
                command=lambda a=app: self._remover_app_watchdog(a),
            )
            btn_remover.grid(row=0, column=2, padx=2)

    def _alternar_app_watchdog(self, app: watchdog_manager.WatchdogApp) -> None:
        self._apps_watchdog = watchdog_manager.alternar_app(self._apps_watchdog, app.name)
        watchdog_manager.salvar_apps(self._apps_watchdog)
        self._log_to_console(f"'{app.name}' {'pausado' if app.enabled else 'ativado'} no Watchdog.")
        self._render_lista_apps_watchdog()

    def _remover_app_watchdog(self, app: watchdog_manager.WatchdogApp) -> None:
        self._apps_watchdog = watchdog_manager.remover_app(self._apps_watchdog, app.name)
        watchdog_manager.salvar_apps(self._apps_watchdog)
        self._log_to_console(f"'{app.name}' removido do Watchdog.")
        self._render_lista_apps_watchdog()
        self._atualizar_lista_processos_watchdog()
        self._atualizar_status_watchdog()

    def _ativar_watchdog(self) -> None:
        if not self._apps_watchdog:
            messagebox.showwarning("PainelTI", "Adicione ao menos um app para monitorar antes de ativar.")
            return

        texto_intervalo = self.entry_intervalo_watchdog.get().strip()
        if not texto_intervalo.isdigit() or int(texto_intervalo) < 1:
            messagebox.showwarning("PainelTI", "Informe um intervalo válido em minutos (mínimo 1).")
            return
        intervalo = int(texto_intervalo)

        def task() -> None:
            self.logger.info(f"Ativação do Watchdog solicitada (a cada {intervalo} min).")
            watchdog_manager.salvar_apps(self._apps_watchdog, intervalo)
            resultado = watchdog_manager.criar_tarefa_watchdog(intervalo)
            self._registrar_resultado(resultado)
            if resultado.success:
                self._intervalo_watchdog = intervalo
                self.after(0, messagebox.showinfo, "PainelTI", resultado.message)
            else:
                self.after(0, messagebox.showerror, "PainelTI", resultado.message)
            self.after(0, self._atualizar_status_watchdog)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _desativar_watchdog(self) -> None:
        resultado = watchdog_manager.remover_tarefa_watchdog()
        self._registrar_resultado(resultado)
        self._atualizar_status_watchdog()

    def _atualizar_status_watchdog(self) -> None:
        ativo = watchdog_manager.tarefa_watchdog_existe()
        self.label_status_watchdog.configure(
            text=f"Status: {'ativo' if ativo else 'inativo'} ({len(self._apps_watchdog)} app(s) na lista)."
        )

    def _build_console(self) -> None:
        self.console = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12), height=160)
        self.console.grid(row=2, column=0, sticky="nsew", padx=16, pady=(4, 16))
        self.console.configure(state="disabled")
        CTkToolTip(self.console, "Console de saída em tempo real das ações executadas.")

    # ------------------------------------------------------------- utilidades
    def _botao_acao(self, master: ctk.CTkFrame, texto: str, comando) -> ctk.CTkButton:
        botao = ctk.CTkButton(master, text=texto, command=comando)
        self._botoes_para_bloquear.append(botao)
        return botao

    def _on_appearance_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)

    def _log_to_console(self, message: str) -> None:
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for botao in self._botoes_para_bloquear:
            botao.configure(state=state)

    def _run_async(self, target) -> None:
        if self._busy:
            messagebox.showwarning("PainelTI", "Aguarde a operação atual terminar.")
            return
        self._set_busy(True)
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def _registrar_resultado(self, resultado) -> None:
        self.after(0, self._log_to_console, resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
        else:
            self.logger.error(resultado.message)

    # --------------------------------------------------------------- ações: Rede
    def _configurar_compartilhamento(self) -> None:
        def task() -> None:
            self.logger.info("Configuração de pasta e compartilhamento solicitada.")
            resultados = network_share.configurar_pasta_compartilhada()
            for resultado in resultados:
                self._registrar_resultado(resultado)

            falhou = next((r for r in resultados if not r.success), None)
            if falhou:
                self.after(0, messagebox.showerror, "PainelTI", falhou.message)
            else:
                self.after(0, messagebox.showinfo, "PainelTI", "Pasta e compartilhamento configurados com sucesso.")
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _salvar_perfil_form(self) -> None:
        nome = self.entry_nome.get().strip()
        senha = self.entry_senha.get()

        if not nome:
            messagebox.showwarning("PainelTI", "Informe o nome (SSID) da rede.")
            return

        self._perfis = wifi_manager.adicionar_ou_atualizar_perfil(self._perfis, nome, senha)
        wifi_manager.salvar_perfis(self._perfis)
        self.logger.success(f"Perfil Wi-Fi '{nome}' salvo.")
        self._log_to_console(f"Perfil Wi-Fi '{nome}' salvo.")

        self.entry_nome.delete(0, "end")
        self.entry_senha.delete(0, "end")
        self._render_lista_perfis()

    def _editar_perfil(self, perfil: wifi_manager.WifiProfile) -> None:
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, perfil.nome)
        self.entry_senha.delete(0, "end")
        self.entry_senha.insert(0, perfil.senha)

    def _remover_perfil(self, perfil: wifi_manager.WifiProfile) -> None:
        self._perfis = wifi_manager.remover_perfil(self._perfis, perfil.nome)
        wifi_manager.salvar_perfis(self._perfis)
        self.logger.info(f"Perfil Wi-Fi '{perfil.nome}' removido da lista.")
        self._log_to_console(f"Perfil Wi-Fi '{perfil.nome}' removido da lista.")
        self._render_lista_perfis()

    def _aplicar_perfil(self, perfil: wifi_manager.WifiProfile) -> None:
        def task() -> None:
            resultado = wifi_manager.aplicar_perfil(perfil)
            self._registrar_resultado(resultado)
            if resultado.success:
                self.after(0, messagebox.showinfo, "PainelTI", resultado.message)
            else:
                self.after(0, messagebox.showerror, "PainelTI", resultado.message)

        threading.Thread(target=task, daemon=True).start()

    def _aplicar_todos_perfis(self) -> None:
        if not self._perfis:
            messagebox.showinfo("PainelTI", "Nenhuma rede cadastrada para aplicar.")
            return

        def task() -> None:
            self.logger.info(f"Aplicando {len(self._perfis)} perfil(is) Wi-Fi salvos.")
            falhas = 0
            for perfil in self._perfis:
                resultado = wifi_manager.aplicar_perfil(perfil)
                self._registrar_resultado(resultado)
                if not resultado.success:
                    falhas += 1

            total = len(self._perfis)
            if falhas == 0:
                self.after(0, messagebox.showinfo, "PainelTI", f"{total} rede(s) aplicada(s) com sucesso.")
            else:
                self.after(
                    0, messagebox.showwarning, "PainelTI",
                    f"{total - falhas} de {total} rede(s) aplicada(s). {falhas} falharam — veja o console.",
                )
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # -------------------------------------------------------------- ações: Domínio
    def _salvar_config_dominio(self) -> None:
        config = dominio.ConfigDominio(
            dominio=self.entry_dominio_nome.get().strip(),
            usuario=self.entry_dominio_usuario.get().strip(),
            senha=self.entry_dominio_senha.get(),
        )
        dominio.salvar_config(config)
        self.logger.success("Configuração de domínio salva.")
        self._log_to_console("Configuração de domínio salva.")

    def _entrar_no_dominio(self) -> None:
        config = dominio.ConfigDominio(
            dominio=self.entry_dominio_nome.get().strip(),
            usuario=self.entry_dominio_usuario.get().strip(),
            senha=self.entry_dominio_senha.get(),
        )
        if not config.dominio or not config.usuario or not config.senha:
            messagebox.showwarning("PainelTI", "Preencha domínio, usuário e senha antes de continuar.")
            return

        dominio.salvar_config(config)

        def task() -> None:
            self.logger.info(f"Entrada no domínio '{config.dominio}' solicitada.")
            resultado = dominio.entrar_no_dominio(config)
            self._registrar_resultado(resultado)
            if resultado.success:
                self.after(0, self._oferecer_reiniciar_windows, resultado.message)
            else:
                self.after(0, messagebox.showerror, "PainelTI", resultado.message)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _oferecer_reiniciar_windows(self, message: str) -> None:
        resposta = messagebox.askyesno("PainelTI", message + "\n\nReiniciar o Windows agora?")
        if not resposta:
            return
        resultado = dominio.reiniciar_windows()
        self._log_to_console(resultado.message)
        if not resultado.success:
            messagebox.showerror("PainelTI", resultado.message)

    # ------------------------------------------------------- ações: Manutenção
    def _resetar_anydesk(self) -> None:
        def task() -> None:
            self.logger.info("Reset do AnyDesk solicitado.")
            resultados = anydesk_module.resetar_anydesk()
            for resultado in resultados:
                self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _desbloquear_explorer(self) -> None:
        def task() -> None:
            resultado = explorer_module.desbloquear()
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _bloquear_explorer(self) -> None:
        def task() -> None:
            resultado = explorer_module.bloquear()
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # ---------------------------------------------- ações: Diagnóstico & Restauração
    def _set_progress_diagnostico(self, current: int, total: int, nome: str = "") -> None:
        fraction = 0.0 if total == 0 else current / total
        self.progress_bar_diagnostico.set(fraction)
        self.progress_label_diagnostico.configure(text=f"{int(fraction * 100)}%")
        if nome:
            self._log_to_console(f"[{current}/{total}] {nome}")

    def _executar_diagnostico(self) -> None:
        def task() -> None:
            self.logger.info("Diagnóstico completo (Dism/SFC) iniciado.")

            def on_output(text: str, overwrite: bool = False) -> None:
                pass  # etapas já são logadas via on_progress; saída bruta é só ruído no console

            def on_progress(current: int, total: int, nome: str) -> None:
                self.after(0, self._set_progress_diagnostico, current, total, nome)

            resultados = manutencao_windows.run_full_diagnostics(on_output, on_progress)
            falhas = 0
            for resultado in resultados:
                if resultado.success:
                    self.logger.success(f"{resultado.step.name} concluído com sucesso.")
                else:
                    self.logger.error(f"{resultado.step.name} falhou (código {resultado.return_code}).")
                    falhas += 1

            if falhas == 0:
                self.after(0, messagebox.showinfo, "PainelTI", "Diagnóstico concluído com sucesso em todas as etapas.")
            else:
                self.after(
                    0, messagebox.showwarning, "PainelTI",
                    f"Diagnóstico concluído com {falhas} etapa(s) com falha. Veja o console.",
                )
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _criar_ponto_restauracao(self) -> None:
        def task() -> None:
            self.logger.info("Criação de ponto de restauração solicitada.")
            resultado = manutencao_windows.create_restore_point()
            self._registrar_resultado(resultado)
            if resultado.success:
                self.after(0, messagebox.showinfo, "PainelTI", resultado.message)
            elif resultado.throttled:
                self.after(0, self._oferecer_bypass_frequencia, resultado.message)
            else:
                self.after(0, messagebox.showerror, "PainelTI", resultado.message)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _oferecer_bypass_frequencia(self, message: str) -> None:
        resposta = messagebox.askyesno(
            "PainelTI", message + "\n\nDeseja permitir múltiplos pontos por dia agora e tentar novamente?"
        )
        if not resposta:
            return

        def task() -> None:
            resultado_bypass = manutencao_windows.allow_frequent_restore_points()
            self._registrar_resultado(resultado_bypass)
            if resultado_bypass.success:
                resultado_retry = manutencao_windows.create_restore_point()
                self._registrar_resultado(resultado_retry)
                if resultado_retry.success:
                    self.after(0, messagebox.showinfo, "PainelTI", resultado_retry.message)
                else:
                    self.after(0, messagebox.showerror, "PainelTI", resultado_retry.message)
            else:
                self.after(0, messagebox.showerror, "PainelTI", resultado_bypass.message)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _listar_pontos_restauracao(self) -> None:
        def task() -> None:
            pontos = manutencao_windows.list_restore_points()

            def render() -> None:
                for child in self.lista_pontos_restauracao_frame.winfo_children():
                    child.destroy()
                if not pontos:
                    vazio = ctk.CTkLabel(self.lista_pontos_restauracao_frame, text="Nenhum ponto de restauração encontrado.")
                    vazio.grid(row=0, column=0, padx=8, pady=8, sticky="w")
                    return
                for i, ponto in enumerate(pontos):
                    data_str = ponto.creation_time.strftime("%d/%m/%Y %H:%M:%S") if ponto.creation_time else "N/D"
                    texto = f"#{ponto.sequence_number} — {data_str} — {ponto.description} ({ponto.type_label})"
                    ctk.CTkLabel(self.lista_pontos_restauracao_frame, text=texto, anchor="w").grid(
                        row=i, column=0, padx=8, pady=2, sticky="w"
                    )

            self.after(0, render)
            self.after(0, self._log_to_console, f"{len(pontos)} ponto(s) de restauração encontrado(s).")
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _gerar_relatorio_diagnostico(self) -> None:
        def task() -> None:
            try:
                caminho = manutencao_windows.gerar_relatorio_pdf(self.logger.events)
                self._registrar_resultado_ok(f"Relatório salvo em: {caminho}")
                self.after(0, messagebox.showinfo, "PainelTI", f"Relatório salvo em:\n{caminho}")
            except Exception as error:  # noqa: BLE001
                self._registrar_resultado_erro(f"Falha ao gerar relatório PDF: {error}")
                self.after(0, messagebox.showerror, "PainelTI", f"Falha ao gerar relatório PDF: {error}")
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _registrar_resultado_ok(self, message: str) -> None:
        self.after(0, self._log_to_console, message)
        self.logger.success(message)

    def _registrar_resultado_erro(self, message: str) -> None:
        self.after(0, self._log_to_console, message)
        self.logger.error(message)

    def _agendar_logon(self) -> None:
        resultado = manutencao_windows.create_logon_task()
        self._log_to_console(resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
            messagebox.showinfo("PainelTI", resultado.message)
        else:
            self.logger.error(resultado.message)
            messagebox.showerror("PainelTI", resultado.message)

    def _remover_agendamento_logon(self) -> None:
        resultado = manutencao_windows.remove_logon_task()
        self._log_to_console(resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
        else:
            self.logger.error(resultado.message)
        messagebox.showinfo("PainelTI", resultado.message)

    def _garantir_agendamento_logon(self) -> None:
        """Garante que o ponto de restauração no logon está ativo, sem precisar
        de nenhum clique manual: toda vez que o PainelTI abre, verifica se a
        tarefa já existe e, se não existir (máquina nova ou removida sem
        querer), cria automaticamente."""
        def task() -> None:
            if manutencao_windows.task_exists():
                return
            resultado = manutencao_windows.create_logon_task()
            if resultado.success:
                self.after(0, self._log_to_console, "Agendamento automático de ponto de restauração no logon ativado.")
                self.logger.success("Agendamento automático de ponto de restauração no logon ativado.")
            else:
                self.after(0, self._log_to_console, f"Não foi possível ativar o agendamento automático: {resultado.message}")
                self.logger.error(f"Falha ao ativar agendamento automático: {resultado.message}")

        threading.Thread(target=task, daemon=True).start()

    def _validar_horario(self, texto: str) -> bool:
        try:
            datetime.strptime(texto.strip(), "%H:%M")
            return True
        except ValueError:
            return False

    def _agendar_checkpoint_diario(self) -> None:
        hora = self.entry_hora_checkpoint_diario.get().strip()
        if not self._validar_horario(hora):
            messagebox.showwarning("PainelTI", "Informe o horário no formato HH:MM (ex.: 08:00).")
            return

        resultado = manutencao_windows.create_daily_checkpoint_task(hora)
        self._log_to_console(resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
            messagebox.showinfo("PainelTI", resultado.message)
        else:
            self.logger.error(resultado.message)
            messagebox.showerror("PainelTI", resultado.message)

    def _remover_checkpoint_diario(self) -> None:
        resultado = manutencao_windows.remove_daily_checkpoint_task()
        self._log_to_console(resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
        else:
            self.logger.error(resultado.message)
        messagebox.showinfo("PainelTI", resultado.message)

    def _agendar_diagnostico_semanal(self) -> None:
        dia = self.option_dia_semana_diagnostico.get()
        hora = self.entry_hora_diagnostico.get().strip()
        if not self._validar_horario(hora):
            messagebox.showwarning("PainelTI", "Informe o horário no formato HH:MM (ex.: 18:00).")
            return

        resultado = manutencao_windows.create_weekly_diagnostic_task(dia, hora)
        self._log_to_console(resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
            messagebox.showinfo("PainelTI", resultado.message)
        else:
            self.logger.error(resultado.message)
            messagebox.showerror("PainelTI", resultado.message)

    def _remover_agendamento_diagnostico(self) -> None:
        resultado = manutencao_windows.remove_weekly_diagnostic_task()
        self._log_to_console(resultado.message)
        if resultado.success:
            self.logger.success(resultado.message)
        else:
            self.logger.error(resultado.message)
        messagebox.showinfo("PainelTI", resultado.message)

    # ------------------------------------------------------- ações: Inventário
    def _gerar_relatorio_inventario(self) -> None:
        def task() -> None:
            self.logger.info("Geração de relatório de inventário solicitada.")
            resultado = inventario_module.gerar_relatorio()
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # ------------------------------------------------------ ações: Rede SEGETI
    def _detectar_adaptadores(self) -> None:
        def task() -> None:
            resultado, interfaces = rede_segeti_module.detectar_adaptadores()
            self._interfaces_detectadas = interfaces
            self._registrar_resultado(resultado)
            for interface in interfaces:
                self.after(0, self._log_to_console, f"  - {interface}")
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _configurar_adaptadores(self) -> None:
        if not self._interfaces_detectadas:
            messagebox.showwarning("PainelTI", "Clique em 'Detectar Adaptadores' primeiro.")
            return

        def task() -> None:
            resultado = rede_segeti_module.configurar_adaptadores(self._interfaces_detectadas)
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _adicionar_entrada_host(self) -> None:
        def task() -> None:
            resultado = rede_segeti_module.adicionar_entrada_host()
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _testar_conectividade(self) -> None:
        def task() -> None:
            resultado = rede_segeti_module.testar_conectividade()
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # --------------------------------------------------- ações: Exchange Online
    def _exchange_criar_conceder_shared(self) -> None:
        grupo = self.entry_exchange_grupo.get().strip()
        email = self.entry_exchange_email.get().strip()
        if not grupo or not email:
            messagebox.showwarning("PainelTI", "Informe o grupo e o e-mail.")
            return

        def task() -> None:
            resultado = exchange_module.criar_conceder_permissao_shared(grupo, email)
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _exchange_verificar_permissoes(self) -> None:
        grupo = self.entry_exchange_grupo.get().strip()
        if not grupo:
            messagebox.showwarning("PainelTI", "Informe o grupo.")
            return

        def task() -> None:
            resultado = exchange_module.verificar_permissoes(grupo)
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _exchange_conceder_permissao(self) -> None:
        grupo = self.entry_exchange_grupo.get().strip()
        email = self.entry_exchange_email.get().strip()
        if not grupo or not email:
            messagebox.showwarning("PainelTI", "Informe o grupo e o e-mail.")
            return

        def task() -> None:
            resultado = exchange_module.conceder_permissoes_shared(grupo, email)
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _exchange_verificar_calendario(self) -> None:
        email = self.entry_exchange_email.get().strip()
        if not email:
            messagebox.showwarning("PainelTI", "Informe o e-mail.")
            return

        def task() -> None:
            resultado = exchange_module.verificar_calendario(email)
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _exchange_compartilhar_calendario(self) -> None:
        grupo = self.entry_exchange_grupo.get().strip()
        email = self.entry_exchange_email.get().strip()
        permissao = self.entry_exchange_permissao.get().strip()
        if not grupo or not email or not permissao:
            messagebox.showwarning("PainelTI", "Informe o grupo, o e-mail e a permissão.")
            return

        def task() -> None:
            resultado = exchange_module.compartilhar_calendario(grupo, email, permissao)
            self._registrar_resultado(resultado)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    # ------------------------------------------------------------ ações: Mikrotik
    def _mikrotik_buscar_logs(self) -> None:
        def task() -> None:
            self.logger.info("Busca de logs do Mikrotik solicitada.")
            resultado, informacoes = mikrotik_module.conectar_e_buscar_logs()
            self._registrar_resultado(resultado)
            for chave, valor in informacoes.items():
                self.after(0, self._log_to_console, f"  {chave}: {valor}")
            self.after(0, self._set_busy, False)

        self._run_async(task)


def run() -> None:
    app = App()
    app.mainloop()
