import { createClient } from 'jsr:@supabase/supabase-js@2'

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
    let matched = 0
    let unmatched = 0
    
    let allFiles: any[] = []
    let limit = 1000
    let offset = 0
    let hasMore = true

    while (hasMore) {
      const { data, error } = await supabase.storage.from('audio').list('', {
        limit,
        offset,
        sortBy: { column: 'name', order: 'asc' },
      })
      if (error) throw error
      if (data && data.length > 0) {
        allFiles.push(...data)
        offset += limit
      } else {
        hasMore = false
      }
    }

    for (const file of allFiles) {
      if (file.name === '.emptyFolderPlaceholder') continue

      const stem = file.name.substring(0, file.name.lastIndexOf('.')) || file.name
      
      const { data, error } = await supabase
        .from('records')
        .select('id, audio_path')
        .eq('record_id', stem)
        .maybeSingle()

      if (error) throw error

      if (data) {
        if (!data.audio_path) {
          const { error: updateError } = await supabase
            .from('records')
            .update({ audio_path: file.name })
            .eq('id', data.id)
            
          if (updateError) throw updateError
        }
        matched++
      } else {
        unmatched++
      }
    }

    return new Response(JSON.stringify({ matched, unmatched }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders })
  }
})
