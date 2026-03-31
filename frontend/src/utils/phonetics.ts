/**
 * Unicode-aware phonetic utilities for handling IPA characters,
 * encoding variants, and diacritic normalization.
 */

/**
 * Normalizes Unicode combining character sequences to a canonical order.
 * Handles the problem where [é̟] might be encoded as base+acute+advanced
 * or base+advanced+acute.
 */
export function normalizeIPA(text: string): string {
  return text.normalize("NFC");
}

/**
 * Strips all combining diacritics from an IPA string, leaving only base characters.
 * Useful for coarse matching before fine comparison.
 */
export function stripDiacritics(text: string): string {
  return text.normalize("NFD").replace(/[\u0300-\u036f\u0320-\u0333]/g, "");
}

/**
 * Checks if a character is an IPA vowel base character.
 */
export function isIPAVowel(char: string): boolean {
  const vowels = new Set([
    "i", "y", "ɨ", "ʉ", "ɯ", "u",
    "ɪ", "ʏ", "ʊ",
    "e", "ø", "ɘ", "ɵ", "ɤ", "o",
    "ə",
    "ɛ", "œ", "ɜ", "ɞ", "ʌ", "ɔ",
    "æ",
    "a", "ɶ", "ɑ", "ɒ",
  ]);
  return vowels.has(char.normalize("NFD")[0] ?? "");
}
