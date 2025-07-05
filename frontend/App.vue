<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import InfoSnackbar from '@/components/InfoSnackbar.vue'

const router = useRouter()
const authStore = useAuthStore()
const showDrawer = ref<boolean>(true)
const { user, isLoggedIn } = storeToRefs(authStore)

async function logout(): Promise<void> {
  try {
    await authStore.logout()
    await router.push('/')
  } catch (error) {
    // エラーハンドリングは必要に応じて追加
  }
}
</script>

<template>
  <v-app>
    

    <v-app-bar v-if="isLoggedIn">
      
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer"></v-app-bar-nav-icon> <!--  v-if="isLoggedIn" @click="drawer = !drawer"> -->
      
      <v-app-bar-title>
        WellBoard
      </v-app-bar-title>

      <span class="pr-4 subheading">
        <v-icon>
            mdi-account
        </v-icon>
        {{ user?.name }} ({{ user?.email }})
      </span>
      <v-btn icon @click="logout">
        <v-icon>mdi-exit-to-app</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer v-if="isLoggedIn" v-model="showDrawer">
      <v-list>
        <v-list-item prepend-icon="mdi-view-dashboard" title="Home" value="home" to="/home"></v-list-item>
        <v-list-item prepend-icon="mdi-account-group" title="Teams" value="teams" to="/teams"></v-list-item>
        <v-list-item prepend-icon="mdi-account-multiple" title="Users" value="users" to="/users"></v-list-item>
        <v-list-item prepend-icon="mdi-note-text" title="Entries" value="entries" to="/entries"></v-list-item>
        <v-list-item prepend-icon="mdi-chart-line" title="TeamEntries" value="team-entries" to="/team-entries"></v-list-item>
        
      </v-list>

    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>

    <InfoSnackbar />

  </v-app>
</template>

<style scoped>
</style>