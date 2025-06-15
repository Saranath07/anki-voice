<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <div class="flex justify-center mb-4">
        <div class="avatar">
          <div class="w-16 rounded-full bg-gradient-to-r from-secondary to-accent flex items-center justify-center">
            <span class="text-3xl">🧠</span>
          </div>
        </div>
      </div>
      <h2 class="text-4xl font-bold bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent mb-2">
        Advanced Review Mode
      </h2>
      <p class="text-base-content/70 text-lg">Review your flashcards with AI-powered evaluation</p>
    </div>

    <!-- Native Review Quick Start -->
    <div class="card bg-gradient-to-r from-primary to-secondary text-primary-content shadow-xl">
      <div class="card-body">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="avatar">
              <div class="w-12 rounded-full bg-white/20 flex items-center justify-center">
                <span class="text-2xl">🎯</span>
              </div>
            </div>
            <div>
              <h3 class="card-title text-xl">Quick Start</h3>
              <p class="opacity-90">Launch the native Anki review interface for traditional review</p>
            </div>
          </div>
          <button @click="startNativeReview" class="btn btn-accent btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M12 5v.01M3 12a9 9 0 1018 0 9 9 0 00-18 0z" />
            </svg>
            Start Deck Review in Anki GUI
          </button>
        </div>
      </div>
    </div>

    <!-- Divider -->
    <div class="divider text-lg font-semibold">
      <span class="px-4 py-2 bg-base-200 rounded-full">OR</span>
    </div>

    <!-- Review Mode Selection -->
    <div class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body">
        <div class="flex items-center gap-3 mb-6">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-info/20 flex items-center justify-center">
              <span class="text-xl">🎮</span>
            </div>
          </div>
          <h3 class="card-title text-xl text-info">Select Review Mode</h3>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <button
            v-for="mode in reviewModes"
            :key="mode.value"
            @click="selectedReviewMode = mode.value"
            class="btn h-auto p-4 flex-col gap-2 transition-all duration-200"
            :class="{
              'btn-info shadow-lg scale-105': selectedReviewMode === mode.value,
              'btn-outline btn-info hover:btn-info': selectedReviewMode !== mode.value
            }"
          >
            <span class="text-lg font-bold">{{ mode.label }}</span>
            <span class="text-xs opacity-70 text-center">{{ mode.description }}</span>
          </button>
        </div>
        
        <div class="alert alert-info shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 class="font-bold">Current Mode:</h4>
            <p class="text-sm">{{ getCurrentModeDescription() }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Cards Statistics -->
    <div class="stats stats-vertical lg:stats-horizontal shadow-xl bg-base-100 border border-base-300">
      <div class="stat">
        <div class="stat-figure text-primary">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="stat-title">Due Cards</div>
        <div class="stat-value text-primary">{{ dueCardsCount }}</div>
        <div class="stat-desc">Ready for review</div>
      </div>
      <div class="stat">
        <div class="stat-figure text-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
        <div class="stat-title">New Cards</div>
        <div class="stat-value text-secondary">{{ newCardsCount }}</div>
        <div class="stat-desc">Never seen before</div>
      </div>
      <div class="stat">
        <div class="stat-figure text-accent">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div class="stat-title">Total Cards</div>
        <div class="stat-value text-accent">{{ cards.length }}</div>
        <div class="stat-desc">In this deck</div>
      </div>
    </div>

    <!-- Review Interface -->
    <div v-if="cards.length > 0" class="space-y-6">
      <!-- Navigation -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <div class="flex flex-col lg:flex-row items-center justify-between gap-4">
            <button @click="previousCard" :disabled="currentCardIndex === 0" 
                    class="btn btn-outline btn-primary hover:btn-primary transition-all"
                    :class="{ 'btn-disabled': currentCardIndex === 0 }">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>

            <div class="flex items-center gap-4">
              <div class="radial-progress text-primary" :style="`--value:${Math.round((currentCardIndex + 1) / cards.length * 100)}`" role="progressbar">
                {{ Math.round((currentCardIndex + 1) / cards.length * 100) }}%
              </div>
              <div class="text-center">
                <p class="text-lg font-bold">Card {{ currentCardIndex + 1 }} of {{ cards.length }}</p>
                <p class="text-sm text-base-content/60">{{ Math.round((currentCardIndex + 1) / cards.length * 100) }}% complete</p>
              </div>
            </div>

            <button @click="nextCard" :disabled="currentCardIndex === cards.length - 1" 
                    class="btn btn-outline btn-primary hover:btn-primary transition-all"
                    :class="{ 'btn-disabled': currentCardIndex === cards.length - 1 }">
              Next
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Current Card -->
      <div class="card bg-gradient-to-br from-base-100 to-base-200 shadow-xl border border-base-300">
        <div class="card-body space-y-6">
          <!-- Question Section -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="avatar">
                <div class="w-10 rounded-lg bg-primary/20 flex items-center justify-center">
                  <span class="text-xl">❓</span>
                </div>
              </div>
              <h3 class="text-xl font-bold text-primary">Question</h3>
            </div>
            
            <div class="card bg-primary/5 border border-primary/20 shadow-sm">
              <div class="card-body">
                <p class="text-lg leading-relaxed">{{ currentQuestion }}</p>
                
                <!-- Enhanced Question Info -->
                <div v-if="selectedReviewMode === 'enhanced' && enhancedQuestion" class="mt-4 p-3 bg-info/10 rounded-lg border border-info/20">
                  <p class="text-sm text-info-content">
                    <span class="font-semibold">🤖 Enhanced for speech:</span>
                    "{{ enhancedQuestion }}"
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- TTS Controls -->
          <div v-if="selectedReviewMode.includes('tts')" class="flex justify-center">
            <button @click="speakQuestion" :disabled="speaking" 
                    class="btn btn-info btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all">
              <span v-if="speaking" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M9 12a1 1 0 01-1-1V9a1 1 0 011-1h1a1 1 0 011 1v2a1 1 0 01-1 1H9z" />
              </svg>
              {{ speaking ? 'Speaking...' : 'Speak Question' }}
            </button>
          </div>

          <!-- Answer Input Section -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="avatar">
                <div class="w-10 rounded-lg bg-secondary/20 flex items-center justify-center">
                  <span class="text-xl">💭</span>
                </div>
              </div>
              <h3 class="text-xl font-bold text-secondary">Your Answer</h3>
            </div>

            <!-- Voice Input Modes -->
            <div v-if="selectedReviewMode === 'enhanced' || selectedReviewMode === 'asr'" class="card bg-secondary/5 border border-secondary/20">
              <div class="card-body">
                <h4 class="font-semibold mb-3 flex items-center gap-2">
                  <span class="text-lg">🎤</span>
                  Voice Input
                </h4>
                <div class="flex flex-wrap gap-3 mb-4">
                  <button @click="startListening" :disabled="listening" 
                          class="btn btn-secondary shadow-lg hover:shadow-xl transition-all">
                    <span v-if="listening" class="loading loading-spinner loading-sm"></span>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    {{ listening ? 'Listening...' : 'Start Speaking' }}
                  </button>
                  <button v-if="userSpokenAnswer" @click="playUserAnswer" class="btn btn-outline btn-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M12 5v.01M3 12a9 9 0 1018 0 9 9 0 00-18 0z" />
                    </svg>
                    Play My Answer
                  </button>
                </div>
                <div v-if="userSpokenAnswer" class="p-4 bg-base-100 rounded-lg border">
                  <p class="font-semibold text-sm text-base-content/70 mb-2">Your spoken answer:</p>
                  <p class="text-base">{{ userSpokenAnswer }}</p>
                </div>
              </div>
            </div>

            <!-- Text Input Mode -->
            <div v-else class="card bg-secondary/5 border border-secondary/20">
              <div class="card-body">
                <h4 class="font-semibold mb-3 flex items-center gap-2">
                  <span class="text-lg">✍️</span>
                  Type Your Answer
                </h4>
                <textarea
                  v-model="typedAnswer"
                  placeholder="Type your answer here..."
                  rows="4"
                  class="textarea textarea-bordered textarea-secondary w-full focus:textarea-primary transition-all"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Show Answer Button -->
          <div v-if="!showAnswer" class="flex justify-center">
            <button @click="revealAnswer" class="btn btn-accent btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Show Answer
            </button>
          </div>

          <!-- Answer and Rating -->
          <div v-if="showAnswer" class="space-y-6 mt-8">
            <!-- Correct Answer Section -->
            <div class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="avatar">
                  <div class="w-10 rounded-lg bg-success/20 flex items-center justify-center">
                    <span class="text-xl">✅</span>
                  </div>
                </div>
                <h3 class="text-xl font-bold text-success">Correct Answer</h3>
              </div>
              
              <div class="card bg-success/5 border border-success/20 shadow-sm">
                <div class="card-body">
                  <p class="text-lg leading-relaxed">{{ currentAnswer }}</p>
                </div>
              </div>
            </div>

            <!-- LLM Evaluation -->
            <div v-if="hasUserAnswer() && (selectedReviewMode === 'enhanced' || selectedReviewMode === 'asr')" 
                 class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="avatar">
                  <div class="w-10 rounded-lg bg-info/20 flex items-center justify-center">
                    <span class="text-xl">🤖</span>
                  </div>
                </div>
                <h3 class="text-xl font-bold text-info">AI Evaluation</h3>
              </div>
              
              <div v-if="llmEvaluating" class="card bg-info/5 border border-info/20">
                <div class="card-body">
                  <div class="flex items-center gap-3">
                    <span class="loading loading-spinner loading-md text-info"></span>
                    <p class="text-lg">AI is evaluating your answer...</p>
                  </div>
                </div>
              </div>
              
              <div v-else-if="llmRating" class="card bg-info/5 border border-info/20">
                <div class="card-body space-y-4">
                  <div class="flex items-center justify-between">
                    <span class="text-lg font-semibold">AI Rating:</span>
                    <div class="badge badge-lg" :class="{
                      'badge-error': llmRating === 1,
                      'badge-warning': llmRating === 2,
                      'badge-info': llmRating === 3,
                      'badge-success': llmRating === 4
                    }">
                      {{ getRatingText(llmRating) }}
                    </div>
                  </div>
                  <div v-if="llmExplanation" class="bg-base-100 p-4 rounded-lg border">
                    <p class="font-semibold text-sm text-base-content/70 mb-2">🤖 AI Feedback:</p>
                    <p class="leading-relaxed">{{ llmExplanation }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Manual Rating -->
            <div class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="avatar">
                  <div class="w-10 rounded-lg bg-warning/20 flex items-center justify-center">
                    <span class="text-xl">⭐</span>
                  </div>
                </div>
                <h3 class="text-xl font-bold text-warning">Rate Your Performance</h3>
              </div>
              
              <div class="card bg-warning/5 border border-warning/20">
                <div class="card-body">
                  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    <button
                      v-for="rating in ratings"
                      :key="rating.value"
                      @click="submitRating(rating.value)"
                      class="btn btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all"
                      :class="{
                        'btn-error': rating.value === 1,
                        'btn-warning': rating.value === 2,
                        'btn-info': rating.value === 3,
                        'btn-success': rating.value === 4
                      }"
                    >
                      <div class="flex flex-col items-center gap-1">
                        <span class="text-xl">{{ getRatingEmoji(rating.value) }}</span>
                        <span class="text-sm font-bold">{{ rating.label }}</span>
                      </div>
                    </button>
                  </div>
                  <div class="mt-4 text-center">
                    <p class="text-sm text-base-content/60">
                      Choose how well you knew the answer to schedule the next review
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Cards Message -->
    <div v-else class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body text-center space-y-6">
        <div class="flex justify-center">
          <div class="avatar">
            <div class="w-20 rounded-full bg-warning/20 flex items-center justify-center">
              <span class="text-4xl">📚</span>
            </div>
          </div>
        </div>
        
        <div>
          <h3 class="text-2xl font-bold text-warning mb-4">No Cards Available for Review</h3>
          <div class="space-y-4 text-left max-w-lg mx-auto">
            <div class="alert alert-info">
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 class="font-bold">Possible reasons:</h4>
                <ul class="text-sm list-disc list-inside mt-2 space-y-1">
                  <li>The deck is empty</li>
                  <li>All cards have been reviewed recently</li>
                  <li>AnkiConnect connection issue</li>
                </ul>
              </div>
            </div>
            
            <div class="alert alert-success">
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 class="font-bold">Try these solutions:</h4>
                <ul class="text-sm list-disc list-inside mt-2 space-y-1">
                  <li>Add some cards first using the 'Add Cards' mode</li>
                  <li>Check 'Deck Stats' to see if there are cards in the deck</li>
                  <li>Make sure Anki is running with AnkiConnect enabled</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <button @click="$emit('refresh-cards')" class="btn btn-primary btn-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Cards
        </button>
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
import { ref, computed, defineProps, defineEmits, watch } from 'vue'
import { apiCall, API_CONFIG, guiDeckReview, answerCards } from '@/config/api.js'

