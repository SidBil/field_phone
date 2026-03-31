/**
 * Client-side shorthand expansion for immediate feedback in the transcription UI.
 * The canonical expansion happens server-side; this provides instant preview.
 */

export interface ShorthandMap {
  [key: string]: string;
}

const DEFAULT_SHORTHAND: ShorthandMap = {
  U: "ʊ",
  I: "ɪ",
  E: "ɛ",
  O: "ɔ",
  "@": "ə",
  A: "æ",
};

export function expandShorthand(
  text: string,
  customMap?: ShorthandMap,
): { expanded: string; applied: Array<{ from: string; to: string }> } {
  const map = { ...DEFAULT_SHORTHAND, ...customMap };
  const applied: Array<{ from: string; to: string }> = [];
  let expanded = text;

  for (const [from, to] of Object.entries(map)) {
    if (expanded.includes(from)) {
      expanded = expanded.replaceAll(from, to);
      applied.push({ from, to });
    }
  }

  return { expanded, applied };
}
