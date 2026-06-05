from __future__ import annotations

from so_intelligence_tools.domain.models import ReasoningMode
from so_intelligence_tools.ports.clipboard import ClipboardPort
from so_intelligence_tools.ports.inference import InferencePort
from so_intelligence_tools.ports.notification import NotificationPort
from so_intelligence_tools.ports.screenshot import ScreenshotPort


IMAGE_OCR_PROMPT = "Extrae exactamente el texto visible en la imagen. No añadas explicación ni texto adicional."


def extract_text_from_image(
    *,
    inference: InferencePort,
    screenshot: ScreenshotPort,
    clipboard: ClipboardPort,
    notifications: NotificationPort,
    reasoning_mode: ReasoningMode = "off",
) -> str:
    image_bytes = screenshot.capture_region()
    result = inference.extract_text_from_image(
        image_bytes=image_bytes,
        prompt=IMAGE_OCR_PROMPT,
        reasoning_mode=reasoning_mode,
        max_output_tokens=256,
        temperature=0.0,
    )
    extracted_text = result.content.strip()
    clipboard.set_text(extracted_text)
    notifications.notify(
        title="Texto copiado",
        body="El texto extraído se ha copiado al portapapeles.",
        level="success",
    )
    return extracted_text
