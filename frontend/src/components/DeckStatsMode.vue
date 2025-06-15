<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <div class="flex justify-center mb-4">
        <div class="avatar">
          <div class="w-16 rounded-full bg-gradient-to-r from-accent to-info flex items-center justify-center">
            <span class="text-3xl">📊</span>
          </div>
        </div>
      </div>
      <h2 class="text-4xl font-bold bg-gradient-to-r from-accent to-info bg-clip-text text-transparent mb-2">
        Deck Statistics
      </h2>
      <div v-if="selectedDeck" class="space-y-2">
        <p class="text-base-content/70 text-lg">Comprehensive analytics for your learning progress</p>
        <div class="badge badge-accent badge-lg">
          <span class="text-lg mr-2">📚</span>
          {{ selectedDeck }}
        </div>
      </div>
      <div v-else class="alert alert-warning max-w-md mx-auto">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <span>Please select a deck to view statistics</span>
      </div>
    </div>

    <div v-if="selectedDeck && deckStats" class="space-y-8">
      <!-- Overview Cards -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <span class="text-xl">📈</span>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-primary">Overview</h3>
        </div>
        
        <div class="stats stats-vertical lg:stats-horizontal shadow-xl bg-base-100 border border-base-300">
          <div class="stat">
            <div class="stat-figure text-primary">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div class="stat-title">Total Cards</div>
            <div class="stat-value text-primary">{{ deckStats.total_in_deck || 0 }}</div>
            <div class="stat-desc">Complete collection</div>
          </div>

          <div class="stat">
            <div class="stat-figure text-secondary">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <div class="stat-title">New Today</div>
            <div class="stat-value text-secondary">{{ deckStats.new_count || 0 }}</div>
            <div class="stat-desc">Fresh content</div>
          </div>

          <div class="stat">
            <div class="stat-figure text-accent">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="stat-title">Learning</div>
            <div class="stat-value text-accent">{{ deckStats.learn_count || 0 }}</div>
            <div class="stat-desc">In progress</div>
          </div>

          <div class="stat">
            <div class="stat-figure text-info">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <div class="stat-title">Review</div>
            <div class="stat-value text-info">{{ deckStats.review_count || 0 }}</div>
            <div class="stat-desc">Due for review</div>
          </div>
        </div>
      </div>

      <!-- Today's Activity -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-secondary/20 flex items-center justify-center">
              <span class="text-xl">🗓️</span>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-secondary">Today's Activity</h3>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="card bg-gradient-to-br from-success/10 to-success/5 border border-success/20 shadow-xl">
            <div class="card-body">
              <div class="flex items-center gap-4">
                <div class="avatar">
                  <div class="w-16 rounded-full bg-success/20 flex items-center justify-center">
                    <span class="text-3xl">✅</span>
                  </div>
                </div>
                <div>
                  <h4 class="text-2xl font-bold text-success">{{ reviewedToday }}</h4>
                  <p class="text-success/70">Cards Reviewed Today</p>
                </div>
              </div>
            </div>
          </div>

          <div class="card bg-gradient-to-br from-warning/10 to-warning/5 border border-warning/20 shadow-xl">
            <div class="card-body">
              <div class="flex items-center gap-4">
                <div class="avatar">
                  <div class="w-16 rounded-full bg-warning/20 flex items-center justify-center">
                    <span class="text-3xl">⏰</span>
                  </div>
                </div>
                <div>
                  <h4 class="text-2xl font-bold text-warning">{{ getStudyTime() }}</h4>
                  <p class="text-warning/70">Estimated Study Time</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Distribution Chart -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-info/20 flex items-center justify-center">
              <span class="text-xl">📊</span>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-info">Card Distribution</h3>
        </div>
        
        <div class="card bg-base-100 shadow-xl border border-base-300">
          <div class="card-body">
            <div class="space-y-6">
              <!-- Bar Chart -->
              <div class="flex items-end justify-center gap-8 h-64 p-6 bg-gradient-to-t from-base-200/50 to-transparent rounded-lg">
                <div class="flex flex-col items-center gap-3">
                  <div class="bg-secondary rounded-lg flex items-end justify-center text-secondary-content font-bold text-sm px-2 py-1 min-h-[2rem]"
                       :style="{ height: getBarHeight('new') }">
                    {{ deckStats.new_count || 0 }}
                  </div>
                  <div class="text-sm font-semibold text-secondary">New</div>
                </div>

                <div class="flex flex-col items-center gap-3">
                  <div class="bg-accent rounded-lg flex items-end justify-center text-accent-content font-bold text-sm px-2 py-1 min-h-[2rem]"
                       :style="{ height: getBarHeight('learning') }">
                    {{ deckStats.learn_count || 0 }}
                  </div>
                  <div class="text-sm font-semibold text-accent">Learning</div>
                </div>

                <div class="flex flex-col items-center gap-3">
                  <div class="bg-info rounded-lg flex items-end justify-center text-info-content font-bold text-sm px-2 py-1 min-h-[2rem]"
                       :style="{ height: getBarHeight('review') }">
                    {{ deckStats.review_count || 0 }}
                  </div>
                  <div class="text-sm font-semibold text-info">Review</div>
                </div>
              </div>

              <!-- Legend -->
              <div class="flex flex-wrap justify-center gap-6">
                <div class="flex items-center gap-2">
                  <div class="w-4 h-4 bg-secondary rounded"></div>
                  <span class="text-sm font-medium">New Cards</span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="w-4 h-4 bg-accent rounded"></div>
                  <span class="text-sm font-medium">Learning Cards</span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="w-4 h-4 bg-info rounded"></div>
                  <span class="text-sm font-medium">Review Cards</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Section -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-success/20 flex items-center justify-center">
              <span class="text-xl">📈</span>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-success">Progress Indicators</h3>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="card bg-base-100 shadow-xl border border-base-300">
            <div class="card-body">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-bold text-lg">Daily Goal Progress</h4>
                <div class="badge badge-primary badge-lg">{{ getDailyProgress() }}%</div>
              </div>
              <div class="space-y-3">
                <progress class="progress progress-primary w-full" :value="getDailyProgress()" max="100"></progress>
                <p class="text-sm text-base-content/60">
                  You've completed {{ getDailyProgress() }}% of your daily study goal
                </p>
              </div>
            </div>
          </div>

          <div class="card bg-base-100 shadow-xl border border-base-300">
            <div class="card-body">
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-bold text-lg">Deck Completion</h4>
                <div class="badge badge-secondary badge-lg">{{ getDeckCompletion() }}%</div>
              </div>
              <div class="space-y-3">
                <progress class="progress progress-secondary w-full" :value="getDeckCompletion()" max="100"></progress>
                <p class="text-sm text-base-content/60">
                  Overall mastery level of this deck
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-warning/20 flex items-center justify-center">
              <span class="text-xl">⚡</span>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-warning">Quick Actions</h3>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button @click="refreshStats" :disabled="loading" 
                  class="btn btn-outline btn-warning hover:btn-warning shadow-lg hover:shadow-xl hover:scale-105 transition-all">
            <span v-if="loading" class="loading loading-spinner loading-sm"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ loading ? 'Refreshing...' : 'Refresh Stats' }}
          </button>

          <button @click="startReview" class="btn btn-primary shadow-lg hover:shadow-xl hover:scale-105 transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Start Review Session
          </button>

          <button @click="exportStats" class="btn btn-outline btn-accent hover:btn-accent shadow-lg hover:shadow-xl hover:scale-105 transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Stats
          </button>
        </div>
      </div>

      <!-- Detailed Breakdown -->
      <div class="space-y-6">
        <div class="flex items-center gap-3">
          <div class="avatar">
            <div class="w-10 rounded-lg bg-accent/20 flex items-center justify-center">
              <span class="text-xl">🔍</span>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-accent">Detailed Breakdown</h3>
        </div>
        
        <div class="card bg-base-100 shadow-xl border border-base-300">
          <div class="card-body">
            <div class="overflow-x-auto">
              <table class="table table-zebra">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Count</th>
                    <th>Percentage</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      <div class="flex items-center gap-3">
                        <div class="w-4 h-4 bg-secondary rounded"></div>
                        <span class="font-medium">New Cards</span>
                      </div>
                    </td>
                    <td>
                      <div class="badge badge-secondary badge-lg">{{ deckStats.new_count || 0 }}</div>
                    </td>
                    <td>{{ getPercentage('new') }}%</td>
                    <td>
                      <div class="badge badge-outline badge-secondary">Fresh</div>
                    </td>
                  </tr>
                  
                  <tr>
                    <td>
                      <div class="flex items-center gap-3">
                        <div class="w-4 h-4 bg-accent rounded"></div>
                        <span class="font-medium">Learning Cards</span>
                      </div>
                    </td>
                    <td>
                      <div class="badge badge-accent badge-lg">{{ deckStats.learn_count || 0 }}</div>
                    </td>
                    <td>{{ getPercentage('learning') }}%</td>
                    <td>
                      <div class="badge badge-outline badge-accent">In Progress</div>
                    </td>
                  </tr>
                  
                  <tr>
                    <td>
                      <div class="flex items-center gap-3">
                        <div class="w-4 h-4 bg-info rounded"></div>
                        <span class="font-medium">Review Cards</span>
                      </div>
                    </td>
                    <td>
                      <div class="badge badge-info badge-lg">{{ deckStats.review_count || 0 }}</div>
                    </td>
                    <td>{{ getPercentage('review') }}%</td>
                    <td>
                      <div class="badge badge-outline badge-info">Due</div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="selectedDeck && !deckStats" class="flex justify-center items-center py-20">
      <div class="card bg-base-100 shadow-xl border border-base-300 text-center">
        <div class="card-body">
          <div class="flex justify-center mb-4">
            <div class="avatar">
              <div class="w-16 rounded-full bg-warning/20 flex items-center justify-center">
                <span class="text-4xl">📊</span>
              </div>
            </div>
          </div>
          <h3 class="text-2xl font-bold text-warning mb-2">No Statistics Available</h3>
          <p class="text-base-content/60 mb-6">Unable to load statistics for this deck.</p>
          <button @click="refreshStats" class="btn btn-warning shadow-lg hover:shadow-xl hover:scale-105 transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
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
import { ref, computed, defineProps } from 'vue'

