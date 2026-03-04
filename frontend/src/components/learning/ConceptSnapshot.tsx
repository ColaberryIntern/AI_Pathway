import { Zap } from 'lucide-react'

interface ConceptSnapshotProps {
  snapshot: string
}

export default function ConceptSnapshot({ snapshot }: ConceptSnapshotProps) {
  return (
    <section className="card border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-white">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-indigo-100">
          <Zap className="h-5 w-5 text-indigo-600" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">Concept Snapshot</h2>
      </div>
      <p className="text-gray-800 text-base leading-relaxed font-medium">
        {snapshot}
      </p>
    </section>
  )
}
