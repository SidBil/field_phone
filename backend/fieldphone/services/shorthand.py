"""Shorthand expansion for transcription conventions."""

import yaml


def load_shorthand_map(config_path: str) -> dict[str, str]:
    """Load shorthand mappings from YAML."""
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    # Ensure all keys and values are strings
    return {str(k): str(v) for k, v in raw.items()}


def expand(
    text: str,
    shorthand_map: dict[str, str],
) -> tuple[str, list[dict]]:
    """Expand shorthand in text. Applies longest-match-first to avoid partial replacements."""
    # Sort by key length descending so longer sequences match first
    sorted_keys = sorted(shorthand_map.keys(), key=len, reverse=True)
    
    applied = []
    result = text
    for key in sorted_keys:
        if key in result:
            replacement = shorthand_map[key]
            result = result.replace(key, replacement)
            applied.append({"from": key, "to": replacement})
    
    return result, applied
