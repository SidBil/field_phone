"""Lobanov normalization for cross-speaker formant comparison."""

import numpy as np


def lobanov_normalize(
    f1: float,
    f2: float,
    speaker_f1_mean: float,
    speaker_f1_std: float,
    speaker_f2_mean: float,
    speaker_f2_std: float,
) -> tuple[float, float]:
    """Apply Lobanov normalization: z-score transform relative to speaker's vowel space."""
    f1_norm = (f1 - speaker_f1_mean) / speaker_f1_std if speaker_f1_std > 0 else 0.0
    f2_norm = (f2 - speaker_f2_mean) / speaker_f2_std if speaker_f2_std > 0 else 0.0
    return (round(f1_norm, 4), round(f2_norm, 4))


def compute_speaker_stats(token_formants: list[dict]) -> dict:
    """Compute mean and std of F1/F2 across a speaker's tokens.
    
    Args:
        token_formants: List of dicts with "f1" and "f2" keys (Hz values).
        
    Returns:
        Dict with f1_mean, f1_std, f2_mean, f2_std.
    """
    f1_values = [t["f1"] for t in token_formants if t.get("f1") is not None]
    f2_values = [t["f2"] for t in token_formants if t.get("f2") is not None]
    
    return {
        "f1_mean": float(np.mean(f1_values)) if f1_values else 0.0,
        "f1_std": float(np.std(f1_values, ddof=1)) if len(f1_values) > 1 else 0.0,
        "f2_mean": float(np.mean(f2_values)) if f2_values else 0.0,
        "f2_std": float(np.std(f2_values, ddof=1)) if len(f2_values) > 1 else 0.0,
    }
