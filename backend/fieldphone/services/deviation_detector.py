"""Script deviation detection for classifying audio segments."""

import numpy as np
import librosa


def classify_segment(
    audio_path: str,
    start_s: float,
    end_s: float,
) -> tuple[str, float]:
    """Classify an audio segment as scripted word-list reading or free speech.
    
    Uses a heuristic based on:
    - Duration (scripted tokens are short, free speech is longer)
    - Amplitude variability (free speech has more variation)
    - Pause ratio (word-list reading has more pauses relative to speech)
    """
    y, sr = librosa.load(audio_path, sr=None, offset=start_s, duration=end_s - start_s)
    duration = end_s - start_s
    
    if len(y) == 0:
        return ("scripted", 0.5)
    
    # Feature 1: Duration — scripted tokens are typically < 3 seconds
    duration_score = min(1.0, duration / 6.0)  # 0 = short (scripted), 1 = long (free speech)
    
    # Feature 2: RMS amplitude variability
    frame_length = int(sr * 0.025)
    hop_length = int(sr * 0.010)
    if len(y) < frame_length:
        return ("scripted", 0.7)
    
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    if len(rms) < 2:
        return ("scripted", 0.6)
    
    rms_cv = float(np.std(rms) / (np.mean(rms) + 1e-10))  # coefficient of variation
    # Higher CV suggests more variation → free speech
    amplitude_score = min(1.0, rms_cv / 2.0)
    
    # Feature 3: Pause ratio — fraction of frames below silence threshold
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    pause_ratio = float(np.mean(rms_db < -30))
    # Word-list reading has higher pause ratio (pauses between words)
    pause_score = 1.0 - pause_ratio  # High pause = scripted, so invert
    
    # Feature 4: Zero-crossing rate variability (speech rhythm indicator)
    zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]
    zcr_cv = float(np.std(zcr) / (np.mean(zcr) + 1e-10))
    rhythm_score = min(1.0, zcr_cv / 1.5)
    
    # Weighted combination: higher = more likely free speech
    free_speech_score = (
        0.35 * duration_score
        + 0.25 * amplitude_score
        + 0.20 * pause_score
        + 0.20 * rhythm_score
    )
    
    if free_speech_score > 0.55:
        return ("free_speech", round(float(free_speech_score), 3))
    else:
        return ("scripted", round(float(1.0 - free_speech_score), 3))
