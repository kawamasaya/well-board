import type { ApiResponse, LoginFormData, TenantRequestFormData, User } from '@/types'
import type { AxiosInstance } from 'axios'

export default function (httpClient: AxiosInstance) {
  return {
    async login(email: string, password: string): Promise<ApiResponse<User>> {
      const data: LoginFormData = { email, password }
      return await httpClient.post('/api/auth/', data)
    },

    async tenantRequest(requestData: TenantRequestFormData): Promise<ApiResponse<any>> {
      return await httpClient.post('/api/auth/tenant-request/', requestData)
    },

    async verify(): Promise<ApiResponse<void>> {
      return await httpClient.post('/api/auth/verify/')
    },

    async refresh(): Promise<ApiResponse<User>> {
      return await httpClient.post('/api/auth/refresh/')
    },

    async logout(): Promise<ApiResponse<void>> {
      return await httpClient.post('/api/auth/logout/')
    },
  }
}
