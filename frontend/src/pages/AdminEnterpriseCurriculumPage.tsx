import { useEffect, useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, CheckCircle2, X, Search, Building2 } from 'lucide-react'
import {
  getEnterpriseCurriculum,
  updateEnterpriseCurriculum,
  getOntology,
} from '../services/api'

interface OntologySkill {
  id: string
  name: string
  domain: string
  level?: number
}

// Enterprise Base Curriculum admin (Jun 23 weekly sync, item D / B2B angle).
// Define the global set of base skills every learner must know; personalized
// paths are layered on top so each served path includes the base.
export default function AdminEnterpriseCurriculumPage() {
  const queryClient = useQueryClient()
  const [skillIds, setSkillIds] = useState<string[]>([])
  const [query, setQuery] = useState('')
  const [initialized, setInitialized] = useState(false)

  const { data: curriculum, isLoading: loadingCurr } = useQuery({
    queryKey: ['enterprise-curriculum'],
    queryFn: getEnterpriseCurriculum,
  })
  const { data: ontology, isLoading: loadingOnt } = useQuery({
    queryKey: ['ontology'],
    queryFn: getOntology,
  })

  // Seed local working state once the saved curriculum loads.
  useEffect(() => {
    if (curriculum && !initialized) {
      setSkillIds(curriculum.skill_ids)
      setInitialized(true)
    }
  }, [curriculum, initialized])

  const allSkills: OntologySkill[] = useMemo(() => ontology?.skills || [], [ontology])
  const nameById = useMemo(() => {
    const m: Record<string, string> = {}
    for (const s of allSkills) m[s.id] = s.name
    return m
  }, [allSkills])

  const saveMutation = useMutation({
    mutationFn: () => updateEnterpriseCurriculum(skillIds),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['enterprise-curriculum'] }),
  })

  const dirty = useMemo(() => {
    const a = [...skillIds].sort().join(',')
    const b = [...(curriculum?.skill_ids || [])].sort().join(',')
    return a !== b
  }, [skillIds, curriculum])

  const addable = useMemo(() => {
    const q = query.trim().toLowerCase()
    return allSkills
      .filter((s) => !skillIds.includes(s.id))
      .filter((s) => !q || s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q))
      .slice(0, 40)
  }, [allSkills, skillIds, query])

  const add = (id: string) => setSkillIds((prev) => (prev.includes(id) ? prev : [...prev, id]))
  const remove = (id: string) => setSkillIds((prev) => prev.filter((x) => x !== id))

  if (loadingCurr || loadingOnt) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-11 h-11 rounded-lg bg-indigo-600 text-white flex items-center justify-center">
          <Building2 className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Enterprise Base Curriculum</h1>
          <p className="text-gray-600 text-sm mt-1 max-w-2xl">
            Define the base skills every learner in your organization must know. These
            are included as the foundation of every personalized learning path, ahead of
            each learner&rsquo;s individual gaps.
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Current base skills */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Base skills ({skillIds.length})
            </h2>
          </div>
          {skillIds.length === 0 ? (
            <p className="text-sm text-gray-500 py-6 text-center">
              No base skills yet. Add skills from the right to define the enterprise base.
            </p>
          ) : (
            <ul className="space-y-2">
              {skillIds.map((id) => (
                <li
                  key={id}
                  className="flex items-center justify-between p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg"
                >
                  <span className="text-sm text-gray-900">
                    <span className="font-mono text-xs text-gray-500 mr-2">{id}</span>
                    {nameById[id] || id}
                  </span>
                  <button
                    onClick={() => remove(id)}
                    className="text-gray-400 hover:text-red-600"
                    aria-label={`Remove ${nameById[id] || id}`}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Add skills */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Add skills</h2>
          <div className="relative mb-3">
            <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search skills by name or id..."
              className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="max-h-72 overflow-y-auto space-y-1.5">
            {addable.map((s) => (
              <button
                key={s.id}
                onClick={() => add(s.id)}
                className="w-full text-left p-2 hover:bg-indigo-50 border border-gray-200 rounded-lg"
              >
                <span className="font-mono text-xs text-gray-500">{s.id}</span>
                <div className="text-sm font-medium text-gray-900">{s.name}</div>
              </button>
            ))}
            {addable.length === 0 && (
              <p className="text-sm text-gray-500 py-4 text-center">No matching skills.</p>
            )}
          </div>
        </div>
      </div>

      {/* Save bar */}
      <div className="flex items-center justify-end gap-3">
        {saveMutation.isSuccess && !dirty && (
          <span className="flex items-center gap-1 text-sm text-emerald-600">
            <CheckCircle2 className="h-4 w-4" /> Saved
          </span>
        )}
        <button
          onClick={() => saveMutation.mutate()}
          disabled={!dirty || saveMutation.isPending}
          className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {saveMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          {saveMutation.isPending ? 'Saving...' : 'Save Curriculum'}
        </button>
      </div>
    </div>
  )
}
