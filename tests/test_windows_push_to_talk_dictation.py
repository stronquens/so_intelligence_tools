from __future__ import annotations

import sys
import types

import numpy as np

from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.push_to_talk_dictation import app as dictation_app
from so_intelligence_tools.push_to_talk_dictation.audio import (
    WindowsSoundDeviceMicrophoneCapture,
    _sounddevice_device,
)


def test_windows_sounddevice_capture_emits_pcm_chunks(monkeypatch):
    chunks: list[bytes] = []
    streams = []

    class FakeInputStream:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs
            self.started = False
            self.stopped = False
            self.closed = False
            streams.append(self)

        def start(self) -> None:
            self.started = True

        def stop(self) -> None:
            self.stopped = True

        def close(self) -> None:
            self.closed = True

    fake_sounddevice = types.SimpleNamespace(InputStream=FakeInputStream)
    monkeypatch.setitem(sys.modules, "sounddevice", fake_sounddevice)

    capture = WindowsSoundDeviceMicrophoneCapture(
        sample_rate_hz=16000,
        chunk_ms=560,
        callback=chunks.append,
    )

    capture.start()
    streams[0].kwargs["callback"](
        np.array([[1], [-2], [300]], dtype=np.int16),
        3,
        None,
        None,
    )
    capture.stop()

    assert streams[0].kwargs["samplerate"] == 16000
    assert streams[0].kwargs["channels"] == 1
    assert streams[0].kwargs["dtype"] == "int16"
    assert streams[0].kwargs["blocksize"] == 8960
    assert streams[0].kwargs["device"] is None
    assert streams[0].started is True
    assert streams[0].stopped is True
    assert streams[0].closed is True
    assert chunks == [np.array([[1], [-2], [300]], dtype=np.int16).tobytes()]


def test_sounddevice_device_accepts_index_or_name():
    assert _sounddevice_device(None) is None
    assert _sounddevice_device(" 2 ") == 2
    assert _sounddevice_device("USB Microphone") == "USB Microphone"


def test_dictation_service_warms_runner_before_listening(monkeypatch):
    events: list[str] = []

    class FakeRunner:
        def warm_up(self) -> None:
            events.append("warm")

        def press(self) -> None:
            events.append("press")

        def release(self) -> None:
            events.append("release")

    class FakeListener:
        def __init__(self, *, shortcut, on_press, on_release, event_log_path=None) -> None:
            events.append(f"listener:{shortcut}")
            events.append(f"log:{event_log_path.name}")
            self.on_press = on_press
            self.on_release = on_release

        def run_forever(self) -> None:
            events.append("listen")

    monkeypatch.setattr(
        dictation_app,
        "build_push_to_talk_runner",
        lambda settings, platform_name=None: FakeRunner(),
    )
    monkeypatch.setattr(dictation_app, "PressAndHoldShortcutListener", FakeListener)

    result = dictation_app.run_push_to_talk_dictation_service(
        ToolRunnerSettings(
            push_to_talk_dictation_shortcut="<ctrl>+<alt>+space",
            windows_push_to_talk_dictation_shortcut="<ctrl>+<shift>+<space>",
        ),
        platform_name="win32",
    )

    assert result == "Push-to-talk dictation service stopped"
    assert events == [
        "warm",
        "listener:<ctrl>+<shift>+<space>",
        "log:so-intelligence-tools-dictation-events.log",
        "listen",
    ]
