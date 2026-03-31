"""Tone analysis and pattern matching."""

import re

from sqlalchemy.orm import Session

from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription


def check_tone_consistency(
    f0_track: list[dict],
    transcribed_tones: str,
) -> dict:
    """Compare F0 track against categorical tone transcription.
    
    Expects transcribed_tones as a string of H/L/M/D (high/low/mid/downstep)
    characters, one per syllable. F0 track points should have syllable_index.
    
    For each syllable, computes mean F0 and checks if it's consistent with
    the transcribed tone category relative to the overall F0 range.
    """
    if not f0_track or not transcribed_tones:
        return {
            "divergence_score": 0.0,
            "details": "Insufficient data for tone consistency check.",
        }
    
    # Group F0 values by syllable
    syllable_f0: dict[int, list[float]] = {}
    for pt in f0_track:
        idx = pt.get("syllable_index", 0)
        syllable_f0.setdefault(idx, []).append(pt["f0_hz"])
    
    if not syllable_f0:
        return {"divergence_score": 0.0, "details": "No F0 data with syllable indices."}
    
    # Compute mean F0 per syllable
    syllable_means: dict[int, float] = {}
    for idx, values in syllable_f0.items():
        syllable_means[idx] = sum(values) / len(values)
    
    # Compute overall F0 range for relative thresholds
    all_f0 = [v for vals in syllable_f0.values() for v in vals]
    f0_min = min(all_f0)
    f0_max = max(all_f0)
    f0_range = f0_max - f0_min
    
    if f0_range < 10:  # Less than 10 Hz range — essentially flat
        return {
            "divergence_score": 0.1,
            "details": "F0 range is very narrow; tone distinctions may not be acoustically realized.",
        }
    
    # Thresholds: divide the F0 range into thirds
    low_boundary = f0_min + f0_range * 0.33
    high_boundary = f0_min + f0_range * 0.67
    
    tones = list(transcribed_tones.upper())
    mismatches = []
    total_checked = 0
    
    for i, tone_char in enumerate(tones):
        if i not in syllable_means:
            continue
        total_checked += 1
        mean_f0 = syllable_means[i]
        
        if tone_char == "H" and mean_f0 < low_boundary:
            mismatches.append(f"Syllable {i}: transcribed H but F0={mean_f0:.0f}Hz (low range)")
        elif tone_char == "L" and mean_f0 > high_boundary:
            mismatches.append(f"Syllable {i}: transcribed L but F0={mean_f0:.0f}Hz (high range)")
        elif tone_char == "M" and (mean_f0 < f0_min + f0_range * 0.2 or mean_f0 > f0_min + f0_range * 0.8):
            mismatches.append(f"Syllable {i}: transcribed M but F0={mean_f0:.0f}Hz (extreme range)")
    
    divergence = len(mismatches) / max(1, total_checked)
    details = "; ".join(mismatches) if mismatches else "Tone transcription is consistent with F0."
    
    return {
        "divergence_score": round(divergence, 4),
        "details": details,
    }


def query_tone_patterns(pattern: str, db_session: Session) -> list[dict]:
    """Search for tokens matching a tonal pattern description.
    
    Supports patterns like:
    - "LH" or "HLH" — exact tone sequence
    - "L before H" — L immediately before H
    - "H after L" — same as "L before H"
    """
    pattern_clean = pattern.strip().upper()
    
    # Parse natural language patterns
    before_match = re.match(r"([HLMD]+)\s+BEFORE\s+([HLMD]+)", pattern_clean)
    after_match = re.match(r"([HLMD]+)\s+AFTER\s+([HLMD]+)", pattern_clean)
    
    if before_match:
        search_seq = before_match.group(1) + before_match.group(2)
    elif after_match:
        search_seq = after_match.group(2) + after_match.group(1)
    else:
        search_seq = re.sub(r"[^HLMD]", "", pattern_clean)
    
    if not search_seq:
        return []
    
    # Search all tokens with transcriptions that have tone_pattern
    tokens_with_tones = (
        db_session.query(Token, Transcription)
        .join(Transcription, Token.id == Transcription.token_id)
        .filter(Transcription.tone_pattern.isnot(None))
        .filter(Transcription.tone_pattern != "")
        .all()
    )
    
    results = []
    seen_token_ids = set()
    for token, trans in tokens_with_tones:
        if token.id in seen_token_ids:
            continue
        
        tone_upper = (trans.tone_pattern or "").upper()
        # Remove non-tone characters for matching
        tone_clean = re.sub(r"[^HLMD]", "", tone_upper)
        
        if search_seq in tone_clean:
            seen_token_ids.add(token.id)
            results.append({
                "token_id": token.id,
                "orthographic_form": token.orthographic_form or "",
                "tone_pattern": trans.tone_pattern or "",
                "audio_url": f"/audio/{token.audio_path}" if token.audio_path else "",
            })
    
    return results
