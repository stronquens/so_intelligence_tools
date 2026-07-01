from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass(slots=True)
class LocalTtsSettings:
    base_url: str = "http://127.0.0.1:9010"
    timeout_seconds: float = 20.0
    playback_command: str | None = None
    voice: str = "default"


@dataclass(slots=True)
class SpeakResult:
    spoken: bool
    status: str
    message: str = ""


class LocalTtsClient:
    def __init__(
        self,
        settings: LocalTtsSettings,
        *,
        http_client: httpx.Client | None = None,
        player: "WavPlayer | None" = None,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._player = player or WavPlayer(command=settings.playback_command)

    def check_ready(self) -> bool:
        try:
            response = self._request("GET", "/health")
        except httpx.HTTPError:
            return False
        return 200 <= response.status_code < 300

    def synthesize(self, text: str) -> bytes | None:
        normalized = text.strip()
        if not normalized:
            return None
        try:
            response = self._request(
                "POST",
                "/v1/audio/speech",
                json={"text": normalized, "voice": self._settings.voice or "default"},
            )
        except httpx.HTTPError:
            return None
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            return None
        return response.content if response.content else None

    def speak(self, text: str) -> SpeakResult:
        audio = self.synthesize(text)
        if not audio:
            return SpeakResult(
                spoken=False,
                status="disabled",
                message="Local TTS service is unavailable or returned no audio.",
            )
        played = self._player.play(audio)
        if not played:
            return SpeakResult(
                spoken=False,
                status="playback_unavailable",
                message="No local WAV playback command is available.",
            )
        return SpeakResult(spoken=True, status="spoken")

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = _url(self._settings.base_url, path)
        if self._http_client is not None:
            return self._http_client.request(method, url, **kwargs)
        with httpx.Client(timeout=self._settings.timeout_seconds) as client:
            return client.request(method, url, **kwargs)


class WavPlayer:
    def __init__(self, *, command: str | None = None) -> None:
        self._command = command

    def play(self, wav_bytes: bytes) -> bool:
        command = self._resolve_command()
        if command is None:
            return False
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix="so-ai-tts-",
                suffix=".wav",
                delete=False,
            ) as temp_file:
                temp_file.write(wav_bytes)
                temp_path = Path(temp_file.name)
            result = subprocess.run(
                [command, str(temp_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return result.returncode == 0
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def _resolve_command(self) -> str | None:
        if self._command:
            return self._command if shutil.which(self._command) else None
        for candidate in ("paplay", "pw-play", "aplay"):
            if shutil.which(candidate):
                return candidate
        return None


def _url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
