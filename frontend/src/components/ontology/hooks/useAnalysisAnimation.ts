import { useState, useEffect } from 'react'

// All domain IDs for sweep animation
const ALL_DOMAINS = [
  'D.DIG', 'D.CTIC', 'D.FND', 'D.PRM', 'D.RAG', 'D.AGT',
  'D.MOD', 'D.MUL', 'D.EVL', 'D.SEC', 'D.OPS', 'D.TOOL',
  'D.PRQ', 'D.GOV', 'D.DOM', 'D.PRD', 'D.COM', 'D.LRN',
]

// Animation sequence tied to analysis steps
// Each step ~3 seconds, with animations within each step
interface AnimationFrame {
  highlightedDomains: string[]
  activeDomain: string | null
  completedDomains: string[]
  delay: number // ms from animation start
}

const ANIMATION_SEQUENCE: AnimationFrame[] = [
  // === Step 0: Profile Analysis (0-3s) ===
  // Highlight foundation domains the user likely has
  { highlightedDomains: [], activeDomain: 'D.DIG', completedDomains: [], delay: 0 },
  { highlightedDomains: ['D.DIG'], activeDomain: 'D.CTIC', completedDomains: [], delay: 500 },
  { highlightedDomains: ['D.DIG', 'D.CTIC'], activeDomain: 'D.FND', completedDomains: [], delay: 1000 },
  { highlightedDomains: [], activeDomain: null, completedDomains: ['D.DIG', 'D.CTIC', 'D.FND'], delay: 2500 },

  // === Step 1: JD Parsing (3-6s) ===
  // Highlight application domains from job requirements
  { highlightedDomains: [], activeDomain: 'D.PRM', completedDomains: ['D.DIG', 'D.CTIC', 'D.FND'], delay: 3000 },
  { highlightedDomains: ['D.PRM'], activeDomain: 'D.EVL', completedDomains: ['D.DIG', 'D.CTIC', 'D.FND'], delay: 3500 },
  { highlightedDomains: ['D.PRM', 'D.EVL'], activeDomain: 'D.GOV', completedDomains: ['D.DIG', 'D.CTIC', 'D.FND'], delay: 4000 },
  { highlightedDomains: ['D.PRM', 'D.EVL', 'D.GOV'], activeDomain: 'D.PRD', completedDomains: ['D.DIG', 'D.CTIC', 'D.FND'], delay: 4500 },
  { highlightedDomains: [], activeDomain: null, completedDomains: ['D.DIG', 'D.CTIC', 'D.FND', 'D.PRM', 'D.EVL', 'D.GOV', 'D.PRD'], delay: 5500 },

  // === Step 2: Gap Analysis (6-9s) ===
  // Sweep through ALL domains quickly
  ...ALL_DOMAINS.map((domain, i) => ({
    highlightedDomains: ALL_DOMAINS.slice(0, i),
    activeDomain: domain,
    completedDomains: ['D.DIG', 'D.CTIC', 'D.FND', 'D.PRM', 'D.EVL', 'D.GOV', 'D.PRD'],
    delay: 6000 + (i * 150), // 150ms per domain = 2.7s total
  })),
  {
    highlightedDomains: [],
    activeDomain: null,
    completedDomains: ALL_DOMAINS.slice(),
    delay: 8700
  },

  // === Step 3: Path Generation (9-12s) ===
  // Show likely learning path chapters (animated selection)
  {
    highlightedDomains: [],
    activeDomain: 'D.PRM',
    completedDomains: ALL_DOMAINS.slice(),
    delay: 9000
  },
  {
    highlightedDomains: [],
    activeDomain: 'D.TOOL',
    completedDomains: ALL_DOMAINS.slice(),
    delay: 9500
  },
  {
    highlightedDomains: [],
    activeDomain: 'D.EVL',
    completedDomains: ALL_DOMAINS.slice(),
    delay: 10000
  },
  {
    highlightedDomains: [],
    activeDomain: 'D.RAG',
    completedDomains: ALL_DOMAINS.slice(),
    delay: 10500
  },
  {
    highlightedDomains: [],
    activeDomain: 'D.GOV',
    completedDomains: ALL_DOMAINS.slice(),
    delay: 11000
  },
  // Final state: all complete, path domains selected
  {
    highlightedDomains: [],
    activeDomain: null,
    completedDomains: ALL_DOMAINS.slice(),
    delay: 11500
  },
]

interface UseAnalysisAnimationResult {
  highlightedDomains: string[]
  activeDomain: string | null
  completedDomains: string[]
  selectedDomains: { domainId: string; chapterNum: number }[]
  isAnimating: boolean
}

export function useAnalysisAnimation(isRunning: boolean): UseAnalysisAnimationResult {
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
      for (let i = ANIMATION_SEQUENCE.length - 1; i >= 0; i--) {
        if (elapsed >= ANIMATION_SEQUENCE[i].delay) {
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
  }, [isRunning, startTime, frameIndex])

  // Get current frame data
  const currentFrame = ANIMATION_SEQUENCE[frameIndex] || ANIMATION_SEQUENCE[0]

  // No chapter badges during animation — actual chapter-to-domain
  // mapping is shown on the completion page using real API data.
  const selectedDomains: { domainId: string; chapterNum: number }[] = []

  return {
    highlightedDomains: currentFrame.highlightedDomains,
    activeDomain: currentFrame.activeDomain,
    completedDomains: currentFrame.completedDomains,
    selectedDomains,
    isAnimating,
  }
}

export default useAnalysisAnimation
