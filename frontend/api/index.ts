import type { HttpClientMethods } from '@/types'
import axios, { AxiosInstance } from 'axios'
import auth from './auth'
import tenant from './tenant'

// Create typed HTTP client that extends AxiosInstance with custom methods
interface TypedHttpClient extends AxiosInstance, HttpClientMethods { }

const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_ENDPOINT,
  withCredentials: true,
  adapter: 'fetch'
}) as TypedHttpClient

// Add authentication methods
httpClient.auth = auth(httpClient)

// Add tenant methods
httpClient.tenant = tenant(httpClient)

// TODO: Add response interceptor for token refresh
// httpClient.interceptors.response.use(
//   response => response,
//   async (error) => {
//     const originalRequest = error.config
//     if (error.response?.status === 401 && !originalRequest._retry) {
//       originalRequest._retry = true
//       try {
//         // Implement token refresh logic
//         await httpClient.auth.refresh()
//         return httpClient(originalRequest)
//       } catch (refreshError) {
//         // Redirect to login or handle refresh failure
//         return Promise.reject(refreshError)
//       }
//     }
//     return Promise.reject(error)
//   }
// )

export default httpClient