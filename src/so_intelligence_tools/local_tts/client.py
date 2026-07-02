from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx


@dataclass(slots=True)
class LocalTtsSettings:
    base_url: str = "http://127.0.0.1:9011"
    timeout_seconds: float = 20.0
    playback_command: str | None = None
    voice: str = "default"


@dataclass(slots=True)
class SpeakResult:
    spoken: bool
    status: str
    message: str = ""


@dataclass(slots=True)
class TimedSpeakResult(SpeakResult):
    synthesis_started_at: datetime | None = None
    synthesis_finished_at: datetime | None = None
    playback_started_at: datetime | None = None
    playback_finished_at: datetime | None = None
    synthesis_seconds: float | None = None
    playback_seconds: float | None = None


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
        return self.speak_timed(text)

    def speak_timed(self, text: str) -> TimedSpeakResult:
        synthesis_started_at = datetime.now(UTC)
        synthesis_started_perf = time_perf_counter()
        audio = self.synthesize(text)
        synthesis_finished_at = datetime.now(UTC)
        synthesis_seconds = time_perf_counter() - synthesis_started_perf
        if not audio:
            return TimedSpeakResult(
                spoken=False,
                status="disabled",
                message="Local TTS service is unavailable or returned no audio.",
                synthesis_started_at=synthesis_started_at,
                synthesis_finished_at=synthesis_finished_at,
                synthesis_seconds=synthesis_seconds,
            )
        playback_started_at = datetime.now(UTC)
        playback_started_perf = time_perf_counter()
        played = self.play_audio(audio)
        playback_finished_at = datetime.now(UTC)
        playback_seconds = time_perf_counter() - playback_started_perf
        if not played:
            return TimedSpeakResult(
                spoken=False,
                status="playback_unavailable",
                message="No local WAV playback command is available.",
                synthesis_started_at=synthesis_started_at,
                synthesis_finished_at=synthesis_finished_at,
                playback_started_at=playback_started_at,
                playback_finished_at=playback_finished_at,
                synthesis_seconds=synthesis_seconds,
                playback_seconds=playback_seconds,
            )
        return TimedSpeakResult(
            spoken=True,
            status="spoken",
            synthesis_started_at=synthesis_started_at,
            synthesis_finished_at=synthesis_finished_at,
            playback_started_at=playback_started_at,
            playback_finished_at=playback_finished_at,
            synthesis_seconds=synthesis_seconds,
            playback_seconds=playback_seconds,
        )

    def play_audio(self, wav_bytes: bytes) -> bool:
        return self._player.play(wav_bytes)

    def stop_playback(self) -> None:
        self._player.stop()

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
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix="so-ai-tts-",
                suffix=".wav",
                delete=False,
            ) as temp_file:
                temp_file.write(wav_bytes)
                temp_path = Path(temp_file.name)
            if self._command:
                return self._play_with_command(temp_path)
            if sys.platform == "win32":
                return self._play_with_winsound(temp_path)
            command = self._resolve_posix_command()
            if command is None:
                return False
            return self._run_player_command(command, temp_path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def stop(self) -> None:
        if sys.platform == "win32":
            try:
                import winsound

                winsound.PlaySound(None, 0)
            except Exception:
                return

    def _play_with_command(self, temp_path: Path) -> bool:
        command = self._command or ""
        return self._run_player_command(command, temp_path) if shutil.which(command) else False

    def _play_with_winsound(self, temp_path: Path) -> bool:
        try:
            import winsound

            winsound.PlaySound(str(temp_path), winsound.SND_FILENAME)
        except Exception:
            return False
        return True

    def _resolve_posix_command(self) -> str | None:
        for candidate in ("paplay", "pw-play", "aplay"):
            if shutil.which(candidate):
                return candidate
        return None

    def _run_player_command(self, command: str, temp_path: Path) -> bool:
        result = subprocess.run(
            [command, str(temp_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.returncode == 0


def _url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def time_perf_counter() -> float:
    import time

    return time.perf_counter()
