"""IPA vowel classification from formant values."""

import math

# Reference formant values for IPA cardinal vowels (Lobanov-normalized z-scores).
# Based on aggregate data from Ladefoged & Maddieson (1996), Hillenbrand et al. (1995).
# F1 increases with openness (low vowels = high F1). F2 increases with frontness.
# These are approximate Lobanov z-scores for a "neutral" speaker.
IPA_REFERENCE_VOWELS: dict[str, tuple[float, float]] = {
    # Close front
    "i":  (-1.5, 1.5),
    "y":  (-1.5, 1.0),
    # Near-close front
    "ɪ":  (-1.0, 1.2),
    "ʏ":  (-1.0, 0.8),
    # Close-mid front
    "e":  (-0.5, 1.3),
    "ø":  (-0.5, 0.7),
    # Open-mid front
    "ɛ":  (0.3, 1.1),
    "œ":  (0.3, 0.6),
    # Near-open front
    "æ":  (0.8, 1.0),
    # Open
    "a":  (1.2, 0.2),
    "ɑ":  (1.2, -0.8),
    "ɒ":  (1.2, -1.0),
    # Open-mid back
    "ɔ":  (0.4, -0.9),
    "ʌ":  (0.4, -0.2),
    # Close-mid back
    "o":  (-0.4, -1.0),
    "ɤ":  (-0.4, -0.5),
    # Near-close back
    "ʊ":  (-0.9, -0.7),
    # Close back
    "u":  (-1.4, -1.2),
    "ɯ":  (-1.4, -0.3),
    # Central
    "ə":  (0.0, 0.0),
    "ɨ":  (-1.3, 0.1),
    "ʉ":  (-1.3, -0.2),
    "ɜ":  (0.3, 0.0),
    "ɵ":  (-0.4, -0.1),
}

# Language-prior inventory subsets (restrict classifier to likely vowels)
LANGUAGE_PRIORS: dict[str, list[str]] = {
    "swahili": ["i", "e", "a", "o", "u"],
    "bantu_7v": ["i", "ɪ", "e", "ɛ", "a", "ɔ", "o", "ʊ", "u"],
    "logoori": ["i", "ɪ", "e", "ɛ", "a", "ɔ", "o", "ʊ", "u"],
    "english": ["i", "ɪ", "e", "ɛ", "æ", "ʌ", "ɑ", "ɔ", "o", "ʊ", "u", "ə"],
    "spanish": ["i", "e", "a", "o", "u"],
    "french": ["i", "y", "e", "ɛ", "a", "ɔ", "o", "u", "ə", "ø", "œ"],
}


def classify_vowel(
    f1_norm: float,
    f2_norm: float,
    language_prior: str | None = None,
    inventory: dict | None = None,
) -> list[dict]:
    """Return ranked list of IPA vowel candidates with confidence scores.
    
    Uses Euclidean distance in normalized F1×F2 space, converted to
    confidence via softmax (temperature-scaled).
    """
    # Determine which vowels to consider
    if inventory is not None:
        ref = {k: v for k, v in inventory.items() if k in IPA_REFERENCE_VOWELS}
        if not ref:
            ref = IPA_REFERENCE_VOWELS
    elif language_prior and language_prior.lower() in LANGUAGE_PRIORS:
        subset = LANGUAGE_PRIORS[language_prior.lower()]
        ref = {k: v for k, v in IPA_REFERENCE_VOWELS.items() if k in subset}
    else:
        ref = IPA_REFERENCE_VOWELS
    
    # Compute distances
    distances = {}
    for symbol, (ref_f1, ref_f2) in ref.items():
        d = math.sqrt((f1_norm - ref_f1) ** 2 + (f2_norm - ref_f2) ** 2)
        distances[symbol] = d
    
    # Softmax over negative distances (temperature=0.5 for sharper distribution)
    temperature = 0.5
    neg_dists = {s: -d / temperature for s, d in distances.items()}
    max_val = max(neg_dists.values())
    exp_vals = {s: math.exp(v - max_val) for s, v in neg_dists.items()}
    total = sum(exp_vals.values())
    
    candidates = []
    for symbol, exp_v in exp_vals.items():
        confidence = exp_v / total
        ref_f1, ref_f2 = IPA_REFERENCE_VOWELS[symbol]
        candidates.append({
            "symbol": symbol,
            "confidence": round(confidence, 4),
            "f1_hz": ref_f1,
            "f2_hz": ref_f2,
        })
    
    candidates.sort(key=lambda c: c["confidence"], reverse=True)
    return candidates


def get_confidence_tier(
    top_confidence: float,
    high_threshold: float = 0.75,
    low_threshold: float = 0.50,
) -> str:
    """Return 'high', 'low', or 'uncertain' based on top candidate confidence."""
    if top_confidence >= high_threshold:
        return "high"
    elif top_confidence >= low_threshold:
        return "low"
    else:
        return "uncertain"
