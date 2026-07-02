from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from so_intelligence_tools.local_tts.codex_desktop import (
    CodexDesktopSessionTailer,
    CodexDesktopSpeechSegment,
    CodexDesktopTimedSpeechPlaybackQueue,
    parse_action_segment_from_codex_session_line,
    parse_lifecycle_segment_from_codex_session_line,
    parse_visible_message_from_codex_session_line,
    parse_visible_text_from_codex_session_line,
    run_codex_desktop_session_listener,
    visible_speech_segments_from_session_lines,
    visible_segments_from_session_lines,
)


class CollectingClient:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str):
        self.spoken.append(text)


class BlockingSynthesisClient:
    def __init__(self) -> None:
        self.synthesized: list[str] = []
        self.played: list[str] = []
        self.started = threading.Event()
        self.release = threading.Event()
        self.stopped = False

    def synthesize(self, text: str) -> bytes:
        self.synthesized.append(text)
        if text == "Mensaje viejo.":
            self.started.set()
            self.release.wait(timeout=2)
        return text.encode("utf-8")

    def play_audio(self, wav_bytes: bytes) -> bool:
        self.played.append(wav_bytes.decode("utf-8"))
        return True

    def stop_playback(self) -> None:
        self.stopped = True


class PlaybackBlocksClient:
    def __init__(self) -> None:
        self.synthesized: list[str] = []
        self.played: list[str] = []
        self.first_playback_started = threading.Event()
        self.second_synthesized = threading.Event()
        self.release_first_playback = threading.Event()
        self.stopped = False

    def synthesize(self, text: str) -> bytes:
        self.synthesized.append(text)
        if text == "Segundo.":
            self.second_synthesized.set()
        return text.encode("utf-8")

    def play_audio(self, wav_bytes: bytes) -> bool:
        text = wav_bytes.decode("utf-8")
        if text == "Primero.":
            self.first_playback_started.set()
            self.release_first_playback.wait(timeout=2)
        self.played.append(text)
        return True

    def stop_playback(self) -> None:
        self.stopped = True
        self.release_first_playback.set()


class BlockingActionSynthesisClient:
    def __init__(self) -> None:
        self.synthesized: list[str] = []
        self.played: list[str] = []
        self.first_action_started = threading.Event()
        self.release_first_action = threading.Event()
        self.message_played = threading.Event()
        self.stopped = False

    def synthesize(self, text: str) -> bytes:
        self.synthesized.append(text)
        if text == "Ejecutando comando.":
            self.first_action_started.set()
            self.release_first_action.wait(timeout=2)
        return text.encode("utf-8")

    def play_audio(self, wav_bytes: bytes) -> bool:
        text = wav_bytes.decode("utf-8")
        self.played.append(text)
        if text == "Mensaje real.":
            self.message_played.set()
        return True

    def stop_playback(self) -> None:
        self.stopped = True
        self.release_first_action.set()


def session_line(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def test_parse_visible_codex_desktop_agent_message():
    text = parse_visible_text_from_codex_session_line(
        session_line(
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Mensaje visible de Desktop.",
                    "phase": "commentary",
                },
            }
        )
    )

    assert text == "Mensaje visible de Desktop."


def test_parse_visible_codex_desktop_message_timestamp():
    message = parse_visible_message_from_codex_session_line(
        session_line(
            {
                "timestamp": "2026-07-02T14:21:14.983Z",
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Mensaje visible de Desktop.",
                    "phase": "commentary",
                },
            }
        )
    )

    assert message is not None
    assert message.timestamp is not None
    assert message.timestamp.isoformat() == "2026-07-02T14:21:14.983000+00:00"


def test_parse_visible_codex_desktop_final_answer():
    text = parse_visible_text_from_codex_session_line(
        session_line(
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Respuesta final visible de Desktop.",
                    "phase": "final_answer",
                },
            }
        )
    )

    assert text == "Respuesta final visible de Desktop."


def test_parse_codex_desktop_lifecycle_events():
    started = parse_lifecycle_segment_from_codex_session_line(
        session_line(
            {
                "timestamp": "2026-07-02T14:21:03.565Z",
                "type": "event_msg",
                "payload": {"type": "task_started", "turn_id": "turn-1"},
            }
        )
    )
    completed = parse_lifecycle_segment_from_codex_session_line(
        session_line(
            {
                "timestamp": "2026-07-02T14:21:15.021Z",
                "type": "event_msg",
                "payload": {"type": "task_complete", "turn_id": "turn-1"},
            }
        )
    )

    assert started is not None
    assert started.text == "Inicio de tarea."
    assert started.kind == "task_started"
    assert completed is not None
    assert completed.text == "Fin de tarea."
    assert completed.kind == "task_complete"


