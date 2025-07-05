import httpClient from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { TeamDetail, TeamFormData } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTeamStore = defineStore('team', () => {
  // State
  const teams = ref<TeamDetail[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchTeams(): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      const res = await httpClient.tenant.getTeams(authStore.user.tenant)
      teams.value = res.data
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teams'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function addTeam(teamData: TeamFormData): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      await httpClient.tenant.addTeam(authStore.user.tenant, teamData)
    } catch (err: any) {
      error.value = err.message || 'Failed to add team'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateTeam(teamId: number, teamData: TeamFormData): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      await httpClient.tenant.updateTeam(authStore.user.tenant, teamId, teamData)
    } catch (err: any) {
      error.value = err.message || 'Failed to update team'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteTeam(teamId: number): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      await httpClient.tenant.deleteTeam(authStore.user.tenant, teamId)
    } catch (err: any) {
      error.value = err.message || 'Failed to delete team'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    teams,
    isLoading,
    error,

    // Actions
    fetchTeams,
    addTeam,
    updateTeam,
    deleteTeam
  }
})
