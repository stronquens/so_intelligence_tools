from __future__ import annotations

import subprocess
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from shutil import which

from so_intelligence_tools.domain.errors import AudioCaptureError, UnsupportedEnvironmentError


def detect_default_monitor_source(*, pactl_bin: str = "pactl") -> str:
    if which(pactl_bin) is None:
        raise UnsupportedEnvironmentError("No se encontró `pactl` para inspeccionar el audio del sistema.")

    default_sink = _run_pactl_and_read_first_line([pactl_bin, "get-default-sink"])
    if default_sink:
        return f"{default_sink}.monitor"

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
        if line.startswith("Default Sink:"):
            default_sink = line.split(":", 1)[1].strip()
            if default_sink:
                return f"{default_sink}.monitor"

    fallback_sink = _parse_first_sink_from_short_list(
        _run_pactl_and_read_full_text([pactl_bin, "list", "short", "sinks"])
    )
    if fallback_sink:
        return f"{fallback_sink}.monitor"

    raise AudioCaptureError("No se pudo detectar el sink por defecto del sistema.")


def _run_pactl_and_read_first_line(command: list[str]) -> str | None:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    first_line = result.stdout.strip().splitlines()
    if not first_line:
        return None
    value = first_line[0].strip()
    return value or None


def _run_pactl_and_read_full_text(command: list[str]) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def _parse_first_sink_from_short_list(output: str) -> str | None:
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            return parts[1].strip() or None
    return None


@dataclass(slots=True)
class LinuxParecAudioCapture:
    sample_rate_hz: int
    chunk_ms: int
    monitor_source: str | None = None
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
            raise UnsupportedEnvironmentError("No se encontró `parec` para capturar audio del sistema.")

        source = self.monitor_source or detect_default_monitor_source(pactl_bin=self.pactl_bin)
        bytes_per_chunk = int(self.sample_rate_hz * (self.chunk_ms / 1000.0) * 2)
        if bytes_per_chunk <= 0:
            raise AudioCaptureError("La configuración de captura produjo un tamaño de chunk inválido.")

        command = [
            self.parec_bin,
            "-d",
            source,
            "--format=s16le",
            "--rate",
            str(self.sample_rate_hz),
            "--channels=1",
            "--latency-msec",
            str(max(self.chunk_ms, 10)),
        ]
        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._callback = callback
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._read_loop,
            args=(bytes_per_chunk,),
            daemon=True,
            name="system-audio-capture",
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