def test_parse_codex_desktop_action_events():
    function_call = parse_action_segment_from_codex_session_line(
        session_line(
            {
                "timestamp": "2026-07-02T14:21:10.000Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "functions.shell_command",
                },
            }
        )
    )
    function_output = parse_action_segment_from_codex_session_line(
        session_line(
            {
                "timestamp": "2026-07-02T14:21:12.000Z",
                "type": "response_item",
                "payload": {"type": "function_call_output", "call_id": "call-1"},
            }
        )
    )

    assert function_call is not None
    assert function_call.text == "Ejecutando comando."
    assert function_call.kind == "tool_started"
    assert function_output is not None
    assert function_output.text == "Herramienta terminada."
    assert function_output.kind == "tool_completed"


def test_parse_visible_codex_desktop_agent_message_with_utf8_bom():
    text = parse_visible_text_from_codex_session_line(
        "\ufeff"
        + session_line(
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Mensaje visible con BOM.",
                    "phase": "commentary",
                },
            }
        )
    )

    assert text == "Mensaje visible con BOM."


def test_parse_codex_desktop_ignores_non_visible_payloads():
    assert (
        parse_visible_text_from_codex_session_line(
            session_line({"type": "response_item", "payload": {"type": "reasoning"}})
        )
        is None
    )
    assert (
        parse_visible_text_from_codex_session_line(
            session_line(
                {
                    "type": "event_msg",
                    "payload": {"type": "token_count", "message": "no leer"},
                }
            )
        )
        is None
    )


def test_visible_segments_clean_code_blocks():
    segments = visible_segments_from_session_lines(
        [
            session_line(
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "agent_message",
                        "message": "Antes. ```bash\nsecret\n``` Despues.",
                        "phase": "final",
                    },
                }
            )
        ]
    )

    assert len(segments) == 1
    assert "Antes." in segments[0]
    assert "Despues." in segments[0]
    assert "secret" not in segments[0]


def test_visible_speech_segments_preserve_event_timestamp():
    segments = visible_speech_segments_from_session_lines(
        [
            session_line(
                {
                    "timestamp": "2026-07-02T14:21:14.983Z",
                    "type": "event_msg",
                    "payload": {
                        "type": "agent_message",
                        "message": "Hola desde Codex Desktop.",
                        "phase": "final_answer",
                    },
                }
            )
        ]
    )

    assert len(segments) == 1
    assert segments[0].text == "Hola desde Codex Desktop."
    assert segments[0].phase == "final_answer"
    assert segments[0].event_timestamp is not None


def test_visible_speech_segments_include_lifecycle_and_minimal_skips_messages():
    lines = [
        session_line(
            {
                "type": "event_msg",
                "payload": {"type": "task_started", "turn_id": "turn-1"},
            }
        ),
        session_line(
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "No debe leerse en minimal.",
                    "phase": "commentary",
                },
            }
        ),
        session_line(
            {
                "type": "event_msg",
                "payload": {"type": "task_complete", "turn_id": "turn-1"},
            }
        ),
    ]

    segments = visible_speech_segments_from_session_lines(lines, speech_detail="minimal")

    assert [segment.text for segment in segments] == ["Inicio de tarea.", "Fin de tarea."]
    assert [segment.kind for segment in segments] == ["task_started", "task_complete"]


def test_visible_speech_segments_actions_reads_tools_not_messages():
    lines = [
        session_line(
            {
                "type": "event_msg",
                "payload": {"type": "task_started", "turn_id": "turn-1"},
            }
        ),
        session_line(
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "No debe leerse en actions.",
                    "phase": "commentary",
                },
            }
        ),
        session_line(
            {
                "type": "response_item",
                "payload": {"type": "function_call", "name": "functions.apply_patch"},
            }
        ),
        session_line(
            {
                "type": "response_item",
                "payload": {"type": "function_call_output", "call_id": "call-1"},
            }
        ),
        session_line(
            {
                "type": "event_msg",
                "payload": {"type": "task_complete", "turn_id": "turn-1"},
            }
        ),
    ]

    segments = visible_speech_segments_from_session_lines(lines, speech_detail="actions")

    assert [segment.text for segment in segments] == [
        "Inicio de tarea.",
        "Preparando cambios de archivos.",
        "Herramienta terminada.",
        "Fin de tarea.",
    ]


def test_visible_speech_segments_task_complete_reads_finish_before_final():
    segments = visible_speech_segments_from_session_lines(
        [
            session_line(
                {
                    "timestamp": "2026-07-02T14:21:15.021Z",
                    "type": "event_msg",
                    "payload": {
                        "type": "task_complete",
                        "turn_id": "turn-1",
                        "last_agent_message": "Respuesta final desde Desktop.",
                    },
                }
            )
        ],
        speech_detail="standard",
    )

    assert [segment.text for segment in segments] == [
        "Fin de tarea.",
        "Respuesta final desde Desktop.",
    ]
    assert [segment.kind for segment in segments] == ["task_complete", "message"]
    assert segments[0].priority_clear is True
    assert segments[1].priority_clear is False


