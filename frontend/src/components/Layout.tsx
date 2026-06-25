import { useEffect } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { Brain, Home, User, BookOpen, Building2, Users } from 'lucide-react'
import MentorChat from './learning/MentorChat'

// Self-paced user-testing mode: when the URL has `?testlink=1` (or any
// truthy value), set localStorage so the rest of the SPA renders a clean
// kiosk view (no admin nav, no profile management). The flag persists for
// the rest of the browser session so the user keeps the clean view even
// when navigating between chapters and the dashboard. Cleared by visiting
// any URL with `?testlink=0` or by clearing site data.
const TESTLINK_FLAG = 'ai_pathway_testlink_mode'

function readTestLinkFlag(): boolean {
  if (typeof window === 'undefined') return false
  const params = new URLSearchParams(window.location.search)
  const fromUrl = params.get('testlink')
  if (fromUrl !== null) {
    const enabled = fromUrl !== '0' && fromUrl.toLowerCase() !== 'false'
    try {
      window.localStorage.setItem(TESTLINK_FLAG, enabled ? '1' : '0')
    } catch {
      // localStorage may be blocked; URL param still wins for this load
    }
    return enabled
  }
  try {
    return window.localStorage.getItem(TESTLINK_FLAG) === '1'
  } catch {
    return false
  }
}

export default function Layout() {
  const location = useLocation()
  const showMentor = location.pathname.startsWith('/learn/')
  const testLinkMode = readTestLinkFlag()

  // Re-evaluate when the URL changes (e.g., navigating between routes).
  // readTestLinkFlag already handles persistence via localStorage, but
  // calling it inside an effect ensures the flag is freshly seeded if a
  // tester pastes a new ?testlink URL while already in the SPA.
  useEffect(() => {
    readTestLinkFlag()
  }, [location.search])

  return (
    <div className="min-h-screen bg-gray-50">
      {!testLinkMode && (
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="flex items-center gap-2">
                  <Brain className="h-8 w-8 text-primary-600" />
                  <span className="text-xl font-bold text-gray-900">AI Pathway</span>
                </Link>
              </div>
              <div className="flex items-center gap-4">
                <Link
                  to="/"
                  className="flex items-center gap-1 text-gray-600 hover:text-primary-600"
                >
                  <Home className="h-5 w-5" />
                  <span>Home</span>
                </Link>
                <Link
                  to="/profiles"
                  className="flex items-center gap-1 text-gray-600 hover:text-primary-600"
                >
                  <User className="h-5 w-5" />
                  <span>Profiles</span>
                </Link>
                <Link
                  to="/dashboard/latest"
                  className="flex items-center gap-1 text-gray-600 hover:text-primary-600"
                >
                  <BookOpen className="h-5 w-5" />
                  <span>My Learning</span>
                </Link>
                <Link
                  to="/admin/enterprise-base-curriculum"
                  className="flex items-center gap-1 text-gray-600 hover:text-primary-600"
                >
                  <Building2 className="h-5 w-5" />
                  <span>Enterprise</span>
                </Link>
                <Link
                  to="/admin/organizations"
                  className="flex items-center gap-1 text-gray-600 hover:text-primary-600"
                >
                  <Users className="h-5 w-5" />
                  <span>Orgs</span>
                </Link>
              </div>
            </div>
          </div>
        </nav>
      )}
      {testLinkMode && (
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-center h-16 items-center gap-2">
              <Brain className="h-7 w-7 text-primary-600" />
              <span className="text-lg font-bold text-gray-900">AI Pathway</span>
            </div>
          </div>
        </nav>
      )}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      {showMentor && <MentorChat />}
    </div>
  )
}
