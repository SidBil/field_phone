import { supabase } from './supabase-client.js'

document.addEventListener('DOMContentLoaded', () => {
  const dbUploadForm = document.getElementById('dbUploadForm')
  const dbStatus = document.getElementById('dbStatus')
  const dbInput = document.getElementById('dbInput')

  if (dbUploadForm) {
    dbUploadForm.addEventListener('submit', async (e) => {
      e.preventDefault()
      const file = dbInput.files[0]
      if (!file) return

      dbStatus.innerText = 'Reading file...'
      const reader = new FileReader()
      reader.onload = async (e) => {
        dbStatus.innerText = 'Ingesting records (this may take a minute)...'
        const rawText = e.target.result
        
        const { data, error } = await supabase.functions.invoke('ingest', {
          body: rawText
        })

        if (error) {
          dbStatus.innerText = `Error: ${error.message}`
        } else {
          dbStatus.innerText = `Ingested ${data.ingested} records, skipped ${data.skipped} malformed lines.`
        }
      }
      reader.readAsText(file)
    })
  }

  const audioUploadForm = document.getElementById('audioUploadForm')
  const audioStatus = document.getElementById('audioStatus')
  const audioInput = document.getElementById('audioInput')
  const progressList = document.getElementById('progressList')

  if (audioUploadForm) {
    audioUploadForm.addEventListener('submit', async (e) => {
      e.preventDefault()
      const files = audioInput.files
      if (files.length === 0) return

      audioStatus.innerText = `Uploading ${files.length} files...`
      progressList.innerHTML = ''

      const uploads = Array.from(files).map(async (file) => {
        const li = document.createElement('li')
        li.innerText = `${file.name} - Uploading...`
        progressList.appendChild(li)

        const { error } = await supabase.storage.from('audio').upload(file.name, file, {
          upsert: true
        })

        if (error) {
          li.innerText = `${file.name} - Error: ${error.message}`
          li.style.color = 'var(--error)'
        } else {
          li.innerText = `${file.name} - Done`
          li.style.color = 'green'
        }
      })

      await Promise.all(uploads)
      audioStatus.innerText = `Uploads complete. Resolving audio paths...`

      const { data, error } = await supabase.functions.invoke('resolve_audio')

      if (error) {
        audioStatus.innerText = `Error resolving: ${error.message}`
      } else {
        audioStatus.innerText = `All done! Matched ${data.matched} records, ${data.unmatched} files were unmatched.`
      }
    })
  }
})
