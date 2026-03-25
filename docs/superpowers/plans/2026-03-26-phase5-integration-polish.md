# Phase 5: Integration & Polish — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the project production-ready and portfolio-presentable — working Docker stack, CI pipeline, comprehensive documentation.

**Architecture:** Two independent streams: infrastructure (Docker + CI) and documentation (README + architecture docs + ADRs). No dependency between streams — can merge in any order.

**Tech Stack:** Docker, docker-compose, GitHub Actions, Markdown.

**Existing infrastructure (do NOT recreate):**
- `docker-compose.yml` — has orchestrator + redis services, needs gateway service added
- `orchestrator/Dockerfile` — stub (`FROM python:3.12-slim`, no build steps)
- `gateway/Dockerfile` — already complete (multi-stage node:20-slim build)
- `.github/workflows/ci.yml` — placeholder stub
- `docs/ARCHITECTURE.md` — skeleton with component list
- `docs/DECISIONS.md` — 6 ADRs with empty rationale fields
- `.env.example` — does not exist yet, needs to be created

**Merge strategy:** Either stream can merge first — no import dependencies.

---

## File Structure

### Stream A — Infrastructure

| File | Responsibility |
|------|---------------|
| `docker-compose.yml` | Add gateway service, network config, health checks |
| `orchestrator/Dockerfile` | Multi-stage Python build |
| `.github/workflows/ci.yml` | Lint + test for both services |
| `.env.example` | Template with all env vars documented |

### Stream B — Documentation

| File | Responsibility |
|------|---------------|
| `README.md` | Project overview, setup, API docs, demo walkthrough |
| `docs/ARCHITECTURE.md` | Full system design document |
| `docs/DECISIONS.md` | Complete ADR rationales |

---

## Stream A: Infrastructure

### Task 1: Orchestrator Dockerfile

**Files:**
- Modify: `orchestrator/Dockerfile`

- [ ] **Step 1: Write the Dockerfile**

```dockerfile
# orchestrator/Dockerfile

# --- Build stage ---
FROM python:3.12-slim AS build
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.12-slim
WORKDIR /app

COPY --from=build /install /usr/local
COPY app/ ./app/
COPY seed/ ./seed/

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Verify Dockerfile builds**

Run: `cd orchestrator && docker build -t techpack-orchestrator:test .`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "feat(orchestrator): multi-stage docker build"
```

---

### Task 2: Update docker-compose.yml

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Update docker-compose.yml**

```yaml
version: "3.8"

services:
  gateway:
    build:
      context: ./gateway
      dockerfile: Dockerfile
    ports:
      - "${GATEWAY_PORT:-3000}:3000"
    environment:
      - GATEWAY_PORT=3000
      - ORCHESTRATOR_URL=http://orchestrator:8000
      - JWT_SECRET=${JWT_SECRET:-dev-secret-change-me}
      - CORS_ORIGINS=${CORS_ORIGINS:-*}
      - RATE_LIMIT_MAX=${RATE_LIMIT_MAX:-100}
      - RATE_LIMIT_WINDOW_MS=${RATE_LIMIT_WINDOW_MS:-900000}
    depends_on:
      orchestrator:
        condition: service_started
    restart: unless-stopped

  orchestrator:
    build:
      context: ./orchestrator
      dockerfile: Dockerfile
    ports:
      - "${ORCHESTRATOR_PORT:-8000}:8000"
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_started
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

- [ ] **Step 2: Create .env.example**

```env
# === Gateway ===
GATEWAY_PORT=3000
ORCHESTRATOR_URL=http://localhost:8000
JWT_SECRET=change-me-in-production
CORS_ORIGINS=*
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=900000

# === Orchestrator ===
ORCHESTRATOR_PORT=8000

# === OpenRouter (LLM) ===
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# === Model Routing ===
MODEL_REASONING=anthropic/claude-sonnet-4
MODEL_EXTRACTION=openai/gpt-4o-mini
MODEL_EMBEDDING=openai/text-embedding-3-small

# === Supabase (Vector DB) ===
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# === Redis ===
REDIS_URL=redis://localhost:6379
```

- [ ] **Step 3: Verify docker-compose config is valid**

Run: `docker-compose config --quiet`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "feat: docker-compose with gateway service and env example"
```

---

