from __future__ import annotations

from dataclasses import dataclass, field

from so_intelligence_tools.domain.models import NotificationMessage, TextGenerationResult


class InlineTextSelectionAdapter:
    def __init__(self, text: str | None) -> None:
        self._text = text

    def get_selected_text(self) -> str | None:
        return self._text


class MemoryTextInsertionAdapter:
    def __init__(self) -> None:
        self.last_text: str | None = None

    def replace_selected_text(self, text: str) -> None:
        self.last_text = text


class MemoryClipboardAdapter:
    def __init__(self) -> None:
        self.last_text: str | None = None

    def set_text(self, text: str) -> None:
        self.last_text = text


@dataclass
class CollectingNotificationAdapter:
    messages: list[NotificationMessage] = field(default_factory=list)

    def notify(self, *, title: str, body: str, level: str = "info") -> None:
        self.messages.append(NotificationMessage(title=title, body=body, level=level))


class StaticImageScreenshotAdapter:
    def __init__(self, image_bytes: bytes) -> None:
        self._image_bytes = image_bytes

    def capture_region(self) -> bytes:
        return self._image_bytes


class FileScreenshotAdapter:
    def __init__(self, path: str) -> None:
        self._path = path

    def capture_region(self) -> bytes:
        with open(self._path, "rb") as handle:
            return handle.read()


class FakeInferenceAdapter:
    def __init__(
        self,
        *,
        text_response: str = "texto corregido",
        image_response: str = "texto extraido",
    ) -> None:
        self.text_response = text_response
        self.image_response = image_response
        self.last_text_prompt: str | None = None
        self.last_text_system_prompt: str | None = None
        self.last_image_bytes: bytes | None = None

    def generate_text(self, **kwargs) -> TextGenerationResult:
        self.last_text_prompt = kwargs["prompt"]
        self.last_text_system_prompt = kwargs.get("system_prompt")
        return TextGenerationResult(
            content=self.text_response,
            model="fake-model",
            reasoning_mode_requested=kwargs.get("reasoning_mode", "off"),
            reasoning_strategy_applied="thinking:off",
        )

    def extract_text_from_image(self, **kwargs) -> TextGenerationResult:
        self.last_image_bytes = kwargs["image_bytes"]
        return TextGenerationResult(
            content=self.image_response,
            model="fake-model",
            reasoning_mode_requested=kwargs.get("reasoning_mode", "off"),
            reasoning_strategy_applied="thinking:off",
        )
