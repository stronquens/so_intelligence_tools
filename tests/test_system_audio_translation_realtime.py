from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace

from so_intelligence_tools.system_audio_translation.openai_realtime import (
    OpenAIRealtimeTranslationController,
    _clean_transcript_text,
)
from so_intelligence_tools.system_audio_translation.session import (
    TranscriptSessionLogger,
)


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


class BlockingFakeConnection(FakeConnection):
    def __init__(self, events: list[object], exhausted: asyncio.Event) -> None:
        super().__init__(events)
        self._exhausted = exhausted

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            self._exhausted.set()
            await asyncio.Event().wait()


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
        on_partial_text_changed=lambda update: partials.append(
            (update.kind, update.text)
        ),
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
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


def test_openai_realtime_controller_reports_input_audio_transcription_delta(
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
    partials: list[tuple[str, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: None,
        on_partial_text_changed=lambda update: partials.append(
            (update.kind, update.text)
        ),
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="Hello team",
        ),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
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
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
        SimpleNamespace(
            type="response.output_text.delta", delta="Por favor, dime si tienes"
        ),
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
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
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="The fantastic my God there's a million of them.",
        ),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
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
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-2")
        ),
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
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


def test_completed_transcript_mode_translates_short_residual_on_normal_stream_end(
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )
    events = [
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="Short fragment",
        )
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [("Short fragment", "ES:Short fragment")]


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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )

    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
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


def test_complete_later_turn_is_not_blocked_by_translation_only_earlier_turn(
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )
    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Exactamente.",
        ),
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-2"),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-2")
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-2",
            transcript="This second turn is complete.",
        ),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-2",
            text="Este segundo turno está completo.",
        ),
    ]

    async def run_live_receiver() -> list[tuple[str | None, str]]:
        exhausted = asyncio.Event()
        task = asyncio.create_task(
            controller._receiver_loop(BlockingFakeConnection(events, exhausted))
        )
        await asyncio.wait_for(exhausted.wait(), timeout=1.0)
        assert blocks == [
            ("This second turn is complete.", "Este segundo turno está completo.")
        ]
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return blocks

    final_blocks = asyncio.run(run_live_receiver())

    assert final_blocks == [
        ("This second turn is complete.", "Este segundo turno está completo."),
        (None, "Exactamente."),
    ]


def test_receiver_cancellation_flushes_complete_partial_turn(tmp_path: Path):
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )
    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.delta",
            item_id="input-1",
            delta="Pending original",
        ),
        SimpleNamespace(
            type="response.output_text.delta",
            response_id="response-1",
            delta="Traducción pendiente",
        ),
    ]

    async def cancel_live_receiver() -> None:
        exhausted = asyncio.Event()
        task = asyncio.create_task(
            controller._receiver_loop(BlockingFakeConnection(events, exhausted))
        )
        await asyncio.wait_for(exhausted.wait(), timeout=1.0)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    asyncio.run(cancel_live_receiver())

    assert blocks == [("Pending original", "Traducción pendiente")]


def test_stream_end_publishes_translation_only_residual_and_logs_fallback(
    tmp_path: Path,
):
    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=logger,
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )
    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="response.created", response=SimpleNamespace(id="response-1")
        ),
        SimpleNamespace(
            type="response.output_text.done",
            response_id="response-1",
            text="Traducción sin original.",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))
    log_path = logger.write_session(controller.history)

    assert blocks == [(None, "Traducción sin original.")]
    assert log_path is not None
    content = log_path.read_text(encoding="utf-8")
    assert '"type": "residual_block_published"' in content
    assert '"translation_only": true' in content


def test_stream_end_logs_original_only_residual_without_publishing_block(
    tmp_path: Path,
):
    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=logger,
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
    )
    blocks: list[tuple[str | None, str]] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: None,
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )
    events = [
        SimpleNamespace(type="input_audio_buffer.committed", item_id="input-1"),
        SimpleNamespace(
            type="conversation.item.input_audio_transcription.completed",
            item_id="input-1",
            transcript="Original without a translation.",
        ),
    ]

    asyncio.run(controller._receiver_loop(FakeConnection(events)))
    log_path = logger.write_session(controller.history)

    assert blocks == []
    assert log_path is not None
    content = log_path.read_text(encoding="utf-8")
    assert '"type": "residual_original_without_translation"' in content
    assert "Original without a translation." in content


def test_distinct_turns_with_identical_translation_are_both_published(tmp_path: Path):
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
        on_block_ready=lambda block: blocks.append(
            (block.original_text, block.translated_text)
        ),
        on_partial_text_changed=lambda update: None,
    )
    events: list[object] = []
    for number, original in ((1, "Yes"), (2, "Yeah")):
        events.extend(
            [
                SimpleNamespace(
                    type="input_audio_buffer.committed", item_id=f"input-{number}"
                ),
                SimpleNamespace(
                    type="response.created",
                    response=SimpleNamespace(id=f"response-{number}"),
                ),
                SimpleNamespace(
                    type="conversation.item.input_audio_transcription.completed",
                    item_id=f"input-{number}",
                    transcript=original,
                ),
                SimpleNamespace(
                    type="response.output_text.done",
                    response_id=f"response-{number}",
                    text="Sí.",
                ),
            ]
        )

    asyncio.run(controller._receiver_loop(FakeConnection(events)))

    assert blocks == [("Yes", "Sí."), ("Yeah", "Sí.")]


def test_realtime_audio_queue_logs_cumulative_overflow(tmp_path: Path):
    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    controller = OpenAIRealtimeTranslationController(
        capture=FakeCapture(),
        session_logger=logger,
        api_key="test-key",
        model="gpt-realtime",
        source_language="auto",
        target_language="es",
        reconnect_backoff_seconds=0.01,
        max_pending_audio_chunks=1,
    )
    controller.state = "active"

    controller._on_audio_chunk(b"first")
    controller._on_audio_chunk(b"second")
    controller._on_audio_chunk(b"third")
    log_path = logger.write_session([])

    assert list(controller._pending_audio) == [b"third"]
    assert log_path is not None
    content = log_path.read_text(encoding="utf-8")
    assert '"dropped_chunks": 1' in content
    assert '"dropped_chunks": 2' in content


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
