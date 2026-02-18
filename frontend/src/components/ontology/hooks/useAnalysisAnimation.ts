import { useState, useEffect, useMemo } from 'react'

// All domain IDs for sweep animation
const ALL_DOMAINS = [
  'D.DIG', 'D.CTIC', 'D.FND', 'D.PRM', 'D.RAG', 'D.AGT',
  'D.MOD', 'D.MUL', 'D.EVL', 'D.SEC', 'D.OPS', 'D.TOOL',
  'D.PRQ', 'D.GOV', 'D.DOM', 'D.PRD', 'D.COM', 'D.LRN',
]

// Default domains when no profile data is available
const DEFAULT_CURRENT_DOMAINS = ['D.DIG', 'D.CTIC', 'D.FND']
const DEFAULT_TARGET_DOMAINS = ['D.PRM', 'D.EVL', 'D.GOV', 'D.PRD']

interface AnimationFrame {
  highlightedDomains: string[]
  activeDomain: string | null
  completedDomains: string[]
  delay: number // ms from animation start
}

export interface ProfileDomains {
  currentDomains: string[] // domains the user already has skills in
  targetDomains: string[]  // domains from expected skill gaps
}

/**
 * Build a personalized animation sequence from profile domains.
 *
 * Step 0 (0-3s)  — Profile Analysis: highlights the user's current skill domains
 * Step 1 (3-6s)  — JD Parsing: highlights the user's target gap domains
 * Step 2 (6-9s)  — Gap Analysis: sweeps all 18 domains
 * Step 3 (9-12s) — Path Generation: spotlights target domains one by one
 */
function buildSequence(profileDomains?: ProfileDomains): AnimationFrame[] {
  const current = profileDomains?.currentDomains?.length
    ? profileDomains.currentDomains
    : DEFAULT_CURRENT_DOMAINS
  const target = profileDomains?.targetDomains?.length
    ? profileDomains.targetDomains
    : DEFAULT_TARGET_DOMAINS

  const frames: AnimationFrame[] = []

  // === Step 0: Profile Analysis (0-3s) ===
  // Reveal current-skill domains one at a time
  const step0Domains = current.slice(0, 5) // cap at 5 for timing
  const step0Interval = Math.min(500, 2000 / Math.max(step0Domains.length, 1))
  step0Domains.forEach((domain, i) => {
    frames.push({
      highlightedDomains: step0Domains.slice(0, i),
      activeDomain: domain,
      completedDomains: [],
      delay: i * step0Interval,
    })
  })
  // Settle: mark them as completed
  frames.push({
    highlightedDomains: [],
    activeDomain: null,
    completedDomains: [...step0Domains],
    delay: 2500,
  })

  // === Step 1: JD Parsing (3-6s) ===
  // Reveal target gap domains one at a time
  const step1Domains = target.slice(0, 5)
  const step1Interval = Math.min(500, 2000 / Math.max(step1Domains.length, 1))
  const completedAfterStep0 = [...step0Domains]
  step1Domains.forEach((domain, i) => {
    frames.push({
      highlightedDomains: step1Domains.slice(0, i),
      activeDomain: domain,
      completedDomains: completedAfterStep0,
      delay: 3000 + i * step1Interval,
    })
  })
  // Settle: mark all as completed
  const completedAfterStep1 = [...new Set([...completedAfterStep0, ...step1Domains])]
  frames.push({
    highlightedDomains: [],
    activeDomain: null,
    completedDomains: completedAfterStep1,
    delay: 5500,
  })

  // === Step 2: Gap Analysis (6-9s) ===
  // Fast sweep through ALL domains
  ALL_DOMAINS.forEach((domain, i) => {
    frames.push({
      highlightedDomains: ALL_DOMAINS.slice(0, i),
      activeDomain: domain,
      completedDomains: completedAfterStep1,
      delay: 6000 + i * 150,
    })
  })
  frames.push({
    highlightedDomains: [],
    activeDomain: null,
    completedDomains: ALL_DOMAINS.slice(),
    delay: 8700,
  })

  // === Step 3: Path Generation (9-12s) ===
  // Spotlight target domains one by one (these are likely in the path)
  const step3Domains = target.slice(0, 5)
  step3Domains.forEach((domain, i) => {
    frames.push({
      highlightedDomains: [],
      activeDomain: domain,
      completedDomains: ALL_DOMAINS.slice(),
      delay: 9000 + i * 500,
    })
  })
  // Final settle
  frames.push({
    highlightedDomains: [],
    activeDomain: null,
    completedDomains: ALL_DOMAINS.slice(),
    delay: 11500,
  })

  return frames
}

interface UseAnalysisAnimationResult {
  highlightedDomains: string[]
  activeDomain: string | null
  completedDomains: string[]
  selectedDomains: { domainId: string; chapterNum: number }[]
  isAnimating: boolean
}

export function useAnalysisAnimation(
  isRunning: boolean,
  profileDomains?: ProfileDomains,
): UseAnalysisAnimationResult {
  const sequence = useMemo(() => buildSequence(profileDomains), [profileDomains])

  const [frameIndex, setFrameIndex] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const [startTime, setStartTime] = useState<number | null>(null)

  // Reset animation when it starts
  useEffect(() => {
    if (isRunning) {
      setFrameIndex(0)
      setIsAnimating(true)
      setStartTime(Date.now())
    } else {
      setIsAnimating(false)
      setStartTime(null)
    }
  }, [isRunning])

  // Progress through animation frames
  useEffect(() => {
    if (!isRunning || !startTime) return

    const checkFrame = () => {
      const elapsed = Date.now() - startTime

      // Find the current frame based on elapsed time
      let newFrameIndex = 0
      for (let i = sequence.length - 1; i >= 0; i--) {
        if (elapsed >= sequence[i].delay) {
          newFrameIndex = i
          break
        }
      }

      if (newFrameIndex !== frameIndex) {
        setFrameIndex(newFrameIndex)
      }
    }

    const interval = setInterval(checkFrame, 50) // Check every 50ms for smooth updates
    return () => clearInterval(interval)
  }, [isRunning, startTime, frameIndex, sequence])

  // Get current frame data
  const currentFrame = sequence[frameIndex] || sequence[0]

  // Show preview chapter badges once animation reaches Step 3 (Path Generation).
  // These use the profile's target gap domains — which are dramatically different
  // per profile — creating visible differentiation during the animation.
  // Real chapter-to-domain mapping replaces these on the completion page.
  const inStep3 = isAnimating && currentFrame.delay >= 9000
  const selectedDomains: { domainId: string; chapterNum: number }[] =
    inStep3 && profileDomains?.targetDomains?.length
      ? profileDomains.targetDomains.slice(0, 5).map((d, i) => ({
          domainId: d,
          chapterNum: i + 1,
        }))
      : []

  return {
    highlightedDomains: currentFrame.highlightedDomains,
    activeDomain: currentFrame.activeDomain,
    completedDomains: currentFrame.completedDomains,
    selectedDomains,
    isAnimating,
  }
}

export default useAnalysisAnimation
