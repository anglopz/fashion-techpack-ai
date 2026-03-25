# Architecture

## Overview

Fashion Tech Pack AI is a multi-agent system that generates structured fashion tech packs from unstructured design inputs. A designer submits a brief (text description, fabric preferences, color palette), and a pipeline of 5 specialized agents collaborates to produce a complete tech pack with measurements, fabric specifications, bill of materials, and construction details.

The system uses a hybrid Node.js + Python architecture: a TypeScript/Express API gateway handles auth, validation, and WebSocket streaming, while a Python/FastAPI service orchestrates AI agents via LangGraph (production) and CrewAI (prototyping).

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                               │
│  React Frontend (optional) / API Consumer / Postman           │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│              NODE.JS API GATEWAY (Express + TS)               │
│  POST /api/v1/techpacks          → Create tech pack request  │
│  GET  /api/v1/techpacks/:id      → Get tech pack status/data │
│  GET  /api/v1/techpacks          → List tech packs            │
│  POST /api/v1/fabrics            → Upload fabric to catalog   │
│  GET  /api/v1/fabrics/search     → Search fabric catalog      │
│  POST /api/v1/crew/techpacks     → CrewAI prototype endpoint  │
│  WS   /api/v1/techpacks/:id/stream → Real-time agent progress │
│  GET  /api/v1/health             → Health check               │
│                                                               │
│  Middleware: JWT auth, rate limiting, request validation       │
│  Proxy: Forwards to FastAPI orchestration service              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (internal)
┌──────────────────────▼──────────────────────────────────────┐
│           FASTAPI ORCHESTRATION SERVICE (Python)              │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  CrewAI Prototype Layer (rapid iteration)              │   │
│  │                                                        │   │
│  │  Crew: TechPackCrew                                    │   │
│  │  ├── Agent: Design Analyst (role + goal + backstory)   │   │
│  │  ├── Agent: Fabric Specialist (RAG tools bound)        │   │
│  │  ├── Agent: Production Planner (BOM generation)        │   │
│  │  └── Agent: Technical Writer (assembly + formatting)   │   │
│  │                                                        │   │
│  │  Process: sequential → validates prompts & tool chains │   │
│  │  Output: Raw tech pack JSON for comparison             │   │
│  └───────────────────────────────────────────────────────┘   │
│                         │ validated roles & prompts           │
│                         ▼                                     │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LangGraph Production Layer (stateful orchestration)   │   │
│  │                                                        │   │
│  │  START → [Brief Analyzer] → [Spec Extractor]           │   │
│  │                                  │                     │   │
│  │                            ┌─────┴─────┐               │   │
│  │                            ▼           ▼               │   │
│  │                    [Fabric Matcher] [BOM Builder]       │   │
│  │                            │           │               │   │
│  │                            └─────┬─────┘               │   │
│  │                                  ▼                     │   │
│  │                          [Tech Pack Writer]            │   │
│  │                                  │                     │   │
│  │                                  ▼                     │   │
│  │                               END                      │   │
│  │                                                        │   │
│  │  State: TechPackState (typed dict, checkpointed)       │   │
│  │  Edges: conditional routing + error recovery           │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  Shared Services:                                             │
│  ├── llm_client.py      → OpenRouter wrapper + model routing  │
│  ├── rag_service.py      → Supabase pgvector search           │
│  ├── embedding_service.py → OpenRouter embeddings             │
│  └── output_service.py   → Tech pack PDF/JSON generation      │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   Supabase   │ │  Redis   │ │  OpenRouter  │
│  PostgreSQL  │ │          │ │              │
│  + pgvector  │ │ Cache +  │ │ Claude /     │
│              │ │ Sessions │ │ GPT-4o-mini  │
│ • fabrics    │ │          │ │ / Embeddings │
│ • techpacks  │ │          │ │              │
│ • embeddings │ │          │ │              │
└──────────────┘ └──────────┘ └──────────────┘
```

## Gateway Layer

The Node.js gateway is the single entry point for all client traffic. It handles cross-cutting concerns and proxies domain requests to the orchestrator.

**Middleware chain** (applied in order):
1. **CORS** — Configurable origins via `CORS_ORIGINS` env var
2. **Rate limiting** — Token bucket per IP, configurable window/max
3. **JWT authentication** — Validates Bearer tokens, attaches user context
4. **Zod validation** — Request body/params validation with type-safe schemas
5. **Proxy** — Forwards validated requests to `ORCHESTRATOR_URL`

**WebSocket relay**: The gateway upgrades HTTP connections on `/api/v1/techpacks/:id/stream` and relays progress events from the orchestrator. The client receives structured JSON messages as each agent completes its work.

**Design decision**: The gateway does not contain domain logic. It validates, authenticates, and forwards. This keeps the Node.js layer thin and testable (33 tests cover all middleware and routing).

## Orchestration Layer

The FastAPI service owns all domain logic: agent orchestration, model interactions, and data persistence.

**Endpoints**:
- `POST /techpacks` — Accepts a design brief, triggers the LangGraph pipeline, returns a job ID
- `GET /techpacks/{id}` — Returns tech pack status and result
- `POST /crew/techpacks` — Triggers the CrewAI prototype pipeline (same input/output schema)
- `POST /fabrics` — Adds a fabric to the catalog with auto-generated embeddings
- `GET /fabrics/search` — Semantic search over the fabric catalog

**State management**: The LangGraph workflow uses `TechPackState`, a typed dictionary that accumulates results as it flows through the pipeline. Each agent reads from and writes to specific state keys, ensuring type safety at every handoff.

## Agent Pipeline

### 1. Brief Analyzer
- **Input**: Raw `DesignBrief` (description, garment type, preferences)
- **Output**: `AnalyzedBrief` (detected garment type, extracted keywords, normalized colors, season)
- **Model**: `anthropic/claude-sonnet-4` (complex reasoning)

### 2. Spec Extractor
- **Input**: `AnalyzedBrief`
- **Output**: `Measurements` (size grading XS-XL, key measurements, fit type, construction notes)
- **Model**: `openai/gpt-4o-mini` (structured extraction)

### 3. Fabric Matcher
- **Input**: `AnalyzedBrief` + fabric preferences
- **Output**: `list[FabricSpec]` (matched fabrics with scores, composition, care instructions)
- **Method**: RAG — embeds query via OpenRouter, searches Supabase pgvector, LLM reranks top results
- **Model**: `openai/text-embedding-3-small` (embeddings) + `openai/gpt-4o-mini` (reranking)

### 4. BOM Builder
- **Input**: `AnalyzedBrief` + `Measurements` + `list[FabricSpec]`
- **Output**: `BillOfMaterials` (fabrics, trims, hardware, thread, labels with quantities)
- **Model**: `openai/gpt-4o-mini` (structured list generation)

### 5. Tech Pack Writer
- **Input**: All previous agent outputs
- **Output**: `TechPack` (complete document with all sections assembled)
- **Model**: `anthropic/claude-sonnet-4` (document synthesis)

**Validation and retry**: A validation node after Tech Pack Writer checks for required fields. If validation fails, the pipeline conditionally retries (max 2 attempts) by re-running the failing agent with error context injected into the prompt.

## Data Flow

1. Client sends `POST /api/v1/techpacks` with a `DesignBrief` JSON body
2. Gateway validates JWT, rate-checks, validates body with Zod, proxies to orchestrator
3. Orchestrator creates a job record, returns `202 Accepted` with job ID
4. LangGraph pipeline executes: Brief Analyzer → Spec Extractor → Fabric Matcher → BOM Builder → Tech Pack Writer
5. Each agent writes its output to `TechPackState`; progress events are emitted via WebSocket
6. Validation node checks the final `TechPack`; retries if incomplete
7. Client polls `GET /api/v1/techpacks/:id` or listens on WebSocket for completion

## Services

### LLM Client (`llm_client.py`)
Wraps the OpenRouter API with model routing. Different agents use different models based on cost/capability:
- **Reasoning tasks** (brief analysis, document synthesis): `anthropic/claude-sonnet-4`
- **Extraction tasks** (specs, BOM, classification): `openai/gpt-4o-mini`
- **Embeddings**: `openai/text-embedding-3-small`

Model selection is config-driven — switching models requires no code changes.

### RAG Service (`rag_service.py`)
Queries the Supabase pgvector fabric catalog. Combines vector similarity (`<=>` cosine distance) with SQL filters (composition, weight range) in a single query. Returns ranked results for LLM reranking.

### Embedding Service (`embedding_service.py`)
Generates embeddings via OpenRouter for fabric descriptions. Used at ingest time (when fabrics are added to the catalog) and at query time (when the Fabric Matcher searches).

### Redis
Caches fabric search results and stores session state. Used by the gateway for rate limiting counters.

## Dual Framework Strategy

The project implements the same pipeline in both CrewAI and LangGraph to enable empirical comparison:

| Dimension | CrewAI | LangGraph |
|-----------|--------|-----------|
| **Agent definition** | Role + goal + backstory | Node function + typed state |
| **State passing** | String output → next agent input | Typed `TechPackState` dict |
| **Control flow** | Sequential process | Graph with conditional edges |
| **Error recovery** | None (fails on first error) | Conditional retry with validation |
| **Streaming** | stdout verbose mode only | WebSocket progress events |
| **Checkpointing** | None | MemorySaver (resume on crash) |
| **Best for** | Prompt iteration, role validation | Production workloads |

CrewAI validates agent roles and prompts quickly. LangGraph adds the production requirements (typed state, error recovery, streaming). Both produce the same `TechPack` Pydantic schema, enabling direct comparison.

## Infrastructure

### Docker Compose
Three services: `gateway` (Node.js), `orchestrator` (Python/FastAPI), `redis` (cache). The gateway depends on the orchestrator; the orchestrator depends on Redis. All services use `unless-stopped` restart policy.

### CI Pipeline
GitHub Actions runs two parallel jobs:
- **Gateway**: `npm ci` → `tsc --noEmit` → `npm test`
- **Orchestrator**: `pip install` → `pytest`

### Environment Configuration
All configuration is via environment variables (see `.env.example`). Secrets (API keys, JWT secret) are never committed. Docker Compose reads from `.env` for local development.
