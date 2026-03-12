export interface Profile {
  id: string
  name: string
  current_role: string
  target_role: string
  industry: string
  experience_years?: number
  ai_exposure_level?: string
  tools_used?: string[]
  technical_background?: string
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
  introduction?: string
  core_concepts: CoreConcept[]
  prompting_examples?: PromptingExample[]
  agent_examples?: AgentExample[]
  exercises: Exercise[]
  key_takeaways?: string[]
  exact_prompt?: ExactPrompt
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

export interface PromptingExample {
  title: string
  description: string
  prompt: string
  expected_output: string
  customization_tips: string
}

export interface AgentExample {
  title: string
  scenario: string
  agent_role: string
  instructions: string[]
  expected_behavior: string
  use_case: string
}

export interface ExactPrompt {
  title: string
  context: string
  prompt_text: string
  expected_output: string
  how_to_customize: string
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

export interface Top10CurrentSkill {
  rank: number
  skill_id: string
  skill_name: string
  domain: string
  domain_label?: string
  current_level: number
  rationale: string
}

export interface Top10TargetSkill {
  rank: number
  skill_id: string
  skill_name: string
  domain: string
  domain_label?: string
  required_level: number
  importance?: string
  rationale: string
}

export interface Top10SkillGap {
  rank?: number
  skill_id: string
  skill_name: string
  domain: string
  domain_label?: string
  current_level: number
  required_level: number
  gap: number
  importance?: string
  rationale?: string
}

export interface JourneySkillAddressed {
  skill_id: string
  skill_name: string
  domain_label: string
  current_level: number
  after_path_level: number
  required_level: number
  gap_closed: number
  gap_remaining: number
}

export interface JourneySkillRemaining {
  skill_id: string
  skill_name: string
  domain_label: string
  current_level: number
  required_level: number
  gap: number
  partial?: boolean
}

export interface JourneyRoadmap {
  path_number: number
  total_gap_levels: number
  path_closes_levels: number
  remaining_gap_levels: number
  estimated_total_paths: number
  skills_addressed: JourneySkillAddressed[]
  skills_remaining: JourneySkillRemaining[]
}

export interface ProficiencyDescription {
  level: number
  label: string
  description: string
}

export interface ParsedSkill {
  rank: number
  skill_id: string
  skill_name: string
  domain: string
  domain_label: string
  required_level: number
  importance: string
  rationale: string
  skill_description: string
  proficiency_descriptions: ProficiencyDescription[]
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
        seniority_level?: string
        technical_depth?: string
      }
    }
    top_10_current_skills?: Top10CurrentSkill[]
    top_10_target_skills?: Top10TargetSkill[]
    top_10_skill_gaps?: Top10SkillGap[]
    all_skill_gaps?: Top10SkillGap[]
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
    journey_roadmap?: JourneyRoadmap
    fit_score?: number
    executive_introduction?: string
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

// ── Learning Execution Types ────────────────────────────────────────

export interface LearningModule {
  id: string
  chapter_number: number
  skill_id: string
  skill_name: string
  title: string
  current_level: number
  target_level: number
  lesson_outline: LessonOutline[]
  total_lessons: number
  completed_lessons: number
  status: 'not_started' | 'in_progress' | 'completed'
}

export interface LessonOutline {
  lesson_number: number
  title: string
  type: 'concept' | 'practice' | 'assessment'
  focus_area: string
  estimated_minutes: number
}

export interface Lesson {
  id: string
  module_id: string
  lesson_number: number
  title: string
  lesson_type: string
  content: LessonContent | null
  status: 'not_started' | 'in_progress' | 'completed'
  quiz_score: number | null
  exercise_attempts: number
}

export interface LessonContent {
  // AI-native sections (present in newly generated lessons)
  concept_snapshot?: string
  ai_strategy?: AIStrategy
  prompt_template?: PromptTemplate
  implementation_task?: ImplementationTask
  reflection_questions?: ReflectionQuestion[]

  // Legacy sections (always present for backward compat)
  explanation: string
  code_examples: CodeExample[]
  exercises: LessonExercise[]
  knowledge_checks: KnowledgeCheck[]
  hands_on_tasks: HandsOnTask[]
}

// ── AI-Native Lesson Types ──────────────────────────────────────────

export interface AIStrategy {
  description: string
  when_to_use_ai: string[]
  human_responsibilities: string[]
  suggested_prompt: string
}

export interface PromptTemplate {
  template: string
  placeholders: PromptPlaceholder[]
  expected_output_shape: string
}

export interface PromptPlaceholder {
  name: string
  description: string
  example: string
}

export interface ImplementationTask {
  title: string
  description: string
  requirements: string[]
  deliverable: string
  requires_architecture_explanation: boolean
  estimated_minutes: number
  tools?: { name: string; url?: string; is_free: boolean }[]
  evidence_requirements?: { name: string; description: string; format: string }[]
}

export interface ImplementationGradeResult {
  score: number
  passed: boolean
  feedback: string
  strengths: string[]
  improvements: string[]
  attempt_number: number
  file_names?: string[]
  extracted_content?: string
  download_urls?: string[]
}

export interface ReflectionQuestion {
  question: string
  prompt_for_deeper_thinking: string
}

export interface CodeExample {
  title: string
  language: string
  code: string
  explanation: string
  validated?: boolean
}

export interface LessonExercise {
  id: string
  title: string
  instructions: string
  starter_code: string
  expected_output: string
  hints: string[]
  estimated_minutes: number
}

export interface KnowledgeCheck {
  question: string
  options: string[]
  correct_answer: string
  explanation: string
  ai_followup_prompt?: string
}

export interface HandsOnTask {
  title: string
  description: string
  requirements: string[]
  deliverable: string
  estimated_minutes: number
}

export interface SkillMastery {
  skill_id: string
  skill_name: string
  initial_level: number
  current_level: number
  target_level: number
  lessons_completed: number
  total_lessons: number
  avg_quiz_score: number | null
  progress_percentage: number
}

export interface LearningDashboard {
  path_id: string
  path_title: string
  target_role: string
  overall_progress: number
  modules: LearningModule[]
  skill_masteries: SkillMastery[]
  current_module: LearningModule | null
  next_lesson: LessonOutline | null
  next_lesson_id: string | null
  total_lessons_completed: number
  total_lessons: number
  estimated_hours_remaining: number
}

export interface ActivatePathResponse {
  modules: LearningModule[]
  total_lessons: number
  skill_masteries: SkillMastery[]
}

// ── Skill Genome Types ────────────────────────────────────────────

export interface SkillGenomeEntry {
  ontology_node_id: string
  skill_name: string
  domain: string | null
  mastery_level: number
  evidence_count: number
  last_evidence: string | null
  confidence: number
  updated_at: string
}

export interface SkillGenomeResponse {
  user_id: string
  entries: SkillGenomeEntry[]
  total_skills: number
}

// ── Lesson Reactions Types ────────────────────────────────────────

export type ReactionType = 'helpful' | 'interesting' | 'mind_blown' | 'confused'

export interface LessonReactionState {
  reactions: ReactionType[]
  confusion_detected: boolean
}

// ── Confusion Recovery Types ──────────────────────────────────────

export interface ConfusionRecovery {
  analogy: string
  step_by_step: string[]
  real_world_example: string
  common_misconceptions: string[]
  suggested_mentor_prompt: string
}

// ── Curiosity Feed Types ──────────────────────────────────────────

export interface CuriosityFeedItem {
  skill_id: string
  skill_name: string
  domain: string | null
  domain_label: string | null
  teaser: string
  unlocked_by: string
  relevance_score: number
  has_learning_path: boolean
}

export interface CuriosityFeedResponse {
  user_id: string
  items: CuriosityFeedItem[]
  total_items: number
}

// ── Personalization Types ─────────────────────────────────────────

export interface PersonalizationResult {
  struggling_skills: { skill_name: string; signal: string }[]
  strong_skills: { skill_name: string; mastery: number }[]
  suggested_review: { lesson_id: string; title: string; reason: string }[]
  pace_recommendation: 'slow_down' | 'on_track' | 'can_accelerate'
  next_focus: { skill_name: string; reason: string } | null
}
