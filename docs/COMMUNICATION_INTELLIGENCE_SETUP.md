# Communication Intelligence Layer - Setup Guide

A complete guide for adding an automated email-to-Basecamp pipeline to any project. Ingests emails from specific senders, uses AI to classify intent and extract actionable items, creates/updates Basecamp topics and todos, and provides daily summaries.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Prerequisites](#2-prerequisites)
3. [Architecture](#3-architecture)
4. [Database Models](#4-database-models)
5. [Services](#5-services)
6. [API Routes](#6-api-routes)
7. [Configuration](#7-configuration)
8. [Gmail API Setup](#8-gmail-api-setup)
9. [Basecamp API Setup](#9-basecamp-api-setup)
10. [Deployment & Automation](#10-deployment--automation)
11. [Implementation Checklist](#11-implementation-checklist)

---

## 1. System Overview

### What It Does

Monitors email from specified senders, classifies each email using AI, extracts actionable todos, syncs them to Basecamp as topics and todolists, tracks completion, and generates daily summaries.

### Pipeline Flow

```
Gmail (monitored senders)
  |
  v
Email Ingestion Service
  - Fetches via Gmail API
  - Deduplicates by message_id
  - Stores in DB
  |
  v
Email Intelligence Service
  - AI classifies: project / task / discussion
  - Extracts: topic, priority, todos, owners
  - Confidence scoring
  |
  v
Priority Engine
  - Scores by: sender weight, keywords, thread length, AI priority
  - Filters out noise (score < threshold)
  |
  v
Thread Resolution Service
  - Checks if email thread already has a Basecamp topic
  - Existing thread -> append mode
  - New thread -> create mode
  |
  v
Todo Generation Service
  - Refines raw todos into atomic, actionable steps
  - Ensures each todo is assignable and measurable
  |
  v
Basecamp Service
  - Creates topics on message board
  - Creates todolists
  - Adds todos with assignees
  - Appends comments to existing topics
  |
  v
Feedback Service
  - Tracks todo completion rates
  - Detects recurring topics
  - Identifies stalled execution
  |
  v
Daily Summary Service
  - Generates digest via LLM
  - Active topics, pending todos, bottlenecks
```

---

## 2. Prerequisites

### APIs Required

| API | Purpose | Auth Method |
|-----|---------|-------------|
| Gmail API | Read emails from monitored senders | OAuth 2.0 (Desktop App) |
| Basecamp 4 API | Create topics, todolists, todos | Bearer token |
| LLM Provider | Classify emails, extract todos, generate summaries | API key (OpenAI/Claude/Vertex) |

### Tech Stack

- Python 3.11+
- FastAPI (async)
- SQLAlchemy (async, SQLite or PostgreSQL)
- httpx (async HTTP client for Basecamp)
- google-api-python-client (Gmail)

### Python Dependencies

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
httpx
```

---

## 3. Architecture

### File Structure

```
backend/
  app/
    models/
      email_thread.py           # Ingested email storage
      topic_thread_map.py       # Email-to-Basecamp mapping
      communication_feedback.py # Execution tracking
    services/
      email_ingestion_service.py      # Gmail API integration
      email_intelligence_service.py   # AI classification
      thread_resolution_service.py    # Thread continuity
      todo_generation_service.py      # Atomic todo creation
      basecamp_service.py             # Basecamp 4 REST client
      priority_engine.py              # Email scoring/filtering
      communication_feedback_service.py  # Completion tracking
      daily_summary_service.py        # Daily digest
      communication_orchestrator.py   # Pipeline coordinator
    api/
      routes/
        communication.py        # REST endpoints
    config.py                   # Add Basecamp/Gmail settings
  credentials/
    gmail_credentials.json      # OAuth client credentials
    gmail_token.json            # Auto-generated after first auth
    .gitignore                  # Prevents committing secrets
  .env                          # API tokens
```

### Safety Rules (Enforced in Code)

1. No duplicate Basecamp topics - TopicThreadMap enforces UNIQUE on email_thread_id
2. No duplicate email processing - processed flag + message_id uniqueness
3. Thread continuity - resolve_thread() always checks existing mapping first
4. AI output validation - confidence threshold, structured JSON schema
5. Idempotent operations - re-running pipeline on processed emails is a no-op

---

## 4. Database Models

### EmailThread

Stores every ingested email message.

```python
class EmailThread(Base):
    __tablename__ = "email_threads"

    id: str                    # UUID PK
    thread_id: str             # Gmail thread ID (indexed)
    message_id: str            # Gmail message ID (unique - dedup key)
    sender: str                # From address
    recipients: JSON           # [str] To addresses
    subject: str               # Email subject
    body: text                 # Email body (plain text)
    timestamp: datetime        # Email send time
    processed: bool            # Pipeline processed flag (default false)
    skipped: bool              # Skipped by priority filter (default false)
    raw_payload: JSON          # Full Gmail API response
    classified_data: JSON      # AI classification output
    created_at: datetime
```

### TopicThreadMap

1:1 mapping between Gmail threads and Basecamp topics. Prevents duplicate topics.

```python
class TopicThreadMap(Base):
    __tablename__ = "topic_thread_maps"

    id: str                        # UUID PK
    email_thread_id: str           # Gmail thread ID (unique, indexed)
    basecamp_topic_id: str         # Basecamp message/topic ID
    basecamp_todolist_id: str      # Basecamp todolist ID (nullable)
    status: str                    # "active" | "resolved" | "stalled"
    last_updated: datetime
    created_at: datetime
```

### CommunicationFeedback

Tracks execution metrics per topic.

```python
class CommunicationFeedback(Base):
    __tablename__ = "communication_feedback"

    id: str                        # UUID PK
    topic_thread_map_id: str       # FK to topic_thread_maps
    todos_created: int             # Total todos generated
    todos_completed: int           # Todos marked done
    is_recurring: bool             # Topic appeared 3+ times
    recurrence_count: int          # How many times
    last_activity: datetime
    created_at: datetime
```

---

## 5. Services

### Email Ingestion Service

**File:** `email_ingestion_service.py`

Connects to Gmail API, fetches emails from monitored senders, normalizes, and stores.

**Key functions:**
- `fetch_new_emails(db, lookback_hours=24)` - Fetch and store new emails
- `get_unprocessed(db)` - Get all unprocessed emails

**Configuration:**
```python
MONITORED_SENDERS = [
    "sender1@gmail.com",
    "sender2@gmail.com",
]
```

**Gmail query format:**
```python
sender_query = " OR ".join(f"from:{s}" for s in MONITORED_SENDERS)
query = f"({sender_query}) after:{unix_timestamp}"
```

### Email Intelligence Service

**File:** `email_intelligence_service.py`

Uses LLM to classify email intent and extract actionable items.

**System prompt instructs the LLM to:**
1. Classify type: project / task / discussion
2. Extract topic title (max 10 words)
3. Determine priority: high / medium / low
4. Extract 3-7 actionable todos (start with verb, assignable, measurable)
5. Identify owners
6. Assign confidence score (0.0-1.0)

**Output schema:**
```json
{
  "topic": "string",
  "type": "project | task | discussion",
  "priority": "high | medium | low",
  "todos": ["Verb + specific task 1", "Verb + specific task 2"],
  "owners": ["person name or email"],
  "confidence": 0.85
}
```

**Rules:**
- Discussion type with no action items = todos: []
- Maximum 7 todos per email
- Normalize vague language: "look into X" becomes "Research X and summarize findings"
- Extract implicit tasks from "we need to..." language

### Thread Resolution Service

**File:** `thread_resolution_service.py`

Maintains email-to-Basecamp continuity.

**Logic:**
- Query TopicThreadMap by email_thread_id
- If found: return existing mapping (append mode)
- If not found: return None (create mode)
- After creating new Basecamp topic: save mapping

### Todo Generation Service

**File:** `todo_generation_service.py`

Refines raw extracted todos into atomic, actionable steps.

**Rules:**
- Each todo starts with an action verb
- Completable by one person
- Clear done state
- Complex todos broken into 2-3 sub-steps
- Uses LLM for refinement if needed
- Cap at 7 todos per email

### Basecamp Service

**File:** `basecamp_service.py`

REST client for Basecamp 4 API.

**Functions:**
```python
# Topics (Message Board)
create_topic(title, content, project_id?) -> topic_id
append_comment(topic_id, content, project_id?) -> comment_id

# Todolists & Todos
create_todo_list(title, description?, project_id?) -> todolist_id
add_todo(todolist_id, content, assignee_ids?, project_id?) -> todo_id
add_todos(todolist_id, todos[], project_id?) -> [todo_id]

# People
get_people(project_id?) -> [{id, name, email}]
```

**Required headers:**
```python
{
    "Authorization": "Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Your App Name (your@email.com)",  # Required by Basecamp
}
```

**API URL format:** `https://3.basecampapi.com/{account_id}/buckets/{project_id}/...`

### Priority Engine

**File:** `priority_engine.py`

Scores emails to filter noise.

**Scoring formula:**
```
score = sender_weight * 3
      + keyword_weights (urgent=3, ASAP=3, blocker=3, important=1.5, FYI=-1)
      + priority_bonus (high=3, medium=1, low=-1)
      + actionable_bonus (num_todos * 0.5)
      + length_bonus (>1000 chars = +1)
      - discussion_penalty (no todos = -2)
```

**Threshold:** score >= 3.0 to create Basecamp items. Below threshold = skipped.

### Communication Feedback Service

**File:** `communication_feedback_service.py`

Tracks execution metrics.

**Detects:**
- Stalled topics: open todos > 7 days with no completion
- Recurring topics: same thread referenced 3+ times
- Bottlenecks: high todo count, low completion rate

### Daily Summary Service

**File:** `daily_summary_service.py`

Generates a daily digest using LLM.

**Input:** Stats, bottlenecks, recurring topics
**Output:** Markdown summary with: Active Topics, Pending Todos, Recurring Issues, Suggested Focus Areas

### Communication Orchestrator

**File:** `communication_orchestrator.py`

Coordinates the full pipeline.

**Pipeline:**
```python
async def run_pipeline(db):
    emails = await get_unprocessed(db)
    for email in emails:
        classified = await classify_and_extract(email)
        score = score_email(email, classified)
        if not should_process(score):
            mark_skipped(email)
            continue
        mapping = await resolve_thread(db, email.thread_id)
        todos = await generate_structured_todos(classified)
        if mapping:
            await basecamp.append_comment(mapping.topic_id, email.body)
            if todos and mapping.todolist_id:
                await basecamp.add_todos(mapping.todolist_id, [t.content for t in todos])
        else:
            topic_id = await basecamp.create_topic(classified.topic, email.body)
            todolist_id = await basecamp.create_todo_list(f"Tasks: {classified.topic}")
            await basecamp.add_todos(todolist_id, [t.content for t in todos])
            await create_mapping(db, email.thread_id, topic_id, todolist_id)
        await update_feedback(db, mapping.id, todos_created=len(todos))
        mark_processed(email)
```

---

## 6. API Routes

**File:** `communication.py`

Register with prefix `/communication`.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/communication/ingest` | Trigger Gmail fetch (param: `lookback_hours`) |
| POST | `/communication/process` | Run pipeline on unprocessed emails |
| POST | `/communication/run` | Ingest + process in one call |
| GET | `/communication/threads` | List all tracked threads with Basecamp links |
| GET | `/communication/threads/{id}` | Get thread detail with messages |
| GET | `/communication/summary` | Generate daily execution summary |
| GET | `/communication/feedback` | Get stats, bottlenecks, recurring topics |

---

## 7. Configuration

### Environment Variables (.env)

```env
# Communication Intelligence - Basecamp
BASECAMP_TOKEN=your_bearer_token_here
BASECAMP_ACCOUNT_ID=your_account_id
BASECAMP_PROJECT_ID=your_project_id

# Communication Intelligence - Gmail
GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json
GMAIL_TOKEN_PATH=credentials/gmail_token.json
```

### Config Class (config.py additions)

```python
# Communication Intelligence - Basecamp
basecamp_token: str = ""
basecamp_account_id: str = ""
basecamp_project_id: str = ""

# Communication Intelligence - Gmail
gmail_credentials_path: str = "credentials/gmail_credentials.json"
gmail_token_path: str = "credentials/gmail_token.json"
```

### Credentials Directory

```
backend/credentials/
  gmail_credentials.json   # OAuth client config (from Google Cloud Console)
  gmail_token.json         # Auto-generated after first auth
  .gitignore               # Contains: *\n!.gitignore
```

---

## 8. Gmail API Setup

### Step 1: Google Cloud Console

1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable the **Gmail API** (APIs & Services > Library > search "Gmail API" > Enable)
4. Go to **Credentials** > Create Credentials > **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **Internal** (for organization) or **External**
   - App name: your project name
   - Add your email as support email
6. Application type: **Desktop app**
7. Name it (e.g., "Project Gmail Ingestion")
8. Click **Create**
9. Download the JSON file

### Step 2: Save Credentials

```bash
mkdir -p backend/credentials
# Save downloaded JSON as:
backend/credentials/gmail_credentials.json
```

### Step 3: First-Time Authorization

Run this once locally to authorize and generate the token:

```python
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds_path = "credentials/gmail_credentials.json"
token_path = "credentials/gmail_token.json"
scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

creds = None
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, scopes)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
        creds = flow.run_local_server(port=0)
    with open(token_path, "w") as token:
        token.write(creds.to_json())

service = build("gmail", "v1", credentials=creds)
profile = service.users().getProfile(userId="me").execute()
print(f"Authenticated as: {profile['emailAddress']}")
```

A browser window opens. Sign in and authorize. The token is saved automatically.

### Step 4: Copy to Server

```bash
scp backend/credentials/gmail_credentials.json server:/path/to/project/backend/credentials/
scp backend/credentials/gmail_token.json server:/path/to/project/backend/credentials/
```

---

## 9. Basecamp API Setup

### Step 1: Get API Token

1. Go to https://launchpad.37signals.com/integrations
2. Create a new integration or use an existing one
3. Get a Bearer token (or use OAuth 2.0)
4. Note the **account ID** from your Basecamp URL: `https://3.basecamp.com/{ACCOUNT_ID}/...`

### Step 2: Create or Identify Project

Get the project ID from the URL: `https://3.basecamp.com/{account_id}/projects/{PROJECT_ID}`

Or create via API:
```python
POST https://3.basecampapi.com/{account_id}/projects.json
{
    "name": "Your Project Name",
    "description": "Project description"
}
```

### Step 3: Add Users to Project

```python
PUT https://3.basecampapi.com/{account_id}/projects/{project_id}/people/users.json
{
    "grant": [user_id_1, user_id_2]
}
```

### Step 4: Verify Connection

```python
GET https://3.basecampapi.com/{account_id}/projects/{project_id}.json
```

Should return 200 with project details including dock items (message_board, todoset, etc.).

### Basecamp 4 API Key Concepts

- **Project** = container for all work
- **Dock** = features within a project (message_board, todoset, vault, chat, etc.)
- **Message Board** = where topics (messages) live
- **Todoset** = container for todolists
- **Todolist** = a named list of todos
- **Todo** = individual actionable item
- **Recording** = generic parent for comments (topics, todos are recordings)

### API URL Patterns

```
Base:     https://3.basecampapi.com/{account_id}
Project:  /projects/{project_id}.json
Topics:   /buckets/{project_id}/message_boards/{board_id}/messages.json
Comments: /buckets/{project_id}/recordings/{recording_id}/comments.json
Todolists: /buckets/{project_id}/todosets/{todoset_id}/todolists.json
Todos:    /buckets/{project_id}/todolists/{todolist_id}/todos.json
Complete: /buckets/{project_id}/todos/{todo_id}/completion.json (POST=complete, DELETE=uncomplete)
People:   /projects/{project_id}/people.json
```

---

## 10. Deployment & Automation

### Deploy Credentials to Server

```bash
# Create credentials directory on server
ssh server "mkdir -p /path/to/project/backend/credentials"

# Copy Gmail credentials
scp backend/credentials/gmail_credentials.json server:/path/to/project/backend/credentials/
scp backend/credentials/gmail_token.json server:/path/to/project/backend/credentials/
```

### Cron Job Setup

Create a runner script on the server:

```bash
#!/bin/bash
# /path/to/project/run_comm_pipeline.sh
curl -s -X POST http://localhost:PORT/api/communication/run?lookback_hours=1 \
  -H "Content-Type: application/json" \
  >> /var/log/comm_pipeline.log 2>&1
echo " [$(date)]" >> /var/log/comm_pipeline.log
```

Set up cron (every 30 minutes, Mon-Fri, 8am-10pm):

```bash
chmod +x /path/to/project/run_comm_pipeline.sh
crontab -e
# Add:
*/30 8-22 * * 1-5 /path/to/project/run_comm_pipeline.sh
```

### Backfill Historical Emails

For first-time setup, ingest a larger lookback window:

```bash
# 30 days = 720 hours
curl -X POST http://localhost:PORT/api/communication/ingest?lookback_hours=720
curl -X POST http://localhost:PORT/api/communication/process
```

---

## 11. Implementation Checklist

### Phase 1: Infrastructure

- [ ] Install Python dependencies: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `httpx`
- [ ] Add config fields to Settings class (basecamp_token, account_id, project_id, gmail paths)
- [ ] Add environment variables to .env
- [ ] Create `credentials/` directory with `.gitignore`

### Phase 2: Gmail Setup

- [ ] Enable Gmail API in Google Cloud Console
- [ ] Create OAuth 2.0 Desktop App credentials
- [ ] Download credentials JSON to `credentials/gmail_credentials.json`
- [ ] Run first-time OAuth authorization (opens browser)
- [ ] Verify: `gmail_token.json` created automatically
- [ ] Test: confirm authenticated email address

### Phase 3: Basecamp Setup

- [ ] Get Basecamp API token
- [ ] Get or create project (note account_id and project_id)
- [ ] Add your user to the project via API
- [ ] Test: create a test topic and todo via API
- [ ] Verify: visible in Basecamp web UI

### Phase 4: Database Models

- [ ] Create `email_thread.py` model
- [ ] Create `topic_thread_map.py` model
- [ ] Create `communication_feedback.py` model
- [ ] Register all 3 in `models/__init__.py`
- [ ] Verify tables created on startup

### Phase 5: Services

- [ ] Create `email_ingestion_service.py` (Gmail fetch + store)
- [ ] Create `email_intelligence_service.py` (AI classification)
- [ ] Create `thread_resolution_service.py` (thread continuity)
- [ ] Create `todo_generation_service.py` (atomic todos)
- [ ] Create `basecamp_service.py` (Basecamp REST client)
- [ ] Create `priority_engine.py` (email scoring)
- [ ] Create `communication_feedback_service.py` (tracking)
- [ ] Create `daily_summary_service.py` (LLM digest)
- [ ] Create `communication_orchestrator.py` (pipeline coordinator)

### Phase 6: API Routes

- [ ] Create `communication.py` route file
- [ ] Register in routes `__init__.py`
- [ ] Test: POST /communication/ingest
- [ ] Test: POST /communication/process
- [ ] Test: GET /communication/threads
- [ ] Test: GET /communication/summary

### Phase 7: Backfill & Verify

- [ ] Run backfill: ingest 30 days of emails
- [ ] Process through pipeline
- [ ] Verify topics and todos appear in Basecamp
- [ ] Add notes to completed items
- [ ] Mark completed todos as done
- [ ] Assign all todos to appropriate user

### Phase 8: Automation

- [ ] Copy credentials to server
- [ ] Create cron runner script
- [ ] Set up cron job (every 30 min)
- [ ] Verify cron is running: `crontab -l`
- [ ] Monitor logs: `tail -f /var/log/comm_pipeline.log`

---

## Quick Reference: Adapting for a New Project

To add this system to a different project:

1. **Copy the file structure** (models, services, routes)
2. **Update monitored senders** in `email_ingestion_service.py`
3. **Update Basecamp config** (.env: token, account_id, project_id)
4. **Set up Gmail OAuth** for the email account you want to monitor
5. **Register the route** in your routes `__init__.py`
6. **Register the models** in your models `__init__.py`
7. **Run first-time auth** locally, then copy token to server
8. **Backfill** historical emails
9. **Set up cron** for automation

The system is fully additive - no modifications needed to existing project code.
