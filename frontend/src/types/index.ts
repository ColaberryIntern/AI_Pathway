export interface Profile {
  id: string
  name: string
  current_role: string
  target_role: string
  industry: string
  experience_years?: number
  ai_exposure_level?: string
  learning_intent?: string
  archetype?: 'Career Switcher' | 'Domain Upskiller' | 'Executive' | 'Technical Pivot'
  current_profile?: {
    summary: string
    technical_skills: string[]
    soft_skills: string[]
    ai_experience: string
  }
  target_jd?: {
    title: string
    requirements: string[]
  }
  expected_skill_gaps?: SkillGapDomain[]
  estimated_current_skills?: Record<string, number>
}

export interface SkillGapDomain {
  domain: string
  description: string
  skills: string[]
}

export interface SkillGap {
  skill_id: string
  skill_name: string
  domain: string
  current_level: number
  target_level: number
  gap: number
  priority: number
  priority_reason?: string
  prerequisites?: string[]
}

export interface Chapter {
  chapter_number: number
  skill_id: string
  skill_name: string
  title: string
  learning_objectives: string[]
  current_level: number
  target_level: number
  core_concepts: CoreConcept[]
  exercises: Exercise[]
  self_assessment_questions: AssessmentQuestion[]
  resources?: Resource[]
  industry_context?: string
  estimated_time_hours?: number
}

export interface CoreConcept {
  title: string
  content: string
  examples?: string[]
}

export interface Exercise {
  id: string
  title: string
  description: string
  type: string
  estimated_time_minutes?: number
  instructions?: string[]
  deliverable?: string
}

export interface AssessmentQuestion {
  question: string
  options: string[]
  answer: string
}

export interface Resource {
  title: string
  url?: string
  type: string
  source?: string
  description?: string
}

export interface LearningPath {
  id: string
  user_id: string
  goal_id: string
  gap_id: string
  title: string
  description: string
  chapters: Chapter[]
  total_chapters: number
  created_at: string
}

export interface Progress {
  id: string
  path_id: string
  current_chapter: number
  chapter_status: Record<string, string>
  quiz_scores?: Record<string, number>
  completion_percentage: number
  updated_at: string
}

export interface AnalysisResult {
  user_id: string
  goal_id: string
  skill_gap_id: string
  learning_path_id: string
  result: {
    workflow_id: string
    profile_analysis: {
      state_a_skills: Record<string, number>
      profile_summary: string
      recommended_focus_domains: string[]
    }
    jd_parsing: {
      state_b_skills: Record<string, number>
      extracted_requirements: Array<{
        skill_id: string
        skill_name: string
        required_level: number
        importance: string
      }>
      role_analysis: {
        primary_function: string
        key_domains: string[]
      }
    }
    gap_analysis: {
      gaps: SkillGap[]
      summary: {
        total_gaps: number
        critical_gaps: number
        primary_domains: string[]
      }
      recommendations: string[]
    }
    learning_path: {
      title: string
      description: string
      chapters: Chapter[]
      total_estimated_hours: number
    }
    summary: {
      profile_summary: string
      target_role: string
      total_gaps_identified: number
      critical_gaps: number
      learning_path_title: string
      total_chapters: number
      estimated_learning_hours: number
      primary_domains: string[]
      recommendations: string[]
    }
  }
}

export interface DashboardData {
  user_id: string
  active_paths: PathSummary[]
  completed_paths: PathSummary[]
  total_skills_learned: number
  total_paths: number
}

export interface PathSummary {
  id: string
  title: string
  total_chapters: number
  completed_chapters: number
  completion_percentage: number
  created_at: string
}
