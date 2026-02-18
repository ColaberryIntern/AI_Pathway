import React, { useState } from 'react';
import { ChevronDown, ChevronRight, CheckCircle, AlertCircle } from 'lucide-react';

const ArchitectureDiagram = () => {
  const [expandedPhases, setExpandedPhases] = useState({
    phase1: true,
    phase2: false,
    phase3: false,
    phase4: false,
    phase5: false,
    phase6: false
  });

  const togglePhase = (phase) => {
    setExpandedPhases(prev => ({
      ...prev,
      [phase]: !prev[phase]
    }));
  };

  const phases = [
    {
      id: 'phase1',
      title: 'Phase 1: Core Data Foundation',
      color: 'bg-blue-50 border-blue-300',
      headerColor: 'bg-blue-100',
      chunks: [
        {
          id: '1.1',
          title: 'AI Skills Ontology Development',
          description: 'Create comprehensive AI skills taxonomy with hierarchies',
          qualityCheck: 'Can you map 10 different JDs to this ontology and extract meaningful skill requirements?',
          deliverable: 'JSON/structured skill taxonomy'
        },
        {
          id: '1.2',
          title: 'Skill Proficiency Rubric',
          description: 'Define proficiency levels (L0-L4) for each skill category',
          qualityCheck: 'Test with 3 sample personas - can you clearly place them at different levels?',
          deliverable: 'Scoring rubric document'
        }
      ]
    },
    {
      id: 'phase2',
      title: 'Phase 2: Input Processing & State Extraction',
      color: 'bg-green-50 border-green-300',
      headerColor: 'bg-green-100',
      chunks: [
        {
          id: '2.1',
          title: 'User Intent Capture',
          description: 'Design intake form for user context, role, industry, and intent',
          qualityCheck: 'Does this give enough context to personalize the path?',
          deliverable: 'Form design + data model'
        },
        {
          id: '2.2',
          title: 'State B JD Parser',
          description: 'LLM-powered analyzer to extract skills from job descriptions',
          qualityCheck: 'Test on 5 diverse JDs - does it extract 80%+ of required skills?',
          deliverable: 'JD parsing service with structured output'
        },
        {
          id: '2.3',
          title: 'LinkedIn Profile Parser',
          description: 'Extract professional context from PDF (role, industry, experience)',
          qualityCheck: 'Test on 10 PDFs - accuracy rate on key fields?',
          deliverable: 'PDF parsing service'
        },
        {
          id: '2.4',
          title: 'State A Assessment Quiz Generator',
          description: 'Dynamic quiz based on State B requirements with adaptive questioning',
          qualityCheck: 'Do quiz results correlate with actual skill levels when tested?',
          deliverable: 'Quiz generation engine + question bank'
        }
      ]
    },
    {
      id: 'phase3',
      title: 'Phase 3: Gap Analysis & Path Generation',
      color: 'bg-purple-50 border-purple-300',
      headerColor: 'bg-purple-100',
      chunks: [
        {
          id: '3.1',
          title: 'Skill Gap Calculator',
          description: 'Map State A → State B differences with priority weighting',
          qualityCheck: 'Generate gap analysis for 3 test personas - does it make intuitive sense?',
          deliverable: 'Gap analysis algorithm'
        },
        {
          id: '3.2',
          title: 'Learning Path Generator (5 Chapters)',
          description: 'Generate personalized curriculum with progressive skill building',
          qualityCheck: 'See Phase 4 - Multi-layer validation system',
          deliverable: 'Curriculum generation engine'
        },
        {
          id: '3.3',
          title: 'Hands-on Project Designer',
          description: 'Generate domain-specific exercises and capstone projects',
          qualityCheck: 'Are projects clearly scoped and achievable?',
          deliverable: 'Project template generator'
        }
      ]
    },
    {
      id: 'phase4',
      title: 'Phase 4: Quality Validation System ⭐',
      color: 'bg-red-50 border-red-300',
      headerColor: 'bg-red-100',
      chunks: [
        {
          id: '4.1',
          title: 'Path Validation Framework',
          description: 'Multi-layer validation: Expert review, persona testing, learning science checks',
          qualityCheck: 'A) Expert review of first 7-20 paths\nB) Simulated persona testing (10-15 personas)\nC) Learning science validation\nD) A/B comparison\nE) Outcome tracking',
          deliverable: 'Validation rubric + scoring system',
          critical: true
        }
      ]
    },
    {
      id: 'phase5',
      title: 'Phase 5: Course Content & Delivery',
      color: 'bg-yellow-50 border-yellow-300',
      headerColor: 'bg-yellow-100',
      chunks: [
        {
          id: '5.1',
          title: 'Content Aggregation Engine',
          description: 'Map curriculum to curated learning resources (updated periodically)',
          qualityCheck: 'Can you find quality resources for 90% of common skills?',
          deliverable: 'Content library + matching algorithm'
        },
        {
          id: '5.2',
          title: 'Progress Tracking & Adaptation',
          description: 'Monitor completion, quiz scores, project submissions, and struggle indicators',
          qualityCheck: 'Does tracking data accurately reflect learning?',
          deliverable: 'Progress tracking system'
        },
        {
          id: '5.3',
          title: 'Re-assessment & Next Level',
          description: 'Support iterative deepening after completing 5 chapters',
          qualityCheck: 'Does the next level properly build on previous?',
          deliverable: 'Re-generation logic'
        }
      ]
    },
    {
      id: 'phase6',
      title: 'Phase 6: Application Architecture',
      color: 'bg-indigo-50 border-indigo-300',
      headerColor: 'bg-indigo-100',
      chunks: [
        {
          id: '6.1',
          title: 'System Design',
          description: 'Frontend (React), Backend (Node.js/Python), AI Layer (LLM integration)',
          qualityCheck: 'Can handle concurrent users and integrate all components?',
          deliverable: 'Full stack architecture'
        },
        {
          id: '6.2',
          title: 'Data Models',
          description: 'User, Goal, LearningPath, Progress schemas',
          qualityCheck: 'Supports all required queries and relationships?',
          deliverable: 'Database schema + API design'
        }
      ]
    }
  ];

  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-gray-50">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Personalized AI Learning Path App
        </h1>
        <h2 className="text-xl text-gray-600">Solution Architecture & Flow</h2>
        <div className="mt-4 p-4 bg-white rounded-lg shadow inline-block">
          <p className="text-sm text-gray-700">
            <strong>Goal:</strong> Take users from State A (current AI skills) → State B (target job/role)
            <br />
            <strong>Output:</strong> 5 personalized chapters with domain-specific hands-on projects
          </p>
        </div>
      </div>

      {/* Flow Arrow */}
      <div className="mb-6 flex items-center justify-center">
        <div className="text-center px-4 py-2 bg-gray-200 rounded-lg font-semibold text-gray-700">
          User Input
        </div>
        <div className="mx-2 text-2xl text-gray-400">→</div>
        <div className="text-center px-4 py-2 bg-gray-200 rounded-lg font-semibold text-gray-700">
          Processing
        </div>
        <div className="mx-2 text-2xl text-gray-400">→</div>
        <div className="text-center px-4 py-2 bg-gray-200 rounded-lg font-semibold text-gray-700">
          Validation
        </div>
        <div className="mx-2 text-2xl text-gray-400">→</div>
        <div className="text-center px-4 py-2 bg-gray-200 rounded-lg font-semibold text-gray-700">
          Delivery
        </div>
      </div>

      {/* Phases */}
      <div className="space-y-4">
        {phases.map((phase) => (
          <div key={phase.id} className={`border-2 rounded-lg ${phase.color} overflow-hidden`}>
            {/* Phase Header */}
            <div
              className={`${phase.headerColor} p-4 cursor-pointer flex items-center justify-between hover:opacity-80 transition-opacity`}
              onClick={() => togglePhase(phase.id)}
            >
              <h3 className="text-lg font-bold text-gray-800 flex items-center">
                {expandedPhases[phase.id] ? <ChevronDown className="mr-2" /> : <ChevronRight className="mr-2" />}
                {phase.title}
              </h3>
              <span className="text-sm text-gray-600">
                {phase.chunks.length} chunk{phase.chunks.length > 1 ? 's' : ''}
              </span>
            </div>

            {/* Chunks */}
            {expandedPhases[phase.id] && (
              <div className="p-4 space-y-4">
                {phase.chunks.map((chunk, idx) => (
                  <div key={chunk.id} className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-bold text-gray-800 flex items-center">
                        <span className="bg-gray-200 rounded-full w-8 h-8 flex items-center justify-center text-sm mr-2">
                          {chunk.id}
                        </span>
                        {chunk.title}
                        {chunk.critical && (
                          <span className="ml-2 text-red-500 text-xs font-normal">(Critical)</span>
                        )}
                      </h4>
                    </div>
                    
                    <p className="text-gray-700 text-sm mb-3 ml-10">
                      {chunk.description}
                    </p>

                    <div className="ml-10 space-y-2">
                      {/* Quality Check */}
                      <div className="bg-green-50 border border-green-200 rounded p-3">
                        <div className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-semibold text-green-800 text-sm mb-1">Quality Check:</p>
                            <p className="text-green-700 text-sm whitespace-pre-line">{chunk.qualityCheck}</p>
                          </div>
                        </div>
                      </div>

                      {/* Deliverable */}
                      <div className="bg-blue-50 border border-blue-200 rounded p-3">
                        <div className="flex items-start">
                          <AlertCircle className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-semibold text-blue-800 text-sm mb-1">Deliverable:</p>
                            <p className="text-blue-700 text-sm">{chunk.deliverable}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Arrow to next chunk */}
                    {idx < phase.chunks.length - 1 && (
                      <div className="flex justify-center mt-3">
                        <div className="text-gray-400 text-xl">↓</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Development Timeline */}
      <div className="mt-8 p-6 bg-white rounded-lg shadow-lg">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Development Roadmap</h3>
        <div className="space-y-3">
          <div className="flex items-center">
            <div className="bg-blue-500 text-white px-3 py-1 rounded font-semibold text-sm w-32">Sprint 1</div>
            <div className="ml-4 text-gray-700">Phase 1 (Ontology) + Phase 2.1-2.2 (2-3 weeks)</div>
          </div>
          <div className="flex items-center">
            <div className="bg-green-500 text-white px-3 py-1 rounded font-semibold text-sm w-32">Sprint 2</div>
            <div className="ml-4 text-gray-700">Phase 2.3-2.4 + Phase 3.1 (2-3 weeks)</div>
          </div>
          <div className="flex items-center">
            <div className="bg-purple-500 text-white px-3 py-1 rounded font-semibold text-sm w-32">Sprint 3</div>
            <div className="ml-4 text-gray-700">Phase 3.2-3.3 + Phase 4 Validation (3-4 weeks)</div>
          </div>
          <div className="flex items-center">
            <div className="bg-yellow-500 text-white px-3 py-1 rounded font-semibold text-sm w-32">Sprint 4</div>
            <div className="ml-4 text-gray-700">Phase 5 + Phase 6 MVP (2-3 weeks)</div>
          </div>
          <div className="flex items-center">
            <div className="bg-indigo-500 text-white px-3 py-1 rounded font-semibold text-sm w-32">Sprint 5</div>
            <div className="ml-4 text-gray-700">Enhanced validation + Polish (2 weeks)</div>
          </div>
        </div>
      </div>

      {/* Key Features Box */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 rounded-lg shadow">
          <h4 className="font-bold mb-2">Differentiation</h4>
          <p className="text-sm">Domain-specific AI skills + industry integration (e.g., AI for Martech)</p>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-4 rounded-lg shadow">
          <h4 className="font-bold mb-2">Personalization</h4>
          <p className="text-sm">Dynamic path based on actual skill gaps, not generic curriculum</p>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-4 rounded-lg shadow">
          <h4 className="font-bold mb-2">Continuous Learning</h4>
          <p className="text-sm">Re-assessment after completion for next-level deepening</p>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureDiagram;