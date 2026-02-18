# AI Pathway Tool

**Author:** Karun Swaroop

A multi-agent AI system that generates **personalized AI learning paths** based on your current skills and career goals. Built with a modern React frontend and FastAPI backend, powered by Claude/OpenAI and RAG (Retrieval Augmented Generation).

## Features

- **Personalized Learning Paths** - AI analyzes your profile and target job to create custom 5-chapter learning journeys
- **153+ Skills Ontology** - Comprehensive GenAI skills taxonomy across 18 domains
- **Multi-Agent Architecture** - Specialized AI agents for profile analysis, JD parsing, gap analysis, and content generation
- **12 Example Profiles** - Pre-built personas across industries (Marketing, Healthcare, Finance, Legal, Education, etc.)
- **Progress Tracking** - Track chapter completion and skill development
- **Beautiful UI** - Modern, responsive interface with smooth animations

## Live Demo

- **Frontend**: https://ai-pathway-frontend-761055070184.us-central1.run.app
- **Backend API**: https://ai-pathway-backend-761055070184.us-central1.run.app

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key (or OpenAI)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│              React + TypeScript + Tailwind CSS                  │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│    │  Home    │  │ Profiles │  │ Analysis │  │ Learning │      │
│    │  Page    │  │  Page    │  │   Page   │  │   Path   │      │
│    └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  PROFILE      │   │  JD PARSER    │   │  GAP ANALYSIS │
│  ANALYZER     │   │  AGENT        │   │  AGENT        │
└───────────────┘   └───────────────┘   └───────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │  PATH         │
                    │  GENERATOR    │
                    └───────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  LLM     │   │  RAG     │   │ Database │
        │ (Claude) │   │(ChromaDB)│   │ (SQLite) │
        └──────────┘   └──────────┘   └──────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query |
| Backend | Python, FastAPI, Pydantic |
| LLM | Claude 3.5 Sonnet (or OpenAI GPT-4) |
| Vector DB | ChromaDB |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Deployment | Google Cloud Run, Artifact Registry |

## Project Structure

```
ai-pathway/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── agents/              # Multi-agent system
│   │   │   ├── orchestrator.py  # Coordinates all agents
│   │   │   ├── profile_analyzer.py
│   │   │   ├── jd_parser.py
│   │   │   ├── gap_analyzer.py
│   │   │   └── path_generator.py
│   │   ├── services/
│   │   │   ├── llm/             # LLM abstraction layer
│   │   │   └── rag/             # RAG with ChromaDB
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── data/
│   │       ├── ontology.json    # 153+ skills ontology
│   │       └── profiles/        # 12 example profiles
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ontology/        # Domain grid visualization
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── ProfileSelectionPage.tsx
│   │   │   ├── AnalysisPage.tsx
│   │   │   ├── LearningPathPage.tsx
│   │   │   └── DashboardPage.tsx
│   │   ├── services/api.ts      # API client
│   │   └── types/index.ts       # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/
│   ├── SYSTEM_DESIGN.md         # Architecture details
│   ├── FRONTEND_UI.md           # UI/UX documentation
│   ├── API_REFERENCE.md         # API documentation
│   └── ONTOLOGIES.md            # Skills ontology docs
│
└── deploy.sh                    # GCP deployment script
```

## 12 Example Profiles

| # | Name | Current Role | Target Role | Industry |
|---|------|--------------|-------------|----------|
| 1 | Alex Rivera | Marketing Manager | AI Product Manager | Consumer Goods |
| 2 | Bethany Chen | High School Teacher | AI Learning Designer | EdTech |
| 3 | Charles Patel | Legal Associate | AI Governance Scientist | Legal/RegTech |
| 4 | Dana Morales | Healthcare Data Analyst | Healthcare Data Scientist | Healthcare |
| 5 | Elena Brooks | Financial Analyst | AI Risk Analyst | Finance |
| 6 | Frank Nguyen | HR Manager | People Analytics Lead | HR |
| 7 | Grace Williams | VP Marketing | AI Marketing Strategist | Retail |
| 8 | Hank Thompson | VP Operations | AI Transformation Leader | Manufacturing |
| 9 | Irene Shah | CIO | Enterprise AI Leader | Insurance |
| 10 | John Miller | Software Developer | ML Engineer | Technology |
| 11 | Kelly Johnson | Content Specialist | Prompt Engineer | Marketing |
| 12 | Kevin Park | Automation Engineer | Robotics AI Engineer | Manufacturing |

## GenAI Skills Ontology

The system uses a comprehensive skills taxonomy:

- **153+ Skills** across 18 domains
- **5-Level Proficiency Scale**: L0 (None) → L4 (Expert)
- **7 Layers**: Foundation, Theory, Application, Tools, Tech Prerequisites, Domain, Soft/Strategy
- **Prerequisite Mapping**: Ensures logical learning progression

### Domains

| Layer | Domains |
|-------|---------|
| Foundation | Digital Literacy, Critical Thinking |
| Theory | AI Foundations |
| Application | Prompting & HITL, RAG Systems, Agents, Model Adaptation, Multimodal AI, Evaluation, Safety & Security, LLMOps |
| Tools | Tools & Frameworks |
| Tech Prerequisites | Tech Prerequisites |
| Domain | Governance, Domain Apps |
| Soft/Strategy | Product & UX, Communication, Learning & Adaptation |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all example profiles |
| GET | `/api/profiles/{id}` | Get profile details |
| POST | `/api/analysis/full` | Run full analysis pipeline |
| GET | `/api/paths/{id}` | Get learning path |
| PUT | `/api/progress/{path_id}` | Update chapter progress |
| GET | `/api/ontology/` | Get skills ontology |

See [API Reference](docs/API_REFERENCE.md) for complete documentation.

## Environment Variables

```env
# LLM Configuration
LLM_PROVIDER=claude              # claude or openai
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key

# Models
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4-turbo-preview

# Database
DATABASE_URL=sqlite+aiosqlite:///./ai_pathway.db

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# CORS (for deployment)
CORS_ORIGINS=["http://localhost:5173"]
```

## Deployment

The application is deployed on Google Cloud Run. See [deploy.sh](deploy.sh) for the deployment script.

```bash
# Build and deploy backend
cd backend
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/ai-pathway-486221/ai-pathway/backend:v1 .
docker push us-central1-docker.pkg.dev/ai-pathway-486221/ai-pathway/backend:v1
gcloud run deploy ai-pathway-backend --image ... --region us-central1

# Build and deploy frontend
cd frontend
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/ai-pathway-486221/ai-pathway/frontend:v1 .
docker push us-central1-docker.pkg.dev/ai-pathway-486221/ai-pathway/frontend:v1
gcloud run deploy ai-pathway-frontend --image ... --region us-central1
```

**Note**: When building on Apple Silicon, always use `--platform linux/amd64` for Cloud Run compatibility.

## Documentation

- [System Design](docs/SYSTEM_DESIGN.md) - Architecture and design decisions
- [Frontend UI](docs/FRONTEND_UI.md) - UI/UX documentation and component guide
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Ontologies](docs/ONTOLOGIES.md) - Skills ontology documentation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Claude](https://anthropic.com) by Anthropic
- Skills ontology developed by Colaberry
- UI inspired by modern design systems
