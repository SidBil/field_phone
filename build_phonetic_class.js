const fs = require('fs');
const data = {
  "mid vowel":        ["e", "ɛ", "o", "ɔ", "e̟", "o̟", "é", "ó", "ɛ́", "ɔ́"],
  "high vowel":       ["i", "ɪ", "u", "ʊ", "í", "ɪ́", "ú", "ʊ́"],
  "tense high vowel": ["i", "u", "í", "ú"],
  "lax high vowel":   ["ɪ", "ʊ", "ɪ́", "ʊ́"],
  "low vowel":        ["a", "á", "à", "ā"],
  "tense mid vowel":  ["e", "o", "é", "ó", "e̟", "o̟"],
  "lax mid vowel":    ["ɛ", "ɔ", "ɛ́", "ɔ́"],
  "front vowel":      ["i", "ɪ", "e", "ɛ", "í", "ɪ́", "é", "ɛ́"],
  "back vowel":       ["u", "ʊ", "o", "ɔ", "ú", "ʊ́", "ó", "ɔ́"],
  "nasal":            ["m", "n", "ŋ", "ɲ", "n̪"],
  "stop":             ["p", "b", "t", "d", "k", "g", "tʃ", "dʒ"],
  "fricative":        ["f", "v", "s", "z", "ʃ", "ʒ", "h"],
  "approximant":      ["l", "r", "w", "j"],
  "glide":            ["w", "j"],
  "labial":           ["p", "b", "m", "f", "v", "w"],
  "alveolar":         ["t", "d", "n", "s", "z", "l", "r"],
  "palatal":          ["tʃ", "dʒ", "ɲ", "j", "ʃ", "ʒ"],
  "velar":            ["k", "g", "ŋ", "w"]
};

const normalized = {};
for (const [key, values] of Object.entries(data)) {
  normalized[key] = values.map(v => v.normalize('NFC'));
}

const json = JSON.stringify(normalized, null, 2);
fs.writeFileSync('frontend/data/phonetic_classes.json', json);
fs.writeFileSync('supabase/functions/search/phonetic_classes.json', json);
console.log('Saved normalized JSON');
