# API Reference

**Author:** Karun Swaroop
**Base URL:** `http://localhost:8000/api` (development)
**Production:** `https://ai-pathway-backend-761055070184.us-central1.run.app/api`

## Authentication

Currently, the API does not require authentication (POC phase).

## Endpoints

### Profiles

#### List All Profiles

```http
GET /api/profiles
```

**Response:**
```json
{
  "profiles": [
    {
      "id": "profile_01",
      "name": "Alex Rivera",
      "current_role": "Marketing Manager",
      "target_role": "AI Product Manager",
      "industry": "Consumer Goods / Retail Marketing",
      "years_experience": 10,
      "ai_exposure_level": "L1",
      "profile_type": "Career Switcher",
      "summary": "Marketing Manager with 10 years in consumer goods...",
      "technical_skills": ["SQL (basic)", "Analytics dashboards", "A/B testing"],
      "soft_skills": ["Stakeholder management", "Digital campaign leadership"],
      "ai_experience": "Uses ChatGPT for copy variants and ideation",
      "target_requirements": [
        "Own AI product roadmap: define vision, requirements, and success metrics",
        "Translate user needs into AI/ML features"
      ],
      "target_jd": "Own AI product roadmap..."
    }
  ]
}
```

#### Get Profile by ID

```http
GET /api/profiles/{profile_id}
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| profile_id | string | Profile identifier (e.g., "profile_01") |

**Response:** Same as single profile object above

---

### Analysis

#### Run Full Analysis

Executes the complete analysis pipeline: Profile → JD Parse → Gap Analysis → Path Generation

```http
POST /api/analysis/full
```

**Request Body:**
```json
{
  "profile_id": "profile_01",
  "target_jd": "Optional custom JD to override profile's default"
}
```

**Response:**
```json
{
  "analysis_id": "a4f9cc5c-a9ef-41b7-af7d-80dfa2b2e00a",
  "profile_id": "profile_01",
  "status": "completed",
  "state_a": {
    "skills": [
      {
        "skill_id": "S.DIG.1",
        "skill_name": "Web browsing & search fundamentals",
        "current_level": 2,
        "domain_id": "D.DIG"
      }
    ]
  },
  "state_b": {
    "skills": [
      {
        "skill_id": "S.DIG.1",
        "skill_name": "Web browsing & search fundamentals",
        "required_level": 3,
        "domain_id": "D.DIG"
      }
    ]
  },
  "gaps": [
    {
      "skill_id": "S.PRQ.1",
      "skill_name": "Command line basics",
      "domain_id": "D.PRQ",
      "current_level": 0,
      "required_level": 3,
      "gap": 3,
      "priority": 1
    }
  ],
  "learning_path": {
    "id": "a4f9cc5c-a9ef-41b7-af7d-80dfa2b2e00a",
    "title": "AI Product Skills for Marketing Managers",
    "description": "A structured learning path...",
    "chapters": [/* see Learning Paths section */]
  }
}
```

#### Parse Job Description

Extract skills from a job description without running full analysis.

```http
POST /api/analysis/parse-jd
```

**Request Body:**
```json
{
  "job_description": "We are looking for an AI Product Manager who can..."
}
```

**Response:**
```json
{
  "required_skills": [
    {
      "skill_id": "S.PRM.1",
      "skill_name": "Basic prompting",
      "required_level": 3,
      "confidence": 0.85
    }
  ]
}
```

#### Get Gap Analysis

```http
GET /api/analysis/gap/{analysis_id}
```

**Response:**
```json
{
  "gaps": [
    {
      "skill_id": "S.PRQ.1",
      "skill_name": "Command line basics",
      "domain_id": "D.PRQ",
      "domain_name": "Tech Prerequisites",
      "current_level": 0,
      "required_level": 3,
      "gap": 3,
      "priority": 1,
      "estimated_hours": 10
    }
  ],
  "summary": {
    "total_gaps": 5,
    "total_hours": 45,
    "top_domains": ["D.PRQ", "D.GOV", "D.EVL"]
  }
}
```

---

### Learning Paths

#### Get Learning Path

```http
GET /api/paths/{path_id}
```

**Response:**
```json
{
  "id": "a4f9cc5c-a9ef-41b7-af7d-80dfa2b2e00a",
  "profile_id": "profile_01",
  "title": "AI Product Skills for Marketing Managers in Consumer Goods",
  "description": "A structured learning path for marketing managers transitioning into AI product roles...",
  "total_hours": 14.5,
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Getting Started with Command Line for AI Projects",
      "skill_id": "S.PRQ.1",
      "skill_name": "Command line basics",
      "domain_id": "D.PRQ",
      "current_level": 0,
      "target_level": 1,
      "estimated_time_hours": 2.5,
      "learning_objectives": [
        "Understand the basic structure and commands of the command line interface",
        "Navigate directories and manage files using command line commands",
        "Execute basic scripts and programs from the command line"
      ],
      "core_concepts": [
        {
          "title": "Introduction to Command Line",
          "content": "Learn the purpose and benefits of using the command line in AI projects.",
          "examples": [
            "Using command line to quickly navigate project directories",
            "Executing Python scripts for data preprocessing"
          ]
        }
      ],
      "exercises": [
        {
          "id": "ex_1_1",
          "type": "hands-on",
          "title": "Hands-On: Navigating Directories",
          "description": "Practice navigating directories and managing files using command line commands.",
          "estimated_time_minutes": 30,
          "instructions": [
            "Open the command line interface on your computer",
            "Navigate to your home directory",
            "Create a new directory named 'AI_Projects'",
            "List all files and directories in your home directory"
          ]
        }
      ],
      "resources": [
        {
          "title": "Command Line Basics for Beginners",
          "type": "course",
          "source": "Codecademy",
          "url": "https://www.codecademy.com/learn/learn-the-command-line"
        }
      ]
    }
  ],
  "created_at": "2026-02-02T18:00:00Z"
}
```

#### Generate Learning Path

```http
POST /api/paths/generate
```

**Request Body:**
```json
{
  "profile_id": "profile_01",
  "gaps": [/* gap objects */],
  "num_chapters": 5
}
```

---

### Progress

#### Get Progress

```http
GET /api/progress/{path_id}
```

**Response:**
```json
{
  "path_id": "a4f9cc5c-a9ef-41b7-af7d-80dfa2b2e00a",
  "chapter_status": {
    "1": "completed",
    "2": "in_progress",
    "3": "not_started",
    "4": "not_started",
    "5": "not_started"
  },
  "completion_percentage": 30,
  "last_updated": "2026-02-02T19:00:00Z"
}
```

#### Create Progress

```http
POST /api/progress/{path_id}
```

**Response:**
```json
{
  "path_id": "a4f9cc5c-a9ef-41b7-af7d-80dfa2b2e00a",
  "chapter_status": {},
  "completion_percentage": 0,
  "created_at": "2026-02-02T18:00:00Z"
}
```

#### Update Progress

```http
PUT /api/progress/{path_id}
```

**Request Body:**
```json
{
  "chapter": 1,
  "status": "completed"
}
```

**Response:**
```json
{
  "path_id": "a4f9cc5c-a9ef-41b7-af7d-80dfa2b2e00a",
  "chapter_status": {
    "1": "completed"
  },
  "completion_percentage": 20,
  "last_updated": "2026-02-02T19:30:00Z"
}
```

---

### Ontology

#### Get Full Ontology

```http
GET /api/ontology/
```

**Response:**
```json
{
  "domains": [
    {
      "id": "D.DIG",
      "label": "Digital Literacy",
      "layer": "L.FOUNDATION",
      "description": "Fundamental digital skills required for AI work",
      "skills": [
        {
          "id": "S.DIG.1",
          "label": "Web browsing & search fundamentals",
          "description": "Ability to effectively search and navigate web resources",
          "prerequisites": []
        }
      ]
    }
  ],
  "layers": [
    {
      "id": "L.FOUNDATION",
      "label": "Foundation",
      "order": 1
    }
  ]
}
```

#### List Skills

```http
GET /api/ontology/skills
```

**Query Parameters:**
| Name | Type | Description |
|------|------|-------------|
| domain_id | string | Filter by domain (e.g., "D.PRM") |
| layer | string | Filter by layer (e.g., "L.APPLICATION") |

**Response:**
```json
{
  "skills": [
    {
      "id": "S.DIG.1",
      "label": "Web browsing & search fundamentals",
      "domain_id": "D.DIG",
      "layer": "L.FOUNDATION"
    }
  ],
  "total": 153
}
```

#### List Domains

```http
GET /api/ontology/domains
```

**Response:**
```json
{
  "domains": [
    {
      "id": "D.DIG",
      "label": "Digital Literacy",
      "layer": "L.FOUNDATION",
      "skill_count": 8
    }
  ],
  "total": 18
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid profile_id format",
    "details": {
      "field": "profile_id",
      "expected": "string matching pattern profile_\\d+"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `ANALYSIS_FAILED` | 500 | Analysis pipeline error |
| `LLM_ERROR` | 502 | LLM provider error |
| `RATE_LIMITED` | 429 | Too many requests |

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| `/api/analysis/full` | 10 requests/minute |
| `/api/paths/generate` | 10 requests/minute |
| All other endpoints | 100 requests/minute |

---

## Webhooks (Planned)

Future support for analysis completion webhooks:

```json
{
  "event": "analysis.completed",
  "data": {
    "analysis_id": "...",
    "path_id": "...",
    "status": "completed"
  },
  "timestamp": "2026-02-02T18:00:00Z"
}
```

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get profiles
profiles = requests.get(f"{BASE_URL}/profiles").json()

# Run analysis
analysis = requests.post(f"{BASE_URL}/analysis/full", json={
    "profile_id": "profile_01"
}).json()

# Get learning path
path = requests.get(f"{BASE_URL}/paths/{analysis['learning_path']['id']}").json()
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8000/api';

// Get profiles
const profiles = await fetch(`${BASE_URL}/profiles`).then(r => r.json());

// Run analysis
const analysis = await fetch(`${BASE_URL}/analysis/full`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ profile_id: 'profile_01' })
}).then(r => r.json());

// Get learning path
const path = await fetch(`${BASE_URL}/paths/${analysis.learning_path.id}`)
  .then(r => r.json());
```

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:

- Development: `http://localhost:8000/openapi.json`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