### Task 3: GitHub Actions CI workflow

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Write the CI workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  gateway:
    name: Gateway (Node.js)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: gateway
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: gateway/package-lock.json
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm test

  orchestrator:
    name: Orchestrator (Python)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: orchestrator
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -r requirements.txt
      - run: python -m pytest --tb=short -q
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: lint and test workflow for gateway and orchestrator"
```

---

## Stream B: Documentation

### Task 4: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
# Fashion Tech Pack AI

A multi-agent AI system that generates structured fashion tech packs from unstructured design inputs. Built with a hybrid Node.js + Python architecture using dual agent frameworks (CrewAI for prototyping, LangGraph for production).

## Architecture

```
Client → Node.js Gateway (Express/TS) → FastAPI Orchestrator (Python)
              │                                    │
              ├── JWT Auth                         ├── LangGraph Pipeline
              ├── Rate Limiting                    │   ├── Brief Analyzer
              ├── Zod Validation                   │   ├── Spec Extractor
              └── WebSocket Relay                  │   ├── Fabric Matcher (RAG)
                                                   │   ├── BOM Builder
                                                   │   └── Tech Pack Writer
                                                   │
                                                   ├── CrewAI Prototype
                                                   ├── Supabase pgvector
                                                   └── Redis Cache
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API Gateway | Node.js, Express, TypeScript | Auth, rate limiting, validation, WebSocket relay |
| Orchestration | Python, FastAPI | AI agent orchestration, domain logic |
| Production Agents | LangGraph | Typed state, conditional routing, checkpointing |
| Prototype Agents | CrewAI | Rapid agent role/prompt iteration |
| LLM Routing | OpenRouter | Unified API for multiple models (Claude, GPT-4o) |
| Vector DB | Supabase pgvector | Fabric catalog with semantic search |
| Cache | Redis | Session state, rate limiting |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenRouter API key ([openrouter.ai](https://openrouter.ai))
- Supabase project with pgvector ([supabase.com](https://supabase.com))

### Setup

```bash
# Clone and configure
git clone https://github.com/anglopz/fashion-techpack-ai.git
cd fashion-techpack-ai
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up --build

# Gateway: http://localhost:3000
# Orchestrator: http://localhost:8000
```

### Local Development (without Docker)

```bash
# Orchestrator
cd orchestrator
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Gateway (separate terminal)
cd gateway
npm install
npm run dev
```

## API Endpoints

### Tech Packs

```bash
# Create a tech pack (returns 202 with job ID)
curl -X POST http://localhost:3000/api/v1/techpacks \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Relaxed-fit organic cotton t-shirt for SS26",
    "garment_type": "top",
    "fabric_preferences": ["organic cotton"],
    "color_palette": ["#2C3E50", "cream"]
  }'

# Check status / get result
curl http://localhost:3000/api/v1/techpacks/tp_abc123 \
  -H "Authorization: Bearer <jwt-token>"

# Stream real-time progress via WebSocket
wscat -c ws://localhost:3000/api/v1/techpacks/tp_abc123/stream
```

### Fabric Catalog

```bash
# Add a fabric
curl -X POST http://localhost:3000/api/v1/fabrics \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Organic Cotton Jersey",
    "composition": "100% Organic Cotton",
    "weight_gsm": 180,
    "width_cm": 150,
    "color": "Natural White",
    "care_instructions": ["Machine wash 30°C"]
  }'

# Semantic search
curl "http://localhost:3000/api/v1/fabrics/search?q=lightweight+cotton+summer&limit=5" \
  -H "Authorization: Bearer <jwt-token>"
```

## Agent Pipeline

The LangGraph pipeline processes a design brief through 5 specialized agents:

1. **Brief Analyzer** — Parses unstructured brief, detects garment type, extracts keywords, normalizes colors
2. **Spec Extractor** — Generates measurements with size grading (XS-XL), construction details
3. **Fabric Matcher** — RAG search against pgvector catalog + LLM reranking
4. **BOM Builder** — Generates bill of materials (fabrics, trims, hardware, thread, labels)
5. **Tech Pack Writer** — Assembles complete tech pack document from all agent outputs

A validation node checks the output and conditionally retries (max 2) if required fields are missing.

## CrewAI vs LangGraph

Both frameworks produce the same `TechPack` schema. The project keeps both implementations for benchmarking:

| | CrewAI | LangGraph |
|---|--------|-----------|
| **Endpoint** | `/api/v1/crew/techpacks` | `/api/v1/techpacks` |
| **Purpose** | Rapid prototyping | Production pipeline |
| **State** | Untyped (string passing) | Typed (`TechPackState` dict) |
| **Error Recovery** | None | Conditional retry with validation |
| **Streaming** | None | WebSocket progress events |
| **Checkpointing** | None | MemorySaver (in-memory) |

## Testing

```bash
# Gateway tests (33 tests)
cd gateway && npm test

# Orchestrator tests (105+ tests)
cd orchestrator && python -m pytest -v
```

## Project Structure

```
fashion-techpack-ai/
├── gateway/                  # Node.js API Gateway
│   ├── src/
│   │   ├── index.ts          # Express app factory
│   │   ├── routes/           # techpacks, fabrics, health
│   │   ├── middleware/        # auth, rateLimit, validation
│   │   ├── ws/               # WebSocket relay
│   │   └── types/            # TypeScript interfaces
│   ├── __tests__/            # Jest + supertest
│   └── Dockerfile
├── orchestrator/             # FastAPI + AI Agents
│   ├── app/
│   │   ├── agents/           # LangGraph node functions
│   │   ├── crews/            # CrewAI prototype
│   │   ├── graphs/           # LangGraph workflow
│   │   ├── models/           # Pydantic domain models
│   │   ├── services/         # LLM, RAG, embedding, Redis
│   │   └── api/              # FastAPI endpoints
│   └── tests/
├── docker-compose.yml
└── docs/
    ├── ARCHITECTURE.md
    └── DECISIONS.md
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design and data flow
- [Decisions](docs/DECISIONS.md) — Architecture Decision Records (ADRs)

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: comprehensive README with setup, API docs, and architecture overview"
```

---

### Task 5: Complete ARCHITECTURE.md

**Files:**
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Write full architecture document**

Replace the entire contents of `docs/ARCHITECTURE.md` with a comprehensive system design document. It should cover:

1. **Overview** — What the system does (multi-agent tech pack generation)
2. **System Architecture** — Copy the ASCII diagram from PLAN.md section 3 (the full client → gateway → orchestrator → agents → services diagram)
3. **Gateway Layer** — Express middleware chain, proxy pattern, WebSocket relay, auth model
4. **Orchestration Layer** — FastAPI endpoints, LangGraph state machine, agent pipeline
5. **Agent Pipeline** — 5 agents with their inputs/outputs, typed state flow
6. **Data Flow** — Step-by-step: client request → gateway → orchestrator → agents → response
7. **Services** — LLM client (OpenRouter routing), RAG service (pgvector search), embedding service, Redis
8. **Dual Framework Strategy** — Why CrewAI + LangGraph, how they compare, benchmarking approach
9. **Infrastructure** — Docker Compose, CI/CD, environment configuration

Use the content from PLAN.md sections 3, 5, 6, 7 as source material. Keep it concise — this is a reference doc, not a tutorial.

- [ ] **Step 2: Commit**

```bash
git add docs/ARCHITECTURE.md
git commit -m "docs: complete system architecture document"
```

---

### Task 6: Complete DECISIONS.md ADR rationales

**Files:**
- Modify: `docs/DECISIONS.md`

- [ ] **Step 1: Fill in all ADR rationales**

The file has 6 ADRs with `_To be documented._` as rationale. Replace each with the rationale from PLAN.md section 12. Here are the exact rationales:

**ADR-001: Hybrid Node.js + Python Architecture**
> Node.js provides the performance and ecosystem expected for a production API gateway (auth, rate limiting, WebSocket). Python provides the AI/ML ecosystem (LangGraph, LangChain, Pydantic) without fighting the tooling. Same pattern used at scale: API gateway in one language, domain services in another.

**ADR-002: CrewAI for Prototyping, LangGraph for Production**
> CrewAI's role-based design (agent + goal + backstory) is the fastest way to iterate on prompt engineering and validate tool bindings. But CrewAI lacks typed state, conditional edges, checkpointing, and WebSocket-compatible progress callbacks. LangGraph adds these production requirements. Keeping both implementations lets us benchmark and provides an ADR backed by empirical data, not opinion.

**ADR-003: OpenRouter for Model Routing**
> Different agents have different cost/capability needs. OpenRouter provides a single API with automatic fallbacks and unified billing. Switching models is a config change, not a code change.

**ADR-004: Supabase pgvector over ChromaDB/FAISS**
> The fabric catalog is relational data with an embedding column. pgvector lets us combine vector similarity with SQL filters in a single query.

**ADR-005: Structured Outputs with Pydantic Validation**
> Pydantic enforces type safety at every handoff between agents. Same pattern as API request/response validation — applied to agent I/O.

**ADR-006: Git Worktrees for Parallel Agent Development**
> Each agent needs its own filesystem context and branch to avoid conflicts. Worktrees share the same .git directory so branches are immediately available across all checkouts. Squash merging keeps main history clean and linear.

- [ ] **Step 2: Commit**

```bash
git add docs/DECISIONS.md
git commit -m "docs: complete ADR rationales for all 6 architecture decisions"
```

---

### Task 7: Final verification

- [ ] **Step 1: Run gateway tests**

Run: `cd gateway && npm test`
Expected: All 33 tests pass

- [ ] **Step 2: Run orchestrator tests**

Run: `cd orchestrator && python3 -m pytest --tb=short -q`
Expected: Tests pass (excluding known CrewAI failures)

- [ ] **Step 3: Verify docker-compose config**

Run: `docker-compose config --quiet`
Expected: No errors

- [ ] **Step 4: Commit any fixes**

```bash
git add -A && git commit -m "fix: final verification fixes" || echo "nothing to fix"
```
