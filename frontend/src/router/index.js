import { createRouter, createWebHistory } from 'vue-router'
import AnkiToolView from '../views/AnkiToolView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'anki',
      component: AnkiToolView,
    },
    // Redirect any other routes to the main app
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

export default router
