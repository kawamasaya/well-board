import type { AxiosInstance } from 'axios'
import type { ApiResponse, Team, TeamDetail, Entry, EntryDetail, TeamEntry, EntryFormData, TeamFormData, User, UserDetail, UserFormData } from '@/types'

export default function (httpClient: AxiosInstance) {
  return {
    async getTeams(tenant_id: number): Promise<ApiResponse<TeamDetail[]>> {
      return httpClient.get(`/api/tenants/${tenant_id}/teams/`)
    },

    async addTeam(tenant_id: number, data: TeamFormData): Promise<ApiResponse<Team>> {
      return await httpClient.post(`/api/tenants/${tenant_id}/teams/`, data)
    },

    async updateTeam(tenant_id: number, team_id: number, data: TeamFormData): Promise<ApiResponse<Team>> {
      return await httpClient.put(`/api/tenants/${tenant_id}/teams/${team_id}/`, data)
    },

    async deleteTeam(tenant_id: number, team_id: number): Promise<ApiResponse<void>> {
      return await httpClient.delete(`/api/tenants/${tenant_id}/teams/${team_id}/`)
    },

    async getEntries(tenant_id: number): Promise<ApiResponse<EntryDetail[]>> {
      return await httpClient.get(`/api/tenants/${tenant_id}/entries/`)
    },

    async addEntry(tenant_id: number, data: EntryFormData): Promise<ApiResponse<Entry>> {
      return await httpClient.post(`/api/tenants/${tenant_id}/entries/`, data)
    },

    async getTeamEntries(tenant_id: number): Promise<ApiResponse<TeamEntry[]>> {
      return await httpClient.get(`/api/tenants/${tenant_id}/team-entries/`)
    },

    async getUsers(tenant_id: number): Promise<ApiResponse<UserDetail[]>> {
      return httpClient.get(`/api/tenants/${tenant_id}/users/`)
    },

    async addUser(tenant_id: number, data: UserFormData): Promise<ApiResponse<User>> {
      return await httpClient.post(`/api/tenants/${tenant_id}/users/`, data)
    },

    async updateUser(tenant_id: number, user_id: number, data: UserFormData): Promise<ApiResponse<User>> {
      return await httpClient.put(`/api/tenants/${tenant_id}/users/${user_id}/`, data)
    },

    async deleteUser(tenant_id: number, user_id: number): Promise<ApiResponse<void>> {
      return await httpClient.delete(`/api/tenants/${tenant_id}/users/${user_id}/`)
    },
  }
}
