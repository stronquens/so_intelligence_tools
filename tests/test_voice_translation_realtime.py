from __future__ import annotations

import base64
import json
from pathlib import Path
from types import SimpleNamespace

from so_intelligence_tools.system_audio_translation.session import TranscriptSessionLogger
from so_intelligence_tools.voice_translation_virtual_microphone.audio import (
    LinuxMicrophoneAudioCapture,
    PulseAudioVirtualMicrophone,
)
from so_intelligence_tools.voice_translation_virtual_microphone.openai_realtime import (
    OpenAIRealtimeVoiceTranslationController,
    _decode_audio_delta,
    _normalize_translation_language,
)


def make_controller(tmp_path: Path) -> OpenAIRealtimeVoiceTranslationController:
    return OpenAIRealtimeVoiceTranslationController(
        capture=LinuxMicrophoneAudioCapture(sample_rate_hz=24000, chunk_ms=80),
        virtual_microphone=PulseAudioVirtualMicrophone(
            sink_name="so_ai_test_mic",
            sample_rate_hz=24000,
        ),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        api_key="test-key",
        model="gpt-realtime-translate",
        source_language="Spanish",
        target_language="English",
        voice="marin",
        reconnect_backoff_seconds=2,
        output_volume=1.0,
    )


def test_controller_can_leave_session_log_ownership_to_pipeline(tmp_path):
    controller = make_controller(tmp_path)
    controller.write_session_log_on_stop = False
    controller.state = "active"

    controller.stop()

    assert controller.last_log_path is None


def test_decode_audio_delta_accepts_ga_and_legacy_names():
    encoded = base64.b64encode(b"pcm").decode("ascii")

    assert _decode_audio_delta(SimpleNamespace(delta=encoded)) == b"pcm"
    assert _decode_audio_delta({"delta": encoded}) == b"pcm"
    assert _decode_audio_delta(SimpleNamespace(audio=encoded)) == b"pcm"
    assert _decode_audio_delta(SimpleNamespace(delta="")) == b""


def test_realtime_session_payload_requests_audio_translation(tmp_path):
    controller = make_controller(tmp_path)

    payload = controller._build_session_update_payload()

    assert payload["type"] == "session.update"
    session = payload["session"]
    assert session["audio"]["output"]["language"] == "en"
    assert "voice" not in session["audio"]["output"]


def test_translation_websocket_url_uses_dedicated_endpoint(tmp_path):
    controller = make_controller(tmp_path)

    assert (
        controller._build_translation_websocket_url()
        == "wss://api.openai.com/v1/realtime/translations?model=gpt-realtime-translate"
    )


async def _collect_sent_audio_message(controller, chunk: bytes) -> dict[str, str]:
    class FakeConnection:
        def __init__(self) -> None:
            self.messages: list[str] = []

        async def send(self, message: str) -> None:
            self.messages.append(message)
            controller._stop_event.set()

    connection = FakeConnection()
    with controller._condition:
        controller._pending_audio.append(chunk)
        controller._condition.notify_all()
    await controller._sender_loop(connection)
    return json.loads(connection.messages[0])


def test_sender_loop_uses_translation_audio_append_event(tmp_path):
    import asyncio

    controller = make_controller(tmp_path)

    message = asyncio.run(_collect_sent_audio_message(controller, b"pcm"))

    assert message == {
        "type": "session.input_audio_buffer.append",
        "audio": base64.b64encode(b"pcm").decode("ascii"),
    }


def test_receiver_loop_writes_translation_audio_delta(tmp_path):
    import asyncio

    class FakeConnection:
        def __init__(self) -> None:
            self.events = iter(
                [
                    json.dumps(
                        {
                            "type": "session.output_audio.delta",
                            "delta": base64.b64encode(b"translated-pcm").decode("ascii"),
                        }
                    ),
                    json.dumps({"type": "session.closed"}),
                ]
            )

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.events)
            except StopIteration as exc:
                raise StopAsyncIteration from exc

    class FakeVirtualMicrophone:
        monitor_source_name = "so_ai_test.monitor"

        def __init__(self) -> None:
            self.writes: list[bytes] = []

        def write(self, pcm_bytes: bytes) -> None:
            self.writes.append(pcm_bytes)

    controller = make_controller(tmp_path)
    fake_virtual_microphone = FakeVirtualMicrophone()
    controller.virtual_microphone = fake_virtual_microphone  # type: ignore[assignment]

    asyncio.run(controller._receiver_loop(FakeConnection()))

    assert fake_virtual_microphone.writes == [b"translated-pcm"]
    assert controller._output_audio_chunks == 1


def test_stop_translation_connection_sends_close_and_waits_for_receiver(tmp_path):
    import asyncio

    class FakeConnection:
        def __init__(self) -> None:
            self.messages: list[str] = []

        async def send(self, message: str) -> None:
            self.messages.append(message)

    async def neverending_sender() -> None:
        await asyncio.sleep(60)

    async def receiver_finishes_after_close(connection: FakeConnection) -> None:
        while not connection.messages:
            await asyncio.sleep(0.01)

    async def run_stop() -> tuple[list[str], bool]:
        controller = make_controller(tmp_path)
        connection = FakeConnection()
        sender = asyncio.create_task(neverending_sender())
        receiver = asyncio.create_task(receiver_finishes_after_close(connection))
        await controller._stop_translation_connection(
            connection=connection,
            sender=sender,
            receiver=receiver,
        )
        return connection.messages, receiver.done()

    messages, receiver_done = asyncio.run(run_stop())

    assert json.loads(messages[0]) == {"type": "session.close"}
    assert receiver_done is True


def test_normalize_translation_language_maps_names_to_codes():
    assert _normalize_translation_language("English") == "en"
    assert _normalize_translation_language("Spanish") == "es"
    assert _normalize_translation_language("fr") == "fr"
