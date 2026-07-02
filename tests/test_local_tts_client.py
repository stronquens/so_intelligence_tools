from __future__ import annotations

import subprocess
import sys
import types

import httpx

from so_intelligence_tools.local_tts.client import LocalTtsClient, LocalTtsSettings, WavPlayer


def test_local_tts_client_speaks_returned_wav(monkeypatch, tmp_path):
    requested_voices: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/audio/speech":
            requested_voices.append(request.read().decode())
            return httpx.Response(200, content=b"RIFFfakewav")
        return httpx.Response(200, json={"status": "ok"})

    played: list[list[str]] = []

    def fake_which(command: str) -> str | None:
        return command if command == "paplay" else None

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        played.append(command)
        assert command[0] == "paplay"
        assert command[1].endswith(".wav")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("so_intelligence_tools.local_tts.client.sys.platform", "linux")
    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)
    client = LocalTtsClient(
        LocalTtsSettings(base_url="http://tts.local", voice="female"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.speak("Hola mundo")

    assert result.spoken is True
    assert result.status == "spoken"
    assert played
    assert '"voice":"female"' in requested_voices[0]


def test_local_tts_client_treats_unavailable_service_as_disabled():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    client = LocalTtsClient(
        LocalTtsSettings(base_url="http://tts.local"),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.speak("Hola mundo")

    assert result.spoken is False
    assert result.status == "disabled"


def test_wav_player_removes_temp_file(monkeypatch):
    temp_paths: list[str] = []

    def fake_which(command: str) -> str | None:
        return command if command == "paplay" else None

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        temp_paths.append(command[1])
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("so_intelligence_tools.local_tts.client.sys.platform", "linux")
    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)

    assert WavPlayer().play(b"RIFFfakewav") is True
    assert temp_paths
    assert not any(path for path in temp_paths if __import__("pathlib").Path(path).exists())


def test_wav_player_uses_winsound_on_windows(monkeypatch):
    played_paths: list[str] = []

    fake_winsound = types.SimpleNamespace(
        SND_FILENAME=1,
        PlaySound=lambda path, flags: played_paths.append(path),
    )

    monkeypatch.setattr("so_intelligence_tools.local_tts.client.sys.platform", "win32")
    monkeypatch.setitem(sys.modules, "winsound", fake_winsound)

    assert WavPlayer().play(b"RIFFfakewav") is True
    assert played_paths
    assert not any(path for path in played_paths if __import__("pathlib").Path(path).exists())
