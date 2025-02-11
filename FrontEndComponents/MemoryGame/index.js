const BASE_URL = 'https://aricemusic-caregiver.hf.space'
let visitorId = 'visitor-' + Math.floor(Math.random() * 1000000)

const startGameBtn = document.getElementById('startGameBtn')
const startGameResult = document.getElementById('startGameResult')

const questionInput = document.getElementById('questionInput')
const askQuestionBtn = document.getElementById('askQuestionBtn')
const questionLog = document.getElementById('questionLog')

const guessInput = document.getElementById('guessInput')
const makeGuessBtn = document.getElementById('makeGuessBtn')
const guessLog = document.getElementById('guessLog')

function setLoading(button, isLoading) {
  button.disabled = isLoading
  button.textContent = isLoading ? 'Loading...' : button.dataset.originalText
}

async function startGame(event) {
  event.preventDefault()
  setLoading(startGameBtn, true)
  startGameResult.textContent = ''

  try {
    const response = await fetch(`${BASE_URL}/api/game/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ visitorId })
    })

    const data = await response.json()
    startGameResult.textContent = data.status === 'success'
      ? `Game started! Debug year: ${data.debug_year || 'unknown'}`
      : `Error: ${data.message}`
  } catch (err) {
    startGameResult.textContent = `Network error: ${err.message}`
  } finally {
    setLoading(startGameBtn, false)
  }
}

async function askQuestion(event) {
  event.preventDefault()
  const question = questionInput.value.trim()
  if (!question) return alert('Please enter a question!')

  questionLog.textContent = ''
  setLoading(askQuestionBtn, true)

  try {
    const response = await fetch(`${BASE_URL}/api/game/question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ visitorId, question })
    })

    const data = await response.json()
    questionLog.textContent = data.status === 'success'
      ? `You: ${question}\nAI: ${data.answer}`
      : `Error: ${data.message}`
  } catch (err) {
    questionLog.textContent = `Network error: ${err.message}`
  } finally {
    setLoading(askQuestionBtn, false)
    questionInput.value = ''
    questionInput.focus()
  }
}

async function makeGuess(event) {
  event.preventDefault()
  const guess = parseInt(guessInput.value.trim(), 10)
  if (isNaN(guess)) return alert('Please enter a valid year!')

  guessLog.textContent = ''
  setLoading(makeGuessBtn, true)

  try {
    const response = await fetch(`${BASE_URL}/api/game/guess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ visitorId, guess })
    })

    const data = await response.json()
    guessLog.textContent = data.status === 'success'
      ? `Your guess: ${guess}\nResult: ${data.message}`
      : `Error: ${data.message}`
  } catch (err) {
    guessLog.textContent = `Network error: ${err.message}`
  } finally {
    setLoading(makeGuessBtn, false)
    guessInput.value = ''
    guessInput.focus()
  }
}

// Store original button text for toggling loading states
startGameBtn.dataset.originalText = startGameBtn.textContent
askQuestionBtn.dataset.originalText = askQuestionBtn.textContent
makeGuessBtn.dataset.originalText = makeGuessBtn.textContent

// Attach event listeners
startGameBtn.addEventListener('click', startGame)
askQuestionBtn.addEventListener('click', askQuestion)
makeGuessBtn.addEventListener('click', makeGuess)

// Enable Enter key functionality for inputs
questionInput.addEventListener('keypress', e => { if (e.key === 'Enter') askQuestion(e) })
guessInput.addEventListener('keypress', e => { if (e.key === 'Enter') makeGuess(e) })
