from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import subprocess
import threading
from shutil import which

from so_intelligence_tools.domain.errors import AudioCaptureError, UnsupportedEnvironmentError


def detect_default_source(*, pactl_bin: str = "pactl") -> str:
    if which(pactl_bin) is None:
        raise UnsupportedEnvironmentError("No se encontró `pactl` para inspeccionar el micrófono.")

    default_source = _run_pactl_and_read_first_line([pactl_bin, "get-default-source"])
    if default_source:
        return default_source

    result = subprocess.run(
        [pactl_bin, "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AudioCaptureError(
            f"No se pudo consultar `pactl info`: {(result.stderr or result.stdout).strip()}"
        )

    for line in result.stdout.splitlines():
        if line.startswith("Default Source:"):
            default_source = line.split(":", 1)[1].strip()
            if default_source:
                return default_source

    fallback_source = _parse_first_physical_source_from_short_list(
        _run_pactl_and_read_full_text([pactl_bin, "list", "short", "sources"])
    )
    if fallback_source:
        return fallback_source

    raise AudioCaptureError("No se pudo detectar el micrófono por defecto del sistema.")


def _run_pactl_and_read_first_line(command: list[str]) -> str | None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return None
    lines = result.stdout.strip().splitlines()
    if not lines:
        return None
    return lines[0].strip() or None


def _run_pactl_and_read_full_text(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout


def _parse_first_physical_source_from_short_list(output: str) -> str | None:
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        source = parts[1].strip()
        if source and not source.endswith(".monitor"):
            return source
    return None


@dataclass(slots=True)
class LinuxMicrophoneAudioCapture:
    sample_rate_hz: int
    chunk_ms: int
    source: str | None = None
    parec_bin: str = "parec"
    pactl_bin: str = "pactl"
    _process: subprocess.Popen[bytes] | None = field(init=False, default=None)
    _stop_event: threading.Event = field(init=False, default_factory=threading.Event)
    _thread: threading.Thread | None = field(init=False, default=None)
    _callback: Callable[[bytes], None] | None = field(init=False, default=None)

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, callback: Callable[[bytes], None]) -> None:
        if self.running:
            return
        if which(self.parec_bin) is None:
            raise UnsupportedEnvironmentError("No se encontró `parec` para capturar el micrófono.")

        source = self.source or detect_default_source(pactl_bin=self.pactl_bin)
        bytes_per_chunk = int(self.sample_rate_hz * (self.chunk_ms / 1000.0) * 2)
        if bytes_per_chunk <= 0:
            raise AudioCaptureError("La configuración produjo un chunk de micrófono inválido.")

        self._process = subprocess.Popen(
            [
                self.parec_bin,
                "-d",
                source,
                "--format=s16le",
                "--rate",
                str(self.sample_rate_hz),
                "--channels=1",
                "--latency-msec",
                str(max(self.chunk_ms, 10)),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._callback = callback
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._read_loop,
            args=(bytes_per_chunk,),
            daemon=True,
            name="voice-translation-microphone-capture",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        process = self._process
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                process.kill()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2.0)
        self._process = None
        self._thread = None
        self._callback = None

    def _read_loop(self, bytes_per_chunk: int) -> None:
        process = self._process
        callback = self._callback
        if process is None or process.stdout is None or callback is None:
            return
        while not self._stop_event.is_set():
            chunk = process.stdout.read(bytes_per_chunk)
            if not chunk:
                break
            callback(chunk)


@dataclass(slots=True)
class PulseAudioPcmPlayback:
    sink_name: str
    sample_rate_hz: int
    channels: int = 1
    pacat_bin: str = "pacat"
    _playback: subprocess.Popen[bytes] | None = field(init=False, default=None)

    @property
    def running(self) -> bool:
        return self._playback is not None and self._playback.poll() is None

    def start(self) -> None:
        if self.running:
            return
        if which(self.pacat_bin) is None:
            raise UnsupportedEnvironmentError("No se encontró `pacat` para escribir audio.")
        self._playback = subprocess.Popen(
            [
                self.pacat_bin,
                "--device",
                self.sink_name,
                "--format=s16le",
                "--rate",
                str(self.sample_rate_hz),
                "--channels",
                str(self.channels),
                "--latency-msec",
                "40",
            ],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def write(self, pcm_bytes: bytes) -> None:
        if not pcm_bytes:
            return
        playback = self._playback
        if playback is None or playback.stdin is None or playback.poll() is not None:
            raise AudioCaptureError("El sink virtual no está aceptando audio.")
        try:
            playback.stdin.write(pcm_bytes)
            playback.stdin.flush()
        except BrokenPipeError as exc:
            raise AudioCaptureError("La salida hacia el micrófono virtual se cerró.") from exc

    def stop(self) -> None:
        playback = self._playback
        if playback is not None:
            if playback.stdin is not None:
                try:
                    playback.stdin.close()
                except OSError:
                    pass
            if playback.poll() is None:
                playback.terminate()
                try:
                    playback.wait(timeout=1.5)
                except subprocess.TimeoutExpired:
                    playback.kill()
        self._playback = None


@dataclass(slots=True)
class PulseAudioMonitorWavRecorder:
    monitor_source_name: str
    sample_rate_hz: int
    recordings_dir: Path
    channels: int = 1
    parecord_bin: str = "parecord"
    file_prefix: str = "voice-translation-final-output"
    _process: subprocess.Popen[bytes] | None = field(init=False, default=None)
    recording_path: Path | None = field(init=False, default=None)

    @property
    def running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> Path:
        if self.running and self.recording_path is not None:
            return self.recording_path
        if which(self.parecord_bin) is None:
            raise UnsupportedEnvironmentError("No se encontró `parecord` para grabar debug WAV.")

        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.recording_path = self.recordings_dir / f"{self.file_prefix}-{timestamp}.wav"
        self._process = subprocess.Popen(
            [
                self.parecord_bin,
                "-d",
                self.monitor_source_name,
                "--format=s16le",
                "--rate",
                str(self.sample_rate_hz),
                "--channels",
                str(self.channels),
                "--file-format=wav",
                str(self.recording_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        return self.recording_path

    def stop(self) -> Path | None:
        process = self._process
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
        self._process = None
        return self.recording_path


@dataclass(slots=True)
class PulseAudioVirtualMicrophone:
    sink_name: str
    sample_rate_hz: int
    channels: int = 1
    pactl_bin: str = "pactl"
    pacat_bin: str = "pacat"
    description: str = "SO_AI_Translated_Microphone"
    _module_id: str | None = field(init=False, default=None)
    _playback: PulseAudioPcmPlayback | None = field(init=False, default=None)

    @property
    def monitor_source_name(self) -> str:
        return f"{self.sink_name}.monitor"

    @property
    def running(self) -> bool:
        return self._playback is not None and self._playback.running

    def start(self) -> None:
        self._ensure_tooling()
        if self._module_id is None:
            self._module_id = self._load_null_sink()
        if self._playback is None:
            self._playback = PulseAudioPcmPlayback(
                sink_name=self.sink_name,
                sample_rate_hz=self.sample_rate_hz,
                channels=self.channels,
                pacat_bin=self.pacat_bin,
            )
        self._playback.start()

    def write(self, pcm_bytes: bytes) -> None:
        if self._playback is None:
            raise AudioCaptureError("El sink virtual no está aceptando audio.")
        self._playback.write(pcm_bytes)

    def stop(self) -> None:
        if self._playback is not None:
            self._playback.stop()
            self._playback = None
        if self._module_id is not None:
            subprocess.run(
                [self.pactl_bin, "unload-module", self._module_id],
                capture_output=True,
                text=True,
                check=False,
            )
        self._module_id = None

    def _ensure_tooling(self) -> None:
        missing = [tool for tool in (self.pactl_bin, self.pacat_bin) if which(tool) is None]
        if missing:
            raise UnsupportedEnvironmentError(
                "Faltan dependencias de audio para el micrófono virtual: "
                + ", ".join(f"`{tool}`" for tool in missing)
            )

    def _load_null_sink(self) -> str:
        result = subprocess.run(
            [
                self.pactl_bin,
                "load-module",
                "module-null-sink",
                f"sink_name={self.sink_name}",
                "format=s16le",
                f"rate={self.sample_rate_hz}",
                f"channels={self.channels}",
                f"sink_properties=device.description={self.description}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise AudioCaptureError(
                "No se pudo crear el micrófono virtual: "
                + (result.stderr or result.stdout).strip()
            )
        module_id = result.stdout.strip()
        if not module_id:
            raise AudioCaptureError("PulseAudio no devolvió ID para el módulo virtual.")
        return module_id


@dataclass(slots=True)
class MicrophonePassthroughToVirtualMicrophone:
    capture: LinuxMicrophoneAudioCapture
    playback: PulseAudioPcmPlayback
    volume: float = 1.0
    on_audio_forwarded: Callable[[int, int, float], None] | None = None
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _chunk_count: int = field(init=False, default=0)
    _byte_count: int = field(init=False, default=0)

    @property
    def running(self) -> bool:
        return self.capture.running and self.playback.running

    def start(self) -> None:
        self._chunk_count = 0
        self._byte_count = 0
        self.playback.start()
        self.capture.start(self._on_audio_chunk)

    def stop(self) -> None:
        self.capture.stop()
        self.playback.stop()

    def set_volume(self, volume: float) -> None:
        with self._lock:
            self.volume = max(volume, 0.0)

    def _on_audio_chunk(self, chunk: bytes) -> None:
        with self._lock:
            volume = self.volume
        self.playback.write(scale_pcm_s16le(chunk, volume))
        self._chunk_count += 1
        self._byte_count += len(chunk)
        if self.on_audio_forwarded is not None:
            self.on_audio_forwarded(self._chunk_count, self._byte_count, volume)


def scale_pcm_s16le(pcm_bytes: bytes, volume: float) -> bytes:
    if not pcm_bytes or volume == 1.0:
        return pcm_bytes
    if volume < 0:
        volume = 0.0
    scaled = bytearray(len(pcm_bytes))
    usable_length = len(pcm_bytes) - (len(pcm_bytes) % 2)
    for index in range(0, usable_length, 2):
        sample = int.from_bytes(pcm_bytes[index : index + 2], "little", signed=True)
        adjusted = int(sample * volume)
        adjusted = max(min(adjusted, 32767), -32768)
        scaled[index : index + 2] = adjusted.to_bytes(2, "little", signed=True)
    if usable_length < len(pcm_bytes):
        scaled[-1] = pcm_bytes[-1]
    return bytes(scaled)
