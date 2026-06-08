from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

from so_intelligence_tools.system_audio_translation.openai_realtime import (
    OpenAIRealtimeTranslationController,
    _clean_transcript_text,
)
from so_intelligence_tools.system_audio_translation.session import TranscriptSessionLogger


class FakeCapture:
    def start(self, callback):  # noqa: ANN001
        self.callback = callback

    def stop(self) -> None:
        return None


class FakeConnection:
    def __init__(self, events: list[object]) -> None:
        self._events = events

    def __aiter__(self):
        self._iter = iter(self._events)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class FakeTextTranslationController(OpenAIRealtimeTranslationController):
    async def _translate_text(self, text: str) -> str:
        return f"ES:{text}"


def test_openai_realtime_controller_receiver_streams_partial_and_final(tmp_path: Path):
    controller = FakeTextTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="en",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    partials: list[tuple[str, str]] = []
    blocks: list[str] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append(block.translated_text),
        on_partial_text_changed=lambda update: partials.append((update.kind, update.text)),
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-1")),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="Hello team",
        ),
        SimpleNamespace(type="response.output_text.delta", delta="Hola"),
        SimpleNamespace(type="response.output_text.delta", delta=" equipo"),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Hola equipo",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert ("original", "Hello team") in partials
    assert ("translation", "Hola") in partials
    assert ("translation", "Hola equipo") in partials
    assert partials[-2:] == [("original", ""), ("translation", "")]
    assert blocks == ["Hola equipo"]


def test_openai_realtime_controller_reports_input_audio_transcription_delta(tmp_path: Path):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    partials: list[tuple[str, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: None,
        on_partial_text_changed=lambda update: partials.append((update.kind, update.text)),
    )

    events = [
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="Hello",
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta=" team",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert partials[:2] == [("original", "Hello"), ("original", "Hello team")]
    assert partials[-2:] == [("original", ""), ("translation", "")]


def test_openai_realtime_controller_adds_original_text_to_final_block(tmp_path: Path):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append((block.original_text, block.translated_text)),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="Hello team",
        ),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-1")),
        SimpleNamespace(type="response.output_text.delta", delta="Hola equipo"),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Hola equipo",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [("Hello team", "Hola equipo")]


def test_openai_realtime_controller_uses_partial_original_when_translation_finishes_first(
    tmp_path: Path,
):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append((block.original_text, block.translated_text)),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="Please let me know if you have any",
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta=" questions before we finish the meeting",
        ),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-1")),
        SimpleNamespace(type="response.output_text.delta", delta="Por favor, dime si tienes"),
        SimpleNamespace(type="response.output_text.delta", delta=" alguna pregunta."),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Por favor, dime si tienes alguna pregunta.",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [
        (
            "Please let me know if you have any questions before we finish the meeting",
            "Por favor, dime si tienes alguna pregunta.",
        )
    ]


def test_openai_realtime_controller_keeps_longer_partial_when_completed_is_shorter(
    tmp_path: Path,
):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append((block.original_text, block.translated_text)),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="We are reviewing the product timeline and the next release milestones",
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="We are reviewing the product timeline",
        ),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-1")),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Estamos revisando el calendario del producto y los proximos hitos.",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [
        (
            "We are reviewing the product timeline and the next release milestones",
            "Estamos revisando el calendario del producto y los proximos hitos.",
        )
    ]


def test_openai_realtime_controller_ignores_late_completed_text_already_emitted(
    tmp_path: Path,
):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append((block.original_text, block.translated_text)),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="The fantastic my God there's a million of them.",
        ),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-1")),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Hay un millon de ellos.",
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="The fantastic my God there's a million of them.",
        ),
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-2"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-2",
            delta=" They are all enmeshed in that never ending battle.",
        ),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-2")),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-2",
            text="Todos estan envueltos en esa batalla interminable.",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [
        (
            "The fantastic my God there's a million of them.",
            "Hay un millon de ellos.",
        ),
        (
            "They are all enmeshed in that never ending battle.",
            "Todos estan envueltos en esa batalla interminable.",
        ),
    ]


def test_openai_realtime_controller_session_config_does_not_interrupt_responses(
    tmp_path: Path,
):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )

    payload = controller._build_session_update_payload()
    session = payload["session"]
    audio = session["audio"]  # type: ignore[index]
    input_config = audio["input"]  # type: ignore[index]
    turn_detection = input_config["turn_detection"]  # type: ignore[index]

    assert turn_detection["type"] == "server_vad"
    assert turn_detection["create_response"] is True
    assert turn_detection["interrupt_response"] is False
    assert session["max_output_tokens"] == 1024  # type: ignore[index]


def test_openai_realtime_controller_transcript_translation_mode_disables_realtime_responses(
    tmp_path: Path,
):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
        translate_completed_transcripts=True,
    )

    payload = controller._build_session_update_payload()
    session = payload["session"]
    audio = session["audio"]  # type: ignore[index]
    input_config = audio["input"]  # type: ignore[index]
    turn_detection = input_config["turn_detection"]  # type: ignore[index]

    assert turn_detection["type"] == "server_vad"
    assert turn_detection["create_response"] is False


def test_openai_realtime_controller_merges_incomplete_transcripts_before_translation(
    tmp_path: Path,
):
    controller = FakeTextTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
        translate_completed_transcripts=True,
    )

    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append((block.original_text, block.translated_text)),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="He filled out the form for his name and age, but when it came to his race he wrote",
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-2",
            transcript="human",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [
        (
            "He filled out the form for his name and age, but when it came to his race he wrote human",
            "ES:He filled out the form for his name and age, but when it came to his race he wrote human",
        )
    ]


def test_clean_transcript_text_removes_duplicate_punctuation():
    assert (
        _clean_transcript_text(
            "Whatever type of fishing you do, the equipment is similar.. In addition"
        )
        == "Whatever type of fishing you do, the equipment is similar. In addition"
    )


def test_openai_realtime_controller_flushes_residual_partial_turn_on_stream_end(
    tmp_path: Path,
):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
        translate_completed_transcripts=False,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append((block.original_text, block.translated_text)),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(type="response.created", response=SimpleNamespace(id="response-1")),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="told me that when he was a young man",
        ),
        SimpleNamespace(
            type="response.output_text.delta",
            response_id="response-1",
            delta="Me dijo que cuando era joven.",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [
        (
            "told me that when he was a young man",
            "Me dijo que cuando era joven.",
        )
    ]


def test_openai_realtime_controller_omits_language_for_auto_source(tmp_path: Path):
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )

    assert "language" not in controller._build_transcription_config()
