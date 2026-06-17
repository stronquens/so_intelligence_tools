from __future__ import annotations

import subprocess
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from shutil import which

from so_intelligence_tools.domain.errors import AudioCaptureError, UnsupportedEnvironmentError


def detect_default_microphone_source(*, pactl_bin: str = "pactl") -> str | None:
    if which(pactl_bin) is None:
        return None
    result = subprocess.run(
        [pactl_bin, "get-default-source"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        source = result.stdout.strip()
        if source:
            return source
    return None


@dataclass(slots=True)
class LinuxParecMicrophoneCapture:
    sample_rate_hz: int
    chunk_ms: int
    callback: Callable[[bytes], None]
    source_name: str | None = None
    parec_bin: str = "parec"
    pactl_bin: str = "pactl"
    _process: subprocess.Popen[bytes] | None = field(init=False, default=None)
    _stop_event: threading.Event = field(init=False, default_factory=threading.Event)
    _thread: threading.Thread | None = field(init=False, default=None)

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.running:
            return
        if which(self.parec_bin) is None:
            raise UnsupportedEnvironmentError("No se encontró `parec` para capturar el micrófono.")

        source = self.source_name or detect_default_microphone_source(pactl_bin=self.pactl_bin)
        bytes_per_chunk = int(self.sample_rate_hz * (self.chunk_ms / 1000.0) * 2)
        if bytes_per_chunk <= 0:
            raise AudioCaptureError("La configuración de dictado produjo un tamaño de chunk inválido.")

        command = [
            self.parec_bin,
            "--format=s16le",
            "--rate",
            str(self.sample_rate_hz),
            "--channels=1",
            "--latency-msec",
            str(max(self.chunk_ms, 10)),
        ]
        if source:
            command[1:1] = ["-d", source]

        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._read_loop,
            args=(bytes_per_chunk,),
            daemon=True,
            name="push-to-talk-dictation-capture",
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

    def _read_loop(self, bytes_per_chunk: int) -> None:
        process = self._process
        if process is None or process.stdout is None:
            return

        while not self._stop_event.is_set():
            chunk = process.stdout.read(bytes_per_chunk)
            if not chunk:
                break
            self.callback(chunk)


@dataclass(slots=True)
class WindowsSoundDeviceMicrophoneCapture:
    sample_rate_hz: int
    chunk_ms: int
    callback: Callable[[bytes], None]
    source_name: str | None = None
    _stream: object | None = field(init=False, default=None)

    @property
    def running(self) -> bool:
        return self._stream is not None

    def start(self) -> None:
        if self.running:
            return
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise UnsupportedEnvironmentError(
                "Falta `sounddevice` para capturar el microfono en Windows."
            ) from exc

        blocksize = int(self.sample_rate_hz * (self.chunk_ms / 1000.0))
        if blocksize <= 0:
            raise AudioCaptureError(
                "La configuracion de dictado produjo un tamano de chunk invalido."
            )

        try:
            stream = sd.InputStream(
                samplerate=self.sample_rate_hz,
                channels=1,
                dtype="int16",
                blocksize=blocksize,
                device=_sounddevice_device(self.source_name),
                callback=self._audio_callback,
            )
            stream.start()
        except Exception as exc:
            raise AudioCaptureError(
                f"No se pudo iniciar la captura de microfono Windows: {exc}"
            ) from exc
        self._stream = stream

    def stop(self) -> None:
        stream = self._stream
        self._stream = None
        if stream is None:
            return
        stop = getattr(stream, "stop")
        close = getattr(stream, "close")
        stop()
        close()

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        if status:
            # PortAudio status flags are diagnostic; keep capture alive.
            pass
        if indata is None:
            return
        self.callback(indata.copy().tobytes())


def _sounddevice_device(source_name: str | None):
    if source_name is None or source_name == "":
        return None
    stripped = source_name.strip()
    if stripped.isdigit():
        return int(stripped)
    return stripped
