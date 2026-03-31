"""Formant extraction via parselmouth for vowel analysis."""

import parselmouth
import numpy as np


def extract_formants(
    audio_path: str,
    max_formant_hz: float = 5500.0,
    num_formants: int = 5,
    window_length_s: float = 0.025,
) -> dict:
    """Extract F1, F2, F3 from the steady-state nucleus of a vowel token.

    Focuses on the middle third of the sound to avoid coarticulatory
    transitions at segment boundaries.
    """
    sound = parselmouth.Sound(audio_path)
    duration = sound.get_total_duration()

    # Focus on the middle third to avoid coarticulation
    start_trim = duration * 0.25
    end_trim = duration * 0.75
    if end_trim - start_trim < 0.02:
        # Token too short for trimming — use the whole thing
        start_trim = 0.0
        end_trim = duration

    formant = sound.to_formant_burg(
        time_step=0.01,
        max_number_of_formants=num_formants,
        maximum_formant=max_formant_hz,
        window_length=window_length_s,
        pre_emphasis_from=50.0,
    )

    # Sample formant values in the steady-state region
    n_samples = max(1, int((end_trim - start_trim) / 0.01))
    times = np.linspace(start_trim, end_trim, n_samples)

    f1_vals, f2_vals, f3_vals = [], [], []
    bw1_vals, bw2_vals = [], []

    for t in times:
        f1 = formant.get_value_at_time(1, t)
        f2 = formant.get_value_at_time(2, t)
        f3 = formant.get_value_at_time(3, t)

        if f1 and not np.isnan(f1) and f1 > 0:
            f1_vals.append(f1)
            bw = formant.get_bandwidth_at_time(1, t)
            if bw and not np.isnan(bw):
                bw1_vals.append(bw)
        if f2 and not np.isnan(f2) and f2 > 0:
            f2_vals.append(f2)
            bw = formant.get_bandwidth_at_time(2, t)
            if bw and not np.isnan(bw):
                bw2_vals.append(bw)
        if f3 and not np.isnan(f3) and f3 > 0:
            f3_vals.append(f3)

    return {
        "f1": float(np.median(f1_vals)) if f1_vals else None,
        "f2": float(np.median(f2_vals)) if f2_vals else None,
        "f3": float(np.median(f3_vals)) if f3_vals else None,
        "bandwidth_f1": float(np.median(bw1_vals)) if bw1_vals else None,
        "bandwidth_f2": float(np.median(bw2_vals)) if bw2_vals else None,
    }
