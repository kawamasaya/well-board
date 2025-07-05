/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App
 */

import { createPinia } from 'pinia'
import { createPersistedState } from "pinia-plugin-persistedstate"
import type { App as VueApp } from 'vue'

// Composables
import { createApp } from 'vue'

// Plugins
import { registerPlugins } from '@/plugins'
// Components
import App from './App.vue'

// Styles
import 'unfonts.css'

// Create Pinia store with persistence
const pinia = createPinia()
pinia.use(createPersistedState())

// Create Vue app instance
const app: VueApp = createApp(App)

// Register plugins (Vuetify, Router, etc.)
registerPlugins(app)

// Add Pinia to the app
app.use(pinia)

// Mount the app
app.mount('#app')
