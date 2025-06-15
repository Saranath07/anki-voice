// API Configuration for Anki Voice Companion

export const API_CONFIG = {
  BASE_URL: 'http://localhost:5001',
  TIMEOUT: 10000, // 10 seconds

  ENDPOINTS: {
    // Health and system
    HEALTH: '/api/health',
    DECKS: '/api/decks',

    // Flashcard operations
    GENERATE_FLASHCARDS: '/api/generate_flashcards_with_llm',
    EVALUATE_ANSWER: '/api/evaluate_answer_with_llm',
    SEND_QUESTION_ANSWER: '/api/send_question_answer',

    // Audio operations
    READ_QUESTION: '/api/read_question',
    RECORD_ANSWER: '/api/record_answer',

    // Mode and stats
    CHANGE_MODES: '/api/change_of_modes',
    DECK_STATS: '/api/deck_stats',

    // Anki operations
    ADD_NOTES: '/api/add_notes',
    NOTE_MODELS: '/api/note_models',
    CREATE_DECK: '/api/create_deck',
    GUI_DECK_REVIEW: '/api/gui_deck_review',
    ANSWER_CARDS: '/api/answer_cards',

    // Documentation
    DOCS: '/docs',
    SWAGGER: '/swagger.yaml',
  },

  // HTTP status codes
  STATUS_CODES: {
    OK: 200,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500,
  },
}

/**
 * Make API call with proper error handling and timeout
 * @param {string} endpoint - API endpoint (use API_CONFIG.ENDPOINTS)
 * @param {object} options - Fetch options
 * @returns {Promise<object>} - API response
 */
export const apiCall = async (endpoint, options = {}) => {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT)

  try {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`
    console.log(`[API] Making request to: ${url}`, options)
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    })

    clearTimeout(timeoutId)
    console.log(`[API] Response status: ${response.status} ${response.statusText}`)

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`[API] Error response body:`, errorText)
      throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`)
    }

    const result = await response.json()
    console.log(`[API] Success response:`, result)
    return result
  } catch (error) {
    clearTimeout(timeoutId)
    console.error(`[API] Request failed:`, error)

    if (error.name === 'AbortError') {
      throw new Error('Request timeout')
    }

    // Check if it's a network error (CORS, connection refused, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Network error: Unable to connect to ${API_CONFIG.BASE_URL}. Check if the backend is running and CORS is enabled.`)
    }

    throw error
  }
}

/**
 * Health check utility
 * @returns {Promise<object>} - Health status
 */
export const checkHealth = async () => {
  return await apiCall(API_CONFIG.ENDPOINTS.HEALTH)
}

/**
 * Get available Anki decks
 * @returns {Promise<object>} - Decks list
 */
export const getDecks = async () => {
  return await apiCall(API_CONFIG.ENDPOINTS.DECKS)
}

/**
 * Generate flashcards from text
 * @param {string} statement - Text to generate flashcards from
 * @returns {Promise<object>} - Generated flashcards
 */
export const generateFlashcards = async (statement) => {
  return await apiCall(API_CONFIG.ENDPOINTS.GENERATE_FLASHCARDS, {
    method: 'POST',
    body: JSON.stringify({ statement }),
  })
}

/**
 * Get deck statistics
 * @param {string} deckName - Name of the deck
 * @returns {Promise<object>} - Deck statistics
 */
export const getDeckStats = async (deckName) => {
  const url = `${API_CONFIG.ENDPOINTS.DECK_STATS}?deck_name=${encodeURIComponent(deckName)}`
  return await apiCall(url)
}

/**
 * Add notes to Anki
 * @param {Array} notes - Array of note objects to add
 * @returns {Promise<object>} - Add notes result
 */
export const addNotesToAnki = async (notes) => {
  return await apiCall(API_CONFIG.ENDPOINTS.ADD_NOTES, {
    method: 'POST',
    body: JSON.stringify({ notes }),
  })
}

/**
 * Get available note models
 * @returns {Promise<object>} - Note models list
 */
export const getNoteModels = async () => {
  return await apiCall(API_CONFIG.ENDPOINTS.NOTE_MODELS)
}

/**
 * Create a new Anki deck
 * @param {string} deckName - Name of the deck to create
 * @returns {Promise<object>} - Create deck result
 */
export const createDeck = async (deckName) => {
  return await apiCall(API_CONFIG.ENDPOINTS.CREATE_DECK, {
    method: 'POST',
    body: JSON.stringify({ deck_name: deckName }),
  })
}

/**
 * Start GUI deck review in Anki
 * @param {string} deckName - Name of the deck to review
 * @returns {Promise<object>} - GUI review result
 */
export const guiDeckReview = async (deckName) => {
  return await apiCall(API_CONFIG.ENDPOINTS.GUI_DECK_REVIEW, {
    method: 'POST',
    body: JSON.stringify({ deck_name: deckName }),
  })
}

/**
 * Answer cards with ratings
 * @param {Array} answers - Array of answer objects with cardId and ease
 * @returns {Promise<object>} - Answer cards result
 */
export const answerCards = async (answers) => {
  return await apiCall(API_CONFIG.ENDPOINTS.ANSWER_CARDS, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  })
}
