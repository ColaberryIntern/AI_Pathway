# System Design - AI Pathway Tool

**Author:** Karun Swaroop
**Last Updated:** February 2026

## Overview

AI Pathway is a multi-agent AI system that generates personalized learning paths for professionals looking to develop AI/ML skills. The system analyzes a user's current profile, parses target job descriptions, identifies skill gaps, and generates customized learning content.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│                                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │   Home      │  │  Profile    │  │  Analysis   │  │  Learning   │       │
│   │   Page      │  │  Selection  │  │   Page      │  │   Path      │       │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│          │                │                │                │               │
│          └────────────────┴────────────────┴────────────────┘               │
│                                    │                                        │
│                         React + TanStack Query                              │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     │ HTTP/REST
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER (FastAPI)                            │
│                                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │  /profiles  │  │  /analysis  │  │   /paths    │  │  /progress  │       │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│          │                │                │                │               │
└──────────┼────────────────┼────────────────┼────────────────┼───────────────┘
           │                │                │                │
           ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                               │
│                                                                             │
│                         ┌─────────────────────┐                             │
│                         │    ORCHESTRATOR     │                             │
│                         │       AGENT         │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│   ┌───────────────┐      ┌───────────────┐      ┌───────────────┐          │
│   │   PROFILE     │      │   JD PARSER   │      │     GAP       │          │
│   │   ANALYZER    │      │     AGENT     │      │   ANALYZER    │          │
│   └───────────────┘      └───────────────┘      └───────────────┘          │
│                                    │                                        │
│                                    ▼                                        │
│                          ┌───────────────┐                                  │
│                          │     PATH      │                                  │
│                          │   GENERATOR   │                                  │
│                          └───────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
           │                         │                         │
           ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   LLM SERVICE   │       │   RAG SERVICE   │       │    DATABASE     │
│                 │       │                 │       │                 │
│  ┌───────────┐  │       │  ┌───────────┐  │       │  ┌───────────┐  │
│  │  Claude   │  │       │  │ ChromaDB  │  │       │  │  SQLite   │  │
│  │  (or GPT) │  │       │  │           │  │       │  │           │  │
│  └───────────┘  │       │  └───────────┘  │       │  └───────────┘  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

## Data Flow

### Analysis Pipeline

```
User Profile + Target JD
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: PROFILE ANALYSIS                    │
│                                                                 │
│  Input: User profile (name, role, experience, skills)           │
│  Process: Extract current skill levels from profile             │
│  Output: State A - Current skill assessment                     │
│                                                                 │
│  Skills mapped to ontology with proficiency levels (L0-L4)      │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: JD PARSING                          │
│                                                                 │
│  Input: Target job description text                             │
│  Process: Extract required skills and levels from JD            │
│  Output: State B - Required skill assessment                    │
│                                                                 │
│  Uses RAG to match JD requirements to ontology skills           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: GAP ANALYSIS                        │
│                                                                 │
│  Input: State A (current) + State B (required)                  │
│  Process: Calculate skill gaps (State B - State A)              │
│  Output: Prioritized list of skill gaps                         │
│                                                                 │
│  Gaps ranked by: importance, prerequisite order, time to learn  │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: PATH GENERATION                     │
│                                                                 │
│  Input: Skill gaps + User context (industry, learning style)    │
│  Process: Generate 5-chapter learning path                      │
│  Output: Complete learning path with chapters                   │
│                                                                 │
│  Each chapter includes:                                         │
│  - Learning objectives                                          │
│  - Core concepts with examples                                  │
│  - Hands-on exercises                                           │
│  - Curated resources (courses, articles, videos)                │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
    Learning Path
```

## Component Details

### 1. Frontend (React + TypeScript)

**Technology Stack:**
- React 18 with functional components and hooks
- TypeScript for type safety
- Vite for fast development and building
- Tailwind CSS for styling
- TanStack Query (React Query) for data fetching and caching
- React Router for navigation

**Key Components:**

| Component | Purpose |
|-----------|---------|
| `HomePage` | Landing page with hero section and feature overview |
| `ProfileSelectionPage` | Profile creation and example profile selection |
| `AnalysisPage` | Real-time analysis visualization with domain grid |
| `LearningPathPage` | Interactive chapter-based learning content |
| `DashboardPage` | Progress tracking and path management |
| `DomainGrid` | Visual representation of 18 skill domains |
| `DomainCard` | Individual domain card with state animations |

### 2. Backend (FastAPI)

**Technology Stack:**
- Python 3.11+
- FastAPI for high-performance async API
- Pydantic for data validation
- SQLAlchemy for ORM
- aiosqlite for async database operations

**API Structure:**

```
/api
├── /profiles
│   ├── GET /           # List all profiles
│   ├── GET /{id}       # Get profile by ID
│   └── POST /upload    # Upload custom profile
│
├── /analysis
│   ├── POST /full      # Run full analysis pipeline
│   ├── POST /parse-jd  # Parse job description only
│   └── GET /gap/{id}   # Get gap analysis results
│
├── /paths
│   ├── GET /{id}       # Get learning path
│   └── POST /generate  # Generate new path
│
├── /progress
│   ├── GET /{path_id}  # Get progress
│   └── PUT /{path_id}  # Update progress
│
└── /ontology
    ├── GET /           # Full ontology
    ├── GET /skills     # List skills
    └── GET /domains    # List domains
```

### 3. Multi-Agent System

The system uses specialized agents that work together:

