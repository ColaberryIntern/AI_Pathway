import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      {/* Hero Section - single page, clean */}
      <section className="relative py-16 px-4 sm:px-6 lg:px-8 overflow-hidden w-full max-w-4xl">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-sky-50 rounded-2xl" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-indigo-100/50 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-gradient-to-tr from-sky-100/50 to-transparent rounded-full blur-3xl" />

        <div className="relative text-center space-y-6 max-w-3xl mx-auto">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
            Your Personalized Path to{' '}
            <span className="bg-gradient-to-r from-indigo-600 to-sky-600 bg-clip-text text-transparent">
              AI Fluency
            </span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Get a customized learning path based on your current skills, target role,
            and industry. Powered by AI to help you master AI.
          </p>

          {/* Features - compact */}
          <div className="grid grid-cols-3 gap-4 pt-4 text-sm text-gray-600">
            <div className="p-3 bg-white/60 rounded-xl">
              <div className="font-semibold text-indigo-600 mb-1">Multi-Agent AI</div>
              Personalized skill gap analysis
            </div>
            <div className="p-3 bg-white/60 rounded-xl">
              <div className="font-semibold text-sky-600 mb-1">186+ Skills</div>
              Comprehensive GenAI ontology
            </div>
            <div className="p-3 bg-white/60 rounded-xl">
              <div className="font-semibold text-emerald-600 mb-1">Industry-Specific</div>
              Tailored to your role
            </div>
          </div>

          <div className="flex justify-center pt-4">
            <Link
              to="/profiles"
              className="btn btn-primary flex items-center gap-2 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all"
            >
              Get Started
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
