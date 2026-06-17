from __future__ import annotations

import io
import wave
from dataclasses import dataclass

import httpx

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.ports.streaming_asr import StreamingAsrEvent


@dataclass(slots=True)
class FasterWhisperHttpSettings:
    base_url: str = "http://127.0.0.1:9000"
    model: str = "whisper-1"
    language: str = "es-ES"
    sample_rate_hz: int = 16000
    timeout_seconds: float = 30.0
    prompt: str | None = None


class FasterWhisperHttpTranscriber:
    def __init__(
        self,
        settings: FasterWhisperHttpSettings,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings
        self._http_client = http_client

    def check_ready(self) -> None:
        try:
            response = self._request("GET", "/v1/models")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ToolRunnerConfigurationError(
                "No se puede contactar con el servidor faster-whisper de dictado "
                f"en `{self._settings.base_url}`."
            ) from exc

    def start_session(self) -> FasterWhisperHttpSession:
        return FasterWhisperHttpSession(self._settings, http_client=self._http_client)

    def _request(self, method: str, path: str) -> httpx.Response:
        url = _url(self._settings.base_url, path)
        if self._http_client is not None:
            return self._http_client.request(method, url)
        with httpx.Client(timeout=self._settings.timeout_seconds) as client:
            return client.request(method, url)


class FasterWhisperHttpSession:
    def __init__(
        self,
        settings: FasterWhisperHttpSettings,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._chunks: list[bytes] = []
        self._closed = False

    def accept_audio(self, pcm_s16le: bytes):
        if self._closed or not pcm_s16le:
            return []
        self._chunks.append(pcm_s16le)
        return []

    def finish(self):
        if self._closed or not self._chunks:
            return []
        wav_bytes = _pcm_s16le_to_wav(
            b"".join(self._chunks),
            sample_rate_hz=self._settings.sample_rate_hz,
        )
        try:
            response = self._post_transcription(wav_bytes)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            return [
                StreamingAsrEvent(
                    kind="error",
                    message=f"Error transcribiendo con faster-whisper: {exc}",
                )
            ]
        text = _transcription_text(payload)
        if not text:
            return []
        return [StreamingAsrEvent(kind="final", text=text)]

    def close(self) -> None:
        self._closed = True

    def _post_transcription(self, wav_bytes: bytes) -> httpx.Response:
        data = {
            "model": self._settings.model,
            "language": _api_language(self._settings.language),
            "response_format": "json",
            "temperature": "0",
        }
        if self._settings.prompt:
            data["prompt"] = self._settings.prompt
        files = {"file": ("dictation.wav", wav_bytes, "audio/wav")}
        url = _url(self._settings.base_url, "/v1/audio/transcriptions")
        if self._http_client is not None:
            return self._http_client.post(url, data=data, files=files)
        with httpx.Client(timeout=self._settings.timeout_seconds) as client:
            return client.post(url, data=data, files=files)


def _pcm_s16le_to_wav(pcm_s16le: bytes, *, sample_rate_hz: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate_hz)
        wav.writeframes(pcm_s16le)
    return buffer.getvalue()


def _api_language(language: str) -> str:
    normalized = language.strip()
    if not normalized or normalized.lower() == "auto":
        return "auto"
    return normalized.split("-", maxsplit=1)[0].lower()


def _transcription_text(payload) -> str:
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        return str(payload.get("text") or "").strip()
    return ""


def _url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
