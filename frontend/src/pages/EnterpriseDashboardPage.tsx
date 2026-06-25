import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, Building2, Plus, Users } from 'lucide-react'
import {
  getOrganizations,
  createOrganization,
  getOrgDashboard,
} from '../services/api'

// Enterprise "who is doing what" dashboard (multi-tenancy increment 1).
// Lists organizations and, for the selected org, its learners + path progress.
export default function EnterpriseDashboardPage() {
  const queryClient = useQueryClient()
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null)
  const [newOrgName, setNewOrgName] = useState('')

  const { data: orgs, isLoading: loadingOrgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: getOrganizations,
  })

  // Default to the first org once loaded.
  useEffect(() => {
    if (orgs && orgs.length > 0 && !selectedOrg) setSelectedOrg(orgs[0].id)
  }, [orgs, selectedOrg])

  const { data: dashboard, isLoading: loadingDash } = useQuery({
    queryKey: ['org-dashboard', selectedOrg],
    queryFn: () => getOrgDashboard(selectedOrg as string),
    enabled: !!selectedOrg,
  })

  const createMutation = useMutation({
    mutationFn: () => createOrganization(newOrgName.trim()),
    onSuccess: (org) => {
      setNewOrgName('')
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      setSelectedOrg(org.id)
    },
  })

  if (loadingOrgs) {
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
          <h1 className="text-2xl font-bold text-gray-900">Enterprise Dashboard</h1>
          <p className="text-gray-600 text-sm mt-1 max-w-2xl">
            See who is doing what across an organization: learners and their learning-path progress.
          </p>
        </div>
      </div>

      {/* Org selector + create */}
      <div className="card">
        <div className="flex flex-wrap items-center gap-3">
          <label className="text-sm font-medium text-gray-700">Organization</label>
          <select
            value={selectedOrg || ''}
            onChange={(e) => setSelectedOrg(e.target.value)}
            className="form-select text-sm border border-gray-300 rounded-lg px-3 py-2"
          >
            {(orgs || []).map((o) => (
              <option key={o.id} value={o.id}>
                {o.name} ({o.member_count})
              </option>
            ))}
          </select>
          <div className="ms-auto flex items-center gap-2">
            <input
              type="text"
              value={newOrgName}
              onChange={(e) => setNewOrgName(e.target.value)}
              placeholder="New organization name"
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
            <button
              onClick={() => createMutation.mutate()}
              disabled={!newOrgName.trim() || createMutation.isPending}
              className="btn btn-primary flex items-center gap-1 disabled:opacity-50"
            >
              <Plus className="h-4 w-4" /> Add
            </button>
          </div>
        </div>
      </div>

      {/* Learners */}
      {loadingDash ? (
        <div className="text-center py-10">
          <Loader2 className="h-6 w-6 animate-spin mx-auto text-indigo-600" />
        </div>
      ) : dashboard ? (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              {dashboard.org_name} - {dashboard.learner_count} learner{dashboard.learner_count === 1 ? '' : 's'}
            </h2>
          </div>
          {dashboard.learners.length === 0 ? (
            <p className="text-sm text-gray-500 py-6 text-center">
              No learners assigned to this organization yet.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-200">
                    <th className="py-2 pr-4 font-medium">Learner</th>
                    <th className="py-2 pr-4 font-medium">Paths</th>
                    <th className="py-2 pr-4 font-medium">Active</th>
                    <th className="py-2 pr-4 font-medium">Completed</th>
                    <th className="py-2 pr-4 font-medium">Overall</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.learners.map((l) => (
                    <tr key={l.user_id} className="border-b border-gray-100">
                      <td className="py-2 pr-4">
                        <div className="font-medium text-gray-900">{l.name || '(unnamed)'}</div>
                        {l.email && <div className="text-xs text-gray-500">{l.email}</div>}
                      </td>
                      <td className="py-2 pr-4">{l.total_paths}</td>
                      <td className="py-2 pr-4">{l.active_paths.length}</td>
                      <td className="py-2 pr-4">{l.completed_paths.length}</td>
                      <td className="py-2 pr-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 rounded-full bg-gray-200 overflow-hidden">
                            <div
                              className="h-full bg-emerald-500"
                              style={{ width: `${l.overall_completion_percentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-600">{l.overall_completion_percentage}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : null}
    </div>
  )
}
