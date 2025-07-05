import { defineStore } from 'pinia'
import { ref } from 'vue'
import httpClient from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { TeamEntry } from '@/types'

export const useTeamEntryStore = defineStore('teamEntry', () => {
  // State
  const teamEntries = ref<TeamEntry[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchTeamEntries(): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      const res = await httpClient.tenant.getTeamEntries(authStore.user.tenant)
      teamEntries.value = res.data
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch team entries'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    teamEntries,
    isLoading,
    error,

    // Actions
    fetchTeamEntries
  }
})
