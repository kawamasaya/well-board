import httpClient from '@/api'
import type { LoginFormData, TenantRequestFormData, User } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const isLoggedIn = ref<boolean>(false)
  const user = ref<User | null>(null)

  // Actions
  async function login(credentials: LoginFormData): Promise<void> {
    try {
      const res = await httpClient.auth.login(credentials.email, credentials.password)
      user.value = res.data
      isLoggedIn.value = true
    } catch (error) {
      throw error
    }
  }


  async function tenantRequest(requestData: TenantRequestFormData): Promise<void> {
    try {
      await httpClient.auth.tenantRequest(requestData)
    } catch (error) {
      throw error
    }
  }

  async function logout(): Promise<void> {
    try {
      await httpClient.auth.logout()
      $reset()
    } catch (error) {
      $reset() // Reset even if logout fails
    }
  }

  async function verifyToken(): Promise<void> {
    try {
      await httpClient.auth.verify()
      isLoggedIn.value = true
    } catch (error) {
      throw error
    }
  }

  async function refreshToken(): Promise<void> {
    try {
      const res = await httpClient.auth.refresh()
      user.value = res.data
      isLoggedIn.value = true
    } catch (error) {
      throw error
    }
  }

  function $reset(): void {
    isLoggedIn.value = false
    user.value = null
  }

  return {
    // State
    isLoggedIn,
    user,

    // Actions
    login,
    tenantRequest,
    logout,
    verifyToken,
    refreshToken,
    $reset
  }
}, {
  persist: true
})