const props = defineProps({
  selectedDeck: String,
  deckStats: Object,
})

// Reactive state
const loading = ref(false)
const reviewedToday = ref(42) // This would come from the API
const statusMessage = ref('')
const statusType = ref('info')

// Computed properties
const totalCards = computed(() => props.deckStats?.total_in_deck || 0)
const newCards = computed(() => props.deckStats?.new_count || 0)
const learningCards = computed(() => props.deckStats?.learn_count || 0)
const reviewCards = computed(() => props.deckStats?.review_count || 0)

// Utility functions
const showStatus = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const getBarHeight = (type) => {
  const maxValue = Math.max(newCards.value, learningCards.value, reviewCards.value)
  if (maxValue === 0) return '0%'

  let value = 0
  switch (type) {
    case 'new':
      value = newCards.value
      break
    case 'learning':
      value = learningCards.value
      break
    case 'review':
      value = reviewCards.value
      break
  }

  const percentage = (value / maxValue) * 100
  return Math.max(percentage, 5) + '%' // Minimum 5% for visibility
}

const getPercentage = (type) => {
  if (totalCards.value === 0) return 0

  let value = 0
  switch (type) {
    case 'new':
      value = newCards.value
      break
    case 'learning':
      value = learningCards.value
      break
    case 'review':
      value = reviewCards.value
      break
  }

  return Math.round((value / totalCards.value) * 100)
}

