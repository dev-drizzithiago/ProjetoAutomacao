"""Interface gráfica moderna (customtkinter) do pointRestaurations."""

from __future__ import annotations

import threading
from datetime import datetime

import customtkinter as ctk

from pointRestaurations.elevation import is_admin
from pointRestaurations.logger import log_event, read_recent_logs
from pointRestaurations.restore_point import create_restore_point
from pointRestaurations.scheduler import install_logon_task, remove_logon_task, task_exists

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class PointRestaurationsApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("pointRestaurations")
        self.geometry("640x520")
        self.minsize(560, 460)

        self._build_layout()
        self._refresh_status()
        self._refresh_log_view()

    # ---------- Layout ----------

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="pointRestaurations", font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        self.admin_badge = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=13), corner_radius=8, padx=10, pady=4
        )
        self.admin_badge.grid(row=0, column=1, sticky="e")

        actions = ctk.CTkFrame(self)
        actions.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        actions.grid_columnconfigure((0, 1, 2), weight=1)

        self.create_btn = ctk.CTkButton(
            actions, text="Criar Ponto de Restauração Agora", command=self._on_create_clicked
        )
        self.create_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.install_task_btn = ctk.CTkButton(
            actions, text="Instalar Tarefa no Logon", command=self._on_install_task_clicked
        )
        self.install_task_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.remove_task_btn = ctk.CTkButton(
            actions, text="Remover Tarefa", fg_color="#7f1d1d", hover_color="#991b1b",
            command=self._on_remove_task_clicked,
        )
        self.remove_task_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Pronto.", font=ctk.CTkFont(size=13))
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame, text="Histórico de Execução", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.log_box = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.log_box.configure(state="disabled")

    # ---------- Estado ----------

    def _refresh_status(self) -> None:
        if is_admin():
            self.admin_badge.configure(text="Administrador", fg_color="#166534", text_color="white")
        else:
            self.admin_badge.configure(text="Sem privilégios de Admin", fg_color="#7f1d1d", text_color="white")
            self.create_btn.configure(state="disabled")
            self.install_task_btn.configure(state="disabled")
            self.remove_task_btn.configure(state="disabled")

    def _refresh_log_view(self) -> None:
        entries = read_recent_logs(max_entries=200)
        lines = [
            f"[{e['timestamp']}] {e['level']:<8} {e['message']}"
            for e in entries
        ]
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "\n".join(lines) if lines else "Nenhum registro para hoje.")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    # ---------- Ações ----------

    def _run_async(self, target) -> None:
        threading.Thread(target=target, daemon=True).start()

    def _on_create_clicked(self) -> None:
        self.create_btn.configure(state="disabled", text="Criando...")
        self._set_status("Criando ponto de restauração...")

        def task() -> None:
            result = create_restore_point()
            self.after(0, lambda: self._on_create_finished(result))

        self._run_async(task)

    def _on_create_finished(self, result) -> None:
        self.create_btn.configure(state="normal", text="Criar Ponto de Restauração Agora")
        self._set_status(result.message)
        self._refresh_log_view()

    def _on_install_task_clicked(self) -> None:
        result = install_logon_task()
        self._set_status(result.message)
        self._refresh_log_view()

    def _on_remove_task_clicked(self) -> None:
        result = remove_logon_task()
        self._set_status(result.message)
        self._refresh_log_view()


def run_gui() -> None:
    app = PointRestaurationsApp()
    app.mainloop()
