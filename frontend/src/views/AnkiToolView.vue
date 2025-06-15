<template>
  <div class="min-h-screen bg-gradient-to-br from-base-100 to-base-200">
    <!-- Header -->
    <div class="navbar bg-gradient-to-r from-primary via-secondary to-accent text-primary-content shadow-xl">
      <div class="navbar-start">
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li v-for="mode in modes" :key="mode.value">
              <a @click="currentMode = mode.value" :class="{ 'active': currentMode === mode.value }">
                {{ mode.label }}
              </a>
            </li>
          </ul>
        </div>
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-full bg-white/20 flex items-center justify-center">
              <span class="text-2xl">🧠</span>
            </div>
          </div>
          <div>
            <h1 class="text-xl font-bold">Anki LLM Companion</h1>
            <p class="text-sm opacity-80">AI-powered learning assistant</p>
          </div>
        </div>
      </div>
      <div class="navbar-end">
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
            <div class="w-10 rounded-full bg-white/20 flex items-center justify-center">
              <span class="text-lg">⚙️</span>
            </div>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><a>Settings</a></li>
            <li><a>Help</a></li>
            <li><a>About</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto p-4 lg:p-8">
      <div class="grid lg:grid-cols-4 gap-6">
        <!-- Sidebar -->
        <div class="lg:col-span-1">
          <div class="sticky top-4 space-y-6">
            <!-- Deck Selection Card -->
            <div class="card bg-base-100 shadow-xl border border-base-300">
              <div class="card-body">
                <h3 class="card-title text-lg text-primary flex items-center gap-2">
                  <span class="text-2xl">📚</span>
                  Deck Selection
                </h3>
                <div class="form-control">
                  <label class="label">
                    <span class="label-text font-medium">Choose your deck</span>
                  </label>
                  <select 
                    v-model="selectedDeck" 
                    @change="onDeckChange"
                    class="select select-bordered select-primary w-full focus:select-secondary"
                  >
                    <option value="">🎯 Select a deck...</option>
                    <option v-for="deck in decks" :key="deck" :value="deck">
                      📝 {{ deck }}
                    </option>
                  </select>
                </div>
                
                <div v-if="!decks.length" class="alert alert-warning">
                  <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <div>
                    <h4 class="font-bold">No decks found</h4>
                    <p class="text-sm">Make sure Anki is running with AnkiConnect enabled.</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Mode Selection Card -->
            <div class="card bg-base-100 shadow-xl border border-base-300">
              <div class="card-body">
                <h3 class="card-title text-lg text-secondary flex items-center gap-2">
                  <span class="text-2xl">🎮</span>
                  Study Mode
                </h3>
                <div class="space-y-2">
                  <button
                    v-for="mode in modes"
                    :key="mode.value"
                    @click="currentMode = mode.value"
                    class="btn w-full justify-start transition-all duration-200"
                    :class="{
                      'btn-primary shadow-lg scale-105': currentMode === mode.value,
                      'btn-outline btn-primary hover:btn-primary': currentMode !== mode.value
                    }"
                  >
                    {{ mode.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Quick Stats Card -->
            <div v-if="selectedDeck" class="card bg-gradient-to-br from-info to-info-content text-info-content shadow-xl">
              <div class="card-body">
                <h3 class="card-title text-sm">📊 Quick Stats</h3>
                <div class="stats stats-vertical">
                  <div class="stat py-2">
                    <div class="stat-title text-info-content/70 text-xs">Current Deck</div>
                    <div class="stat-value text-sm">{{ selectedDeck }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="lg:col-span-3">
          <div class="card bg-base-100 shadow-xl border border-base-300 min-h-[600px]">
            <div class="card-body">
              <!-- Loading State -->
              <div v-if="loading" class="flex flex-col justify-center items-center py-20">
                <span class="loading loading-spinner loading-lg text-primary mb-4"></span>
                <p class="text-base-content/60">Loading your data...</p>
              </div>

              <!-- Error Message -->
              <div v-else-if="error" class="alert alert-error shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 class="font-bold">Error occurred!</h3>
                  <div class="text-xs">{{ error }}</div>
                </div>
              </div>

              <!-- Mode Content -->
              <div v-else class="mode-content">
                <!-- Add Cards Mode -->
                <AddCardsMode
                  v-if="currentMode === 'add'"
                  :selected-deck="selectedDeck"
                  :model-names="modelNames"
                  @deck-created="refreshDecks"
                />
                
                <!-- Review Cards Mode -->
                <ReviewCardsMode
                  v-if="currentMode === 'review'"
                  :selected-deck="selectedDeck"
                  :cards="reviewCards"
                  @refresh-cards="loadReviewCards"
                />
                
                <!-- Deck Stats Mode -->
                <DeckStatsMode 
                  v-if="currentMode === 'stats'" 
                  :selected-deck="selectedDeck" 
                  :deck-stats="deckStats" 
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AddCardsMode from '../components/AddCardsMode.vue'
import ReviewCardsMode from '../components/ReviewCardsMode.vue'
import DeckStatsMode from '../components/DeckStatsMode.vue'
import { apiCall, getDecks, getDeckStats, getNoteModels, API_CONFIG } from '@/config/api.js'

// Reactive state
const selectedDeck = ref('')
const currentMode = ref('add')
const decks = ref([])
const modelNames = ref([])
const reviewCards = ref([])
const deckStats = ref({})
const loading = ref(false)
const error = ref('')

// Constants
const modes = [
  { value: 'add', label: '➕ Add Cards' },
  { value: 'review', label: '📝 Review Cards' },
  { value: 'stats', label: '📊 Deck Stats' },
]

// API methods using Flask backend
const getDeckNames = async () => {
  try {
    const response = await getDecks()
    return response.success ? response.decks : []
  } catch (err) {
    console.error('Failed to get deck names:', err)
    return []
  }
}

const getModelNames = async () => {
  try {
    const response = await getNoteModels()
    return response.success ? response.models : []
  } catch (err) {
    console.error('Failed to get model names:', err)
    return []
  }
}

// Note: These functions still need AnkiConnect integration through Flask backend
// For now, they will use the existing API endpoints
const findCards = async (query) => {
  try {
    // This functionality would need a new Flask endpoint
    // For now, return empty array
    console.warn('findCards: Function needs Flask backend endpoint')
    return []
  } catch (err) {
    console.error('Failed to find cards:', err)
    return []
  }
}

const getCardsInfo = async (cardIds) => {
  try {
    // This functionality would need a new Flask endpoint  
    // For now, return empty array
    console.warn('getCardsInfo: Function needs Flask backend endpoint')
    return []
  } catch (err) {
    console.error('Failed to get cards info:', err)
    return []
  }
}

// Load initial data
const loadDecks = async () => {
  loading.value = true
  try {
    const deckList = await getDeckNames()
    decks.value = deckList || []
  } catch (err) {
    error.value = 'Failed to load decks'
  } finally {
    loading.value = false
  }
}

const loadModelNames = async () => {
  try {
    const models = await getModelNames()
    modelNames.value = models || []
  } catch (err) {
    console.error('Failed to load model names:', err)
  }
}

const loadDeckStats = async () => {
  if (!selectedDeck.value) return

  try {
    const stats = await getDeckStats(selectedDeck.value)
    deckStats.value = stats
  } catch (err) {
    console.error('Failed to load deck stats:', err)
    deckStats.value = {}
  }
}

const loadReviewCards = async () => {
  if (!selectedDeck.value) return

  try {
    // Get due cards
    const dueCardIds = await findCards(`deck:"${selectedDeck.value}" is:due`)
    // Get new cards
    const newCardIds = await findCards(`deck:"${selectedDeck.value}" is:new`)

    // Combine and deduplicate
    const allCardIds = [...new Set([...(dueCardIds || []), ...(newCardIds || [])])]

    // If no due/new cards, get all cards
    if (allCardIds.length === 0) {
      const allDeckCardIds = await findCards(`deck:"${selectedDeck.value}"`)
      allCardIds.push(...(allDeckCardIds || []))
    }

    // Get card information
    const cards = await getCardsInfo(allCardIds)
    reviewCards.value = cards || []
  } catch (err) {
    console.error('Failed to load review cards:', err)
    reviewCards.value = []
  }
}

// Event handlers
const onDeckChange = () => {
  if (currentMode.value === 'stats') {
    loadDeckStats()
  } else if (currentMode.value === 'review') {
    loadReviewCards()
  }
}

const refreshDecks = () => {
  loadDecks()
}

// Lifecycle
onMounted(async () => {
  await loadDecks()
  await loadModelNames()
})
</script>
