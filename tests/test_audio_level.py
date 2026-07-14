from so_intelligence_tools.audio_level import normalized_pcm_s16le_rms


def test_normalized_pcm_level_tracks_silence_and_amplitude() -> None:
    silence = b"\x00\x00" * 8
    medium = (8192).to_bytes(2, "little", signed=True) * 8
    maximum = (32767).to_bytes(2, "little", signed=True) * 8

    assert normalized_pcm_s16le_rms(silence) == 0.0
    assert 0.24 < normalized_pcm_s16le_rms(medium) < 0.26
    assert 0.99 < normalized_pcm_s16le_rms(maximum) <= 1.0
