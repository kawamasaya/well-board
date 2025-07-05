import httpClient from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { EntryDetail, EntryFormData } from '@/types'
import dayjs from 'dayjs'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEntryStore = defineStore('entry', () => {
  // State
  const entries = ref<EntryDetail[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchEntries(): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      const res = await httpClient.tenant.getEntries(authStore.user.tenant)

      // Format dates
      const formattedEntries = res.data.map(entry => ({
        ...entry,
        reported_at: dayjs(entry.reported_at).format("YYYY/MM/DD")
      }))

      entries.value = formattedEntries
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch entries'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function addEntries(entry: EntryFormData): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    try {
      // 日付のみを送信するため、時刻情報を削除
      const formattedEntry = {
        ...entry,
        reported_at: dayjs(entry.reported_at).format('YYYY-MM-DD')
      }
      await httpClient.tenant.addEntry(authStore.user.tenant, formattedEntry as any)
    } catch (err: any) {
      error.value = err.message || 'Failed to add entry'
      throw err
    }
  }

  return {
    // State
    entries,
    isLoading,
    error,

    // Actions
    fetchEntries,
    addEntries
  }
})
