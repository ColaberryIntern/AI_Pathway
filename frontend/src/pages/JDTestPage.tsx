import { useState } from 'react'
import { Loader2, Copy, CheckCircle, FileText, Target } from 'lucide-react'
import { parseJDSkills } from '../services/api'
import type { ParsedSkill } from '../types'
import { copyToClipboard } from '../utils/clipboard'

const IMPORTANCE_COLORS: Record<string, string> = {
  high: 'bg-red-50 text-red-700 border-red-200',
  medium: 'bg-amber-50 text-amber-700 border-amber-200',
  low: 'bg-gray-50 text-gray-600 border-gray-200',
}

export default function JDTestPage() {
  const [jdText, setJdText] = useState('')
  const [targetRole, setTargetRole] = useState('')
  const [skills, setSkills] = useState<ParsedSkill[]>([])
  const [detectedRole, setDetectedRole] = useState('')
  const [roleAnalysis, setRoleAnalysis] = useState<Record<string, unknown> | null>(null)
  const [isParsing, setIsParsing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleParse = async () => {
    if (!jdText.trim() || jdText.trim().length < 50) return
    setIsParsing(true)
    setError(null)
    setSkills([])
    try {
      const result = await parseJDSkills({ jd_text: jdText, target_role: targetRole })
      setSkills(result.top_10_skills)
      setDetectedRole(result.target_role)
      setRoleAnalysis(result.role_analysis)
    } catch {
      setError('Failed to parse job description. Please try again.')
    } finally {
      setIsParsing(false)
    }
  }

  const handleCopyJSON = () => {
    const data = {
      target_role: detectedRole,
      role_analysis: roleAnalysis,
      top_10_skills: skills.map(s => ({
        rank: s.rank,
        skill_id: s.skill_id,
        skill_name: s.skill_name,
        domain: s.domain,
        domain_label: s.domain_label,
        required_level: s.required_level,
        importance: s.importance,
        rationale: s.rationale,
      })),
    }
    copyToClipboard(JSON.stringify(data, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          JD Skills Analyzer
        </h1>
        <p className="text-gray-600">
          Test how job descriptions map to the GenAI Skills Ontology.
          Paste a JD below to see the top 10 extracted skills.
        </p>
      </div>

      {/* Input */}
      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Role (optional)
          </label>
          <input
            type="text"
            className="input"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g., AI Operations Manager"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Job Description
          </label>
          <textarea
            className="input min-h-[200px]"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the full job description here..."
          />
          <p className="text-xs text-gray-400 mt-1">
            {jdText.trim().length} characters (min 50)
          </p>
        </div>
        <div className="flex justify-center">
          <button
            onClick={handleParse}
            disabled={!jdText.trim() || jdText.trim().length < 50 || isParsing}
            className={`btn flex items-center gap-2 px-6 py-3 ${
              jdText.trim().length >= 50 && !isParsing
                ? 'btn-primary'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isParsing ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Parsing JD...
              </>
            ) : (
              <>
                <FileText className="h-5 w-5" />
                Parse Job Description
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {skills.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Top 10 Skills Identified
              </h2>
              {detectedRole && (
                <p className="text-sm text-primary-700 flex items-center gap-1 mt-1">
                  <Target className="h-4 w-4" />
                  Detected Role: <strong>{detectedRole}</strong>
                </p>
              )}
            </div>
            <button
              onClick={handleCopyJSON}
              className="btn bg-gray-100 text-gray-700 hover:bg-gray-200 flex items-center gap-2"
            >
              {copied ? (
                <>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy as JSON
                </>
              )}
            </button>
          </div>

          {/* Skills Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left">
                  <th className="py-3 px-2 text-gray-500 font-medium w-12">#</th>
                  <th className="py-3 px-2 text-gray-500 font-medium">Skill ID</th>
                  <th className="py-3 px-2 text-gray-500 font-medium">Skill Name</th>
                  <th className="py-3 px-2 text-gray-500 font-medium">Domain</th>
                  <th className="py-3 px-2 text-gray-500 font-medium w-16">Level</th>
                  <th className="py-3 px-2 text-gray-500 font-medium w-24">Importance</th>
                  <th className="py-3 px-2 text-gray-500 font-medium">Rationale</th>
                </tr>
              </thead>
              <tbody>
                {skills.map((skill) => (
                  <tr key={skill.skill_id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-2 text-gray-400 font-mono">{skill.rank}</td>
                    <td className="py-3 px-2 font-mono text-xs text-gray-600">{skill.skill_id}</td>
                    <td className="py-3 px-2 font-medium text-gray-900">{skill.skill_name}</td>
                    <td className="py-3 px-2">
                      <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full border border-primary-200">
                        {skill.domain_label}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center font-semibold">{skill.required_level}</td>
                    <td className="py-3 px-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${IMPORTANCE_COLORS[skill.importance] || IMPORTANCE_COLORS.low}`}>
                        {skill.importance}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-gray-500 max-w-xs">{skill.rationale}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
