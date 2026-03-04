import { Outlet, Link, useLocation } from 'react-router-dom'
import { Brain, Home, User, BookOpen } from 'lucide-react'
import MentorChat from './learning/MentorChat'

export default function Layout() {
  const location = useLocation()
  const showMentor = location.pathname.startsWith('/learn/')

  return (
    <div className="min-h-screen bg-gray-50">
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
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      {showMentor && <MentorChat />}
    </div>
  )
}
