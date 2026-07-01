from __future__ import annotations

import io
import json
import os
import threading
import wave
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from huggingface_hub import hf_hub_download
from pydantic import BaseModel, Field


MODEL_REPO = os.getenv("PIPER_TTS_MODEL_REPO", "rhasspy/piper-voices")
MODEL_FILE = os.getenv(
    "PIPER_TTS_MODEL_FILE",
    "es/es_ES/davefx/medium/es_ES-davefx-medium.onnx",
)
CONFIG_FILE = os.getenv(
    "PIPER_TTS_CONFIG_FILE",
    "es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json",
)
MODEL_DIR = Path(os.getenv("PIPER_TTS_MODEL_DIR", "/var/lib/piper-tts/models"))


@dataclass(slots=True)
class VoiceDefinition:
    name: str
    model_repo: str
    model_file: str
    config_file: str


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    voice: str | None = None
    speaker: int | None = None
    speed: float = Field(default=1.0, gt=0.2, le=3.0)


class PiperRuntime:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._voices: dict[str, object] = {}
        self._sample_rates: dict[str, int] = {}
        self._definitions: dict[str, VoiceDefinition] = {}
        self._model_paths: dict[str, Path] = {}
        self._config_paths: dict[str, Path] = {}

    @property
    def ready(self) -> bool:
        return bool(self._voices)

    @property
    def voice_names(self) -> list[str]:
        return sorted(self._definitions)

    def sample_rate(self, voice_name: str = "default") -> int | None:
        return self._sample_rates.get(self._resolve_voice_name(voice_name))

    def load(self) -> None:
        from piper.voice import PiperVoice

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self._definitions = _load_voice_definitions()
        for name, definition in self._definitions.items():
            model_path = Path(
                hf_hub_download(
                    definition.model_repo,
                    filename=definition.model_file,
                    local_dir=MODEL_DIR,
                    local_dir_use_symlinks=False,
                )
            )
            config_path = Path(
                hf_hub_download(
                    definition.model_repo,
                    filename=definition.config_file,
                    local_dir=MODEL_DIR,
                    local_dir_use_symlinks=False,
                )
            )
            voice = PiperVoice.load(str(model_path), config_path=str(config_path))
            self._voices[name] = voice
            self._sample_rates[name] = int(
                getattr(getattr(voice, "config", None), "sample_rate", 22050)
            )
            self._model_paths[name] = model_path
            self._config_paths[name] = config_path

    def synthesize(
        self,
        text: str,
        *,
        voice_name: str = "default",
        speaker: int | None = None,
        speed: float = 1.0,
    ) -> bytes:
        selected_voice_name = self._resolve_voice_name(voice_name)
        voice = self._voices.get(selected_voice_name)
        if voice is None:
            raise KeyError(selected_voice_name)
        from piper.config import SynthesisConfig

        buffer = io.BytesIO()
        with self._lock:
            with wave.open(buffer, "wb") as wav_file:
                voice.synthesize_wav(
                    text,
                    wav_file,
                    syn_config=SynthesisConfig(
                        speaker_id=speaker,
                        length_scale=1.0 / speed,
                    ),
                )
                if wav_file.getnframes() <= 0:
                    raise RuntimeError("Piper returned empty audio")
        return buffer.getvalue()

    def _resolve_voice_name(self, voice_name: str | None) -> str:
        selected = (voice_name or "default").strip().lower()
        aliases = {"": "default", "hombre": "male", "mujer": "female"}
        selected = aliases.get(selected, selected)
        if selected in self._voices or selected in self._definitions:
            return selected
        if selected == "male" and "default" in self._voices:
            return "default"
        raise KeyError(selected)


def _load_voice_definitions() -> dict[str, VoiceDefinition]:
    definitions: dict[str, VoiceDefinition] = {
        "default": VoiceDefinition(
            name="default",
            model_repo=MODEL_REPO,
            model_file=MODEL_FILE,
            config_file=CONFIG_FILE,
        ),
        "male": VoiceDefinition(
            name="male",
            model_repo=MODEL_REPO,
            model_file=MODEL_FILE,
            config_file=CONFIG_FILE,
        ),
    }
    raw = os.getenv("PIPER_TTS_VOICES_JSON")
    if not raw:
        return definitions
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("PIPER_TTS_VOICES_JSON must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("PIPER_TTS_VOICES_JSON must be a JSON object")
    for name, value in payload.items():
        if not isinstance(value, dict):
            raise RuntimeError(f"Voice {name!r} must be a JSON object")
        voice_name = str(name).strip().lower()
        definitions[voice_name] = VoiceDefinition(
            name=voice_name,
            model_repo=str(value.get("model_repo") or MODEL_REPO),
            model_file=str(value["model_file"]),
            config_file=str(value["config_file"]),
        )
    return definitions


runtime = PiperRuntime()
app = FastAPI(title="so_intelligence_tools Piper TTS")


@app.on_event("startup")
def startup() -> None:
    runtime.load()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok" if runtime.ready else "loading",
        "model_repo": MODEL_REPO,
        "model_file": MODEL_FILE,
        "config_file": CONFIG_FILE,
        "sample_rate": runtime.sample_rate(),
        "voices": runtime.voice_names,
    }


@app.post("/v1/audio/speech")
def speech(request: SpeechRequest) -> Response:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail={"error": "text must not be empty"})
    voice_name = request.voice or "default"
    if not runtime.ready:
        raise HTTPException(
            status_code=503,
            detail={"error": "Piper voices are not loaded"},
        )
    try:
        audio = runtime.synthesize(
            text,
            voice_name=voice_name,
            speaker=request.speaker,
            speed=request.speed,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"unknown voice: {exc.args[0]}",
                "available_voices": runtime.voice_names,
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    return Response(content=audio, media_type="audio/wav")
