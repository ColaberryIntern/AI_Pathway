import { Link } from 'react-router-dom'
import { Sparkles, Target, BookOpen, TrendingUp, ArrowRight } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="space-y-16">
      {/* Hero Section with gradient background */}
      <section className="relative py-16 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-sky-50" />

        {/* Subtle decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-indigo-100/50 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-gradient-to-tr from-sky-100/50 to-transparent rounded-full blur-3xl" />

        <div className="relative text-center space-y-6 max-w-4xl mx-auto">
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
          <div className="flex justify-center gap-4 pt-4">
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

      {/* How it works */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            How It Works
          </h2>
          <p className="text-gray-600">Four simple steps to your personalized AI learning journey</p>
        </div>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { icon: Sparkles, title: '1. Select Profile', description: 'Give your Profile or choose from 12 example profiles.' },
            { icon: Target, title: '2. Set Your Goal', description: 'Paste a target job description to define your learning destination.' },
            { icon: BookOpen, title: '3. Get Your Path', description: 'Our AI analyzes gaps and generates a 5-chapter personalized path.' },
            { icon: TrendingUp, title: '4. Learn & Grow', description: 'Complete chapters with hands-on exercises and track your progress.' },
          ].map((step, i) => (
            <div
              key={i}
              className="card text-center card-hover group"
            >
              <div className="w-14 h-14 bg-gradient-to-br from-indigo-100 to-sky-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <step.icon className="h-7 w-7 text-indigo-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2 text-gray-900">{step.title}</h3>
              <p className="text-gray-600">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="bg-gradient-to-br from-white to-slate-50 rounded-2xl p-8 space-y-8 border border-gray-100">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Powered by Advanced AI
          </h2>
          <p className="text-gray-600">Built on cutting-edge technology to deliver personalized learning experiences</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              title: 'Multi-Agent System',
              description: 'Specialized AI agents analyze your profile, parse job descriptions, identify gaps, and generate personalized content.',
              color: 'indigo',
            },
            {
              title: '186+ Skills Ontology',
              description: 'Based on a comprehensive GenAI skills ontology covering 22 domains from foundations to emerging AI capabilities.',
              color: 'sky',
            },
            {
              title: 'Industry-Specific',
              description: "Get learning content tailored to your industry whether it's healthcare, finance, marketing, or technology.",
              color: 'emerald',
            },
          ].map((feature, i) => (
            <div key={i} className="relative group">
              <div className={`absolute inset-0 bg-gradient-to-r from-${feature.color}-100 to-${feature.color}-50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity -z-10`} />
              <div className="p-4">
                <h3 className={`font-semibold text-lg mb-2 text-${feature.color}-600`}>
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="text-center py-12">
        <div className="max-w-2xl mx-auto space-y-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">
            Ready to start your AI learning journey?
          </h2>
          <p className="text-gray-600">
            Join thousands of professionals upskilling in AI. Your personalized path awaits.
          </p>
          <Link
            to="/profiles"
            className="btn btn-primary inline-flex items-center gap-2 text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-all"
          >
            Choose Your Profile
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
