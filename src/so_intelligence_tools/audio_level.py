from __future__ import annotations

from array import array
import math
import sys


def normalized_pcm_s16le_rms(pcm_bytes: bytes) -> float:
    """Return the RMS amplitude of mono/stereo s16le PCM in the 0..1 range."""
    usable = len(pcm_bytes) - (len(pcm_bytes) % 2)
    if usable <= 0:
        return 0.0
    samples = array("h")
    samples.frombytes(pcm_bytes[:usable])
    if sys.byteorder != "little":
        samples.byteswap()
    mean_square = sum(sample * sample for sample in samples) / len(samples)
    return min(max(math.sqrt(mean_square) / 32768.0, 0.0), 1.0)
