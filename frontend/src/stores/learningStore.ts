import { create } from 'zustand'
import type { LearningModule, SkillMastery } from '../types'

interface LearningState {
  pathId: string | null
  modules: LearningModule[]
  currentModuleId: string | null
  currentLessonId: string | null
  skillMasteries: SkillMastery[]
  overallProgress: number
  isActivated: boolean

  // Actions
  setPath: (pathId: string) => void
  setModules: (modules: LearningModule[]) => void
  setCurrentLesson: (moduleId: string, lessonId: string) => void
  updateSkillMastery: (mastery: SkillMastery) => void
  updateModuleStatus: (moduleId: string, status: LearningModule['status'], completedLessons: number) => void
  setOverallProgress: (progress: number) => void
  setActivated: (activated: boolean) => void
  reset: () => void
}

const initialState = {
  pathId: null as string | null,
  modules: [] as LearningModule[],
  currentModuleId: null as string | null,
  currentLessonId: null as string | null,
  skillMasteries: [] as SkillMastery[],
  overallProgress: 0,
  isActivated: false,
}

export const useLearningStore = create<LearningState>((set) => ({
  ...initialState,

  setPath: (pathId) => set({ pathId }),

  setModules: (modules) => set({ modules }),

  setCurrentLesson: (moduleId, lessonId) =>
    set({ currentModuleId: moduleId, currentLessonId: lessonId }),

  updateSkillMastery: (updated) =>
    set((state) => ({
      skillMasteries: state.skillMasteries.map((m) =>
        m.skill_id === updated.skill_id ? updated : m
      ),
    })),

  updateModuleStatus: (moduleId, status, completedLessons) =>
    set((state) => ({
      modules: state.modules.map((m) =>
        m.id === moduleId ? { ...m, status, completed_lessons: completedLessons } : m
      ),
    })),

  setOverallProgress: (progress) => set({ overallProgress: progress }),

  setActivated: (activated) => set({ isActivated: activated }),

  reset: () => set(initialState),
}))
