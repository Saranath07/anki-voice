<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <div class="flex justify-center mb-4">
        <div class="avatar">
          <div class="w-16 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center">
            <span class="text-3xl">✨</span>
          </div>
        </div>
      </div>
      <h2 class="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">
        Add QA Cards
      </h2>
      <p class="text-base-content/70 text-lg">Generate intelligent flashcards from your content using AI</p>
    </div>

    <!-- Deck Creation -->
    <div class="card bg-gradient-to-br from-primary/5 to-secondary/5 shadow-xl border border-primary/20">
      <div class="card-body">
        <div class="flex items-center gap-3 mb-4">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <span class="text-xl">🆕</span>
            </div>
          </div>
          <h3 class="card-title text-xl text-primary">Create New Deck</h3>
        </div>
        
        <div class="form-control">
          <label class="label">
            <span class="label-text font-semibold text-base">Deck Name</span>
            <span class="label-text-alt text-primary">Optional</span>
          </label>
          <div class="join shadow-lg">
            <input
              v-model="newDeckName"
              type="text"
              placeholder="Enter new deck name..."
              class="input input-bordered input-primary join-item flex-1 focus:shadow-lg transition-all"
              @keyup.enter="createDeck"
            />
            <button
              @click="createDeck"
              :disabled="!newDeckName.trim() || creating"
              class="btn btn-primary join-item hover:btn-secondary transition-all"
            >
              <span v-if="creating" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              {{ creating ? 'Creating...' : 'Create' }}
            </button>
          </div>
          <label class="label">
            <span class="label-text-alt text-base-content/60">Create a new deck to organize your flashcards</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Statement Input -->
    <div class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body">
        <div class="flex items-center gap-3 mb-6">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-secondary/20 flex items-center justify-center">
              <span class="text-xl">📝</span>
            </div>
          </div>
          <h3 class="card-title text-xl text-secondary">Content Input</h3>
        </div>
        
        <div class="space-y-6">
          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold text-base">Statement, Theorem, or Fact</span>
              <span class="label-text-alt badge badge-secondary badge-sm">Required</span>
            </label>
            <textarea
              v-model="statement"
              placeholder="Enter your statement, theorem, or fact here...

