"""Tooltip simples para widgets customtkinter (biblioteca não inclui um nativo)."""
from __future__ import annotations

import customtkinter as ctk


class CTkToolTip:
    """Exibe um balão de texto explicativo ao passar o mouse sobre um widget."""

    def __init__(self, widget: ctk.CTkBaseClass, text: str, delay_ms: int = 400) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id: str | None = None
        self._tooltip_window: ctk.CTkToplevel | None = None

        self._bind_recursive(widget)

    def _bind_recursive(self, widget: ctk.CTkBaseClass) -> None:
        # Alguns widgets compostos do customtkinter (ex.: CTkSegmentedButton)
        # não implementam bind() diretamente e lançam NotImplementedError.
        # Nesse caso, o tooltip é aplicado recursivamente aos widgets internos.
        try:
            widget.bind("<Enter>", self._schedule, add="+")
            widget.bind("<Leave>", self._hide, add="+")
            widget.bind("<ButtonPress>", self._hide, add="+")
        except NotImplementedError:
            for child in widget.winfo_children():
                self._bind_recursive(child)

    def _schedule(self, _event: object = None) -> None:
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self) -> None:
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self) -> None:
        if self._tooltip_window is not None or not self.text:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self._tooltip_window = ctk.CTkToplevel(self.widget)
        self._tooltip_window.wm_overrideredirect(True)
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
        self._tooltip_window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            self._tooltip_window,
            text=self.text,
            fg_color=("#2b2b2b", "#1a1a1a"),
            text_color="white",
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            padx=8,
            pady=4,
            wraplength=280,
            justify="left",
        )
        label.pack()

    def _hide(self, _event: object = None) -> None:
        self._cancel()
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
            self._tooltip_window = None
