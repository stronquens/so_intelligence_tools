from __future__ import annotations

import io
import os
import shutil
import subprocess
import threading
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from huggingface_hub import snapshot_download
from pydantic import BaseModel, Field
from safetensors.torch import load_file as load_safetensors

from chatterbox.models.s3gen import S3Gen
from chatterbox.models.t3 import T3
from chatterbox.models.t3.modules.t3_config import T3Config
from chatterbox.models.tokenizers import MTLTokenizer
from chatterbox.models.voice_encoder import VoiceEncoder
from chatterbox.mtl_tts import ChatterboxMultilingualTTS, Conditionals


MODEL_REPO = os.getenv("CHATTERBOX_TTS_MODEL_REPO", "ResembleAI/chatterbox")
ES_ES_REPO = os.getenv(
    "CHATTERBOX_TTS_ES_ES_REPO",
    "ResembleAI/Chatterbox-Multilingual-es-es",
)
MODEL_DIR = Path(os.getenv("CHATTERBOX_TTS_MODEL_DIR", "/var/lib/chatterbox-tts/models"))
DEVICE = os.getenv("CHATTERBOX_TTS_DEVICE", "cuda").strip().lower()
DEFAULT_VOICE = os.getenv("CHATTERBOX_TTS_DEFAULT_VOICE", "female").strip().lower()


@dataclass(slots=True)
class VoicePreset:
    name: str
    audio_prompt_path: str | None
    exaggeration: float
    cfg_weight: float
    temperature: float
    description: str


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    voice: str | None = None
    exaggeration: float | None = Field(default=None, ge=0.0, le=2.0)
    cfg_weight: float | None = Field(default=None, ge=0.0, le=2.0)
    temperature: float | None = Field(default=None, gt=0.0, le=2.0)
    response_format: str = "wav"


