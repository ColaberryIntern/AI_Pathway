// Path-wide lesson navigation helpers.
//
// Jun 23 weekly sync: "let users walk through the chapters themselves."
// The chapter-format lesson view previously had only "Back to Dashboard" +
// "Mark Complete", so a learner could not move chapter-to-chapter without
// bouncing through the dashboard and marking each one complete. These pure
// helpers flatten every navigable lesson across the path in reading order and
// resolve the previous/next lesson for the current one, so the lesson page can
// offer real Prev/Next navigation that does NOT require completion.
//
// Kept as a pure module (no React, no I/O) so the ordering logic is trivially
// verifiable in isolation.
import type { LearningModule } from '../types'

export interface FlatLesson {
  lessonId: string
  moduleId: string
  chapterNumber: number
  lessonNumber: number
  title: string
}

// Flatten all lessons across the path into reading order (chapter, then
// lesson). Only lessons with a DB id are included - those are the ones a user
// can actually open. Input is treated as immutable.
export function flattenPathLessons(modules: LearningModule[] | undefined | null): FlatLesson[] {
  if (!modules || modules.length === 0) return []
  const sortedModules = [...modules].sort((a, b) => a.chapter_number - b.chapter_number)
  const flat: FlatLesson[] = []
  for (const m of sortedModules) {
    const outline = [...(m.lesson_outline || [])].sort((a, b) => a.lesson_number - b.lesson_number)
    for (const l of outline) {
      if (!l.id) continue
      flat.push({
        lessonId: l.id,
        moduleId: m.id,
        chapterNumber: m.chapter_number,
        lessonNumber: l.lesson_number,
        title: l.title,
      })
    }
  }
  return flat
}

export interface AdjacentLessons {
  prev: FlatLesson | null
  next: FlatLesson | null
  position: number // 1-based position of the current lesson; 0 if not found
  total: number
}

// Resolve previous/next lesson for the current lesson across the whole path.
export function getAdjacentLessons(
  modules: LearningModule[] | undefined | null,
  currentLessonId: string | undefined | null,
): AdjacentLessons {
  const flat = flattenPathLessons(modules)
  const idx = currentLessonId ? flat.findIndex((f) => f.lessonId === currentLessonId) : -1
  if (idx === -1) {
    return { prev: null, next: null, position: 0, total: flat.length }
  }
  return {
    prev: idx > 0 ? flat[idx - 1] : null,
    next: idx < flat.length - 1 ? flat[idx + 1] : null,
    position: idx + 1,
    total: flat.length,
  }
}
