"""Janela principal do CorrecaoSistema (customtkinter)."""
from __future__ import annotations

import sys
import threading
import webbrowser
from tkinter import messagebox

import customtkinter as ctk

from app import restore_point, scheduler, system_repair
from app.logger import EventLogger
from app.report import generate_pdf_report
from app.tooltip import CTkToolTip

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CorrecaoSistema")
        self.geometry("860x620")
        self.minsize(760, 560)

        self.logger = EventLogger()
        self._busy = False

        self._build_layout()
        self.logger.info("Aplicação iniciada.")
        self._log_to_console("Bem-vindo ao CorrecaoSistema. Selecione uma ação abaixo.")

    # ---------------------------------------------------------------- layout
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_top_bar()
        self._build_actions_bar()
        self._build_console()
        self._build_progress_bar()

    def _build_top_bar(self) -> None:
        top = ctk.CTkFrame(self, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(top, text="CorrecaoSistema", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=16, pady=12, sticky="w")

        appearance_switch = ctk.CTkSegmentedButton(
            top, values=["System", "Light", "Dark"], command=self._on_appearance_change
        )
        appearance_switch.set("System")
        appearance_switch.grid(row=0, column=1, padx=16, pady=12, sticky="e")
        CTkToolTip(appearance_switch, "Alterna entre tema claro, escuro ou o padrão do Windows.")

    def _build_actions_bar(self) -> None:
        bar = ctk.CTkFrame(self)
        bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 4))
        for col in range(5):
            bar.grid_columnconfigure(col, weight=1)

        self.btn_diagnostics = ctk.CTkButton(
            bar, text="Executar Diagnóstico Completo", command=self._start_full_diagnostics
        )
        self.btn_diagnostics.grid(row=0, column=0, padx=6, pady=10, sticky="ew")
        CTkToolTip(
            self.btn_diagnostics,
            "Executa em sequência: Dism /Cleanup-Mountpoints, Dism /ScanHealth, "
            "Dism /RestoreHealth e SFC /SCANNOW. Cada etapa aguarda a anterior terminar.",
        )

        self.btn_restore_point = ctk.CTkButton(
            bar, text="Criar Ponto de Restauração", command=self._create_restore_point
        )
        self.btn_restore_point.grid(row=0, column=1, padx=6, pady=10, sticky="ew")
        CTkToolTip(
            self.btn_restore_point,
            "Cria um ponto de restauração do Windows antes de aplicar correções. "
            "O Windows limita a 1 por dia quando criado via script.",
        )

        self.btn_schedule = ctk.CTkButton(
            bar, text="Agendar no Logon", command=self._schedule_logon_task
        )
        self.btn_schedule.grid(row=0, column=2, padx=6, pady=10, sticky="ew")
        CTkToolTip(
            self.btn_schedule,
            "Registra o CorrecaoSistema no Agendador de Tarefas do Windows para "
            "iniciar automaticamente a cada logon, com privilégios de Administrador.",
        )

        self.btn_unschedule = ctk.CTkButton(
            bar, text="Remover Agendamento", command=self._unschedule_logon_task,
            fg_color="transparent", border_width=1,
        )
        self.btn_unschedule.grid(row=0, column=3, padx=6, pady=10, sticky="ew")
        CTkToolTip(self.btn_unschedule, "Remove a tarefa agendada de execução automática no logon.")

        self.btn_report = ctk.CTkButton(
            bar, text="Gerar Relatório PDF", command=self._generate_report
        )
        self.btn_report.grid(row=0, column=4, padx=6, pady=10, sticky="ew")
        CTkToolTip(
            self.btn_report,
            "Gera um PDF com todos os eventos registrados nesta sessão e salva em "
            "Documentos\\CorrecaoSistema\\Relatorios.",
        )

    def _build_console(self) -> None:
        self.console = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.console.grid(row=2, column=0, sticky="nsew", padx=16, pady=4)
        self.console.configure(state="disabled")
        CTkToolTip(self.console, "Console de saída em tempo real dos comandos executados.")

    def _build_progress_bar(self) -> None:
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 12))
        bottom.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(bottom)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        CTkToolTip(self.progress_bar, "Progresso da operação atual, em porcentagem.")

        self.progress_label = ctk.CTkLabel(bottom, text="0%", width=50)
        self.progress_label.grid(row=0, column=1)

    # ------------------------------------------------------------- utilidades
    def _on_appearance_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)

    def _log_to_console(self, message: str) -> None:
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _set_progress(self, current: int, total: int, label: str = "") -> None:
        fraction = 0.0 if total == 0 else current / total
        self.progress_bar.set(fraction)
        self.progress_label.configure(text=f"{int(fraction * 100)}%")
        if label:
            self._log_to_console(f"[{current}/{total}] {label}")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        for btn in (self.btn_diagnostics, self.btn_restore_point, self.btn_schedule, self.btn_unschedule, self.btn_report):
            btn.configure(state=state)

    def _run_async(self, target) -> None:
        if self._busy:
            messagebox.showwarning("CorrecaoSistema", "Aguarde a operação atual terminar.")
            return
        self._set_busy(True)
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    # --------------------------------------------------------------- ações
    def _start_full_diagnostics(self) -> None:
        def task() -> None:
            self.logger.info("Diagnóstico completo iniciado pelo usuário.")

            def on_output(line: str) -> None:
                self.after(0, self._log_to_console, line)

            def on_progress(current: int, total: int, name: str) -> None:
                self.after(0, self._set_progress, current, total, name)

            try:
                results = system_repair.run_full_diagnostics(on_output, on_progress)
                for result in results:
                    if result.success:
                        self.logger.success(f"{result.step.name} concluído com sucesso.")
                    else:
                        self.logger.error(
                            f"{result.step.name} falhou (código {result.return_code}).",
                            output=result.output[-2000:],
                        )
                self.after(0, self._diagnostics_finished, results)
            except PermissionError:
                self.logger.error("Permissão negada ao executar comandos de reparo.")
                self.after(0, messagebox.showerror, "CorrecaoSistema",
                           "Permissão negada. Execute o aplicativo como Administrador.")
            except Exception as exc:  # noqa: BLE001 - reportar qualquer falha inesperada ao usuário
                self.logger.error(f"Falha inesperada no diagnóstico: {exc}")
                self.after(0, messagebox.showerror, "CorrecaoSistema", f"Falha inesperada: {exc}")
            finally:
                self.after(0, self._set_busy, False)

        self._run_async(task)

    def _diagnostics_finished(self, results: list) -> None:
        failures = [r for r in results if not r.success]
        if failures:
            messagebox.showwarning(
                "CorrecaoSistema",
                f"Diagnóstico concluído com {len(failures)} etapa(s) com falha. Veja o console para detalhes.",
            )
        else:
            messagebox.showinfo("CorrecaoSistema", "Diagnóstico concluído com sucesso em todas as etapas.")

    def _create_restore_point(self) -> None:
        def task() -> None:
            self.logger.info("Criação de ponto de restauração solicitada.")
            result = restore_point.create_restore_point()
            self.after(0, self._log_to_console, result.message)
            if result.success:
                self.logger.success(result.message)
                self.after(0, messagebox.showinfo, "CorrecaoSistema", result.message)
            else:
                self.logger.warning(result.message)
                if result.limited_by_frequency:
                    self.after(0, self._offer_frequency_bypass, result.message)
                else:
                    self.after(0, messagebox.showerror, "CorrecaoSistema", result.message)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _offer_frequency_bypass(self, message: str) -> None:
        answer = messagebox.askyesno(
            "CorrecaoSistema",
            message + "\n\nDeseja permitir múltiplos pontos por dia agora e tentar novamente?",
        )
        if not answer:
            return

        def task() -> None:
            bypass_result = restore_point.allow_frequent_restore_points()
            self.after(0, self._log_to_console, bypass_result.message)
            if bypass_result.success:
                self.logger.info(bypass_result.message)
                retry = restore_point.create_restore_point()
                self.after(0, self._log_to_console, retry.message)
                if retry.success:
                    self.logger.success(retry.message)
                    self.after(0, messagebox.showinfo, "CorrecaoSistema", retry.message)
                else:
                    self.logger.error(retry.message)
                    self.after(0, messagebox.showerror, "CorrecaoSistema", retry.message)
            else:
                self.logger.error(bypass_result.message)
                self.after(0, messagebox.showerror, "CorrecaoSistema", bypass_result.message)
            self.after(0, self._set_busy, False)

        self._run_async(task)

    def _schedule_logon_task(self) -> None:
        if getattr(sys, "frozen", False):
            # Executável gerado via PyInstaller: roda diretamente, sem argumentos.
            target, args = sys.executable, ""
        else:
            # Execução via script: dispara o mesmo interpretador com main.py.
            target, args = sys.executable, f'"{sys.argv[0]}"'
        result = scheduler.create_logon_task(target, args)
        self._log_to_console(result.message)
        if result.success:
            self.logger.success(result.message)
            messagebox.showinfo("CorrecaoSistema", result.message)
        else:
            self.logger.error(result.message)
            messagebox.showerror("CorrecaoSistema", result.message)

    def _unschedule_logon_task(self) -> None:
        result = scheduler.remove_logon_task()
        self._log_to_console(result.message)
        if result.success:
            self.logger.success(result.message)
        else:
            self.logger.error(result.message)
        messagebox.showinfo("CorrecaoSistema", result.message)

    def _generate_report(self) -> None:
        if not self.logger.events:
            messagebox.showinfo("CorrecaoSistema", "Nenhum evento registrado nesta sessão ainda.")
            return
        try:
            path = generate_pdf_report(self.logger.events)
            self._log_to_console(f"Relatório salvo em: {path}")
            self.logger.success(f"Relatório PDF gerado: {path}")
            if messagebox.askyesno("CorrecaoSistema", f"Relatório salvo em:\n{path}\n\nAbrir agora?"):
                webbrowser.open(str(path))
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Falha ao gerar relatório: {exc}")
            messagebox.showerror("CorrecaoSistema", f"Falha ao gerar relatório: {exc}")


def run() -> None:
    app = App()
    app.mainloop()