```python
class BaseAgent:
    """Base class for all agents"""
    def __init__(self, llm_service, rag_service):
        self.llm = llm_service
        self.rag = rag_service

    async def execute(self, input_data) -> AgentResult:
        raise NotImplementedError
```

**Agent Responsibilities:**

| Agent | Input | Output | LLM Calls |
|-------|-------|--------|-----------|
| ProfileAnalyzer | User profile JSON | Skill assessments with levels | 1 |
| JDParser | Job description text | Required skills with levels | 1-2 |
| GapAnalyzer | State A + State B | Prioritized skill gaps | 1 |
| PathGenerator | Gaps + Context | 5-chapter learning path | 5+ |

### 4. RAG System (ChromaDB)

The RAG system stores and retrieves:
- Skills ontology (153+ skills)
- Domain descriptions
- Skill prerequisites
- Learning resources

**Collections:**
```
chroma_db/
├── skills_collection      # Skill definitions and metadata
├── domains_collection     # Domain descriptions
└── resources_collection   # Learning resources
```

**Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)

### 5. LLM Service

Abstraction layer supporting multiple providers:

```python
class LLMService:
    """Abstraction for LLM providers"""

    async def generate(self, prompt: str, system: str = None) -> str:
        if self.provider == "claude":
            return await self._call_claude(prompt, system)
        elif self.provider == "openai":
            return await self._call_openai(prompt, system)
```

**Supported Models:**
- Claude 3.5 Sonnet (default)
- GPT-4 Turbo

## Database Schema

```sql
-- Profiles table
CREATE TABLE profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    current_role TEXT,
    target_role TEXT,
    industry TEXT,
    years_experience INTEGER,
    ai_exposure_level TEXT,
    skills JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning paths table
CREATE TABLE learning_paths (
    id TEXT PRIMARY KEY,
    profile_id TEXT REFERENCES profiles(id),
    title TEXT,
    description TEXT,
    chapters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Progress tracking table
CREATE TABLE progress (
    id TEXT PRIMARY KEY,
    path_id TEXT REFERENCES learning_paths(id),
    chapter_status JSONB,  -- {"1": "completed", "2": "in_progress", ...}
    completion_percentage INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Skills Ontology Structure

```json
{
  "domains": [
    {
      "id": "D.PRM",
      "label": "Prompting & HITL",
      "layer": "L.APPLICATION",
      "skills": [
        {
          "id": "S.PRM.1",
          "label": "Basic prompting",
          "description": "Write clear instructions for LLMs",
          "proficiency_levels": {
            "L0": "No knowledge",
            "L1": "Can write simple prompts",
            "L2": "Understands prompt patterns",
            "L3": "Designs complex prompts",
            "L4": "Expert in prompt engineering"
          },
          "prerequisites": ["S.DIG.1", "S.CTIC.1"]
        }
      ]
    }
  ]
}
```

## Security Considerations

1. **API Security**
   - CORS configuration for allowed origins
   - Rate limiting on analysis endpoints
   - Input validation with Pydantic

2. **Data Privacy**
   - No PII stored beyond session
   - API keys stored in environment variables
   - HTTPS enforced in production

3. **LLM Safety**
   - System prompts prevent harmful content generation
   - Output validation before returning to client

## Scalability

### Current Architecture (POC)
- Single instance deployment
- SQLite database
- In-memory ChromaDB

### Production Architecture (Planned)
- Kubernetes deployment with autoscaling
- PostgreSQL with read replicas
- Persistent ChromaDB cluster
- Redis for caching
- CDN for static assets

## Performance Optimizations

1. **Frontend**
   - React Query caching
   - Code splitting with lazy loading
   - Optimistic updates for progress

2. **Backend**
   - Async operations throughout
   - Connection pooling
   - Response streaming for long operations

3. **LLM Calls**
   - Parallel agent execution where possible
   - Caching of common queries
   - Streaming responses for UI feedback

## Deployment Architecture (GCP)

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Cloud Run                           │   │
│  │                                                      │   │
│  │  ┌─────────────────┐     ┌─────────────────┐        │   │
│  │  │    Frontend     │     │    Backend      │        │   │
│  │  │   (Container)   │────▶│   (Container)   │        │   │
│  │  └─────────────────┘     └─────────────────┘        │   │
│  │                                  │                   │   │
│  └──────────────────────────────────┼───────────────────┘   │
│                                     │                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Artifact Registry                       │   │
│  │    (Docker images: frontend:v1, backend:v3)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

### Frontend
```typescript
// Global error boundary
// React Query retry logic
// User-friendly error messages
```

### Backend
```python
# Custom exception handlers
# Structured error responses
# Logging with correlation IDs
```

## Monitoring (Planned)

- **Metrics**: Request latency, error rates, LLM costs
- **Logging**: Structured JSON logs to Cloud Logging
- **Tracing**: OpenTelemetry for distributed tracing
- **Alerting**: PagerDuty integration for critical errors

## Future Enhancements

1. **Assessment System**
   - Pre-path skill assessment quizzes
   - Post-chapter knowledge checks
   - Adaptive difficulty based on performance

2. **Social Features**
   - Learning cohorts
   - Progress sharing
   - Peer discussions

3. **Content Integration**
   - Direct course enrollment
   - Video embedding
   - Interactive coding exercises

4. **Analytics**
   - Learning analytics dashboard
   - Skill progression tracking
   - Time-to-competency metrics
