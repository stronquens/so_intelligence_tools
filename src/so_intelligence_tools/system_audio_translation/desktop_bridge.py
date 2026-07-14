from __future__ import annotations

from collections.abc import Callable
import json
import sys
import threading
from typing import IO, Any

from so_intelligence_tools.domain.models import (
    LivePartialUpdate,
    LiveSessionState,
    SystemAudioSessionMode,
    TranscriptBlock,
)
from so_intelligence_tools.infrastructure.config import (
    ToolRunnerSettings,
    get_tool_runner_settings,
)
from so_intelligence_tools.system_audio_translation.app import (
    ModeAwareSystemAudioTranslationApp,
)
from so_intelligence_tools.system_audio_translation.modes import (
    SYSTEM_AUDIO_MODE_LABELS,
    normalize_system_audio_mode,
)


class JsonLineEventWriter:
    def __init__(self, output: IO[str]) -> None:
        self._output = output
        self._lock = threading.Lock()

    def publish(self, event: dict[str, object]) -> None:
        payload = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            self._output.write(f"{payload}\n")
            self._output.flush()


class DesktopTranslationBridgeWindow:
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
        on_languages_changed: Callable[[str, str], None],
        input_stream: IO[str] | None = None,
        output_stream: IO[str] | None = None,
    ) -> None:
        self.title = title
        self._mode = initial_mode
        self._on_pause = on_pause
        self._on_resume = on_resume
        self._on_reset = on_reset
        self._on_close = on_close
        self._on_mode_changed = on_mode_changed
        self._on_voice_translation_toggle = on_voice_translation_toggle
        self._on_languages_changed = on_languages_changed
        self._input = input_stream or sys.stdin
        self._writer = JsonLineEventWriter(output_stream or sys.stdout)
        self._closed = threading.Event()
        self._close_lock = threading.Lock()
        self._block_sequence = 0

    def run(self) -> None:
        self.set_mode(self._mode)
        command_thread = threading.Thread(
            target=self._read_commands,
            daemon=True,
            name="desktop-translation-command-reader",
        )
        command_thread.start()
        self._closed.wait()

    def set_state(self, state: LiveSessionState, message: str) -> None:
        self._writer.publish(
            {"type": "session_state", "state": state, "message": message}
        )

    def add_block(self, block: TranscriptBlock) -> None:
        self._block_sequence += 1
        event: dict[str, object] = {
            "type": "block",
            "id": f"{block.timestamp.isoformat()}-{self._block_sequence}",
            "translatedText": block.translated_text,
            "timestamp": block.timestamp.strftime("%H:%M:%S"),
        }
        if block.original_text is not None:
            event["sourceText"] = block.original_text
        if block.speaker_label is not None:
            event["speakerLabel"] = block.speaker_label
        self._writer.publish(event)

    def set_partial_text(self, update: LivePartialUpdate | str) -> None:
        if isinstance(update, str):
            update = LivePartialUpdate(kind="translation", text=update)
        self._writer.publish(
            {
                "type": "partial",
                "kind": update.kind,
                "text": update.text,
            }
        )

    def set_mode(self, mode: SystemAudioSessionMode) -> None:
        self._mode = mode
        self._writer.publish({"type": "mode", "mode": mode})

    def set_voice_translation_state(
        self, active: bool, message: str, state: str | None = None
    ) -> None:
        event: dict[str, object] = {
            "type": "voice_translation_state",
            "active": active,
            "message": message,
        }
        if state is not None:
            event["state"] = state
        self._writer.publish(event)

    def set_voice_translation_output(self, chunks: int, byte_count: int) -> None:
        self._writer.publish(
            {
                "type": "voice_translation_output",
                "chunks": max(int(chunks), 0),
                "bytes": max(int(byte_count), 0),
            }
        )

    def set_audio_level(self, level: float, source: str = "system") -> None:
        self._writer.publish(
            {
                "type": "audio_level",
                "source": source,
                "level": min(max(float(level), 0.0), 1.0),
            }
        )

    def set_session_config(
        self,
        source_language: str,
        target_language: str,
        languages: list[dict[str, str]],
    ) -> None:
        self._writer.publish(
            {
                "type": "session_config",
                "sourceLanguage": source_language,
                "targetLanguage": target_language,
                "languages": languages,
            }
        )

    def close_from_controller(self) -> None:
        self._closed.set()

    def _read_commands(self) -> None:
        try:
            for raw_line in self._input:
                if self._closed.is_set():
                    return
                line = raw_line.strip()
                if not line:
                    continue
                self._handle_command_line(line)
        finally:
            self._close_session()

    def _handle_command_line(self, line: str) -> None:
        try:
            command = json.loads(line)
        except json.JSONDecodeError as exc:
            self._publish_error(f"Comando JSON no valido: {exc.msg}")
            return
        if not isinstance(command, dict):
            self._publish_error("El comando debe ser un objeto JSON.")
            return
        self._dispatch_command(command)

    def _dispatch_command(self, command: dict[str, Any]) -> None:
        command_type = command.get("type")
        if command_type == "pause":
            self._on_pause()
            return
        if command_type == "resume":
            self._on_resume()
            return
        if command_type == "reset":
            self._on_reset()
            return
        if command_type == "toggle_voice_translation":
            self._on_voice_translation_toggle()
            return
        if command_type == "change_mode":
            mode = command.get("mode")
            if not isinstance(mode, str) or mode not in SYSTEM_AUDIO_MODE_LABELS:
                self._publish_error(f"Modo de traduccion no valido: {mode}")
                return
            canonical = normalize_system_audio_mode(mode)
            self._on_mode_changed(canonical)
            return
        if command_type == "change_languages":
            source_language = command.get("sourceLanguage")
            target_language = command.get("targetLanguage")
            if not isinstance(source_language, str) or not isinstance(
                target_language, str
            ):
                self._publish_error("Los idiomas deben ser codigos de texto validos.")
                return
            self._on_languages_changed(source_language, target_language)
            return
        if command_type == "stop":
            self._close_session()
            return
        self._publish_error(f"Comando no soportado: {command_type}")

    def _publish_error(self, message: str) -> None:
        self._writer.publish({"type": "error", "message": message})

    def _close_session(self) -> None:
        with self._close_lock:
            if self._closed.is_set():
                return
            try:
                self._on_close()
            finally:
                self._closed.set()


def run_system_audio_translation_desktop_bridge(
    settings: ToolRunnerSettings | None = None,
    *,
    input_stream: IO[str] | None = None,
    output_stream: IO[str] | None = None,
) -> None:
    runtime_settings = settings or get_tool_runner_settings()

    def window_factory(**kwargs: object) -> DesktopTranslationBridgeWindow:
        return DesktopTranslationBridgeWindow(
            **kwargs,
            input_stream=input_stream,
            output_stream=output_stream,
        )

    app = ModeAwareSystemAudioTranslationApp(
        runtime_settings,
        window_factory=window_factory,
    )
    app.run()