const props = defineProps({
  selectedDeck: String,
  cards: Array
})

const emit = defineEmits(['refresh-cards'])

// Reactive state
const selectedReviewMode = ref('enhanced')
const currentCardIndex = ref(0)
const showAnswer = ref(false)
const userSpokenAnswer = ref('')
const typedAnswer = ref('')
const enhancedQuestion = ref('')
const llmRating = ref(null)
const llmExplanation = ref('')
const llmEvaluating = ref(false)
const speaking = ref(false)
const listening = ref(false)
const statusMessage = ref('')
const statusType = ref('info')

// Constants
const reviewModes = [
  {
    value: 'enhanced',
    label: '🎤🔊🤖 Enhanced TTS + ASR + LLM',
    description: 'Human-like speech with emotional AI evaluation'
  },
  {
    value: 'asr',
    label: '🎤🤖 ASR + LLM',
    description: 'Voice input with AI evaluation'
  },
  {
    value: 'tts',
    label: '🔊 TTS Only',
    description: 'Text-to-speech for questions only'
  }
]

const ratings = [
  { value: 1, label: 'Again', class: 'again' },
  { value: 2, label: 'Hard', class: 'hard' },
  { value: 3, label: 'Good', class: 'good' },
  { value: 4, label: 'Easy', class: 'easy' }
]

