"""Query parsing for natural language phonetic queries."""

import re
import regex


def parse_natural_language(query: str, class_definitions: dict) -> str:
    """Convert a natural language phonetic query into a regex pattern.
    
    Handles queries like:
    - "mid vowel followed by a nasal"
    - "high vowel"  
    - "[ɛ] preceding a high vowel"
    - "nasal followed by tense high vowel"
    
    The parser tokenizes the query, identifies phonetic class references,
    and builds a regex character class for each.
    """
    query_lower = query.lower().strip()
    
    # Handle literal IPA in brackets: [ɛ], [e], etc.
    literal_pattern = re.compile(r'\[([^\]]+)\]')
    
    # Split on connectors
    connectors = re.compile(
        r'\b(?:followed\s+by|preceding|before|after|then)\b',
        re.IGNORECASE,
    )
    
    parts = connectors.split(query_lower)
    if len(parts) == 1:
        # No connectors — treat as a single class query
        return _resolve_to_regex(parts[0].strip(), class_definitions, literal_pattern)
    
    # Build regex by concatenating resolved parts with .* between if needed
    regex_parts = []
    for part in parts:
        part = part.strip()
        if part:
            resolved = _resolve_to_regex(part, class_definitions, literal_pattern)
            regex_parts.append(resolved)
    
    return "".join(regex_parts)


def _resolve_to_regex(
    term: str,
    class_definitions: dict,
    literal_pattern: re.Pattern,
) -> str:
    """Resolve a single term (class name or literal) to a regex fragment."""
    # Check for literal IPA in brackets
    lit_match = literal_pattern.search(term)
    if lit_match:
        chars = lit_match.group(1)
        return regex.escape(chars)
    
    # Try matching against class definitions
    # Try the full term first, then progressively shorter combinations
    term_normalized = term.strip().replace(" ", "_").replace("-", "_")
    
    # Direct match
    for class_name, char_set in class_definitions.items():
        cn = class_name.lower().replace(" ", "_").replace("-", "_")
        if cn == term_normalized:
            return _chars_to_class(char_set)
    
    # Try removing articles/prepositions
    cleaned = re.sub(r'\b(a|an|the|of|in)\b', '', term_normalized).strip("_")
    cleaned = re.sub(r'_+', '_', cleaned).strip("_")
    for class_name, char_set in class_definitions.items():
        cn = class_name.lower().replace(" ", "_").replace("-", "_")
        if cn == cleaned:
            return _chars_to_class(char_set)
    
    # Intersection: e.g. "tense high vowel" → tense ∩ high ∩ vowel
    words = [w for w in cleaned.split("_") if w]
    if len(words) > 1:
        matching_sets = []
        for word in words:
            for class_name, char_set in class_definitions.items():
                cn = class_name.lower().replace(" ", "_").replace("-", "_")
                if word in cn.split("_") or cn == word:
                    matching_sets.append(char_set)
                    break
        
        if matching_sets:
            intersection = matching_sets[0]
            for s in matching_sets[1:]:
                intersection = intersection & s
            if intersection:
                return _chars_to_class(intersection)
            # If intersection is empty, use union instead
            union = set()
            for s in matching_sets:
                union |= s
            return _chars_to_class(union)
    
    # Fallback: treat the term as a literal
    return regex.escape(term.replace("_", " ").strip())


def _chars_to_class(char_set: set[str]) -> str:
    """Convert a set of characters to a regex character class [...]."""
    if not char_set:
        return ""
    if len(char_set) == 1:
        return regex.escape(next(iter(char_set)))
    escaped = [regex.escape(c) for c in sorted(char_set)]
    return "[" + "".join(escaped) + "]"


def validate_regex(pattern: str) -> str:
    """Validate and normalize a regex pattern.
    
    Replaces common alternatives for consistency:
    - ^ and $ always mean start/end of string
    - \\b for word boundary is supported
    """
    # Normalize common variations
    pattern = pattern.replace("\\<", "\\b").replace("\\>", "\\b")
    
    # Validate by attempting compilation
    try:
        regex.compile(pattern, regex.UNICODE)
    except regex.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")
    
    return pattern
