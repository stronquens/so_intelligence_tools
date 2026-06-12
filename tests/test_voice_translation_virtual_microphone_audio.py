from __future__ import annotations

import subprocess

from so_intelligence_tools.voice_translation_virtual_microphone.audio import (
    MicrophonePassthroughToVirtualMicrophone,
    PulseAudioMonitorWavRecorder,
    PulseAudioVirtualMicrophone,
    detect_default_source,
    limit_pcm_s16le,
    scale_pcm_s16le,
    validate_physical_source,
)


def test_detect_default_source_uses_pactl_default_source(monkeypatch):
    def fake_run(command, **_kwargs):
        if command[-1] == "get-default-source":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="alsa_input.usb.logitech.analog-stereo\n",
                stderr="",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "so_intelligence_tools.voice_translation_virtual_microphone.audio.which",
        lambda name: f"/usr/bin/{name}",
    )

    assert detect_default_source() == "alsa_input.usb.logitech.analog-stereo"


def test_detect_default_source_falls_back_to_first_physical_source(monkeypatch):
    def fake_run(command, **_kwargs):
        if command[-1] == "get-default-source":
            return subprocess.CompletedProcess(
                args=command,
                returncode=1,
                stdout="",
                stderr="unsupported",
            )
        if command[-1] == "sources":
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout=(
                    "1 alsa_output.pci.monitor module.c s16le 2ch 44100Hz SUSPENDED\n"
                    "2 alsa_input.internal module.c s16le 2ch 44100Hz SUSPENDED\n"
                ),
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="Server Name: pulseaudio\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "so_intelligence_tools.voice_translation_virtual_microphone.audio.which",
        lambda name: f"/usr/bin/{name}",
    )

    assert detect_default_source() == "alsa_input.internal"


def test_virtual_microphone_loads_internal_sink_and_public_source(monkeypatch):
    run_calls: list[list[str]] = []

    class FakePopen:
        stdin = None
        stderr = None

        def __init__(self, command, **_kwargs):
            self.command = command
            self.stdin = FakeStdin()
            self._returncode = None

        def poll(self):
            return self._returncode

        def terminate(self):
            self._returncode = 0

        def wait(self, timeout=None):
            self._returncode = 0
            return 0

        def kill(self):
            self._returncode = -9

    class FakeStdin:
        def __init__(self):
            self.written = bytearray()

        def write(self, data):
            self.written.extend(data)

        def flush(self):
            return None

        def close(self):
            return None

    def fake_run(command, **_kwargs):
        run_calls.append(command)
        if command[:3] == ["pactl", "load-module", "module-null-sink"]:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="42\n",
                stderr="",
            )
        if command[:3] == ["pactl", "load-module", "module-remap-source"]:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="43\n",
                stderr="",
            )
        if command[:2] == ["pactl", "unload-module"]:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="",
                stderr="",
            )
        raise AssertionError(f"Unexpected command: {command}")

    popen_calls = []

    def fake_popen(command, **kwargs):
        popen_calls.append(command)
        return FakePopen(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        "so_intelligence_tools.voice_translation_virtual_microphone.audio.which",
        lambda name: f"/usr/bin/{name}",
    )

    virtual_mic = PulseAudioVirtualMicrophone(
        sink_name="so_ai_test_mic",
        sample_rate_hz=24000,
    )
    virtual_mic.start()
    virtual_mic.write(b"\x00\x01")
    virtual_mic.stop()

    assert run_calls[0][:3] == ["pactl", "load-module", "module-null-sink"]
    assert "sink_name=so_ai_test_mic_sink" in run_calls[0]
    assert "rate=24000" in run_calls[0]
    assert run_calls[1][:3] == ["pactl", "load-module", "module-remap-source"]
    assert "master=so_ai_test_mic_sink.monitor" in run_calls[1]
    assert "source_name=so_ai_test_mic" in run_calls[1]
    assert popen_calls[0][:4] == [
        "pacat",
        "--device",
        "so_ai_test_mic_sink",
        "--format=s16le",
    ]
    assert run_calls[-2:] == [
        ["pactl", "unload-module", "43"],
        ["pactl", "unload-module", "42"],
    ]