class ChatterboxRuntime:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._model: ChatterboxMultilingualTTS | None = None
        self._load_notes = ""
        self._device = self._resolve_device()
        self._voices = self._load_voice_presets()
        self._metrics: dict[str, Any] = {
            "requests_total": 0,
            "successful_requests_total": 0,
            "failures_total": 0,
            "synthesis_seconds_total": 0.0,
            "audio_seconds_total": 0.0,
            "realtime_factor_total": 0.0,
            "last_synthesis_seconds": None,
            "last_audio_seconds": None,
            "last_realtime_factor": None,
            "last_voice": None,
            "last_vram_mib": None,
            "voices": {name: {"requests": 0, "failures": 0} for name in self._voices},
        }

    @property
    def ready(self) -> bool:
        return self._model is not None

    @property
    def voice_names(self) -> list[str]:
        return sorted(self._voices)

    def load(self) -> None:
        ckpt_dir = self._prepare_checkpoint()
        self._model, self._load_notes = self._load_model(ckpt_dir)

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.ready else "loading",
            "backend": "chatterbox",
            "model_repo": MODEL_REPO,
            "es_es_repo": ES_ES_REPO,
            "device": self._device,
            "sample_rate": self._model.sr if self._model is not None else None,
            "default_voice": DEFAULT_VOICE,
            "voices": {
                name: {
                    "description": preset.description,
                    "has_audio_prompt": preset.audio_prompt_path is not None,
                    "exaggeration": preset.exaggeration,
                    "cfg_weight": preset.cfg_weight,
                    "temperature": preset.temperature,
                }
                for name, preset in self._voices.items()
            },
            "load_notes": self._load_notes,
            "vram_mib": nvidia_used_mib(),
        }

    def metrics(self) -> dict[str, Any]:
        payload = dict(self._metrics)
        successful_requests_total = int(payload["successful_requests_total"])
        payload["average_synthesis_seconds"] = (
            payload["synthesis_seconds_total"] / successful_requests_total
            if successful_requests_total
            else None
        )
        payload["average_audio_seconds"] = (
            payload["audio_seconds_total"] / successful_requests_total
            if successful_requests_total
            else None
        )
        payload["average_realtime_factor"] = (
            payload["realtime_factor_total"] / successful_requests_total
            if successful_requests_total
            else None
        )
        payload["current_vram_mib"] = nvidia_used_mib()
        return payload

    def synthesize(
        self,
        text: str,
        *,
        voice_name: str | None,
        exaggeration: float | None,
        cfg_weight: float | None,
        temperature: float | None,
    ) -> bytes:
        if self._model is None:
            raise RuntimeError("Chatterbox model is not loaded")
        preset_name = self._resolve_voice_name(voice_name)
        preset = self._voices[preset_name]
        started = time.perf_counter()
        try:
            with self._lock:
                wav = self._model.generate(
                    text,
                    language_id="es",
                    audio_prompt_path=preset.audio_prompt_path,
                    exaggeration=preset.exaggeration if exaggeration is None else exaggeration,
                    cfg_weight=preset.cfg_weight if cfg_weight is None else cfg_weight,
                    temperature=preset.temperature if temperature is None else temperature,
                )
            synthesis_seconds = time.perf_counter() - started
            audio_seconds = float(wav.shape[-1]) / float(self._model.sr)
            realtime_factor = synthesis_seconds / audio_seconds if audio_seconds else None
            self._record_success(
                preset_name,
                synthesis_seconds=synthesis_seconds,
                audio_seconds=audio_seconds,
                realtime_factor=realtime_factor,
            )
            return tensor_to_wav_bytes(wav, self._model.sr)
        except Exception:
            self._record_failure(preset_name)
            raise

    def _prepare_checkpoint(self) -> Path:
        base_dir = Path(
            snapshot_download(
                MODEL_REPO,
                repo_type="model",
                revision="main",
                local_dir=MODEL_DIR / "base",
                allow_patterns=[
                    "ve.pt",
                    "s3gen.pt",
                    "conds.pt",
                    "grapheme_mtl_merged_expanded_v1.json",
                ],
            )
        )
        es_dir = Path(
            snapshot_download(
                ES_ES_REPO,
                repo_type="model",
                revision="main",
                local_dir=MODEL_DIR / "es-es",
                allow_patterns=[
                    "t3_es_es.safetensors",
                    "s3gen_v3.pt",
                    "grapheme_mtl_merged_expanded_v1.json",
                ],
            )
        )
        combined = MODEL_DIR / "es-es-combined"
        combined.mkdir(parents=True, exist_ok=True)
        copy_if_needed(base_dir / "ve.pt", combined / "ve.pt")
        copy_if_needed(base_dir / "conds.pt", combined / "conds.pt")
        copy_if_needed(es_dir / "t3_es_es.safetensors", combined / "t3_es_es.safetensors")
        copy_if_needed(es_dir / "s3gen_v3.pt", combined / "s3gen.pt")
        copy_if_needed(
            es_dir / "grapheme_mtl_merged_expanded_v1.json",
            combined / "grapheme_mtl_merged_expanded_v1.json",
        )
        return combined

    def _load_model(self, ckpt_dir: Path) -> tuple[ChatterboxMultilingualTTS, str]:
        map_location = torch.device("cpu") if self._device in {"cpu", "mps"} else None

        ve = VoiceEncoder()
        ve.load_state_dict(torch.load(ckpt_dir / "ve.pt", map_location=map_location, weights_only=True))
        ve.to(self._device).eval()

        t3 = T3(T3Config.multilingual())
        t3_state = load_safetensors(ckpt_dir / "t3_es_es.safetensors")
        if "model" in t3_state.keys():
            t3_state = t3_state["model"][0]
        t3.load_state_dict(t3_state)
        t3.to(self._device).eval()

        s3gen = S3Gen()
        s3_state = torch.load(ckpt_dir / "s3gen.pt", map_location=map_location, weights_only=True)
        missing, unexpected = s3gen.load_state_dict(s3_state, strict=False)
        s3gen.to(self._device).eval()

        tokenizer = MTLTokenizer(str(ckpt_dir / "grapheme_mtl_merged_expanded_v1.json"))
        conds = Conditionals.load(ckpt_dir / "conds.pt", map_location=map_location).to(self._device)
        model = ChatterboxMultilingualTTS(t3, s3gen, ve, tokenizer, self._device, conds=conds)
        notes = (
            "Loaded es-ES single-language pack with S3Gen strict=False; "
            f"missing={list(missing)} unexpected={list(unexpected)}."
        )
        return model, notes

    def _resolve_voice_name(self, voice_name: str | None) -> str:
        selected = (voice_name or DEFAULT_VOICE or "female").strip().lower()
        aliases = {"": DEFAULT_VOICE, "default": DEFAULT_VOICE, "hombre": "male", "mujer": "female"}
        selected = aliases.get(selected, selected)
        if selected not in self._voices:
            raise KeyError(selected)
        return selected

    def _record_success(
        self,
        voice_name: str,
        *,
        synthesis_seconds: float,
        audio_seconds: float,
        realtime_factor: float | None,
    ) -> None:
        self._metrics["requests_total"] += 1
        self._metrics["successful_requests_total"] += 1
        self._metrics["synthesis_seconds_total"] += synthesis_seconds
        self._metrics["audio_seconds_total"] += audio_seconds
        if realtime_factor is not None:
            self._metrics["realtime_factor_total"] += realtime_factor
        self._metrics["last_synthesis_seconds"] = synthesis_seconds
        self._metrics["last_audio_seconds"] = audio_seconds
        self._metrics["last_realtime_factor"] = realtime_factor
        self._metrics["last_voice"] = voice_name
        self._metrics["last_vram_mib"] = nvidia_used_mib()
        self._metrics["voices"][voice_name]["requests"] += 1

    def _record_failure(self, voice_name: str) -> None:
        self._metrics["requests_total"] += 1
        self._metrics["failures_total"] += 1
        self._metrics["last_voice"] = voice_name
        self._metrics["last_vram_mib"] = nvidia_used_mib()
        self._metrics["voices"][voice_name]["failures"] += 1

    @staticmethod
    def _resolve_device() -> str:
        requested = DEVICE
        if requested == "cuda" and not torch.cuda.is_available():
            return "cpu"
        return requested

    @staticmethod
    def _load_voice_presets() -> dict[str, VoicePreset]:
        female_reference = os.getenv(
            "CHATTERBOX_TTS_FEMALE_REFERENCE",
            "/app/voices/common_voice_female_es_ref_01_row_410.wav",
        )
        return {
            "male": VoicePreset(
                name="male",
                audio_prompt_path=None,
                exaggeration=float(os.getenv("CHATTERBOX_TTS_MALE_EXAGGERATION", "0.5")),
                cfg_weight=float(os.getenv("CHATTERBOX_TTS_MALE_CFG_WEIGHT", "0.5")),
                temperature=float(os.getenv("CHATTERBOX_TTS_MALE_TEMPERATURE", "0.8")),
                description="Built-in Chatterbox es-ES conditioning.",
            ),
            "female": VoicePreset(
                name="female",
                audio_prompt_path=female_reference,
                exaggeration=float(os.getenv("CHATTERBOX_TTS_FEMALE_EXAGGERATION", "0.65")),
                cfg_weight=float(os.getenv("CHATTERBOX_TTS_FEMALE_CFG_WEIGHT", "0.35")),
                temperature=float(os.getenv("CHATTERBOX_TTS_FEMALE_TEMPERATURE", "0.75")),
                description="User-selected Common Voice female Spanish clone, warm preset.",
            ),
        }


