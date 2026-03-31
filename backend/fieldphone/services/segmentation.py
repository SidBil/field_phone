"""Audio segmentation for token boundary detection."""

import numpy as np
import soundfile as sf
import librosa


def detect_silence_boundaries(
    audio_path: str,
    threshold_db: float = -40.0,
    min_silence_ms: int = 200,
    min_token_ms: int = 100,
) -> list[tuple[float, float]]:
    """Run silence detection on a recording, returning (start_s, end_s) for each token."""
    y, sr = librosa.load(audio_path, sr=None)

    # Convert to dB-scaled amplitude envelope
    frame_length = int(sr * 0.025)  # 25ms frames
    hop_length = int(sr * 0.010)  # 10ms hop
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)

    # Find non-silent frames
    is_sound = rms_db > threshold_db

    # Convert frame indices to time
    times = librosa.frames_to_time(np.arange(len(rms_db)), sr=sr, hop_length=hop_length)

    # Find contiguous regions of sound
    boundaries = []
    in_token = False
    token_start = 0.0
    silence_start = 0.0
    min_silence_s = min_silence_ms / 1000.0
    min_token_s = min_token_ms / 1000.0

    for i, (t, sound) in enumerate(zip(times, is_sound)):
        if sound and not in_token:
            # Starting a new token
            if not boundaries or (t - silence_start) >= min_silence_s:
                token_start = t
                in_token = True
            else:
                # Silence too short — merge with previous token
                if boundaries:
                    token_start = boundaries.pop()[0]
                else:
                    token_start = t
                in_token = True
        elif not sound and in_token:
            silence_start = t
            in_token = False
            duration = t - token_start
            if duration >= min_token_s:
                boundaries.append((token_start, t))

    # Handle case where audio ends during a token
    if in_token:
        duration = times[-1] - token_start
        if duration >= min_token_s:
            boundaries.append((token_start, float(times[-1])))

    return boundaries


def extract_token(
    audio_path: str,
    start_s: float,
    end_s: float,
    output_path: str,
) -> str:
    """Extract a segment from a recording and write it to disk."""
    y, sr = librosa.load(audio_path, sr=None)
    start_sample = int(start_s * sr)
    end_sample = int(end_s * sr)
    segment = y[start_sample:end_sample]
    sf.write(output_path, segment, sr)
    return output_path