def test_virtual_microphone_unloads_sink_when_public_source_fails(monkeypatch):
    run_calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        run_calls.append(command)
        if command[:3] == ["pactl", "load-module", "module-null-sink"]:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="42\n",
                stderr="",
            )
        if command[:3] == ["pactl", "load-module", "module-remap-source"]:
            return subprocess.CompletedProcess(
                args=command,
                returncode=1,
                stdout="",
                stderr="remap failed",
            )
        if command[:2] == ["pactl", "unload-module"]:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout="",
                stderr="",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "so_intelligence_tools.voice_translation_virtual_microphone.audio.which",
        lambda name: f"/usr/bin/{name}",
    )

    virtual_mic = PulseAudioVirtualMicrophone(
        sink_name="so_ai_test_mic",
        sample_rate_hz=24000,
    )

    try:
        virtual_mic.start()
    except Exception as exc:
        assert "No se pudo publicar el micrófono virtual de entrada" in str(exc)
    else:
        raise AssertionError("Expected virtual source creation failure")

    assert run_calls[-1] == ["pactl", "unload-module", "42"]


def test_scale_pcm_s16le_changes_volume():
    sample = (1000).to_bytes(2, "little", signed=True)

    assert scale_pcm_s16le(sample, 0.5) == (500).to_bytes(2, "little", signed=True)
    assert scale_pcm_s16le(sample, 1.0) == sample
    assert scale_pcm_s16le((30000).to_bytes(2, "little", signed=True), 2.0) == (
        32767
    ).to_bytes(2, "little", signed=True)


def test_limit_pcm_s16le_clamps_to_ceiling():
    hot_positive = (32767).to_bytes(2, "little", signed=True)
    hot_negative = (-32768).to_bytes(2, "little", signed=True)

    assert limit_pcm_s16le(hot_positive + hot_negative, ceiling=0.5) == (
        (16383).to_bytes(2, "little", signed=True)
        + (-16383).to_bytes(2, "little", signed=True)
    )


def test_validate_physical_source_rejects_monitor_and_project_virtual_source():
    for source in [
        "alsa_output.pci.monitor",
        "so_ai_translated_mic",
        "so_ai_translated_mic.monitor",
        "so_ai_translated_mic_sink.monitor",
    ]:
        try:
            validate_physical_source(source)
        except Exception as exc:
            assert "Fuente de micrófono no válida" in str(exc)
        else:
            raise AssertionError(f"Expected unsafe source rejection for {source}")


def test_validate_physical_source_accepts_physical_input():
    validate_physical_source("alsa_input.usb-logitech.analog-stereo")


def test_passthrough_scales_microphone_audio():
    class FakeCapture:
        running = False

        def start(self, callback):
            self.running = True
            self.callback = callback

        def stop(self):
            self.running = False

    class FakePlayback:
        running = False

        def __init__(self) -> None:
            self.writes: list[bytes] = []

        def start(self):
            self.running = True

        def stop(self):
            self.running = False

        def write(self, pcm_bytes: bytes):
            self.writes.append(pcm_bytes)

    capture = FakeCapture()
    playback = FakePlayback()
    passthrough = MicrophonePassthroughToVirtualMicrophone(
        capture=capture,  # type: ignore[arg-type]
        playback=playback,  # type: ignore[arg-type]
        volume=0.25,
    )

    passthrough.start()
    capture.callback((4000).to_bytes(2, "little", signed=True))

    assert playback.writes == [(1000).to_bytes(2, "little", signed=True)]


def test_monitor_wav_recorder_records_virtual_microphone_monitor(monkeypatch, tmp_path):
    popen_calls = []

    class FakePopen:
        def __init__(self, command, **_kwargs):
            self.command = command
            self._returncode = None

        def poll(self):
            return self._returncode

        def terminate(self):
            self._returncode = 0

        def wait(self, timeout=None):
            self._returncode = 0
            return 0

        def kill(self):
            self._returncode = -9

    def fake_popen(command, **kwargs):
        popen_calls.append(command)
        return FakePopen(command, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        "so_intelligence_tools.voice_translation_virtual_microphone.audio.which",
        lambda name: f"/usr/bin/{name}",
    )

    recorder = PulseAudioMonitorWavRecorder(
        monitor_source_name="so_ai_translated_mic.monitor",
        sample_rate_hz=24000,
        recordings_dir=tmp_path,
    )

    recording_path = recorder.start()
    stopped_path = recorder.stop()

    assert recording_path == stopped_path
    assert recording_path.parent == tmp_path
    assert recording_path.name.startswith("voice-translation-final-output-")
    assert recording_path.suffix == ".wav"
    assert popen_calls == [
        [
            "parecord",
            "-d",
            "so_ai_translated_mic.monitor",
            "--format=s16le",
            "--rate",
            "24000",
            "--channels",
            "1",
            "--file-format=wav",
            str(recording_path),
        ]
    ]
