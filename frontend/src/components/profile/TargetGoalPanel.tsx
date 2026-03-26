import { Target, Loader2, CheckCircle, Briefcase, Wrench, Users, BarChart3 } from 'lucide-react'

interface JDAnalysisResult {
  technical_skills?: string[]
  soft_skills?: string[]
  ai_requirements?: string
  summary?: string
  seniority_level?: string
  key_tools?: string[]
}

interface TargetGoalPanelProps {
  targetJD: string
  onTargetJDChange: (value: string) => void
  learningIntent: string
  onLearningIntentChange: (value: string) => void
  isAnalyzing?: boolean
  analysisComplete?: boolean
  detectedRole?: string
  jdAnalysis?: JDAnalysisResult | null
}

export default function TargetGoalPanel({
  targetJD,
  onTargetJDChange,
  learningIntent,
  onLearningIntentChange,
  isAnalyzing,
  analysisComplete,
  detectedRole,
  jdAnalysis,
}: TargetGoalPanelProps) {
  return (
    <div className="bg-white rounded-xl p-7 shadow-sm border border-gray-100 space-y-6">
      {/* Panel header */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <Target className="h-5 w-5 text-indigo-600" />
          Target Goal
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Paste the job description and we'll automatically analyze the required skills.
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
          placeholder="Paste the job description of the job you want to get. Analysis starts automatically."
        />
        {/* Status indicator */}
        {isAnalyzing && (
          <div className="flex items-center gap-2 mt-2 text-sm text-indigo-600">
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing job description...
          </div>
        )}
        {!isAnalyzing && !analysisComplete && targetJD.trim().length > 0 && targetJD.trim().length < 50 && (
          <p className="text-xs text-amber-600 mt-1">
            Please paste a more detailed job description (at least 50 characters).
          </p>
        )}
        {!isAnalyzing && !analysisComplete && targetJD.trim().length === 0 && (
          <p className="text-xs text-gray-500 mt-1">
            The more detailed the job description, the better the skill gap analysis.
          </p>
        )}
      </div>

      {/* JD Analysis Results */}
      {analysisComplete && jdAnalysis && (
        <div className="space-y-4 border-t border-gray-100 pt-4">
          {/* Detected Role */}
          {detectedRole && (
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0" />
              <span className="text-gray-600">Detected role:</span>
              <span className="font-semibold text-gray-900">{detectedRole}</span>
            </div>
          )}

          {/* Seniority Level */}
          {jdAnalysis.seniority_level && (
            <div className="flex items-center gap-2 text-sm">
              <BarChart3 className="h-4 w-4 text-indigo-500 flex-shrink-0" />
              <span className="text-gray-600">Seniority:</span>
              <span className="font-medium text-gray-800">{jdAnalysis.seniority_level}</span>
            </div>
          )}

          {/* Technical Skills */}
          {jdAnalysis.technical_skills && jdAnalysis.technical_skills.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Wrench className="h-3.5 w-3.5" />
                Required Technical Skills
              </p>
              <div className="flex flex-wrap gap-2">
                {jdAnalysis.technical_skills.map((skill, i) => (
                  <span key={i} className="text-xs bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md border border-indigo-200">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Soft Skills */}
          {jdAnalysis.soft_skills && jdAnalysis.soft_skills.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Users className="h-3.5 w-3.5" />
                Required Soft Skills
              </p>
              <div className="flex flex-wrap gap-2">
                {jdAnalysis.soft_skills.map((skill, i) => (
                  <span key={i} className="text-xs bg-sky-50 text-sky-700 px-2.5 py-1 rounded-md border border-sky-200">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Key Tools */}
          {jdAnalysis.key_tools && jdAnalysis.key_tools.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <Briefcase className="h-3.5 w-3.5" />
                Key Tools & Platforms
              </p>
              <div className="flex flex-wrap gap-2">
                {jdAnalysis.key_tools.map((tool, i) => (
                  <span key={i} className="text-xs bg-amber-50 text-amber-700 px-2.5 py-1 rounded-md border border-amber-200">
                    {tool}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* AI Requirements Summary */}
          {jdAnalysis.ai_requirements && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">AI Requirements</p>
              <p className="text-sm text-gray-600 bg-gray-50 p-2.5 rounded-md border border-gray-200">
                {jdAnalysis.ai_requirements}
              </p>
            </div>
          )}
        </div>
      )}

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
