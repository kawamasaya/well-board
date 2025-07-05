// Data Model
export interface User {
  id: number
  name: string
  email: string
  tenant: number
  teams?: number[]
  role?: number
}

export interface UserDetail extends Omit<User, 'teams'> {
  teams?: Team[]
}

export interface Team {
  id: number
  name: string
  tenant: number
  questions?: QuestionSet
  managers?: number[]
}

export interface TeamDetail extends Omit<Team, 'managers'> {
  managers?: User[]
}

export interface Entry {
  id: number
  user: number
  team: number
  tenant: number
  answers: AnswerSet
  stress_score?: number
  score?: number
  created_at: string
  reported_at: string
  comment?: string
  q_and_a?: string
}

export interface EntryDetail extends Omit<Entry, 'user' | 'team'> {
  user: {
    id: number
    name: string
  }
  team: {
    id: number
    name: string
  }
}

export interface TeamEntry {
  id: number
  name: string
  users: UserWithEntries[]
}

export interface UserWithEntries {
  id: number
  name: string
  entries: {
    labels: string[]
    stress_values: number[]
    motivation_values: number[]
  }
}

// Question and Answer Types (JSON fields from backend)
export interface QuestionSet {
  [key: string]: string | Question
}

export interface Question {
  text: string
  type?: 'text' | 'number' | 'scale' | 'boolean'
  required?: boolean
}

export interface AnswerSet {
  [key: string]: string | number | boolean
}

// Form Data Types
export interface LoginFormData {
  email: string
  password: string
}

export interface TenantRequestFormData {
  tenantName: string
  email: string
  name: string
  domain: string
}

export interface UserFormData {
  name: string
  email: string
  role: number
  teams?: number[]
}

export interface TeamFormData {
  name: string
  questions?: QuestionSet
}

export interface EntryFormData {
  team: number
  reported_at: Date
  questions: QuestionSet
  answers: AnswerSet
}


// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface ApiError {
  message: string
  status: number
  errors?: Record<string, string[]>
}

// HTTP Client Types
export interface HttpClientMethods {
  auth: {
    login: (email: string, password: string) => Promise<ApiResponse<User>>
    tenantRequest: (requestData: TenantRequestFormData) => Promise<ApiResponse<any>>
    logout: () => Promise<ApiResponse<void>>
    verify: () => Promise<ApiResponse<void>>
    refresh: () => Promise<ApiResponse<User>>
  }
  tenant: {
    getTeams: (tenantId: number) => Promise<ApiResponse<TeamDetail[]>>
    addTeam: (tenantId: number, team: TeamFormData) => Promise<ApiResponse<Team>>
    updateTeam: (tenantId: number, teamId: number, team: TeamFormData) => Promise<ApiResponse<Team>>
    deleteTeam: (tenantId: number, teamId: number) => Promise<ApiResponse<void>>
    getUsers: (tenantId: number) => Promise<ApiResponse<UserDetail[]>>
    addUser: (tenantId: number, user: any) => Promise<ApiResponse<User>>
    updateUser: (tenantId: number, userId: number, user: any) => Promise<ApiResponse<User>>
    deleteUser: (tenantId: number, userId: number) => Promise<ApiResponse<void>>
    getEntries: (tenantId: number) => Promise<ApiResponse<EntryDetail[]>>
    addEntry: (tenantId: number, entry: EntryFormData) => Promise<ApiResponse<Entry>>
    getTeamEntries: (tenantId: number) => Promise<ApiResponse<TeamEntry[]>>
  }
}

// Utility Types
export type NotificationColor = 'success' | 'error' | 'warning' | 'info'
