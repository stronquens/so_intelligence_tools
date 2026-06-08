from __future__ import annotations

import subprocess

import pytest

from so_intelligence_tools.domain.errors import AudioCaptureError
from so_intelligence_tools.system_audio_translation.audio_capture import (
    detect_default_monitor_source,
)


def test_detect_default_monitor_source_parses_default_sink(monkeypatch):
    def fake_run(*args, **kwargs):
        if args[0][-1] == "get-default-sink":
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="alsa_output.pci-0000_00_1f.3.analog-stereo\n",
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Default Sink: alsa_output.pci-0000_00_1f.3.analog-stereo\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "so_intelligence_tools.system_audio_translation.audio_capture.which",
        lambda name: f"/usr/bin/{name}",
    )

    assert (
        detect_default_monitor_source()
        == "alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"
    )


def test_detect_default_monitor_source_raises_when_sink_missing(monkeypatch):
    def fake_run(*args, **kwargs):
        if args[0][-1] == "get-default-sink":
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=1,
                stdout="",
                stderr="boom",
            )
        if args[0][-1] == "sinks":
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="",
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Server Name: pulseaudio\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "so_intelligence_tools.system_audio_translation.audio_capture.which",
        lambda name: f"/usr/bin/{name}",
    )

    with pytest.raises(AudioCaptureError, match="sink por defecto"):
        detect_default_monitor_source()


def test_detect_default_monitor_source_falls_back_to_short_sinks(monkeypatch):
    def fake_run(*args, **kwargs):
        if args[0][-1] == "get-default-sink":
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=1,
                stdout="",
                stderr="unsupported",
            )
        if args[0][-1] == "sinks":
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="0 alsa_output.pci-0000_00_1f.3.analog-stereo module-alsa-card.c s16le 2ch 44100Hz SUSPENDED\n",
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Server Name: pulseaudio\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "so_intelligence_tools.system_audio_translation.audio_capture.which",
        lambda name: f"/usr/bin/{name}",
    )

    assert (
        detect_default_monitor_source()
        == "alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"
    )
