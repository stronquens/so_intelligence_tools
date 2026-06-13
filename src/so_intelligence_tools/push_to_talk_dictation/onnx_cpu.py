from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.ports.streaming_asr import StreamingAsrEvent, StreamingAsrSession


DEFAULT_ONNX_MODEL_REPO = "onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4"
LANGUAGE_IDS = {
    "es-ES": "2",
    "es-US": "3",
}


@dataclass(slots=True)
class OnnxCpuNemotronSettings:
    model_repo: str = DEFAULT_ONNX_MODEL_REPO
    model_path: str | None = None
    language: str = "es-ES"
    sample_rate_hz: int = 16000
    chunk_samples: int = 8960
    use_vad: bool = False


class OnnxCpuNemotronTranscriber:
    def __init__(self, settings: OnnxCpuNemotronSettings) -> None:
        self._settings = settings
        self._model = None
        self._tokenizer = None
        self._resolved_model_path: Path | None = None

    def check_ready(self) -> None:
        self._resolve_model_path()
        self._load_model()

    def start_session(self) -> StreamingAsrSession:
        self.check_ready()
        return OnnxCpuNemotronSession(
            model=self._model,
            tokenizer=self._tokenizer,
            language_id=self._language_id(),
            use_vad=self._settings.use_vad,
        )

    def _resolve_model_path(self) -> Path:
        if self._resolved_model_path is not None:
            return self._resolved_model_path
        configured_path = self._settings.model_path
        if configured_path:
            path = Path(configured_path).expanduser()
            if not path.exists():
                raise ToolRunnerConfigurationError(
                    f"No se encontró el modelo ONNX de dictado en `{path}`."
                )
            self._resolved_model_path = path
            return path

        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise ToolRunnerConfigurationError(
                "Falta `huggingface-hub` para descargar el modelo ONNX de dictado."
            ) from exc
        path = Path(snapshot_download(repo_id=self._settings.model_repo))
        self._resolved_model_path = path
        return path

    def _load_model(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        try:
            import onnxruntime_genai as og
        except ImportError as exc:
            raise ToolRunnerConfigurationError(
                "Falta `onnxruntime-genai` para ejecutar Nemotron ONNX en CPU."
            ) from exc
        model_path = str(self._resolve_model_path())
        config = og.Config(model_path)
        config.clear_providers()
        self._model = og.Model(config)
        self._tokenizer = og.Tokenizer(self._model)

    def _language_id(self) -> str:
        try:
            return LANGUAGE_IDS[self._settings.language]
        except KeyError as exc:
            raise ToolRunnerConfigurationError(
                f"Idioma de dictado no soportado por la ruta ONNX: {self._settings.language}"
            ) from exc


class OnnxCpuNemotronSession:
    def __init__(self, *, model, tokenizer, language_id: str, use_vad: bool) -> None:
        import onnxruntime_genai as og

        self._model = model
        self._tokenizer = tokenizer
        self._processor = self._model.create_streaming_processor()
        self._processor.set_option("use_vad", "true" if use_vad else "false")
        self._params = og.GeneratorParams(self._model)
        self._generator = og.Generator(self._model, self._params)
        self._generator.set_runtime_option("lang_id", language_id)
        self._token_stream = self._tokenizer.create_stream()
        self._closed = False

    def accept_audio(self, pcm_s16le: bytes):
        if self._closed or not pcm_s16le:
            return []
        audio = np.frombuffer(pcm_s16le, dtype=np.int16).astype(np.float32) / 32768.0
        inputs = self._processor.process(audio)
        if inputs is None:
            return []
        self._generator.set_inputs(inputs)
        return self._drain_final_events()

    def finish(self):
        if self._closed:
            return []
        inputs = self._processor.flush()
        if inputs is None:
            return []
        self._generator.set_inputs(inputs)
        return self._drain_final_events()

    def close(self) -> None:
        self._closed = True

    def _drain_final_events(self) -> list[StreamingAsrEvent]:
        events: list[StreamingAsrEvent] = []
        while not self._generator.is_done():
            self._generator.generate_next_token()
            tokens = self._generator.get_next_tokens()
            if len(tokens) == 0:
                continue
            piece = self._token_stream.decode(tokens[0])
            if piece:
                events.append(StreamingAsrEvent(kind="final", text=piece))
        return events
