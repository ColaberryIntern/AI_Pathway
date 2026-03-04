import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toggleReaction, getLessonReactions } from '../../services/api'
import type { ReactionType } from '../../types'

const REACTIONS: { type: ReactionType; emoji: string; label: string }[] = [
  { type: 'helpful', emoji: '👍', label: 'Helpful' },
  { type: 'interesting', emoji: '💡', label: 'Interesting' },
  { type: 'mind_blown', emoji: '🤯', label: 'Mind Blown' },
  { type: 'confused', emoji: '😕', label: 'Confused' },
]

interface LessonReactionsProps {
  pathId: string
  lessonId: string
  onConfused?: () => void
}

export default function LessonReactions({ pathId, lessonId, onConfused }: LessonReactionsProps) {
  const queryClient = useQueryClient()

  const { data } = useQuery({
    queryKey: ['lesson-reactions', pathId, lessonId],
    queryFn: () => getLessonReactions(pathId, lessonId),
  })

  const activeReactions = data?.reactions ?? []

  const mutation = useMutation({
    mutationFn: (reaction: ReactionType) => toggleReaction(pathId, lessonId, reaction),
    onSuccess: (result, reaction) => {
      queryClient.setQueryData(['lesson-reactions', pathId, lessonId], result)
      if (reaction === 'confused' && result.confusion_detected) {
        onConfused?.()
      }
    },
  })

  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-gray-400 mr-1">React:</span>
      {REACTIONS.map(({ type, emoji, label }) => {
        const isActive = activeReactions.includes(type)
        return (
          <button
            key={type}
            onClick={() => mutation.mutate(type)}
            disabled={mutation.isPending}
            title={label}
            className={`px-2.5 py-1 rounded-full text-sm transition-all ${
              isActive
                ? type === 'confused'
                  ? 'bg-red-100 border-red-300 border scale-105'
                  : 'bg-indigo-100 border-indigo-300 border scale-105'
                : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
            }`}
          >
            <span className="mr-0.5">{emoji}</span>
            <span className="text-[10px] hidden sm:inline">{label}</span>
          </button>
        )
      })}
    </div>
  )
}
