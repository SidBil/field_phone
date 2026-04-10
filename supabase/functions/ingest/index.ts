import { createClient } from 'jsr:@supabase/supabase-js@2'
import { normalize } from '../search/index.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

const supabaseUrl = Deno.env.get('SUPABASE_URL') || '';
const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '';
const supabase = createClient(supabaseUrl, serviceRoleKey);

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }
  
  try {
    const text = await req.text()
    const lines = text.split('\n')
    
    let ingested = 0
    let skipped = 0
    const batch = []

    for (const line of lines) {
      if (!line.trim()) continue
      
      let ort = null
      let cleanLine = line
      const ortMatch = line.match(/<ORT>(.*?)<\/ORT>/)
      if (ortMatch) {
        ort = ortMatch[1].trim()
        cleanLine = line.replace(/<ORT>.*?<\/ORT>/, '').trim()
      }

      const parts = cleanLine.split(/\t+| {2,}/).map(p => p.trim()).filter(Boolean)
      
      if (parts.length < 2) {
        skipped++
        continue
      }
      
      const record_id = parts[0]
      const transcription = parts[1]
      const gloss = parts.slice(2).join(' ') || null
      
      if (!record_id || !transcription) {
        skipped++
        continue
      }

      const transcription_normalized = normalize(transcription, false)

      batch.push({
        record_id,
        transcription,
        transcription_normalized,
        gloss,
        ort
      })
    }

    for (let i = 0; i < batch.length; i += 1000) {
      const chunk = batch.slice(i, i + 1000)
      const { error } = await supabase
        .from('records')
        .upsert(chunk, { onConflict: 'record_id' })
      if (error) {
        console.error("Upsert error:", error)
        throw error
      }
      ingested += chunk.length
    }

    return new Response(JSON.stringify({ ingested, skipped }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders })
  }
})
