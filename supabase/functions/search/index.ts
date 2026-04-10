import { createClient } from 'jsr:@supabase/supabase-js@2'
import phoneticClasses from './phonetic_classes.json' with { type: "json" };

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
const supabase = createClient(supabaseUrl, serviceRoleKey);

export function normalize(text: string, stripTone: boolean = false): string {
  let s = (text || '').normalize('NFC');
  
  const rewrites: [RegExp, string][] = [
    // Acute + tilde diacritic -> Canonical NFC. (Reordering combination).
    [/\u0301\u0303/g, '\u0303\u0301'],
    [/e\u0320/g, 'e̟'],
    [/o\u0320/g, 'o̟'],
    [/ng'/g, 'ŋ'],
    // ny followed by vowel -> ɲ + vowel
    [/ny([aeiouɛɔɪʊáéíóúàèìòùāēīōū])/ig, 'ɲ$1'],
    [/\u0301\u0301/g, '\u0301'],
  ];

  for (const [pattern, replacement] of rewrites) {
    s = s.replace(pattern, replacement);
  }
  
  s = s.normalize('NFC');

  if (stripTone) {
    s = s.replace(/[\u0301\u0300\u0304\u030C\uA71D]/g, '');
    s = s.normalize('NFC');
  }

  return s;
}

function expandClass(name: string): string[] {
  const trimmed = name.trim().toLowerCase();
  const cls = (phoneticClasses as Record<string, string[]>)[trimmed];
  if (cls) {
    return cls.map(c => normalize(c, false));
  }
  return [normalize(name.trim(), false)];
}

export function translate(query: string, stripTone: boolean = false): { patterns: string[], warning?: string } {
  const isClassMode = query.includes("followed by") || 
                      Object.keys(phoneticClasses).some(k => query.toLowerCase().includes(k));
                      
  if (!isClassMode) {
    return { patterns: [normalize(query, stripTone)] };
  }

  const segments = query.split("followed by");
  const expandedSegments = segments.map(seg => {
    let expanded = expandClass(seg);
    if (stripTone) {
      expanded = expanded.map(c => normalize(c, true));
    }
    return Array.from(new Set(expanded));
  });

  let patterns = [''];
  for (const charset of expandedSegments) {
    const nextPatterns: string[] = [];
    for (const prefix of patterns) {
      for (const char of charset) {
        nextPatterns.push(prefix + char);
      }
    }
    patterns = nextPatterns;
    if (patterns.length > 500) {
      return { 
        patterns: [normalize(query, stripTone)], 
        warning: "Query produced over 500 patterns. Reverting to literal search." 
      };
    }
  }

  return { patterns: Array.from(new Set(patterns)) };
}

async function searchRecords(patterns: string[], stripTone: boolean, limit: number) {
  let queryBuilder = supabase.from('records').select('*').limit(limit)

  if (patterns.length === 1) {
    queryBuilder = queryBuilder.ilike('transcription_normalized', `%${patterns[0]}%`)
  } else if (patterns.length > 1) {
    // using proper postgREST syntax for .or()
    const conditions = patterns.map(p => `transcription_normalized.ilike.%${p}%`).join(',')
    queryBuilder = queryBuilder.or(conditions)
  }

  const { data, error } = await queryBuilder
  if (error) throw error

  const resultsWithAudio = await Promise.all(
    (data || []).map(async (record) => {
      let audio_url = null
      if (record.audio_path) {
        const { data: signed } = await supabase.storage
          .from('audio')
          .createSignedUrl(record.audio_path, 3600)
        if (signed) audio_url = signed.signedUrl
      }
      return { ...record, audio_url }
    })
  )

  return resultsWithAudio
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }
  try {
    const payload = await req.json()
    const query = payload.query || ''
    const strip_tone = payload.strip_tone === true
    const limit = payload.limit || 100

    const translation = translate(normalize(query, strip_tone), strip_tone)
    const patterns = translation.patterns
    const results = await searchRecords(patterns, strip_tone, limit)
    
    const responsePayload: any = { 
      results, 
      count: results.length, 
      patterns_searched: patterns 
    }
    if (translation.warning) {
      responsePayload.warning = translation.warning
    }

    return new Response(JSON.stringify(responsePayload), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders })
  }
})
