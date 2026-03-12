import { Target } from 'lucide-react'

interface TargetGoalPanelProps {
  targetJD: string
  onTargetJDChange: (value: string) => void
  learningIntent: string
  onLearningIntentChange: (value: string) => void
}

export default function TargetGoalPanel({ targetJD, onTargetJDChange, learningIntent, onLearningIntentChange }: TargetGoalPanelProps) {
  return (
    <div className="bg-white rounded-xl p-7 shadow-sm border border-gray-100 space-y-6">
      {/* Panel header */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <Target className="h-5 w-5 text-indigo-600" />
          Target Goal
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          We compare this job description against your current skills.
        </p>
      </div>

      {/* Target Job Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Target Job Description <span className="text-red-500">*</span>
        </label>
        <textarea
          className="input min-h-[180px]"
          value={targetJD}
          onChange={(e) => onTargetJDChange(e.target.value)}
          placeholder="Paste the job description of the job you want to get."
        />
        <p className="text-xs text-gray-500 mt-1">
          The more detailed the job description, the better the skill gap analysis.
        </p>
      </div>

      {/* Learning Intent */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Learning Intent</label>
        <textarea
          className="input min-h-[100px]"
          value={learningIntent}
          onChange={(e) => onLearningIntentChange(e.target.value)}
          placeholder="What do you want to achieve? What skills do you want to develop?"
        />
      </div>
    </div>
  )
}
