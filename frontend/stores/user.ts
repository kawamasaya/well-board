import httpClient from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { UserDetail, UserFormData } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<UserDetail[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchUsers(): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      const res = await httpClient.tenant.getUsers(authStore.user.tenant)
      users.value = res.data
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch users'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function addUser(userData: UserFormData): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      await httpClient.tenant.addUser(authStore.user.tenant, userData)
    } catch (err: any) {
      error.value = err.message || 'Failed to add user'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateUser(userId: number, userData: UserFormData): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      await httpClient.tenant.updateUser(authStore.user.tenant, userId, userData)
    } catch (err: any) {
      error.value = err.message || 'Failed to update user'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteUser(userId: number): Promise<void> {
    const authStore = useAuthStore()

    if (!authStore.user?.tenant) {
      throw new Error('No tenant found for user')
    }

    isLoading.value = true
    error.value = null

    try {
      await httpClient.tenant.deleteUser(authStore.user.tenant, userId)
    } catch (err: any) {
      error.value = err.message || 'Failed to delete user'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    users,
    isLoading,
    error,

    // Actions
    fetchUsers,
    addUser,
    updateUser,
    deleteUser
  }
})