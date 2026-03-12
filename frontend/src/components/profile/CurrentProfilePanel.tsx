import {
  User, FileText, X, CheckCircle2, AlertCircle, Loader2,
} from 'lucide-react'

interface ProfileFields {
  name: string
  current_role: string
  industry: string
  experience_years: string
  ai_exposure_level: string
  learning_intent: string
  current_jd: string
  tools_used: string[]
  technical_background: string
}

interface CurrentProfilePanelProps {
  customProfile: ProfileFields
  onProfileChange: (updates: Partial<ProfileFields>) => void
  resumeFile: File | null
  isParsingResume: boolean
  resumeError: string | null
  resumeParsed: boolean
  isDragOver: boolean
  fileInputRef: React.RefObject<HTMLInputElement>
  onResumeUpload: (file: File) => void
  onDrop: (e: React.DragEvent) => void
  onDragOver: (e: React.DragEvent) => void
  onDragLeave: () => void
  onClearResume: () => void
}

const AI_TOOLS = [
  'ChatGPT / Claude / Gemini',
  'GitHub Copilot',
  'Midjourney / DALL-E',
  'OpenAI API / Anthropic API',
  'None',
]

export default function CurrentProfilePanel({
  customProfile,
  onProfileChange,
  resumeFile,
  isParsingResume,
  resumeError,
  resumeParsed,
  isDragOver,
  fileInputRef,
  onResumeUpload,
  onDrop,
  onDragOver,
  onDragLeave,
  onClearResume,
}: CurrentProfilePanelProps) {
  return (
    <div className="bg-white rounded-xl p-7 shadow-sm border border-gray-100 space-y-6">
      {/* Panel header */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <User className="h-5 w-5 text-indigo-600" />
          Your Current Profile
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          This information helps us estimate your starting skill level.
        </p>
      </div>

      {/* Resume Upload Zone */}
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all ${
          isDragOver
            ? 'border-indigo-400 bg-indigo-50'
            : resumeParsed
              ? 'border-green-300 bg-green-50'
              : resumeError
                ? 'border-red-300 bg-red-50'
                : 'border-gray-200 bg-gray-50 hover:border-gray-300'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) onResumeUpload(file)
          }}
        />

        {isParsingResume ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 text-indigo-500 animate-spin" />
            <div>
              <p className="text-sm font-medium text-gray-700">Analyzing {resumeFile?.name}...</p>
              <p className="text-xs text-gray-500 mt-1">Extracting profile information from your resume</p>
            </div>
          </div>
        ) : resumeParsed && resumeFile ? (
          <div className="flex items-center justify-center gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
            <div className="text-left">
              <p className="text-sm font-medium text-green-700">
                Extracted from {resumeFile.name}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">Fields have been auto-filled. You can edit them below.</p>
            </div>
            <button
              onClick={onClearResume}
              className="ml-2 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div
            className="flex flex-col items-center gap-3 cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
              <FileText className="h-6 w-6 text-indigo-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">
                Upload your LinkedIn Profile PDF to auto-fill
              </p>
              <p className="text-xs text-gray-500 mt-1">
                PDF or DOCX (max 10 MB) - drag & drop or click to browse
              </p>
            </div>
            {resumeError && (
              <div className="flex items-center gap-1.5 text-red-600 text-sm">
                <AlertCircle className="h-4 w-4" />
                {resumeError}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Short fields - 2 column grid */}
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
          <input
            type="text"
            className="input"
            value={customProfile.name}
            onChange={(e) => onProfileChange({ name: e.target.value })}
            placeholder="e.g., John Smith"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Current Role</label>
          <input
            type="text"
            className="input"
            value={customProfile.current_role}
            onChange={(e) => onProfileChange({ current_role: e.target.value })}
            placeholder="e.g., Marketing Manager"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
          <input
            type="text"
            className="input"
            value={customProfile.industry}
            onChange={(e) => onProfileChange({ industry: e.target.value })}
            placeholder="e.g., Healthcare"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
          <input
            type="number"
            className="input"
            value={customProfile.experience_years}
            onChange={(e) => onProfileChange({ experience_years: e.target.value })}
            placeholder="e.g., 5"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            How would you describe your current AI knowledge?
          </label>
          <select
            className="input"
            value={customProfile.ai_exposure_level}
            onChange={(e) => onProfileChange({ ai_exposure_level: e.target.value })}
          >
            <option value="None">None</option>
            <option value="Basic">Basic</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            What is your technical or coding background?
          </label>
          <select
            className="input"
            value={customProfile.technical_background}
            onChange={(e) => onProfileChange({ technical_background: e.target.value })}
          >
            <option value="">Select...</option>
            <option value="No coding experience">No coding experience</option>
            <option value="Basic scripting (Excel, simple automation)">Basic scripting (Excel, simple automation)</option>
            <option value="Some programming">Some programming</option>
            <option value="Professional developer">Professional developer</option>
          </select>
        </div>
      </div>

      {/* AI Tools Used - Multi-select */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Which AI tools have you used? <span className="text-gray-400 font-normal">(Select all that apply)</span>
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {AI_TOOLS.map((tool) => {
            const isSelected = customProfile.tools_used.includes(tool)
            const isNone = tool === 'None'
            return (
              <label
                key={tool}
                className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
                    : 'border-gray-200 bg-white hover:border-gray-300 text-gray-700'
                }`}
              >
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  checked={isSelected}
                  onChange={() => {
                    let next: string[]
                    if (isNone) {
                      next = isSelected ? [] : ['None']
                    } else {
                      next = isSelected
                        ? customProfile.tools_used.filter(t => t !== tool)
                        : [...customProfile.tools_used.filter(t => t !== 'None'), tool]
                    }
                    onProfileChange({ tools_used: next })
                  }}
                />
                <span className="text-sm">{tool}</span>
              </label>
            )
          })}
        </div>
      </div>

      {/* Current Job Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Current Job Description</label>
        <textarea
          className="input min-h-[100px]"
          value={customProfile.current_jd}
          onChange={(e) => onProfileChange({ current_jd: e.target.value })}
          placeholder="Paste your current job description to help us better understand your existing skills..."
        />
        <p className="text-xs text-gray-500 mt-1">
          Helps us better assess your current skill level.
        </p>
      </div>
    </div>
  )
}