runtime = ChatterboxRuntime()
app = FastAPI(title="so_intelligence_tools Chatterbox TTS")


@app.on_event("startup")
def startup() -> None:
    runtime.load()


@app.get("/health")
def health() -> dict[str, Any]:
    return runtime.health()


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    return runtime.metrics()


@app.post("/v1/audio/speech")
def speech(request: SpeechRequest) -> Response:
    if request.response_format != "wav":
        raise HTTPException(
            status_code=400,
            detail={"error": "only wav response_format is supported"},
        )
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail={"error": "text must not be empty"})
    if not runtime.ready:
        raise HTTPException(
            status_code=503,
            detail={"error": "Chatterbox model is not loaded"},
        )
    try:
        audio = runtime.synthesize(
            text,
            voice_name=request.voice,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight,
            temperature=request.temperature,
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


def tensor_to_wav_bytes(wav: torch.Tensor, sample_rate: int) -> bytes:
    samples = wav.detach().cpu().squeeze(0).clamp(-1.0, 1.0)
    pcm = (samples * 32767.0).to(torch.int16).numpy()
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return buffer.getvalue()


def copy_if_needed(source: Path, target: Path) -> None:
    if not target.exists() or target.stat().st_size != source.stat().st_size:
        shutil.copy2(source, target)


def nvidia_used_mib() -> int | None:
    try:
        completed = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            check=True,
            text=True,
            capture_output=True,
            timeout=5,
        )
    except Exception:
        return None
    line = completed.stdout.strip().splitlines()[0].strip()
    return int(line) if line else None
