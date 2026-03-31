"""Phonetic class definitions for query expansion."""

import unicodedata
import yaml


def load_class_definitions(config_path: str) -> dict:
    """Load phonetic class definitions from YAML.
    
    Returns dict mapping class names to sets of characters (including
    NFC/NFD variants for each character).
    """
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    
    definitions = {}
    for class_name, members in raw.items():
        if not isinstance(members, list):
            continue
        char_set = set()
        for char in members:
            s = str(char)
            char_set.add(s)
            # Add both NFC and NFD normalized forms
            char_set.add(unicodedata.normalize("NFC", s))
            char_set.add(unicodedata.normalize("NFD", s))
        definitions[class_name] = char_set
    
    return definitions


def expand_class(class_name: str, definitions: dict) -> set[str]:
    """Return the full set of characters for a named class.
    
    Handles underscore/space/hyphen variations in class names.
    """
    # Try exact match first
    if class_name in definitions:
        return definitions[class_name]
    
    # Normalize: lowercase, replace spaces/hyphens with underscores
    normalized = class_name.lower().replace(" ", "_").replace("-", "_")
    for key, value in definitions.items():
        if key.lower().replace(" ", "_").replace("-", "_") == normalized:
            return value
    
    return set()
