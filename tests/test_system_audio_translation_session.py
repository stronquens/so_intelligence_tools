from __future__ import annotations

import threading
import time
from pathlib import Path

from so_intelligence_tools.system_audio_translation.session import (
    PcmSegmentAccumulator,
    SystemAudioTranslationController,
    ToggleSocketServer,
    TranscriptSessionLogger,
    send_toggle_command,
)


class FakeCapture:
    def __init__(self) -> None:
        self.running = False
        self._callback = None

    def start(self, callback):
        self.running = True
        self._callback = callback

    def stop(self):
        self.running = False

    def emit(self, chunk: bytes) -> None:
        if self._callback is not None:
            self._callback(chunk)


class FakeProvider:
    def transcribe_and_translate(self, **kwargs):
        return ("hello world", "hola mundo")


def test_pcm_segment_accumulator_emits_segments_with_overlap():
    accumulator = PcmSegmentAccumulator(
        sample_rate_hz=4,
        segment_seconds=1.0,
        overlap_seconds=0.5,
    )

    ready = accumulator.add_chunk(b"1234")
    assert ready == []

    ready = accumulator.add_chunk(b"5678")
    assert len(ready) == 1
    assert ready[0] == b"12345678"


def test_transcript_session_logger_writes_session_file(tmp_path: Path):
    from datetime import datetime
    from so_intelligence_tools.domain.models import TranscriptBlock

    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    logger.record_event("state_changed", state="active", message="Escuchando")
    file_path = logger.write_session(
        [TranscriptBlock(timestamp=datetime(2026, 1, 1, 12, 0, 0), translated_text="hola")]
    )

    assert file_path is not None
    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")
    assert "# Session Events" in content
    assert '"type": "state_changed"' in content
    assert "# Final Blocks" in content
    assert "hola" in content


def test_toggle_socket_server_receives_toggle(tmp_path: Path):
    socket_path = tmp_path / "toggle.sock"
    event = threading.Event()
    server = ToggleSocketServer(socket_path=socket_path, on_toggle=event.set)
    server.start()
    try:
        assert send_toggle_command(socket_path) is True
        assert event.wait(timeout=1.0) is True
    finally:
        server.stop()


def test_system_audio_translation_controller_processes_segment_and_logs(tmp_path: Path):
    capture = FakeCapture()
    controller = SystemAudioTranslationController(
        capture=capture,
        provider=FakeProvider(),
        session_logger=TranscriptSessionLogger(logs_dir=tmp_path),
        source_language="en",
        target_language="es",
        sample_rate_hz=10,
        segment_seconds=0.1,
        overlap_seconds=0.0,
        pending_segment_limit=4,
        reconnect_backoff_seconds=0.01,
    )
    states: list[str] = []
    blocks: list[str] = []
    controller.bind_callbacks(
        on_state_changed=lambda state, message: states.append(state),
        on_block_ready=lambda block: blocks.append(block.translated_text),
    )

    controller.start()
    capture.emit(b"\x00\x00")
    deadline = time.time() + 1.0
    while not blocks and time.time() < deadline:
        time.sleep(0.02)
    controller.stop()

    assert "active" in states
    assert blocks == ["hola mundo"]
    assert controller.last_log_path is not None
    assert controller.last_log_path.exists()
