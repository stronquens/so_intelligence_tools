from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import librosa
import numpy as np
import onnxruntime as ort
import soundfile as sf
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer


S3GEN_SR = 24000
START_SPEECH_TOKEN = 6561
STOP_SPEECH_TOKEN = 6562
MODEL_ID = "onnx-community/chatterbox-multilingual-ONNX"
EVIDENCE_DIR = Path("/evidence")
OUT_JSON = EVIDENCE_DIR / "onnx-runtime-spike.json"
VOICE_PATH = Path("/app/voices/common_voice_female_es_ref_01_row_410.wav")
MODEL_CACHE_DIR = Path(os.getenv("ONNX_MODEL_CACHE_DIR", "/tmp/chatterbox-onnx-cache"))


class RepetitionPenaltyLogitsProcessor:
    def __init__(self, penalty: float) -> None:
        self.penalty = penalty

    def __call__(self, input_ids: np.ndarray, scores: np.ndarray) -> np.ndarray:
        score = np.take_along_axis(scores, input_ids, axis=1)
        score = np.where(score < 0, score * self.penalty, score / self.penalty)
        scores_processed = scores.copy()
        np.put_along_axis(scores_processed, input_ids, score, axis=1)
        return scores_processed


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


def audio_seconds(path: Path) -> float:
    info = sf.info(str(path))
    return float(info.frames) / float(info.samplerate)


def session(path: str, providers: list[str]) -> ort.InferenceSession:
    return ort.InferenceSession(path, providers=providers)


def prepare_language(text: str, language_id: str = "es") -> str:
    return f"[{language_id.lower()}]{text}"


def load_onnx_sessions(output_dir: Path) -> dict[str, object]:
    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    speech_encoder_path = hf_hub_download(MODEL_ID, "speech_encoder.onnx", local_dir=output_dir, subfolder="onnx")
    hf_hub_download(MODEL_ID, "speech_encoder.onnx_data", local_dir=output_dir, subfolder="onnx")
    embed_tokens_path = hf_hub_download(MODEL_ID, "embed_tokens.onnx", local_dir=output_dir, subfolder="onnx")
    hf_hub_download(MODEL_ID, "embed_tokens.onnx_data", local_dir=output_dir, subfolder="onnx")
    decoder_path = hf_hub_download(MODEL_ID, "conditional_decoder.onnx", local_dir=output_dir, subfolder="onnx")
    hf_hub_download(MODEL_ID, "conditional_decoder.onnx_data", local_dir=output_dir, subfolder="onnx")
    language_model_path = hf_hub_download(MODEL_ID, "language_model.onnx", local_dir=output_dir, subfolder="onnx")
    hf_hub_download(MODEL_ID, "language_model.onnx_data", local_dir=output_dir, subfolder="onnx")

    return {
        "providers_requested": providers,
        "speech_encoder": session(speech_encoder_path, providers),
        "embed_tokens": session(embed_tokens_path, providers),
        "language_model": session(language_model_path, providers),
        "decoder": session(decoder_path, providers),
        "tokenizer": AutoTokenizer.from_pretrained(MODEL_ID),
    }


