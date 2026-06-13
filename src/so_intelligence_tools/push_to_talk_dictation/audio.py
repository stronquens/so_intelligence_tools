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
