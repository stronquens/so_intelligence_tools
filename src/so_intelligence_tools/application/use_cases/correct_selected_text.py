from __future__ import annotations

from so_intelligence_tools.domain.errors import NoSelectionError
from so_intelligence_tools.domain.models import ReasoningMode
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
) -> str:
    selected_text = text_selection.get_selected_text()
    if not selected_text or not selected_text.strip():
        notifications.notify(
            title="Sin texto seleccionado",
            body="Selecciona texto antes de ejecutar la corrección.",
            level="warning",
        )
        raise NoSelectionError("No hay texto seleccionado.")

    result = inference.generate_text(
        prompt=selected_text,
        system_prompt=CORRECTION_SYSTEM_PROMPT,
        reasoning_mode=reasoning_mode,
        max_output_tokens=max(256, len(selected_text) * 2),
        temperature=0.0,
    )
    corrected_text = result.content.strip()
    text_insertion.replace_selected_text(corrected_text)
    notifications.notify(
        title="Texto corregido",
        body="La corrección se ha completado correctamente.",
        level="success",
    )
    return corrected_text
