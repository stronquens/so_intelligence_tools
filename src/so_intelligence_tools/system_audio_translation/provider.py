from __future__ import annotations

import io
import wave
from dataclasses import dataclass

import httpx

from so_intelligence_tools.domain.errors import InferenceUnavailableError
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient


@dataclass(slots=True)
class ChunkedAudioTranslationProvider:
    transcription_base_url: str
    transcription_api_key: str
    transcription_model: str
    inference_client: LocalInferenceClient | None = None
    translation_base_url: str | None = None
    translation_api_key: str | None = None
    translation_model: str | None = None
    timeout_seconds: int = 60
    transport: httpx.BaseTransport | None = None

    def transcribe_and_translate(
        self,
        *,
        pcm_bytes: bytes,
        sample_rate_hz: int,
        source_language: str,
        target_language: str,
    ) -> tuple[str, str]:
        transcript = self.transcribe_pcm(
            pcm_bytes=pcm_bytes,
            sample_rate_hz=sample_rate_hz,
            source_language=source_language,
        )
        if not transcript.strip():
            return "", ""
        translated = self.translate_text(
            transcript=transcript,
            target_language=target_language,
        )
        return transcript, translated

    def transcribe_pcm(
        self,
        *,
        pcm_bytes: bytes,
        sample_rate_hz: int,
        source_language: str,
    ) -> str:
        wav_bytes = pcm16_to_wav_bytes(pcm_bytes=pcm_bytes, sample_rate_hz=sample_rate_hz)
        files = {"file": ("chunk.wav", wav_bytes, "audio/wav")}
        data = {
            "model": self.transcription_model,
            "language": source_language,
            "temperature": "0",
        }
        try:
            with httpx.Client(
                base_url=self.transcription_base_url.rstrip("/"),
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.post(
                    "/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.transcription_api_key}"},
                    data=data,
                    files=files,
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise InferenceUnavailableError(_extract_error_detail(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise InferenceUnavailableError(
                "No se pudo contactar con el backend remoto de transcripción de audio."
            ) from exc

        text = payload.get("text")
        if not isinstance(text, str):
            raise InferenceUnavailableError(
                "El backend remoto de transcripción devolvió una respuesta inválida."
            )
        return text.strip()

    def translate_text(self, *, transcript: str, target_language: str) -> str:
        language_name = "español" if target_language == "es" else target_language
        if self.translation_base_url and self.translation_api_key and self.translation_model:
            return self._translate_via_remote_chat(
                transcript=transcript,
                language_name=language_name,
            )
        if self.inference_client is None:
            raise InferenceUnavailableError(
                "No hay ningún backend disponible para traducir el texto transcrito."
            )
        result = self.inference_client.generate_text(
            prompt=(
                "Traduce el siguiente fragmento de transcripción al "
                f"{language_name}. Devuelve solo la traducción final, sin comentarios ni etiquetas.\n\n"
                f"{transcript}"
            ),
            system_prompt=(
                "Eres un traductor simultáneo. Mantén el significado, sé conciso y no "
                "añadas explicaciones."
            ),
            reasoning_mode="off",
            max_output_tokens=256,
            temperature=0.0,
        )
        return result.content.strip()

    def _translate_via_remote_chat(self, *, transcript: str, language_name: str) -> str:
        payload = {
            "model": self.translation_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un traductor simultáneo. Mantén el significado, sé conciso y no "
                        "añadas explicaciones."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Traduce el siguiente fragmento de transcripción al "
                        f"{language_name}. Devuelve solo la traducción final, sin comentarios ni etiquetas.\n\n"
                        f"{transcript}"
                    ),
                },
            ],
            "temperature": 0.0,
            "max_tokens": 256,
        }
        try:
            with httpx.Client(
                base_url=self.translation_base_url.rstrip("/"),
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.post(
                    "/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.translation_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            raise InferenceUnavailableError(_extract_error_detail(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise InferenceUnavailableError(
                "No se pudo contactar con el backend remoto de traducción de texto."
            ) from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise InferenceUnavailableError(
                "El backend remoto de traducción devolvió una respuesta inválida."
            ) from exc
        return str(content).strip()


def pcm16_to_wav_bytes(*, pcm_bytes: bytes, sample_rate_hz: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(pcm_bytes)
    return buffer.getvalue()


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "El backend remoto devolvió un error."
    if isinstance(payload, dict):
        return (
            payload.get("detail")
            or payload.get("error")
            or response.text
            or "El backend remoto devolvió un error."
        )
    return response.text or "El backend remoto devolvió un error."
