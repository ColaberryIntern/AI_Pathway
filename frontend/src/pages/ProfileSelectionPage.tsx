import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getProfiles } from '../services/api'
import { User, Upload, Briefcase, Target, ChevronRight, Clock, Sparkles, ChevronDown } from 'lucide-react'
import type { Profile } from '../types'
import ArchetypeBadge from '../components/ArchetypeBadge'
import JourneyArrow from '../components/JourneyArrow'
import { getProficiencyLevel } from '../components/ProficiencyLegend'

export default function ProfileSelectionPage() {
  const navigate = useNavigate()
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null)
  const [customProfile, setCustomProfile] = useState({
    name: '',
    current_role: '',
    target_role: '',
    industry: '',
    experience_years: '',
    ai_exposure_level: 'Basic',
    learning_intent: '',
  })
  const [targetJD, setTargetJD] = useState('')

  const { data: profiles, isLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: getProfiles,
  })

  const handleSelectProfile = (profileId: string) => {
    setSelectedProfile(profileId)
  }

  const handleDoubleClick = (profileId: string) => {
    setSelectedProfile(profileId)
    navigate(`/analysis/${profileId}`)
  }

  const handleCustomContinue = () => {
    if (customProfile.name && targetJD) {
      // Store custom profile in session storage for the analysis page
      sessionStorage.setItem('customProfile', JSON.stringify(customProfile))
      sessionStorage.setItem('targetJD', targetJD)
      navigate('/analysis/custom')
    }
  }

  const handleExampleContinue = () => {
    if (selectedProfile) {
      navigate(`/analysis/${selectedProfile}`)
    }
  }

  const scrollToExamples = () => {
    document.getElementById('example-profiles')?.scrollIntoView({ behavior: 'smooth' })
  }

  const isCustomValid = customProfile.name && customProfile.current_role && targetJD

  return (
    <div className="max-w-6xl mx-auto space-y-12">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
          Choose Your Starting Point
        </h1>
        <p className="text-gray-600 text-lg">
          Create your profile or choose from 12 example profiles
        </p>

        {/* Navigation buttons */}
        <div className="flex justify-center gap-4 pt-4">
          <button className="btn btn-primary flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Custom Profile
          </button>
          <button
            onClick={scrollToExamples}
            className="btn btn-secondary flex items-center gap-2"
          >
            <User className="h-4 w-4" />
            Example Profiles
            <ChevronDown className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Section 1: Custom Profile Form */}
      <section className="card space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-xl flex items-center justify-center">
            <Upload className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Create Your Custom Profile</h2>
            <p className="text-sm text-gray-500">Tell us about yourself and your goals</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name
            </label>
            <input
              type="text"
              className="input"
              value={customProfile.name}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, name: e.target.value })
              }
              placeholder="e.g., John Smith"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Role
            </label>
            <input
              type="text"
              className="input"
              value={customProfile.current_role}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, current_role: e.target.value })
              }
              placeholder="e.g., Marketing Manager"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Role
            </label>
            <input
              type="text"
              className="input"
              value={customProfile.target_role}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, target_role: e.target.value })
              }
              placeholder="e.g., AI Product Manager"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry
            </label>
            <input
              type="text"
              className="input"
              value={customProfile.industry}
              onChange={(e) =>
                setCustomProfile({ ...customProfile, industry: e.target.value })
              }
              placeholder="e.g., Healthcare"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Years of Experience
            </label>
            <input
              type="number"
              className="input"
              value={customProfile.experience_years}
              onChange={(e) =>
                setCustomProfile({
                  ...customProfile,
                  experience_years: e.target.value,
                })
              }
              placeholder="e.g., 5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              AI Exposure Level
            </label>
            <select
              className="input"
              value={customProfile.ai_exposure_level}
              onChange={(e) =>
                setCustomProfile({
                  ...customProfile,
                  ai_exposure_level: e.target.value,
                })
              }
            >
              <option value="None">None</option>
              <option value="Basic">Basic</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Learning Intent
          </label>
          <textarea
            className="input min-h-[100px]"
            value={customProfile.learning_intent}
            onChange={(e) =>
              setCustomProfile({
                ...customProfile,
                learning_intent: e.target.value,
              })
            }
            placeholder="What do you want to achieve? What skills do you want to develop?"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Job Description <span className="text-red-500">*</span>
          </label>
          <textarea
            className="input min-h-[150px]"
            value={targetJD}
            onChange={(e) => setTargetJD(e.target.value)}
            placeholder="Paste the job description for your target role here..."
          />
          <p className="text-xs text-gray-500 mt-1">
            The more detailed the JD, the better the skill gap analysis.
          </p>
        </div>

        <div className="flex justify-end pt-4">
          <button
            onClick={handleCustomContinue}
            disabled={!isCustomValid}
            className={`btn flex items-center gap-2 text-lg px-8 py-3 ${
              isCustomValid
                ? 'btn-primary'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Continue to Analysis
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </section>

      {/* Divider */}
      <div className="flex items-center gap-4">
        <div className="flex-1 h-px bg-gray-200" />
        <span className="text-gray-400 font-medium px-4">OR</span>
        <div className="flex-1 h-px bg-gray-200" />
      </div>

      {/* Section 2: Example Profiles */}
      <section id="example-profiles" className="scroll-mt-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-xl flex items-center justify-center">
            <User className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Choose an Example Profile</h2>
            <p className="text-sm text-gray-500">Select from pre-defined profiles with realistic backgrounds</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center gap-2 text-gray-500">
              <div className="w-5 h-5 border-2 border-gray-300 border-t-indigo-500 rounded-full animate-spin" />
              Loading profiles...
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {profiles?.map((profile: Profile) => (
              <ProfileCard
                key={profile.id}
                profile={profile}
                isSelected={selectedProfile === profile.id}
                onSelect={() => handleSelectProfile(profile.id)}
                onDoubleClick={() => handleDoubleClick(profile.id)}
              />
            ))}
          </div>
        )}
      </section>

      {/* Floating Continue button when example selected */}
      {selectedProfile && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
          <button
            onClick={handleExampleContinue}
            className="btn btn-primary flex items-center gap-2 text-lg px-8 py-4 shadow-xl hover:shadow-2xl transition-all"
          >
            Continue to Analysis
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}

      {/* Bottom padding when floating button is visible */}
      {selectedProfile && <div className="h-24" />}
    </div>
  )
}

interface ProfileCardProps {
  profile: Profile
  isSelected: boolean
  onSelect: () => void
  onDoubleClick: () => void
}

function ProfileCard({ profile, isSelected, onSelect, onDoubleClick }: ProfileCardProps) {
  const proficiencyLevel = getProficiencyLevel(profile.ai_exposure_level)

  return (
    <div
      onClick={onSelect}
      onDoubleClick={onDoubleClick}
      className={`card cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 ${
        isSelected
          ? 'border-2 border-indigo-500 ring-2 ring-indigo-100 shadow-lg'
          : 'hover:border-gray-200'
      }`}
    >
      {/* Header row: Archetype badge, Experience, AI Level */}
      <div className="flex items-center justify-between mb-4">
        <ArchetypeBadge archetype={profile.archetype} />
        <div className="flex items-center gap-3 text-sm text-gray-500">
          {profile.experience_years && (
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {profile.experience_years} yrs
            </span>
          )}
          <span className="flex items-center gap-1 font-medium text-indigo-600">
            <Sparkles className="h-4 w-4" />
            {proficiencyLevel} AI
          </span>
        </div>
      </div>

      {/* Name */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="h-6 w-6 text-indigo-600" />
        </div>
        <h3 className="font-semibold text-gray-900 text-xl">
          {profile.name}
        </h3>
      </div>

      {/* Journey: Point A → Point B */}
      <div className="bg-gray-50 rounded-lg p-4 mb-5">
        <div className="flex items-start gap-4">
          {/* Where You Are */}
          <div className="flex-1">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2 flex items-center gap-1">
              <Briefcase className="h-3.5 w-3.5" />
              Where you are
            </div>
            <div className="text-base font-medium text-gray-700">
              {profile.current_role}
            </div>
          </div>

          {/* Arrow */}
          <div className="pt-6">
            <JourneyArrow variant="icon" size="lg" />
          </div>

          {/* Where You're Going */}
          <div className="flex-1">
            <div className="text-xs uppercase tracking-wide text-gray-400 mb-2 flex items-center gap-1">
              <Target className="h-3.5 w-3.5" />
              Where you're going
            </div>
            <div className="text-base font-medium text-indigo-700">
              {profile.target_role}
            </div>
          </div>
        </div>
      </div>

      {/* Learning Intent */}
      {profile.learning_intent && (
        <p className="text-sm text-gray-600 italic mb-4 leading-relaxed">
          "{profile.learning_intent}"
        </p>
      )}

      {/* Technical Skills Tags */}
      {profile.current_profile?.technical_skills && profile.current_profile.technical_skills.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {profile.current_profile.technical_skills.map((skill, i) => (
            <span
              key={i}
              className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-md"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {/* Industry */}
      <div className="text-sm text-gray-500 border-t border-gray-100 pt-3 mt-auto">
        {profile.industry}
      </div>

      {/* Selection indicator */}
      {isSelected && (
        <div className="text-xs text-indigo-600 text-center mt-3 font-medium">
          Selected - Double-click or press Continue
        </div>
      )}
    </div>
  )
}
