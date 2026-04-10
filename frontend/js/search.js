import { supabase } from './supabase-client.js'
import { play } from './player.js'

document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('searchForm')
  const searchInput = document.getElementById('searchInput')
  const stripToneCheck = document.getElementById('stripToneCheck')
  const resultsTable = document.getElementById('resultsTable')
  const summaryBox = document.getElementById('summaryBox')
  const errorBox = document.getElementById('errorBox')

  function highlightPatterns(text, patterns) {
    if (!patterns || patterns.length === 0) return text
    const sorted = [...patterns].sort((a,b) => b.length - a.length)
    const escaped = sorted.map(p => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    const regex = new RegExp(`(${escaped.join('|')})`, 'g')
    return text.replace(regex, '<mark>$1</mark>')
  }

  if (searchForm) {
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault()
      
      const query = searchInput.value.trim()
      if (!query) return

      resultsTable.innerHTML = '<li class="result-row">Searching...</li>'
      if (summaryBox) summaryBox.style.display = 'none'
      if (errorBox) errorBox.style.display = 'none'

      const { data, error } = await supabase.functions.invoke('search', {
        body: { query, strip_tone: stripToneCheck.checked, limit: 100 }
      })

      if (error) {
        resultsTable.innerHTML = ''
        errorBox.innerText = `Error: ${error.message}`
        errorBox.style.display = 'block'
        return
      }

      resultsTable.innerHTML = ''
      
      if (!data.results || data.results.length === 0) {
        resultsTable.innerHTML = '<li class="result-row">No results found.</li>'
        return
      }

      if (summaryBox) {
        summaryBox.innerText = `${data.count} results for "${query}" (searched: ${data.patterns_searched.join(', ')})`
        if (data.warning) {
          summaryBox.innerText += `\nWarning: ${data.warning}`
        }
        summaryBox.style.display = 'block'
      }

      data.results.forEach(result => {
        const li = document.createElement('li')
        li.className = 'result-row'

        const contentDiv = document.createElement('div')
        contentDiv.className = 'row-content'

        const transcription = document.createElement('div')
        transcription.className = 'transcription ipa'
        transcription.innerHTML = highlightPatterns(result.transcription_normalized, data.patterns_searched)
        contentDiv.appendChild(transcription)

        if (result.gloss) {
          const gloss = document.createElement('div')
          gloss.className = 'gloss'
          gloss.innerText = result.gloss
          contentDiv.appendChild(gloss)
        }

        if (result.ort) {
          const ort = document.createElement('div')
          ort.className = 'ort'
          ort.innerText = `orth: ${result.ort}`
          contentDiv.appendChild(ort)
        }

        li.appendChild(contentDiv)

        const btn = document.createElement('button')
        btn.className = 'play-btn'
        btn.innerHTML = '▶'
        if (result.audio_url) {
          btn.onclick = () => play(result.audio_url, li)
        } else {
          btn.disabled = true
          btn.title = 'no audio file linked'
        }
        li.appendChild(btn)

        resultsTable.appendChild(li)
      })
    })
  }
})