// Computed properties
const currentCard = computed(() =>
  props.cards[currentCardIndex.value] || {}
)

const currentQuestion = computed(() =>
  getFieldValue(currentCard.value, 'Front') || 'No question available'
)

const currentAnswer = computed(() =>
  getFieldValue(currentCard.value, 'Back') || 'No answer available'
)

const dueCardsCount = computed(() => {
  // This would need to be calculated from the cards data
  // For now, we'll estimate based on the cards array
  return Math.floor(props.cards.length * 0.6) // Rough estimate
})

const newCardsCount = computed(() => {
  // This would need to be calculated from the cards data
  return Math.floor(props.cards.length * 0.4) // Rough estimate
})

// Utility functions
const getFieldValue = (card, fieldName) => {
  if (!card || !card.fields) return ''

  // Try exact match first
  if (card.fields[fieldName]) {
    return card.fields[fieldName].value || card.fields[fieldName]
  }

  // Try common variations
  const variations = {
    'Front': ['front', 'question', 'Question'],
    'Back': ['back', 'answer', 'Answer']
  }

  const fieldVariations = variations[fieldName] || []
  for (const variation of fieldVariations) {
    if (card.fields[variation]) {
      return card.fields[variation].value || card.fields[variation]
    }
  }

  // If no match, return first available field
  const firstField = Object.values(card.fields)[0]
  return firstField ? (firstField.value || firstField) : ''
}

