from __future__ import annotations

import queue
import tkinter as tk
from tkinter import ttk
from collections.abc import Callable

from so_intelligence_tools.domain.models import LivePartialUpdate, LiveSessionState, TranscriptBlock
from so_intelligence_tools.domain.models import SystemAudioSessionMode
from so_intelligence_tools.system_audio_translation.modes import SYSTEM_AUDIO_MODE_LABELS


class SystemAudioTranslationWindow:
    def __init__(
        self,
        *,
        title: str,
        initial_mode: SystemAudioSessionMode,
        on_pause: Callable[[], None],
        on_resume: Callable[[], None],
        on_reset: Callable[[], None],
        on_close: Callable[[], None],
        on_mode_changed: Callable[[SystemAudioSessionMode], None],
        on_voice_translation_toggle: Callable[[], None],
    ) -> None:
        self._on_pause = on_pause
        self._on_resume = on_resume
        self._on_reset = on_reset
        self._on_close = on_close
        self._on_mode_changed = on_mode_changed
        self._on_voice_translation_toggle = on_voice_translation_toggle
        self._ui_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._closed = False
        self._mode_value_to_label = dict(SYSTEM_AUDIO_MODE_LABELS)
        self._mode_label_to_value = {
            label: value for value, label in self._mode_value_to_label.items()
        }
        self._mode_change_suspended = False

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("920x620")
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

        self.status_var = tk.StringVar(value="Preparando sesión…")
        self.state_var = tk.StringVar(value="inactive")
        self.voice_translation_status_var = tk.StringVar(
            value="Micrófono traducido: apagado"
        )

        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)
        ttk.Label(top, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Label(top, textvariable=self.state_var).pack(side=tk.RIGHT)

        controls = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        controls.pack(fill=tk.X)
        ttk.Label(controls, text="Modo").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value=self._mode_value_to_label[initial_mode])
        self.mode_combobox = ttk.Combobox(
            controls,
            textvariable=self.mode_var,
            values=list(self._mode_label_to_value.keys()),
            state="readonly",
            width=34,
        )
        self.mode_combobox.pack(side=tk.LEFT, padx=(8, 12))
        self.mode_combobox.bind("<<ComboboxSelected>>", self._handle_mode_selected)
        self.pause_button = ttk.Button(controls, text="Pausar", command=self._on_pause)
        self.resume_button = ttk.Button(controls, text="Reanudar", command=self._on_resume)
        self.reset_button = ttk.Button(controls, text="Reset", command=self._on_reset)
        self.voice_translation_button = ttk.Button(
            controls,
            text="Activar mi voz traducida",
            command=self._on_voice_translation_toggle,
        )
        self.close_button = ttk.Button(controls, text="Cerrar", command=self._handle_close)
        self.pause_button.pack(side=tk.LEFT)
        self.resume_button.pack(side=tk.LEFT, padx=(8, 0))
        self.reset_button.pack(side=tk.LEFT, padx=(8, 0))
        self.voice_translation_button.pack(side=tk.LEFT, padx=(8, 0))
        self.close_button.pack(side=tk.RIGHT)

        voice_status = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        voice_status.pack(fill=tk.X)
        ttk.Label(voice_status, textvariable=self.voice_translation_status_var).pack(
            side=tk.LEFT
        )

        live_frame = ttk.LabelFrame(self.root, text="En vivo", padding=8)
        live_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        live_grid = ttk.Frame(live_frame)
        live_grid.pack(fill=tk.X)
        live_grid.columnconfigure(0, weight=1)
        live_grid.columnconfigure(1, weight=1)

        self.original_live_var = tk.StringVar(value="")
        self.translation_live_var = tk.StringVar(value="")
        ttk.Label(live_grid, text="Original EN", font=("Sans", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4)
        )
        ttk.Label(live_grid, text="Traduccion ES", font=("Sans", 10, "bold")).grid(
            row=0, column=1, sticky="w", pady=(0, 4)
        )
        self.original_live_label = tk.Label(
            live_grid,
            textvariable=self.original_live_var,
            wraplength=400,
            justify=tk.LEFT,
            anchor="nw",
            bg="#eff6ff",
            fg="#1e3a8a",
            font=("Sans", 12),
            padx=14,
            pady=12,
            relief=tk.FLAT,
        )
        self.original_live_label.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.translation_live_label = tk.Label(
            live_grid,
            textvariable=self.translation_live_var,
            wraplength=400,
            justify=tk.LEFT,
            anchor="nw",
            bg="#f0fdf4",
            fg="#166534",
            font=("Sans", 12, "bold"),
            padx=14,
            pady=12,
            relief=tk.FLAT,
        )
        self.translation_live_label.grid(row=1, column=1, sticky="nsew")

        history_frame = ttk.LabelFrame(self.root, text="Traduccion en vivo", padding=8)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        body = ttk.Frame(history_frame)
        body.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(body)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text = tk.Text(
            body,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            font=("Sans", 12),
            background="#f8fafc",
            borderwidth=0,
            padx=10,
            pady=10,
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_text.yview)
        self._configure_history_tags()

        self.root.after(80, self._pump_events)

    def run(self) -> None:
        self.root.mainloop()

    def set_state(self, state: LiveSessionState, message: str) -> None:
        self._ui_queue.put(("state", (state, message)))

    def add_block(self, block: TranscriptBlock) -> None:
        self._ui_queue.put(("block", block))

    def set_partial_text(self, update: LivePartialUpdate | str) -> None:
        if isinstance(update, str):
            update = LivePartialUpdate(kind="translation", text=update)
        self._ui_queue.put(("partial", update))

    def set_mode(self, mode: SystemAudioSessionMode) -> None:
        self._ui_queue.put(("mode", mode))

    def set_voice_translation_state(self, active: bool, message: str) -> None:
        self._ui_queue.put(("voice_translation", (active, message)))

    def close_from_controller(self) -> None:
        self._ui_queue.put(("close", None))

    def _pump_events(self) -> None:
        while True:
            try:
                kind, payload = self._ui_queue.get_nowait()
            except queue.Empty:
                break
            if kind == "state":
                state, message = payload  # type: ignore[misc]
                self.state_var.set(state)
                self.status_var.set(message)
                self._sync_buttons(state)
            elif kind == "block":
                self._append_block(payload)  # type: ignore[arg-type]
            elif kind == "partial":
                self._render_partial_text(payload)  # type: ignore[arg-type]
            elif kind == "mode":
                self._apply_mode(payload)  # type: ignore[arg-type]
            elif kind == "voice_translation":
                active, message = payload  # type: ignore[misc]
                self._apply_voice_translation_state(active=active, message=message)
            elif kind == "close":
                self._destroy_window()
        if not self._closed:
            self.root.after(80, self._pump_events)

    def _append_block(self, block: TranscriptBlock) -> None:
        speaker = f"[{block.speaker_label}] " if block.speaker_label else ""
        original_text = block.original_text or "—"
        self.original_live_var.set("")
        self.translation_live_var.set("")
        self._append_history_block(
            speaker=speaker,
            original_text=original_text,
            translated_text=block.translated_text,
        )

    def _render_partial_text(self, update: LivePartialUpdate) -> None:
        clean_text = update.text.strip()
        if update.kind == "original":
            self.original_live_var.set(clean_text)
        else:
            self.translation_live_var.set(clean_text)

    def _configure_history_tags(self) -> None:
        self.history_text.tag_configure(
            "original_label",
            foreground="#1d4ed8",
            font=("Sans", 9, "bold"),
            lmargin1=14,
            lmargin2=14,
        )
        self.history_text.tag_configure(
            "original_bubble",
            background="#dbeafe",
            foreground="#0f172a",
            font=("Sans", 12),
            lmargin1=14,
            lmargin2=54,
            rmargin=18,
            spacing1=4,
            spacing3=8,
        )
        self.history_text.tag_configure(
            "translation_label",
            foreground="#16a34a",
            font=("Sans", 9, "bold"),
            lmargin1=14,
            lmargin2=14,
        )
        self.history_text.tag_configure(
            "translation_bubble",
            background="#dcfce7",
            foreground="#052e16",
            font=("Sans", 12),
            lmargin1=14,
            lmargin2=54,
            rmargin=18,
            spacing1=4,
            spacing3=10,
        )
        self.history_text.tag_configure(
            "block_separator",
            foreground="#cbd5e1",
            font=("Sans", 8),
            spacing3=8,
        )
    def _append_history_block(
        self,
        *,
        speaker: str,
        original_text: str,
        translated_text: str,
    ) -> None:
        self.history_text.configure(state=tk.NORMAL)
        self.history_text.insert(tk.END, "ORIGINAL EN\n", ("original_label",))
        self.history_text.insert(
            tk.END,
            f"{speaker}{original_text}\n",
            ("original_bubble",),
        )
        self.history_text.insert(tk.END, "TRADUCCION ES\n", ("translation_label",))
        self.history_text.insert(
            tk.END,
            f"{speaker}{translated_text}\n",
            ("translation_bubble",),
        )
        self.history_text.insert(tk.END, "─" * 72 + "\n", ("block_separator",))
        self.history_text.configure(state=tk.DISABLED)
        self.history_text.see(tk.END)

    def _sync_buttons(self, state: LiveSessionState) -> None:
        self.pause_button.state(["!disabled"] if state in {"active", "reconnecting"} else ["disabled"])
        self.resume_button.state(["!disabled"] if state == "paused" else ["disabled"])
        self.reset_button.state(["!disabled"] if state in {"error", "reconnecting", "paused"} else ["disabled"])

    def _handle_mode_selected(self, _event: object) -> None:
        if self._mode_change_suspended:
            return
        label = self.mode_var.get()
        mode = self._mode_label_to_value.get(label)
        if mode is not None:
            self._on_mode_changed(mode)

    def _apply_mode(self, mode: SystemAudioSessionMode) -> None:
        label = self._mode_value_to_label[mode]
        self._mode_change_suspended = True
        try:
            self.mode_var.set(label)
        finally:
            self._mode_change_suspended = False

    def _apply_voice_translation_state(self, *, active: bool, message: str) -> None:
        self.voice_translation_status_var.set(message)
        self.voice_translation_button.configure(
            text="Desactivar mi voz traducida" if active else "Activar mi voz traducida"
        )

    def _handle_close(self) -> None:
        self._on_close()
        self._destroy_window()

    def _destroy_window(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.root.after_idle(self.root.destroy)