Example: 
The Pythagorean theorem states that in a right-angled triangle, the square of the length of the hypotenuse is equal to the sum of the squares of the lengths of the other two sides."
              rows="8"
              class="textarea textarea-bordered textarea-secondary focus:textarea-primary transition-all shadow-sm"
            ></textarea>
            <label class="label">
              <span class="label-text-alt text-base-content/60">
                💡 Tip: Provide detailed explanations for better question generation
              </span>
            </label>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-semibold text-base">Note Model</span>
              <span class="label-text-alt text-info">Choose card format</span>
            </label>
            <select v-model="selectedModel" class="select select-bordered select-info focus:select-primary transition-all shadow-sm">
              <option value="">🎯 Select a model...</option>
              <option v-for="model in modelNames" :key="model" :value="model">
                📋 {{ model }}
              </option>
            </select>
            <label class="label">
              <span class="label-text-alt text-base-content/60">
                The note model determines the card format and fields
              </span>
            </label>
          </div>
        </div>

        <div class="card-actions justify-end mt-8">
          <button
            @click="generateQAPairs"
            :disabled="!statement.trim() || generating"
            class="btn btn-primary btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all"
          >
            <span v-if="generating" class="loading loading-spinner loading-sm"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {{ generating ? 'Generating Magic...' : 'Generate QA Pairs' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Generated QA Pairs -->
    <div v-if="qaPairs.length > 0" class="card bg-base-100 shadow-xl border border-accent/30">
      <div class="card-body">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <div class="avatar">
              <div class="w-10 rounded-lg bg-accent/20 flex items-center justify-center">
                <span class="text-xl">✨</span>
              </div>
            </div>
            <h3 class="card-title text-xl text-accent">Generated QA Pairs</h3>
            <div class="badge badge-accent badge-lg">{{ qaPairs.length }} pairs</div>
          </div>
          
          <div class="flex flex-wrap gap-2">
            <button @click="selectAll" class="btn btn-sm btn-outline btn-accent hover:btn-accent">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Select All
            </button>
            <button @click="selectNone" class="btn btn-sm btn-outline btn-warning hover:btn-warning">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Select None
            </button>
            <button @click="clearQAPairs" class="btn btn-sm btn-error btn-outline hover:btn-error">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Clear All
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <div v-for="(qa, index) in qaPairs" :key="index" 
               class="card bg-gradient-to-r from-base-50 to-base-100 border border-base-300 hover:shadow-lg transition-all duration-200">
            <div class="card-body">
              <div class="flex items-start gap-4">
                <div class="form-control">
                  <label class="label cursor-pointer">
                    <input v-model="qa.selected" type="checkbox" class="checkbox checkbox-primary checkbox-lg" />
                  </label>
                </div>
                
                <div class="flex-1 space-y-4">
                  <div class="form-control">
                    <label class="label">
                      <span class="label-text font-semibold text-primary flex items-center gap-2">
                        <span class="text-lg">❓</span>
                        Question
                      </span>
                    </label>
                    <div class="p-4 bg-primary/5 rounded-lg border border-primary/20 shadow-sm">
                      <p class="text-base-content leading-relaxed">{{ qa.question }}</p>
                    </div>
                  </div>
                  
                  <div class="form-control">
                    <label class="label">
                      <span class="label-text font-semibold text-secondary flex items-center gap-2">
                        <span class="text-lg">✅</span>
                        Answer
                      </span>
                    </label>
                    <div class="p-4 bg-secondary/5 rounded-lg border border-secondary/20 shadow-sm">
                      <p class="text-base-content leading-relaxed">{{ qa.answer }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col lg:flex-row items-center justify-between gap-4 mt-8 p-6 bg-gradient-to-r from-success/10 to-info/10 rounded-xl border border-success/20">
          <div class="stats shadow-lg bg-base-100">
            <div class="stat">
              <div class="stat-figure text-success">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="stat-title">Selected</div>
              <div class="stat-value text-success">{{ selectedQACount }}</div>
              <div class="stat-desc">of {{ qaPairs.length }} pairs</div>
            </div>
          </div>
          
          <button
            @click="addSelectedToAnki"
            :disabled="selectedQACount === 0 || adding"
            class="btn btn-success btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all"
          >
            <span v-if="adding" class="loading loading-spinner loading-sm"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            {{ adding ? 'Adding to Anki...' : 'Add Selected to Anki' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessage" class="alert shadow-lg" :class="{
      'alert-success': statusType === 'success',
      'alert-error': statusType === 'error',
      'alert-info': statusType === 'info',
      'alert-warning': statusType === 'warning'
    }">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path v-if="statusType === 'success'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        <path v-else-if="statusType === 'error'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        <path v-else-if="statusType === 'warning'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div>
        <h3 class="font-bold">{{ getStatusTitle() }}</h3>
        <div class="text-xs">{{ statusMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { generateFlashcards, addNotesToAnki, getNoteModels, createDeck as createDeckAPI, apiCall, API_CONFIG } from '@/config/api.js'

const props = defineProps({
  selectedDeck: String,
  modelNames: Array
})

const emit = defineEmits(['deck-created'])

// Reactive state
const newDeckName = ref('')
const statement = ref('')
const selectedModel = ref('')
const qaPairs = ref([])
const creating = ref(false)
const generating = ref(false)
const adding = ref(false)
const statusMessage = ref('')
const statusType = ref('success') // 'success', 'error', 'info'

// Computed
const selectedQACount = computed(() =>
  qaPairs.value.filter(qa => qa.selected).length
)

const showStatus = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

// LLM integration via Flask backend
const generateQAPairs = async () => {
  if (!statement.value.trim()) {
    showStatus('Please enter a statement to generate flashcards', 'error')
    return
  }

  generating.value = true
  try {
    const response = await generateFlashcards(statement.value.trim())

    if (response.success && response.flashcards) {
      qaPairs.value = response.flashcards.map((qa, index) => ({
        ...qa,
        id: `qa-${Date.now()}-${index}`,
        selected: true
      }))
      showStatus(`Generated ${response.count} flashcards successfully!`, 'success')
    } else {
      throw new Error('Failed to generate flashcards')
    }
  } catch (err) {
    showStatus(`Failed to generate QA pairs: ${err.message}`, 'error')
  } finally {
    generating.value = false
  }
}

const parseQAResponse = (responseText) => {
  try {
    // Clean up the response text
    const cleaned = responseText.trim()

    // Try to parse as JSON first
    try {
      const parsed = JSON.parse(cleaned)
      if (Array.isArray(parsed)) {
        return parsed.map(item => ({
          question: item.question || item.Q || '',
          answer: item.answer || item.A || '',
          selected: true
        }))
      }
    } catch (e) {
      // JSON parsing failed, continue with other methods
    }

    // Try to find a list pattern
    const listPattern = /\[.*?\]/s
    const matches = cleaned.match(listPattern)

    if (matches) {
      try {
        const parsed = JSON.parse(matches[0])
        return parsed.map(item => ({
          question: item.question || item.Q || '',
          answer: item.answer || item.A || '',
          selected: true
        }))
      } catch (e) {
        // Continue with fallback
      }
    }

    // Fallback: convert old Q/A format
    const lines = cleaned.split('\n')
    const pairs = []
    let currentQ = null

    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed.startsWith('Q:') || trimmed.startsWith('Question:')) {
        currentQ = trimmed.replace(/^(Q:|Question:)\s*/, '')
      } else if ((trimmed.startsWith('A:') || trimmed.startsWith('Answer:')) && currentQ) {
        const answer = trimmed.replace(/^(A:|Answer:)\s*/, '')
        pairs.push({
          question: currentQ,
          answer: answer,
          selected: true
        })
        currentQ = null
      }
    }

    return pairs.length > 0 ? pairs : []
  } catch (err) {
    console.error('Error parsing QA response:', err)
    return []
  }
}

// Actions
const createDeck = async () => {
  if (!newDeckName.value.trim()) return

  creating.value = true
  try {
    await createDeckAPI(newDeckName.value.trim())
    showStatus(`Deck "${newDeckName.value}" created successfully!`, 'success')
    newDeckName.value = ''
    emit('deck-created')
  } catch (err) {
    showStatus(`Failed to create deck: ${err.message}`, 'error')
  } finally {
    creating.value = false
  }
}

const selectAll = () => {
  qaPairs.value.forEach(qa => qa.selected = true)
}

const selectNone = () => {
  qaPairs.value.forEach(qa => qa.selected = false)
}

const clearQAPairs = () => {
  qaPairs.value = []
  showStatus('Cleared all QA pairs', 'info')
}

const addSelectedToAnki = async () => {
  const selectedPairs = qaPairs.value.filter(qa => qa.selected)
  if (selectedPairs.length === 0) return

  if (!props.selectedDeck) {
    showStatus('Please select a deck first', 'error')
    return
  }

  if (!selectedModel.value) {
    showStatus('Please select a note model first', 'error')
    return
  }

  adding.value = true
  try {
    const notes = selectedPairs.map(qa => ({
      deckName: props.selectedDeck,
      modelName: selectedModel.value,
      fields: {
        Front: qa.question,
        Back: qa.answer
      }
    }))

    const result = await addNotesToAnki(notes)
    const successCount = result.success_count || 0

    if (successCount > 0) {
      showStatus(`Successfully added ${successCount} cards to Anki!`, 'success')
      // Remove successfully added pairs
      qaPairs.value = qaPairs.value.filter(qa => !qa.selected)
    } else {
      showStatus('Failed to add cards to Anki', 'error')
    }
  } catch (err) {
    showStatus(`Failed to add cards: ${err.message}`, 'error')
  } finally {
    adding.value = false
  }
}

const getStatusTitle = () => {
  switch (statusType.value) {
    case 'success': return 'Success!'
    case 'error': return 'Error'
    case 'warning': return 'Warning'
    case 'info': return 'Information'
    default: return 'Status'
  }
}
</script>
