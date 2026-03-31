"""Orthographic normalization for language-specific transcription rules."""

import unicodedata
import yaml


def load_rules(rules_path: str) -> dict:
    """Load normalization rules from a YAML config file.
    
    Expected format:
        strip_diacritics: [list of combining codepoints to strip]
        replacements: {source: target, ...}
        lowercase: true/false
        unicode_form: NFC/NFD/NFKC/NFKD
    """
    with open(rules_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalize(form: str, rules_path: str) -> str:
    """Apply language-specific normalization rules to an orthographic form."""
    rules = load_rules(rules_path)
    result = form
    
    # Unicode normalization
    unicode_form = rules.get("unicode_form", "NFC")
    if unicode_form in ("NFC", "NFD", "NFKC", "NFKD"):
        result = unicodedata.normalize(unicode_form, result)
    
    # Strip specified diacritics (combining characters)
    strip_chars = rules.get("strip_diacritics", [])
    if strip_chars:
        strip_set = set(strip_chars)
        decomposed = unicodedata.normalize("NFD", result)
        result = "".join(c for c in decomposed if c not in strip_set)
        result = unicodedata.normalize("NFC", result)
    
    # Apply replacements
    replacements = rules.get("replacements", {})
    for source, target in replacements.items():
        result = result.replace(str(source), str(target))
    
    # Lowercase if specified
    if rules.get("lowercase", False):
        result = result.lower()
    
    return result
