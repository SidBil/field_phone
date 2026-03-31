"""F0 track extraction for tone analysis."""

import parselmouth
import numpy as np


def extract_f0(audio_path: str) -> list[dict]:
    """Extract F0 contour from audio using parselmouth.

    Returns only voiced frames (where F0 is defined).
    """
    sound = parselmouth.Sound(audio_path)
    pitch = sound.to_pitch_ac(
        time_step=0.005,
        pitch_floor=75.0,
        pitch_ceiling=600.0,
    )

    f0_track = []
    for i in range(pitch.n_frames):
        t = pitch.get_time_from_frame_number(i + 1)
        f0 = pitch.get_value_in_frame(i + 1)
        if f0 and not np.isnan(f0) and f0 > 0:
            f0_track.append({"time_s": round(float(t), 4), "f0_hz": round(float(f0), 1)})

    return f0_track


def align_f0_with_syllables(
    f0_track: list[dict],
    syllable_boundaries: list[float],
) -> list[dict]:
    """Add syllable_index to each F0 data point based on timing.

    syllable_boundaries is a list of time points marking syllable edges.
    A point at time t belongs to syllable i if boundaries[i] <= t < boundaries[i+1].
    """
    if not syllable_boundaries:
        return [{"syllable_index": 0, **pt} for pt in f0_track]

    result = []
    for pt in f0_track:
        t = pt["time_s"]
        syllable_idx = 0
        for i in range(len(syllable_boundaries) - 1):
            if t >= syllable_boundaries[i]:
                syllable_idx = i
            else:
                break
        result.append({"syllable_index": syllable_idx, **pt})

    return result
