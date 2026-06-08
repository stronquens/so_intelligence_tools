from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from so_intelligence_tools.domain.errors import NoSelectionError, ToolRunnerError
from so_intelligence_tools.domain.models import ReasoningMode
from so_intelligence_tools.ports.clipboard import ClipboardPort
from so_intelligence_tools.ports.inference import InferencePort
from so_intelligence_tools.ports.notification import NotificationPort
from so_intelligence_tools.ports.text_insertion import TextInsertionPort
from so_intelligence_tools.ports.text_selection import TextSelectionPort


CORRECTION_SYSTEM_PROMPT = (
    "Corrige ortografía, gramática y puntuación del texto manteniendo el idioma original. "
    "Haz cambios mínimos, no traduzcas y no añadas explicación."
)


def correct_selected_text(
    *,
    inference: InferencePort,
    text_selection: TextSelectionPort,
    text_insertion: TextInsertionPort,
    notifications: NotificationPort,
    reasoning_mode: ReasoningMode = "off",
    debug_log_path: Path | None = None,
    fallback_clipboard: ClipboardPort | None = None,
) -> str:
    selected_text = text_selection.get_selected_text()
    if not selected_text or not selected_text.strip():
        _append_debug_log(
            debug_log_path,
            selected_text=selected_text,
            corrected_text=None,
            event="missing-selection",
        )
        notifications.notify(
            title="Sin texto seleccionado",
            body="Selecciona texto antes de ejecutar la corrección.",
            level="warning",
        )
        raise NoSelectionError("No hay texto seleccionado.")

    _append_debug_log(
        debug_log_path,
        selected_text=selected_text,
        corrected_text=None,
        event="captured-selection",
    )
    notifications.notify(
        title="Corrigiendo texto",
        body="Enviando selección al modelo local.",
        level="info",
    )
    result = inference.generate_text(
        prompt=selected_text,
        system_prompt=CORRECTION_SYSTEM_PROMPT,
        reasoning_mode=reasoning_mode,
        max_output_tokens=max(256, len(selected_text) * 2),
        temperature=0.0,
    )
    corrected_text = result.content.strip()
    _append_debug_log(
        debug_log_path,
        selected_text=selected_text,
        corrected_text=corrected_text,
        event="completed",
    )
    try:
        text_insertion.replace_selected_text(corrected_text)
    except ToolRunnerError:
        _append_debug_log(
            debug_log_path,
            selected_text=selected_text,
            corrected_text=corrected_text,
            event="insertion-failed",
        )
        if fallback_clipboard is None:
            raise
        fallback_clipboard.set_text(corrected_text)
        notifications.notify(
            title="Texto corregido en portapapeles",
            body="No se pudo pegar automáticamente. Usa Ctrl+V para insertarlo.",
            level="warning",
        )
        return corrected_text

    notifications.notify(
        title="Texto corregido",
        body="La corrección se ha completado correctamente.",
        level="success",
    )
    return corrected_text


def _append_debug_log(
    debug_log_path: Path | None,
    *,
    selected_text: str | None,
    corrected_text: str | None,
    event: str,
) -> None:
    if debug_log_path is None:
        return

    debug_log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with debug_log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(
            "\n".join(
                [
                    f"[{timestamp}] selected-text-correction {event}",
                    f"selected={selected_text!r}",
                    f"corrected={corrected_text!r}",
                    "",
                ]
            )
        )