def test_codex_desktop_tailer_reads_incremental_lines(tmp_path: Path):
    session_dir = tmp_path / "sessions" / "2026" / "07" / "02"
    session_dir.mkdir(parents=True)
    session = session_dir / "rollout-test.jsonl"
    session.write_text("", encoding="utf-8")
    tailer = CodexDesktopSessionTailer(tmp_path / "sessions", start_at_end=True)

    assert tailer.read_new_lines() == []

    first = session_line(
        {
            "type": "event_msg",
            "payload": {
                "type": "agent_message",
                "message": "Primero.",
                "phase": "commentary",
            },
        }
    )
    session.write_text(first, encoding="utf-8")

    assert tailer.read_new_lines() == [first]
    assert tailer.read_new_lines() == []


def test_codex_desktop_listener_speaks_visible_lines(tmp_path: Path):
    session_dir = tmp_path / "sessions" / "2026" / "07" / "02"
    session_dir.mkdir(parents=True)
    session = session_dir / "rollout-test.jsonl"
    session.write_text(
        session_line(
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Hola desde Codex Desktop.",
                    "phase": "final",
                },
            }
        ),
        encoding="utf-8",
    )
    client = CollectingClient()

    result = run_codex_desktop_session_listener(
        client=client,  # type: ignore[arg-type]
        sessions_dir=tmp_path / "sessions",
        start_at_end=False,
        idle_timeout_seconds=0.05,
        poll_interval_seconds=0.05,
    )

    assert result == 0
    assert client.spoken == ["Hola desde Codex Desktop."]


def test_codex_desktop_queue_discards_superseded_audio_before_playback():
    client = BlockingSynthesisClient()
    playback = CodexDesktopTimedSpeechPlaybackQueue(client)  # type: ignore[arg-type]
    playback.start()

    playback.enqueue(CodexDesktopSpeechSegment(text="Mensaje viejo."))
    assert client.started.wait(timeout=2)
    playback.clear(cancel_current=True)
    playback.enqueue(CodexDesktopSpeechSegment(text="Fin de tarea.", kind="task_complete"))
    client.release.set()
    playback.stop()

    assert client.stopped is True
    assert client.synthesized == ["Mensaje viejo.", "Fin de tarea."]
    assert client.played == ["Fin de tarea."]


def test_codex_desktop_queue_synthesizes_next_segment_while_playing_current():
    client = PlaybackBlocksClient()
    playback = CodexDesktopTimedSpeechPlaybackQueue(client)  # type: ignore[arg-type]
    playback.start()

    playback.enqueue(CodexDesktopSpeechSegment(text="Primero."))
    playback.enqueue(CodexDesktopSpeechSegment(text="Segundo."))

    assert client.first_playback_started.wait(timeout=2)
    assert client.second_synthesized.wait(timeout=2)
    assert client.played == []

    client.release_first_playback.set()
    deadline = time.monotonic() + 2
    while client.played != ["Primero.", "Segundo."] and time.monotonic() < deadline:
        time.sleep(0.01)
    playback.stop()

    assert client.synthesized == ["Primero.", "Segundo."]
    assert client.played == ["Primero.", "Segundo."]


def test_codex_desktop_queue_clear_discards_prefetched_audio():
    client = PlaybackBlocksClient()
    playback = CodexDesktopTimedSpeechPlaybackQueue(client)  # type: ignore[arg-type]
    playback.start()

    playback.enqueue(CodexDesktopSpeechSegment(text="Primero."))
    playback.enqueue(CodexDesktopSpeechSegment(text="Segundo."))

    assert client.first_playback_started.wait(timeout=2)
    assert client.second_synthesized.wait(timeout=2)
    playback.clear(cancel_current=True)
    playback.enqueue(CodexDesktopSpeechSegment(text="Fin de tarea.", kind="task_complete"))

    deadline = time.monotonic() + 2
    while "Fin de tarea." not in client.played and time.monotonic() < deadline:
        time.sleep(0.01)
    playback.stop()

    assert client.stopped is True
    assert "Segundo." not in client.played
    assert "Fin de tarea." in client.played


def test_codex_desktop_queue_message_drops_pending_action_segments():
    client = BlockingActionSynthesisClient()
    playback = CodexDesktopTimedSpeechPlaybackQueue(client)  # type: ignore[arg-type]
    playback.start()

    playback.enqueue(CodexDesktopSpeechSegment(text="Ejecutando comando.", kind="tool_started"))
    playback.enqueue(CodexDesktopSpeechSegment(text="Ejecutando comando.", kind="tool_started"))
    playback.enqueue(CodexDesktopSpeechSegment(text="Ejecutando comando.", kind="tool_started"))
    assert client.first_action_started.wait(timeout=2)

    playback.enqueue(CodexDesktopSpeechSegment(text="Mensaje real.", kind="message"))
    client.release_first_action.set()
    assert client.message_played.wait(timeout=2)
    playback.stop()

    assert client.played == ["Mensaje real."]
    assert client.synthesized.count("Ejecutando comando.") == 1
    assert client.synthesized[-1] == "Mensaje real."