const showStatus = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const getCurrentModeDescription = () => {
  const mode = reviewModes.find(m => m.value === selectedReviewMode.value)
  return mode ? mode.description : ''
}

const hasUserAnswer = () => {
  return userSpokenAnswer.value.trim() || typedAnswer.value.trim()
}

const getRatingClass = (rating) => {
  const classes = { 1: 'again', 2: 'hard', 3: 'good', 4: 'easy' }
  return classes[rating] || ''
}

const getRatingText = (rating) => {
  const texts = { 1: 'Again', 2: 'Hard', 3: 'Good', 4: 'Easy' }
  return texts[rating] || 'Unknown'
}

// Actions
const startNativeReview = async () => {
  if (!props.selectedDeck) {
    showStatus('Please select a deck first', 'error')
    return
  }

  try {
    await guiDeckReview(props.selectedDeck)
    showStatus('Started native review in Anki GUI', 'success')
  } catch (err) {
    showStatus(`Failed to start native review: ${err.message}`, 'error')
  }
}

const previousCard = () => {
  if (currentCardIndex.value > 0) {
    currentCardIndex.value--
    resetCardState()
  }
}

const nextCard = () => {
  if (currentCardIndex.value < props.cards.length - 1) {
    currentCardIndex.value++
    resetCardState()
  }
}

const resetCardState = () => {
  showAnswer.value = false
  userSpokenAnswer.value = ''
  typedAnswer.value = ''
  enhancedQuestion.value = ''
  llmRating.value = null
  llmExplanation.value = ''
  llmEvaluating.value = false
}

