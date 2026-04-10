const audio = new Audio()
let currentRow = null

export function play(url, rowElement) {
  audio.pause()
  if (currentRow) {
    currentRow.classList.remove('playing')
    // Remove pulse if exists
    const pulse = currentRow.querySelector('.pulse')
    if (pulse) pulse.remove()
  }
  
  audio.src = url
  audio.play()
  currentRow = rowElement
  rowElement.classList.add('playing')
  
  // Add pulse right before transcription
  const rowContent = rowElement.querySelector('.row-content')
  const pulse = document.createElement('span')
  pulse.classList.add('pulse')
  rowContent.prepend(pulse)

  audio.onended = () => {
    rowElement.classList.remove('playing')
    if (pulse) pulse.remove()
  }
}

export function stop() {
  audio.pause()
  if (currentRow) {
    currentRow.classList.remove('playing')
    const pulse = currentRow.querySelector('.pulse')
    if (pulse) pulse.remove()
  }
}
