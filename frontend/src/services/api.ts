import axios from 'axios'
import type { Profile, LearningPath, Progress, AnalysisResult, DashboardData } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Profiles
export const getProfiles = async (): Promise<Profile[]> => {
  const { data } = await api.get('/profiles/')
  return data
}

export const getProfile = async (profileId: string): Promise<Profile> => {
  const { data } = await api.get(`/profiles/${profileId}`)
  return data
}

export const uploadProfile = async (profile: Partial<Profile>): Promise<{ id: string; user_id: string }> => {
  const { data } = await api.post('/profiles/upload', profile)
  return data
}

// Analysis
export const runFullAnalysis = async (params: {
  profile_id?: string
  custom_profile?: Record<string, unknown>
  target_jd_text: string
  target_role?: string
  skip_assessment?: boolean
}): Promise<AnalysisResult> => {
  const { data } = await api.post('/analysis/full', params)
  return data
}

export const parseJD = async (params: {
  jd_text: string
  target_role?: string
}): Promise<{
  extracted_skills: Array<{ skill_id: string; skill_name: string; required_level: number }>
  role_analysis: Record<string, unknown>
}> => {
  const { data } = await api.post('/analysis/parse-jd', params)
  return data
}

export const getSkillGap = async (userId: string) => {
  const { data } = await api.get(`/analysis/gap/${userId}`)
  return data
}

// Learning Paths
export const getLearningPath = async (pathId: string): Promise<LearningPath> => {
  const { data } = await api.get(`/paths/${pathId}`)
  return data
}

export const getUserPaths = async (userId: string): Promise<LearningPath[]> => {
  const { data } = await api.get(`/paths/user/${userId}`)
  return data
}

export const generatePath = async (params: {
  goal_id: string
  gap_id: string
  top_skills?: number
}) => {
  const { data } = await api.post('/paths/generate', params)
  return data
}

// Progress
export const getProgress = async (pathId: string): Promise<Progress> => {
  const { data } = await api.get(`/progress/${pathId}`)
  return data
}

export const createProgress = async (pathId: string) => {
  const { data } = await api.post('/progress/', { path_id: pathId })
  return data
}

export const updateProgress = async (pathId: string, params: {
  chapter: number
  status: 'not_started' | 'in_progress' | 'completed'
  quiz_score?: number
}) => {
  const { data } = await api.put(`/progress/${pathId}`, params)
  return data
}

export const getDashboard = async (userId: string): Promise<DashboardData> => {
  const { data } = await api.get(`/progress/user/${userId}/dashboard`)
  return data
}

// Ontology
export const getOntology = async () => {
  const { data } = await api.get('/ontology/')
  return data
}

export const searchSkills = async (query: string, domain?: string) => {
  const params = new URLSearchParams({ q: query })
  if (domain) params.append('domain', domain)
  const { data } = await api.get(`/ontology/search?${params}`)
  return data
}

export const getDomains = async () => {
  const { data } = await api.get('/ontology/domains')
  return data
}

export default api