def synthesize(
    sessions: dict[str, object],
    text: str,
    *,
    label: str,
    exaggeration: float,
    max_new_tokens: int = 384,
) -> dict[str, object]:
    wav_path = EVIDENCE_DIR / f"{label}.wav"
    started = time.perf_counter()

    audio_values, _ = librosa.load(str(VOICE_PATH), sr=S3GEN_SR)
    audio_values = audio_values[np.newaxis, :].astype(np.float32)
    tokenizer = sessions["tokenizer"]
    input_ids = tokenizer(prepare_language(text), return_tensors="np")["input_ids"].astype(np.int64)
    position_ids = np.where(
        input_ids >= START_SPEECH_TOKEN,
        0,
        np.arange(input_ids.shape[1])[np.newaxis, :] - 1,
    )

    embed_inputs = {
        "input_ids": input_ids,
        "position_ids": position_ids.astype(np.int64),
        "exaggeration": np.array([exaggeration], dtype=np.float32),
    }
    processor = RepetitionPenaltyLogitsProcessor(penalty=1.2)
    num_hidden_layers = 30
    num_key_value_heads = 16
    head_dim = 64
    generate_tokens = np.array([[START_SPEECH_TOKEN]])
    prompt_token = None
    ref_x_vector = None
    prompt_feat = None

    for i in range(max_new_tokens):
        inputs_embeds = sessions["embed_tokens"].run(None, embed_inputs)[0]
        if i == 0:
            cond_emb, prompt_token, ref_x_vector, prompt_feat = sessions["speech_encoder"].run(
                None,
                {"audio_values": audio_values},
            )
            inputs_embeds = np.concatenate((cond_emb, inputs_embeds), axis=1)
            batch_size, seq_len, _ = inputs_embeds.shape
            past_key_values = {
                f"past_key_values.{layer}.{kv}": np.zeros(
                    [batch_size, num_key_value_heads, 0, head_dim],
                    dtype=np.float32,
                )
                for layer in range(num_hidden_layers)
                for kv in ("key", "value")
            }
            attention_mask = np.ones((batch_size, seq_len), dtype=np.int64)

        logits, *present_key_values = sessions["language_model"].run(
            None,
            dict(inputs_embeds=inputs_embeds, attention_mask=attention_mask, **past_key_values),
        )
        logits = logits[:, -1, :]
        next_token_logits = processor(generate_tokens, logits)
        next_token = np.argmax(next_token_logits, axis=-1, keepdims=True).astype(np.int64)
        generate_tokens = np.concatenate((generate_tokens, next_token), axis=-1)
        if (next_token.flatten() == STOP_SPEECH_TOKEN).all():
            break

        embed_inputs["input_ids"] = next_token
        embed_inputs["position_ids"] = np.full((input_ids.shape[0], 1), i + 1, dtype=np.int64)
        attention_mask = np.concatenate([attention_mask, np.ones((batch_size, 1), dtype=np.int64)], axis=1)
        for j, key in enumerate(past_key_values):
            past_key_values[key] = present_key_values[j]

    speech_tokens = generate_tokens[:, 1:-1]
    if prompt_token is not None:
        speech_tokens = np.concatenate([prompt_token, speech_tokens], axis=1)
    wav = sessions["decoder"].run(
        None,
        {
            "speech_tokens": speech_tokens,
            "speaker_embeddings": ref_x_vector,
            "speaker_features": prompt_feat,
        },
    )[0]
    wav = np.squeeze(wav, axis=0)
    sf.write(str(wav_path), wav, S3GEN_SR)

    elapsed = time.perf_counter() - started
    duration = audio_seconds(wav_path)
    return {
        "label": label,
        "exaggeration": exaggeration,
        "elapsed_seconds": elapsed,
        "audio_seconds": duration,
        "rtf": elapsed / duration if duration else None,
        "generated_tokens": int(generate_tokens.shape[1] - 2),
        "stopped": bool(generate_tokens[0, -1] == STOP_SPEECH_TOKEN),
        "text_chars": len(text),
        "wav_path": str(wav_path),
        "vram_mib": nvidia_used_mib(),
    }


def main() -> None:
    payload: dict[str, object] = {
        "backend": "onnx-community/chatterbox-multilingual-ONNX",
        "onnxruntime": ort.__version__,
        "available_providers": ort.get_available_providers(),
        "voice_path": str(VOICE_PATH),
        "vram_before_mib": nvidia_used_mib(),
        "results": [],
    }
    try:
        load_started = time.perf_counter()
        payload["model_cache_dir"] = str(MODEL_CACHE_DIR)
        sessions = load_onnx_sessions(MODEL_CACHE_DIR)
        payload["load_seconds"] = time.perf_counter() - load_started
        payload["session_providers"] = {
            name: sess.get_providers()
            for name, sess in sessions.items()
            if hasattr(sess, "get_providers")
        }
        payload["vram_after_load_mib"] = nvidia_used_mib()

        medium = (
            "Prueba de voz en espanol para Codex Desktop. "
            "Quiero una lectura natural, clara y con poca latencia mientras se redacta la respuesta."
        )
        for exaggeration in (0.5, 0.7):
            synthesize(sessions, medium, label=f"onnx_medium_exag_{exaggeration}", exaggeration=exaggeration)
            result = synthesize(
                sessions,
                medium,
                label=f"onnx_medium_measured_exag_{exaggeration}",
                exaggeration=exaggeration,
            )
            payload["results"].append(result)
    except Exception as exc:
        import traceback

        payload["error"] = repr(exc)
        payload["traceback"] = traceback.format_exc()
    finally:
        OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
