import axios from 'axios'
import type {
  Profile, LearningPath, Progress, AnalysisResult, DashboardData,
  LearningDashboard, LearningModule, Lesson, SkillMastery, ActivatePathResponse,
  SkillGenomeResponse, SkillGenomeEntry, ReactionType, LessonReactionState,
  ConfusionRecovery, CuriosityFeedResponse, PersonalizationResult,
  ImplementationGradeResult,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Profiles - DB-backed CRUD
export interface ProfileListItem {
  id: string
  name: string
  current_role: string
  target_role: string | null
  industry: string
  experience_years: number | null
  ai_exposure_level: string | null
  learning_intent: string | null
  created_at: string | null
  has_analysis: boolean
  has_learning_path: boolean
  learning_path_id: string | null
  goal_id: string | null
  user_id: string | null
  overall_progress: number
  lessons_completed: number
  total_lessons: number
  tools_used: string[]
  technical_background: string
  current_profile: Record<string, unknown> | null
}

export const getProfiles = async (): Promise<ProfileListItem[]> => {
  const { data } = await api.get('/profiles/')
  return data
}

export const getProfile = async (profileId: string): Promise<Profile> => {
  const { data } = await api.get(`/profiles/${profileId}`)
  return data
}

export const createProfile = async (profile: Record<string, unknown>): Promise<{ id: string; user_id: string; name: string }> => {
  const { data } = await api.post('/profiles/', profile)
  return data
}

export const updateProfile = async (profileId: string, updates: Record<string, unknown>): Promise<{ id: string }> => {
  const { data } = await api.put(`/profiles/${profileId}`, updates)
  return data
}

export const deleteProfile = async (profileId: string): Promise<void> => {
  await api.delete(`/profiles/${profileId}`)
}

export const uploadProfile = async (profile: Partial<Profile>): Promise<{ id: string; user_id: string }> => {
  const { data } = await api.post('/profiles/', profile)
  return data
}

// Resume parsing
export const parseResume = async (file: File): Promise<{
  name?: string
  current_role?: string
  target_role?: string
  industry?: string
  experience_years?: number
  ai_exposure_level?: string
  technical_skills?: string[]
  soft_skills?: string[]
  ai_experience?: string
  summary?: string
  archetype?: string
  current_jd?: string
}> => {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/profiles/parse-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

// JD profile parsing
export const parseJDProfile = async (params: {
  jd_text: string
  target_role?: string
}): Promise<{
  target_role?: string
  technical_skills: string[]
  soft_skills: string[]
  ai_requirements?: string
  summary?: string
  seniority_level?: string
  key_tools: string[]
}> => {
  const { data } = await api.post('/profiles/parse-jd-profile', params)
  return data
}

// Analysis
export const runFullAnalysis = async (params: {
  profile_id?: string
  custom_profile?: Record<string, unknown>
  target_jd_text: string
  target_role?: string
  skip_assessment?: boolean
  self_assessed_skills?: Record<string, number>
}): Promise<AnalysisResult> => {
  const { data } = await api.post('/analysis/full', params)
  return data
}

// JD-first flow: parse JD and get skills with proficiency descriptions.
// When learner_profile is provided, runs 3-step chain (JD -> learner context -> rubric)
// that returns skills pre-ranked for this specific learner.
export const parseJDSkills = async (params: {
  jd_text: string
  target_role?: string
  learner_profile?: Record<string, unknown>
}): Promise<{
  target_role: string
  top_10_skills: Array<{
    rank: number
    skill_id: string
    skill_name: string
    domain: string
    domain_label: string
    required_level: number
    importance: string
    rationale: string
    skill_description: string
    proficiency_descriptions: Array<{ level: number; label: string; description: string }>
    scores?: { importance: number; breadth: number; momentum: number; connectivity: number; career_signal: number }
    total_score?: number
  }>
  role_analysis: Record<string, unknown>
  reranked?: boolean
}> => {
  const { data } = await api.post('/analysis/parse-jd-skills', params)
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

export const getVisualization = async (analysisResult: Record<string, unknown>): Promise<string> => {
  const { data } = await api.post('/analysis/visualization', {
    analysis_result: analysisResult,
  }, { responseType: 'text' })
  return data
}

export const getSkillGap = async (userId: string) => {
  const { data } = await api.get(`/analysis/gap/${userId}`)
  return data
}

export const getAnalysisResults = async (profileId: string) => {
  const { data } = await api.get(`/analysis/results/${profileId}`)
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

// ── Learning Execution ───────────────────────────────────────────────

export const activateLearningPath = async (pathId: string): Promise<ActivatePathResponse> => {
  const { data } = await api.post(`/learning/${pathId}/activate`)
  return data
}

export const getLearningDashboard = async (pathId: string): Promise<LearningDashboard> => {
  const { data } = await api.get(`/learning/${pathId}/dashboard`)
  return data
}

export const getLearningModules = async (pathId: string): Promise<LearningModule[]> => {
  const { data } = await api.get(`/learning/${pathId}/modules`)
  return data
}

export const startLesson = async (pathId: string, lessonId: string, regenerate = false): Promise<Lesson> => {
  const params = regenerate ? '?regenerate=true' : ''
  const { data } = await api.post(`/learning/${pathId}/lessons/${lessonId}/start${params}`)
  return data
}

export const completeLesson = async (pathId: string, lessonId: string, params: {
  quiz_score?: number
  exercise_completed?: boolean
}) => {
  const { data } = await api.put(`/learning/${pathId}/lessons/${lessonId}/complete`, params)
  return data
}

export const getSkillMasteries = async (pathId: string): Promise<SkillMastery[]> => {
  const { data } = await api.get(`/learning/${pathId}/skills`)
  return data
}

// ── Prompt Lab ──────────────────────────────────────────────────────

export const executePrompt = async (
  pathId: string,
  params: { lesson_id: string; prompt: string; iteration: number }
): Promise<{
  response: string
  iteration: number
  tokens_used: number
  execution_time_ms: number
}> => {
  const { data } = await api.post(`/learning/${pathId}/prompt-lab/execute`, params)
  return data
}

export const getPromptHistory = async (
  pathId: string,
  lessonId: string
): Promise<{
  lesson_id: string
  iterations: Array<{
    iteration: number
    prompt_text: string
    response_text: string
    execution_time_ms: number
    created_at: string
  }>
  total_iterations: number
}> => {
  const { data } = await api.get(`/learning/${pathId}/prompt-lab/${lessonId}/history`)
  return data
}

// ── Implementation Task ─────────────────────────────────────────────

export const submitImplementationTask = async (
  pathId: string,
  params: {
    lesson_id: string
    artifact_text: string
    files: File[]
  }
): Promise<ImplementationGradeResult> => {
  const formData = new FormData()
  formData.append('lesson_id', params.lesson_id)
  formData.append('artifact_text', params.artifact_text)
  for (const file of params.files) {
    formData.append('files', file)
  }
  const { data } = await api.post(
    `/learning/${pathId}/implementation-task/submit`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return data
}

export const simulateImplementationTask = async (
  pathId: string,
  params: { lesson_id: string }
): Promise<ImplementationGradeResult> => {
  const formData = new FormData()
  formData.append('lesson_id', params.lesson_id)
  const { data } = await api.post(
    `/learning/${pathId}/implementation-task/simulate`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return data
}

// ── AI Mentor ───────────────────────────────────────────────────────

export const sendMentorMessage = async (
  pathId: string,
  params: { message: string; lesson_id?: string; mode?: string }
): Promise<{
  response: string
  suggested_prompts: string[]
  conversation_id: string
}> => {
  const { data } = await api.post(`/learning/${pathId}/mentor/chat`, params)
  return data
}

export const getMentorHistory = async (
  pathId: string,
  lessonId?: string
): Promise<{
  conversation_id: string
  messages: Array<{ role: string; content: string; timestamp: string }>
  last_suggested_prompts: string[]
}> => {
  const params = lessonId ? `?lesson_id=${lessonId}` : ''
  const { data } = await api.get(`/learning/${pathId}/mentor/history${params}`)
  return data
}

// ── Skill Genome ───────────────────────────────────────────────────

export const getSkillGenome = async (userId: string): Promise<SkillGenomeResponse> => {
  const { data } = await api.get(`/genome/${userId}`)
  return data
}

export const getSkillGenomeEntry = async (
  userId: string,
  skillId: string
): Promise<SkillGenomeEntry> => {
  const { data } = await api.get(`/genome/${userId}/${skillId}`)
  return data
}

// ── Lesson Reactions ───────────────────────────────────────────────

export const toggleReaction = async (
  pathId: string,
  lessonId: string,
  reaction: ReactionType
): Promise<LessonReactionState> => {
  const { data } = await api.post(
    `/learning/${pathId}/lessons/${lessonId}/react`,
    { reaction }
  )
  return data
}

export const getLessonReactions = async (
  pathId: string,
  lessonId: string
): Promise<LessonReactionState> => {
  const { data } = await api.get(
    `/learning/${pathId}/lessons/${lessonId}/reactions`
  )
  return data
}

// ── Confusion Recovery ─────────────────────────────────────────────

export const getConfusionRecovery = async (
  pathId: string,
  lessonId: string,
  section: string
): Promise<ConfusionRecovery> => {
  const { data } = await api.post(
    `/learning/${pathId}/lessons/${lessonId}/confusion-recovery`,
    { section }
  )
  return data
}

// ── Curiosity Feed ─────────────────────────────────────────────────

export const getCuriosityFeed = async (
  userId: string,
  limit: number = 10
): Promise<CuriosityFeedResponse> => {
  const { data } = await api.get(`/genome/${userId}/curiosity-feed?limit=${limit}`)
  return data
}

// ── Personalization ────────────────────────────────────────────────

export const getPersonalization = async (
  userId: string,
  pathId?: string
): Promise<PersonalizationResult> => {
  const url = pathId
    ? `/personalization/${userId}/path/${pathId}`
    : `/personalization/${userId}`
  const { data } = await api.get(url)
  return data
}

export default api
