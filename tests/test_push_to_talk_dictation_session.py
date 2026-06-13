from __future__ import annotations

from so_intelligence_tools.adapters.testing.fakes import (
    CollectingNotificationAdapter,
    MemoryTextInsertionAdapter,
)
from so_intelligence_tools.ports.streaming_asr import StreamingAsrEvent
from so_intelligence_tools.push_to_talk_dictation.session import (
    PressAndHoldDictationRunner,
    StreamingDictationController,
)


class FakeAsrSession:
    def __init__(self) -> None:
        self.accepted_audio: list[bytes] = []
        self.finished = False
        self.closed = False

    def accept_audio(self, pcm_s16le: bytes):
        self.accepted_audio.append(pcm_s16le)
        return [
            StreamingAsrEvent(kind="partial", text="hola par"),
            StreamingAsrEvent(kind="final", text="hola "),
        ]

    def finish(self):
        self.finished = True
        return [StreamingAsrEvent(kind="final", text="mundo")]

    def close(self) -> None:
        self.closed = True


class FakeTranscriber:
    def __init__(self) -> None:
        self.ready_checks = 0
        self.session = FakeAsrSession()

    def check_ready(self) -> None:
        self.ready_checks += 1

    def start_session(self):
        return self.session


def test_streaming_dictation_inserts_only_final_segments():
    transcriber = FakeTranscriber()
    insertion = MemoryTextInsertionAdapter()
    notifications = CollectingNotificationAdapter()
    controller = StreamingDictationController(
        transcriber=transcriber,
        text_insertion=insertion,
        notifications=notifications,
    )

    controller.start()
    controller.accept_audio(b"pcm")
    result = controller.stop()

    assert transcriber.ready_checks == 1
    assert transcriber.session.accepted_audio == [b"pcm"]
    assert transcriber.session.finished is True
    assert transcriber.session.closed is True
    assert result.final_segments == ["hola ", "mundo"]
    assert result.inserted_text == "hola mundo"
    assert insertion.last_text == "mundo"
    assert [message.level for message in notifications.messages] == ["info", "success"]


class CumulativeAsrSession:
    def accept_audio(self, pcm_s16le: bytes):
        return [
            StreamingAsrEvent(kind="final", text="hola"),
            StreamingAsrEvent(kind="final", text="hola mundo"),
        ]

    def finish(self):
        return []

    def close(self) -> None:
        pass


class CumulativeTranscriber:
    def check_ready(self) -> None:
        pass

    def start_session(self):
        return CumulativeAsrSession()


def test_streaming_dictation_tracks_stable_delta_for_cumulative_finals():
    insertion = MemoryTextInsertionAdapter()
    controller = StreamingDictationController(
        transcriber=CumulativeTranscriber(),
        text_insertion=insertion,
    )

    controller.start()
    controller.accept_audio(b"pcm")
    result = controller.stop()

    assert result.final_segments == ["hola", " mundo"]
    assert result.inserted_text == "hola mundo"


class FakeCapture:
    def __init__(self, callback) -> None:
        self.callback = callback
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True
        self.callback(b"chunk")

    def stop(self) -> None:
        self.stopped = True


def test_press_and_hold_runner_stops_capture_before_finalizing():
    transcriber = FakeTranscriber()
    insertion = MemoryTextInsertionAdapter()
    controller = StreamingDictationController(
        transcriber=transcriber,
        text_insertion=insertion,
    )
    captures: list[FakeCapture] = []

    def capture_factory(callback):
        capture = FakeCapture(callback)
        captures.append(capture)
        return capture

    runner = PressAndHoldDictationRunner(
        controller=controller,
        audio_capture_factory=capture_factory,
    )

    runner.press()
    result = runner.release()

    assert captures[0].started is True
    assert captures[0].stopped is True
    assert transcriber.session.finished is True
    assert result.inserted_text == "hola mundo"
