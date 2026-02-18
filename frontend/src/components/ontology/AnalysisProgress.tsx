import { User, FileText, BarChart3, BookOpen, Check, Loader2 } from 'lucide-react'

type StepStatus = 'pending' | 'active' | 'complete'

interface AnalysisProgressProps {
  currentStep: number
}

const STEPS = [
  { label: 'Profile', icon: User },
  { label: 'JD Parse', icon: FileText },
  { label: 'Gap Analysis', icon: BarChart3 },
  { label: 'Learning Path', icon: BookOpen },
]

export default function AnalysisProgress({ currentStep }: AnalysisProgressProps) {
  const getStepStatus = (index: number): StepStatus => {
    if (index < currentStep) return 'complete'
    if (index === currentStep) return 'active'
    return 'pending'
  }

  return (
    <div className="flex items-center justify-center gap-2 sm:gap-4">
      {STEPS.map((step, index) => {
        const status = getStepStatus(index)
        const Icon = step.icon

        return (
          <div key={step.label} className="flex items-center">
            {/* Step indicator */}
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center
                  transition-all duration-300 shadow-sm
                  ${status === 'complete' ? 'bg-green-500 shadow-green-200' : ''}
                  ${status === 'active' ? 'bg-sky-500 shadow-sky-200' : ''}
                  ${status === 'pending' ? 'bg-gray-200' : ''}
                `}
              >
                {status === 'complete' ? (
                  <Check className="h-5 w-5 text-white" />
                ) : status === 'active' ? (
                  <Loader2 className="h-5 w-5 text-white animate-spin" />
                ) : (
                  <Icon className="h-5 w-5 text-gray-400" />
                )}
              </div>
              <span
                className={`
                  text-xs mt-1.5 font-medium
                  ${status === 'complete' ? 'text-green-600' : ''}
                  ${status === 'active' ? 'text-sky-600' : ''}
                  ${status === 'pending' ? 'text-gray-400' : ''}
                `}
              >
                {step.label}
              </span>
            </div>

            {/* Connector line (not after last step) */}
            {index < STEPS.length - 1 && (
              <div
                className={`
                  h-0.5 w-6 sm:w-12 mx-2 rounded
                  transition-colors duration-300
                  ${index < currentStep ? 'bg-green-500' : 'bg-gray-200'}
                `}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