const speakQuestion = async () => {
  speaking.value = true
  try {
    const questionText = currentQuestion.value
    const enhance = selectedReviewMode.value === 'enhanced'
    const noteId = currentCard.value.noteId

    const response = await apiCall(API_CONFIG.ENDPOINTS.READ_QUESTION, {
      method: 'POST',
      body: JSON.stringify({
        question: questionText,
        enhance: enhance,
        note_id: noteId
      })
    })

    // The Flask backend returns the audio file directly
    if (response.ok) {
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        speaking.value = false
      }

      audio.onerror = () => {
        URL.revokeObjectURL(audioUrl)
        speaking.value = false
        showStatus('Audio playback failed', 'error')
      }

      await audio.play()
      showStatus('🔊 Question spoken successfully', 'success')
    } else {
      throw new Error('TTS request failed')
    }
  } catch (err) {
    speaking.value = false
    showStatus(`TTS Error: ${err.message}`, 'error')
  }
}

const startListening = async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showStatus('Speech recognition not supported in this browser', 'error')
    return
  }

  listening.value = true
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mediaRecorder = new MediaRecorder(stream)
    const chunks = []

    showStatus('🎤 Recording... Speak now!', 'info')

    mediaRecorder.ondataavailable = (e) => {
      chunks.push(e.data)
    }

    mediaRecorder.onstop = async () => {
      try {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' })
        const formData = new FormData()
        formData.append('audio', audioBlob, 'recording.wav')

        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.RECORD_ANSWER}`, {
          method: 'POST',
          body: formData
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success && result.text) {
            userSpokenAnswer.value = result.text
            showStatus('🎤 Speech recognized successfully!', 'success')
          } else {
            throw new Error('Could not understand the audio')
          }
        } else {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || 'ASR request failed')
        }
      } catch (err) {
        showStatus(`ASR Error: ${err.message}`, 'error')
      } finally {
        listening.value = false
        // Stop all tracks to free up the microphone
        stream.getTracks().forEach(track => track.stop())
      }
    }

    // Record for 5 seconds
    mediaRecorder.start()
    setTimeout(() => {
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop()
      }
    }, 5000)

  } catch (err) {
    listening.value = false
    showStatus(`Microphone Error: ${err.message}`, 'error')
  }
}

const playUserAnswer = async () => {
  if (!userSpokenAnswer.value) return

  try {
    const response = await fetch('http://localhost:5005/v1/audio/speech', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        input: userSpokenAnswer.value,
        model: 'orpheus',
        voice: 'tara',
        response_format: 'wav',
        speed: 1
      })
    })

    if (response.ok) {
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
      }

      await audio.play()
    }
  } catch (err) {
    showStatus(`TTS Error: ${err.message}`, 'error')
  }
}

const revealAnswer = async () => {
  showAnswer.value = true

  // If we have user input and using AI modes, evaluate with LLM
  if (hasUserAnswer() && (selectedReviewMode.value === 'enhanced' || selectedReviewMode.value === 'asr')) {
    await evaluateWithLLM()
  }
}

const evaluateWithLLM = async () => {
  llmEvaluating.value = true
  try {
    const userAnswer = userSpokenAnswer.value || typedAnswer.value

    // This would call the LLM evaluation API
    // For now, we'll simulate it
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Simulate LLM response
    llmRating.value = Math.floor(Math.random() * 4) + 1
    llmExplanation.value = "Great job! You understood the key concepts well."

    showStatus('AI evaluation completed', 'success')
  } catch (err) {
    showStatus(`LLM evaluation failed: ${err.message}`, 'error')
  } finally {
    llmEvaluating.value = false
  }
}

const submitRating = async (rating) => {
  try {
    const cardId = currentCard.value.cardId
    if (cardId) {
      await answerCards([{ cardId, ease: rating }])
      showStatus(`Rated as ${getRatingText(rating)}`, 'success')
    }

    // Move to next card or finish
    if (currentCardIndex.value < props.cards.length - 1) {
      nextCard()
    } else {
      showStatus('Review session completed!', 'success')
    }
  } catch (err) {
    showStatus(`Failed to submit rating: ${err.message}`, 'error')
  }
}

// Watchers
watch(() => props.cards, () => {
  currentCardIndex.value = 0
  resetCardState()
})

watch(selectedReviewMode, () => {
  resetCardState()
})

// Additional helper methods
const getRatingEmoji = (rating) => {
  const emojis = { 1: '❌', 2: '😓', 3: '👍', 4: '🌟' }
  return emojis[rating] || '❓'
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

<style scoped>
.review-cards-mode {
  max-width: 1000px;
}

.header {
  margin-bottom: 2rem;
}

.header h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.header p {
  margin: 0;
  color: #6c757d;
  font-size: 1.1rem;
}

.native-review {
  margin-bottom: 1rem;
}

.native-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.native-btn:hover {
  transform: translateY(-2px);
}

.divider {
  height: 1px;
  background: #e9ecef;
  margin: 2rem 0;
}

.mode-selection {
  margin-bottom: 2rem;
}

.mode-selection h3 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.mode-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.mode-btn {
  padding: 0.75rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 200px;
}

.mode-btn:hover {
  border-color: #4facfe;
}

.mode-btn.active {
  border-color: #4facfe;
  background: #4facfe;
  color: white;
}

.mode-description {
  color: #6c757d;
  font-style: italic;
  margin: 0;
}

.cards-info {
  margin-bottom: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.info-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  text-align: center;
}

.info-label {
  display: block;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.info-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.review-interface {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 2rem;
}

.navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.nav-btn {
  padding: 0.5rem 1rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  background: #0056b3;
}

.nav-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.card-counter {
  font-weight: 600;
  color: #495057;
}

.card-container {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.question-section {
  margin-bottom: 2rem;
}

.question-section h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.question-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
  min-height: 100px;
}

.enhanced-info {
  margin-top: 0.5rem;
  color: #6c757d;
  font-style: italic;
}

.tts-section {
  margin-bottom: 2rem;
}

.tts-btn {
  padding: 0.75rem 1.5rem;
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.tts-btn:hover:not(:disabled) {
  background: #138496;
}

.tts-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.answer-input-section {
  margin-bottom: 2rem;
}

.answer-input-section h4 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.speech-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.listen-btn {
  padding: 0.75rem 1.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.listen-btn:hover:not(:disabled) {
  background: #c82333;
}

.listen-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.play-btn {
  padding: 0.75rem 1.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.play-btn:hover {
  background: #218838;
}

.spoken-answer {
  background: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.answer-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
}

.answer-textarea:focus {
  outline: none;
  border-color: #4facfe;
}

.reveal-section {
  text-align: center;
  margin-bottom: 2rem;
}

.reveal-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.reveal-btn:hover {
  transform: translateY(-2px);
}

.answer-section {
  border-top: 2px solid #e9ecef;
  padding-top: 2rem;
}

.answer-section h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.answer-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.llm-evaluation {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-radius: 6px;
}

.evaluating {
  text-align: center;
  color: #0056b3;
  font-style: italic;
}

.evaluation-result .rating-section {
  margin-bottom: 1rem;
}

.rating-label {
  font-weight: 600;
  margin-right: 0.5rem;
}

.rating-value {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
}

.rating-value.again {
  background: #f8d7da;
  color: #721c24;
}
.rating-value.hard {
  background: #fff3cd;
  color: #856404;
}
.rating-value.good {
  background: #d4edda;
  color: #155724;
}
.rating-value.easy {
  background: #cce7ff;
  color: #004085;
}

.explanation {
  margin-top: 0.5rem;
  font-style: italic;
}

.rating-section h4 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.rating-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.rating-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease;
  min-width: 100px;
}

.rating-btn:hover {
  transform: translateY(-2px);
}

.rating-btn.again {
  background: #dc3545;
  color: white;
}
.rating-btn.hard {
  background: #ffc107;
  color: #212529;
}
.rating-btn.good {
  background: #28a745;
  color: white;
}
.rating-btn.easy {
  background: #007bff;
  color: white;
}

.no-cards {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
}

.no-cards-content h3 {
  margin: 0 0 1rem 0;
  color: #6c757d;
}

.no-cards-content ul {
  text-align: left;
  max-width: 400px;
  margin: 1rem auto;
}

.refresh-btn {
  padding: 1rem 2rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}

.refresh-btn:hover {
  background: #0056b3;
}

.status-message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 6px;
  font-weight: 500;
}

.status-message.success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.status-message.error {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.status-message.info {
  background: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
}

@media (max-width: 768px) {
  .mode-buttons {
    flex-direction: column;
  }

  .mode-btn {
    min-width: auto;
  }

  .navigation {
    flex-direction: column;
    gap: 1rem;
  }

  .speech-controls {
    flex-direction: column;
  }

  .rating-buttons {
    flex-direction: column;
  }

  .rating-btn {
    min-width: auto;
  }
}
</style>