const getDailyProgress = () => {
  const dailyGoal = 50 // This could be configurable
  return Math.min(Math.round((reviewedToday.value / dailyGoal) * 100), 100)
}

const getDeckCompletion = () => {
  if (totalCards.value === 0) return 0
  const completedCards = totalCards.value - newCards.value - learningCards.value
  return Math.round((completedCards / totalCards.value) * 100)
}

const getStudyTime = () => {
  const totalCardsToReview = newCards.value + learningCards.value + reviewCards.value
  const averageTimePerCard = 30 // seconds
  const totalSeconds = totalCardsToReview * averageTimePerCard
  const minutes = Math.round(totalSeconds / 60)

  if (minutes < 60) {
    return `${minutes} min`
  } else {
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}h ${remainingMinutes}m`
  }
}

// Actions
const refreshStats = async () => {
  loading.value = true
  try {
    // Emit event to parent to refresh stats
    // This would typically call the AnkiConnect API
    await new Promise((resolve) => setTimeout(resolve, 1000)) // Simulate API call
    showStatus('Statistics refreshed successfully!', 'success')
  } catch (err) {
    showStatus('Failed to refresh statistics', 'error')
  } finally {
    loading.value = false
  }
}

const startReview = () => {
  if (!props.selectedDeck) {
    showStatus('Please select a deck first', 'error')
    return
  }

  // This would navigate to review mode or emit event
  showStatus('Starting review session...', 'info')
}

const exportStats = () => {
  try {
    const statsData = {
      deck: props.selectedDeck,
      timestamp: new Date().toISOString(),
      stats: props.deckStats,
      reviewedToday: reviewedToday.value,
    }

    const dataStr = JSON.stringify(statsData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)

    const link = document.createElement('a')
    link.href = url
    link.download = `anki-stats-${props.selectedDeck}-${new Date().toISOString().split('T')[0]}.json`
    link.click()

    URL.revokeObjectURL(url)
    showStatus('Statistics exported successfully!', 'success')
  } catch (err) {
    showStatus('Failed to export statistics', 'error')
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

<style scoped>
.deck-stats-mode {
  max-width: 1200px;
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

.no-deck {
  color: #dc3545;
  font-weight: 500;
}

.stats-container {
  display: grid;
  gap: 2rem;
}

.overview-section h3,
.activity-section h3,
.chart-section h3,
.progress-section h3,
.actions-section h3,
.breakdown-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.total {
  border-left: 4px solid #6c757d;
}
.stat-card.new {
  border-left: 4px solid #28a745;
}
.stat-card.learning {
  border-left: 4px solid #ffc107;
}
.stat-card.review {
  border-left: 4px solid #007bff;
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.7;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.activity-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 2rem;
}

.activity-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.activity-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.activity-icon {
  font-size: 1.5rem;
  opacity: 0.7;
}

.activity-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.activity-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-wrapper {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 2rem;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: end;
  height: 200px;
  gap: 1rem;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.bar {
  width: 60px;
  min-height: 20px;
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: start;
  justify-content: center;
  padding-top: 0.5rem;
  transition: all 0.3s ease;
  position: relative;
}

.bar:hover {
  transform: scaleY(1.05);
}

.new-bar {
  background: linear-gradient(to top, #28a745, #34ce57);
}
.learning-bar {
  background: linear-gradient(to top, #ffc107, #ffcd39);
}
.review-bar {
  background: linear-gradient(to top, #007bff, #339af0);
}

.bar-value {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.bar-label {
  font-weight: 500;
  color: #495057;
  text-align: center;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #495057;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.new-color {
  background: #28a745;
}
.learning-color {
  background: #ffc107;
}
.review-color {
  background: #007bff;
}

.progress-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.progress-items {
  display: grid;
  gap: 1.5rem;
}

.progress-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-label {
  font-weight: 500;
  color: #495057;
}

.progress-value {
  font-weight: 600;
  color: #2c3e50;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-fill.completion {
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
}

.actions-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 160px;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.action-btn:disabled {
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  opacity: 0.6;
}

.action-btn.refresh {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  color: white;
}

.action-btn.review {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
}

.action-btn.export {
  background: linear-gradient(135deg, #28a745 0%, #218838 100%);
  color: white;
}

.btn-icon {
  font-size: 1.1rem;
}

.breakdown-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.breakdown-table {
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  background: #e9ecef;
  font-weight: 600;
  color: #495057;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  border-top: 1px solid #dee2e6;
}

.table-row.total-row {
  background: #dee2e6;
}

.table-cell {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.new-indicator {
  background: #28a745;
}
.learning-indicator {
  background: #ffc107;
}
.review-indicator {
  background: #007bff;
}

.empty-state,
.no-deck-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3,
.no-deck-state h3 {
  margin: 0 0 1rem 0;
  color: #495057;
}

.refresh-btn {
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
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
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .activity-stats {
    grid-template-columns: 1fr;
  }

  .chart-legend {
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-btn {
    min-width: auto;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .table-cell {
    padding: 0.75rem;
    justify-content: space-between;
  }
}
</style>
