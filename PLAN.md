# Fashion Tech Pack AI — Multi-Agent System

## Portfolio Project Plan (v2)

**Angelo Lopez · March 2026**
**Target role:** NodeJS Software Engineer – Conversational AI (Mango)
**Repo:** `github.com/anglopz/fashion-techpack-ai`

---

## 1. What This Project Demonstrates

This is a multi-agent AI system that generates structured fashion tech packs from
unstructured design inputs. A designer uploads a brief (text description, reference
images, fabric preferences), and a team of specialized agents collaborates to
produce a structured tech pack document with measurements, fabric specifications,
bill of materials, and construction details.

The system showcases two orchestration paradigms side by side:
- **CrewAI** for rapid prototyping and validating agent role definitions
- **LangGraph** for production-grade stateful orchestration with typed state

This dual-framework approach demonstrates framework evaluation — a real engineering
decision that shows understanding of trade-offs, not just API familiarity.

### Why This Project Maps to the Mango Role

| Mango JD Requirement | This Project Demonstrates |
|---|---|
| Node.js/TypeScript + microservices | Node.js API gateway with Express, auth, WebSocket streaming |
| Agentic AI architectures (LangGraph, CrewAI, MCP) | Both LangGraph AND CrewAI — with documented trade-off analysis |
| LLMs / Generative AI | OpenRouter multi-model routing (Claude for reasoning, GPT-4o-mini for extraction) |
| Backend with microservices | FastAPI orchestration layer behind Node.js gateway — clean service separation |
| Cloud experience | Docker Compose local, structured for GKE/ECS deployment |
| Prompt engineering & guardrails | Structured output validation with Pydantic, system prompts per agent role |
| Multi-channel integration | REST API + WebSocket — same pattern as web/WhatsApp/Instagram channels |
| Redis, Pub/Sub patterns | Redis for caching fabric lookups and session state |
| API integrations | OpenRouter, Supabase, potential Salesforce-style CRM pattern |

### Architecture Principles Showcased

- **Clean Architecture**: Domain models (TechPack, Fabric, BOM) decoupled from infra
- **Dual-framework orchestration**: CrewAI prototype → LangGraph production migration
- **RAG pipeline**: Fabric catalog embedded in Supabase pgvector for semantic retrieval
- **Structured outputs**: Every agent produces Pydantic-validated JSON, not free text
- **Hybrid Node.js + Python**: Right tool for each layer (API surface vs AI orchestration)
- **Event-driven patterns**: WebSocket for real-time agent progress streaming

---

## 2. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **API Gateway** | Node.js + Express + TypeScript | Matches JD requirement. Handles auth, rate limiting, WS |
| **Orchestration** | Python + FastAPI | LangGraph and AI tooling ecosystem lives in Python |
| **Agent Framework (proto)** | CrewAI | Rapid prototyping of agent roles, prompts, tool bindings |
| **Agent Framework (prod)** | LangGraph | Graph-based state machine — production-grade orchestration |
| **LLM Routing** | OpenRouter | Unified API, model switching, cost control |
| **RAG / Vector DB** | Supabase (PostgreSQL + pgvector) | Managed vector search + auth + dashboard |
| **Caching** | Redis | Fabric lookup cache, session state |
| **Document Tools** | LangChain (loaders + splitters only) | PDF/image parsing, text chunking |
| **Structured Output** | Pydantic | Type-safe agent I/O contracts |
| **Container** | Docker Compose | Local dev, structured for cloud deployment |

### Model Routing Strategy (OpenRouter)

```
Task                    → Model                        → Why
─────────────────────────────────────────────────────────────────
Design brief analysis   → anthropic/claude-sonnet-4     → Complex reasoning
Measurement extraction  → openai/gpt-4o-mini            → Structured extraction, cheap
Fabric matching (RAG)   → openai/text-embedding-3-small → Embeddings ($0.02/1M tokens)
BOM generation          → openai/gpt-4o-mini            → Structured list generation
Tech pack assembly      → anthropic/claude-sonnet-4     → Document synthesis
Classification/routing  → openai/gpt-4o-mini            → Fast intent classification
```

---

## 3. System Architecture

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

### CrewAI → LangGraph Migration Strategy

The CrewAI layer is NOT throwaway code. It serves three purposes:

1. **Rapid prompt iteration**: Define agent roles (backstory, goal, expected output)
   and test them against real design briefs before investing in LangGraph wiring.

2. **Tool validation**: Bind RAG search, embedding, and LLM tools to CrewAI agents
   to verify they work correctly before the same tools are used in LangGraph nodes.

3. **Documented comparison**: Both implementations process the same input and
   produce the same output schema (TechPack). The README includes a comparison
   table: execution time, token usage, output quality, error recovery capability.
   This is ADR-002 in action — showing you evaluated both frameworks empirically.

```python
# CrewAI prototype (orchestrator/app/crews/techpack_crew.py)
from crewai import Agent, Task, Crew, Process

design_analyst = Agent(
    role="Design Analyst",
    goal="Parse unstructured design briefs into structured garment specifications",
    backstory="You are a senior fashion designer with 15 years of experience...",
    tools=[brief_parser_tool],
    llm="openai/gpt-4o-mini",  # via OpenRouter
    verbose=True
)

fabric_specialist = Agent(
    role="Fabric Specialist",
    goal="Find the best fabric matches from the catalog for the given design",
    backstory="You are a textile expert specializing in sustainable fabrics...",
    tools=[fabric_search_tool, embedding_tool],
    llm="openai/gpt-4o-mini",
    verbose=True
)

# ... more agents ...

techpack_crew = Crew(
    agents=[design_analyst, fabric_specialist, production_planner, technical_writer],
    tasks=[analyze_task, match_task, bom_task, assemble_task],
    process=Process.sequential,
    verbose=True
)

# Run and get result
result = techpack_crew.kickoff(inputs={"brief": design_brief_text})
```

The LangGraph version uses the same prompts and tools but adds:
- Typed state (`TechPackState`) flowing between nodes
- Conditional edges (retry on validation failure, skip BOM for accessories)
- Checkpointing (resume on crash)
- WebSocket progress streaming (CrewAI only has stdout verbose mode)

---

## 4. Domain Models (Pydantic)

### Core Models

```python
class GarmentType(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    ACCESSORY = "accessory"

class DesignBrief(BaseModel):
    """Input from the designer"""
    description: str                          # Free-text design description
    garment_type: GarmentType | None = None   # Auto-detected if not provided
    target_season: str | None = None          # e.g., "SS26", "AW26"
    style_references: list[str] = []          # URLs or descriptions
    fabric_preferences: list[str] = []        # e.g., "organic cotton", "silk blend"
    color_palette: list[str] = []             # e.g., ["#2C3E50", "navy", "cream"]

class Measurements(BaseModel):
    """Extracted by spec_extractor agent"""
    garment_type: GarmentType
    size_range: str                           # e.g., "XS-XL"
    key_measurements: dict[str, dict[str, float]]  # {"chest": {"XS": 84, "S": 88, ...}}
    fit_type: str                             # e.g., "relaxed", "slim", "oversized"
    notes: list[str] = []

class FabricSpec(BaseModel):
    """Matched by fabric_matcher agent (from RAG)"""
    name: str
    composition: str                          # e.g., "95% Cotton, 5% Elastane"
    weight_gsm: float                         # Grams per square meter
    width_cm: float
    color: str
    supplier: str | None = None
    price_per_meter: float | None = None
    care_instructions: list[str] = []
    similarity_score: float = 0.0             # RAG retrieval score

class BOMItem(BaseModel):
    """Bill of Materials item from bom_builder agent"""
    category: str                             # "fabric", "trim", "hardware", "thread", "label"
    description: str
    quantity: str
    unit: str                                 # "meters", "pieces", "rolls"
    color: str | None = None
    supplier: str | None = None

class ConstructionDetail(BaseModel):
    """Assembly instructions"""
    step: int
    description: str
    stitch_type: str | None = None            # e.g., "lockstitch", "overlock"
    seam_allowance: str | None = None         # e.g., "1cm"

class TechPack(BaseModel):
    """Final output — assembled by tech_pack_writer agent"""
    id: str                                   # UUID
    brief: DesignBrief
    measurements: Measurements
    primary_fabric: FabricSpec
    secondary_fabrics: list[FabricSpec] = []
    bom: list[BOMItem]
    construction: list[ConstructionDetail]
    colorways: list[dict[str, str]] = []      # [{"name": "Midnight", "hex": "#2C3E50"}]
    status: str = "draft"                     # draft, review, approved
    created_at: str
    version: int = 1
```

### LangGraph State

```python
class TechPackState(TypedDict):
    """State that flows through the LangGraph"""
    brief: DesignBrief
    garment_type: GarmentType | None
    measurements: Measurements | None
    fabrics: list[FabricSpec]
    bom: list[BOMItem]
    construction: list[ConstructionDetail]
    tech_pack: TechPack | None
    current_agent: str
    agent_messages: list[dict]               # Progress log for WebSocket streaming
    errors: list[str]
    retry_count: int                         # For conditional retry edges
```

---

## 5. Agent Definitions

### Agent 1: Brief Analyzer (a.k.a. Design Analyst in CrewAI)
- **Role**: Parse unstructured design brief into structured data
- **Input**: Raw `DesignBrief.description` text
- **Output**: Detected `GarmentType`, extracted keywords for fabric search, normalized color palette
- **Model**: `openai/gpt-4o-mini` (fast classification + extraction)
- **Prompt strategy**: Few-shot examples of design briefs → structured output
- **CrewAI backstory**: "You are a senior fashion designer with 15 years of experience reading design briefs from creative directors. You excel at extracting precise specifications from vague creative language."

### Agent 2: Spec Extractor
- **Role**: Generate standard measurements based on garment type and fit description
- **Input**: `GarmentType`, fit preferences from brief
- **Output**: `Measurements` with size grading (XS-XL)
- **Model**: `anthropic/claude-sonnet-4` (needs reasoning about garment construction)
- **Prompt strategy**: System prompt with measurement tables per garment type

### Agent 3: Fabric Matcher (a.k.a. Fabric Specialist in CrewAI)
- **Role**: Search fabric catalog via RAG and recommend best matches
- **Input**: Fabric preferences, garment type, season
- **Output**: Ranked list of `FabricSpec` with similarity scores
- **Model**: `openai/text-embedding-3-small` (embeddings) + `openai/gpt-4o-mini` (reranking)
- **Tools**: Supabase pgvector similarity search
- **RAG pipeline**: Query → embed → vector search → rerank → return top-3

### Agent 4: BOM Builder (a.k.a. Production Planner in CrewAI)
- **Role**: Generate complete bill of materials
- **Input**: `GarmentType`, `FabricSpec`, construction requirements
- **Output**: List of `BOMItem` covering fabric, trims, hardware, thread, labels
- **Model**: `openai/gpt-4o-mini` (structured list generation)
- **Prompt strategy**: Template BOM per garment type, customized by fabric and style

### Agent 5: Tech Pack Writer (a.k.a. Technical Writer in CrewAI)
- **Role**: Assemble all outputs into final tech pack
- **Input**: All previous agent outputs from state
- **Output**: Complete `TechPack` + construction details
- **Model**: `anthropic/claude-sonnet-4` (document synthesis, reasoning)
- **Prompt strategy**: Template with all fields, agent fills in from state data

---

## 6. LangGraph Workflow

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(TechPackState)

# Add nodes
workflow.add_node("brief_analyzer", brief_analyzer_node)
workflow.add_node("spec_extractor", spec_extractor_node)
workflow.add_node("fabric_matcher", fabric_matcher_node)
workflow.add_node("bom_builder", bom_builder_node)
workflow.add_node("tech_pack_writer", tech_pack_writer_node)
workflow.add_node("validation", validation_node)  # Validates final output

# Define edges
workflow.set_entry_point("brief_analyzer")
workflow.add_edge("brief_analyzer", "spec_extractor")
workflow.add_edge("spec_extractor", "fabric_matcher")
workflow.add_edge("fabric_matcher", "bom_builder")
workflow.add_edge("bom_builder", "tech_pack_writer")
workflow.add_edge("tech_pack_writer", "validation")

# Conditional edge: retry or finish
workflow.add_conditional_edges(
    "validation",
    lambda state: "retry" if state["errors"] and state["retry_count"] < 2 else "end",
    {"retry": "tech_pack_writer", "end": END}
)

# Compile with checkpointing
from langgraph.checkpoint.memory import MemorySaver
app = workflow.compile(checkpointer=MemorySaver())
```

---

## 7. API Design

### Node.js Gateway Endpoints

#### POST /api/v1/techpacks
```
Request:
{
  "description": "Relaxed-fit organic cotton t-shirt for SS26...",
  "garment_type": "top",
  "fabric_preferences": ["organic cotton"],
  "color_palette": ["#2C3E50", "cream"],
  "style_references": [],
  "engine": "langgraph"           // "langgraph" (default) | "crewai"
}

Response (202 Accepted):
{
  "id": "tp_abc123",
  "status": "processing",
  "engine": "langgraph",
  "ws_url": "/api/v1/techpacks/tp_abc123/stream"
}
```

#### GET /api/v1/techpacks/:id
```
Response (200):
{
  "id": "tp_abc123",
  "status": "completed",
  "engine": "langgraph",
  "tech_pack": { ... },
  "created_at": "2026-03-25T...",
  "processing_time_ms": 12400
}
```

#### WS /api/v1/techpacks/:id/stream
```
{ "agent": "brief_analyzer", "status": "running", "message": "Parsing design brief..." }
{ "agent": "brief_analyzer", "status": "completed", "data": { "garment_type": "top" } }
{ "agent": "spec_extractor", "status": "running", "message": "Generating measurements..." }
...
{ "status": "completed", "tech_pack": { ... } }
```

#### POST /api/v1/fabrics
```
Request:
{
  "name": "Organic Cotton Jersey",
  "composition": "100% Organic Cotton",
  "weight_gsm": 180,
  "width_cm": 150,
  "color": "Natural White",
  "care_instructions": ["Machine wash 30°C", "Tumble dry low"]
}

Response (201):
{ "id": "fab_xyz789", "name": "Organic Cotton Jersey", "embedded": true }
```

#### GET /api/v1/fabrics/search
```
Query: ?q=lightweight+cotton+summer&limit=5

Response (200):
{
  "results": [
    { "id": "fab_001", "name": "Organic Cotton Jersey", "similarity": 0.92, ... },
    { "id": "fab_002", "name": "Cotton Poplin", "similarity": 0.87, ... }
  ]
}
```

---

## 8. Database Schema (Supabase)

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Fabric catalog with embeddings for RAG
CREATE TABLE fabrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    composition TEXT NOT NULL,
    weight_gsm NUMERIC,
    width_cm NUMERIC,
    color TEXT,
    supplier TEXT,
    price_per_meter NUMERIC,
    care_instructions TEXT[],
    description TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON fabrics USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Tech pack records
CREATE TABLE tech_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brief JSONB NOT NULL,
    measurements JSONB,
    fabrics JSONB,
    bom JSONB,
    construction JSONB,
    full_pack JSONB,
    engine TEXT DEFAULT 'langgraph',  -- 'langgraph' | 'crewai'
    status TEXT DEFAULT 'processing',
    processing_time_ms INTEGER,
    error_log TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent execution log
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tech_pack_id UUID REFERENCES tech_packs(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    engine TEXT NOT NULL,
    status TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    model_used TEXT,
    tokens_used INTEGER,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON agent_logs(tech_pack_id);
```

---

## 9. Project Structure

```
fashion-techpack-ai/
├── gateway/                         # Node.js API Gateway
│   ├── src/
│   │   ├── index.ts                 # Express app setup
│   │   ├── routes/
│   │   │   ├── techpacks.ts         # Tech pack CRUD + proxy to orchestrator
│   │   │   ├── fabrics.ts           # Fabric catalog endpoints
│   │   │   └── health.ts
│   │   ├── middleware/
│   │   │   ├── auth.ts              # JWT validation
│   │   │   ├── rateLimit.ts
│   │   │   └── validation.ts        # Zod schemas
│   │   ├── ws/
│   │   │   └── techpackStream.ts    # WebSocket handler
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── orchestrator/                    # FastAPI + LangGraph + CrewAI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app factory
│   │   ├── config.py
│   │   ├── agents/                  # LangGraph agent node functions
│   │   │   ├── __init__.py
│   │   │   ├── brief_analyzer.py
│   │   │   ├── spec_extractor.py
│   │   │   ├── fabric_matcher.py
│   │   │   ├── bom_builder.py
│   │   │   └── tech_pack_writer.py
│   │   ├── crews/                   # CrewAI prototype definitions
│   │   │   ├── __init__.py
│   │   │   ├── techpack_crew.py     # Crew with agents + tasks
│   │   │   └── tools.py             # Shared tool definitions (used by both)
│   │   ├── graphs/                  # LangGraph definitions
│   │   │   ├── __init__.py
│   │   │   └── techpack_graph.py
│   │   ├── models/                  # Pydantic domain models
│   │   │   ├── __init__.py
│   │   │   ├── brief.py
│   │   │   ├── measurements.py
│   │   │   ├── fabric.py
│   │   │   ├── bom.py
│   │   │   ├── techpack.py
│   │   │   └── state.py
│   │   ├── services/                # Infrastructure services
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py        # OpenRouter wrapper + model routing
│   │   │   ├── rag_service.py       # Supabase pgvector search
│   │   │   ├── embedding_service.py
│   │   │   └── redis_service.py
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── techpacks.py
│   │       └── fabrics.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_agents/
│   │   ├── test_crews/
│   │   ├── test_services/
│   │   └── test_api/
│   ├── requirements.txt
│   └── Dockerfile
│
├── seed/
│   ├── fabrics.json
│   └── seed_embeddings.py
│
├── docs/                            # Tracked in git
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   └── diagrams/
│
├── initiatives/                     # .gitignored — local dev orchestration
│   ├── overview.md
│   ├── phase0-scaffolding/
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── progress.md
│   │   └── findings.md
│   ├── phase1-services-models/
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── progress.md
│   │   └── findings.md
│   ├── phase2-crewai-prototype/
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── progress.md
│   │   └── findings.md
│   ├── phase3-langgraph-production/
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── progress.md
│   │   └── findings.md
│   ├── phase4-gateway/
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── progress.md
│   │   └── findings.md
│   ├── phase5-integration-polish/
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   ├── progress.md
│   │   └── findings.md
│   └── tasks_lessons.md
│
├── docker-compose.yml
├── .env.example
├── .gitignore                       # Includes: initiatives/
├── .github/
│   └── workflows/
│       └── ci.yml
├── README.md
└── PLAN.md                          # This file
```

---

## 10. Multi-Agent Claude Code Development Workflow

### Philosophy

Each phase runs on its own git worktree and branch. Multiple Claude Code agents
work in parallel tmux panes, each with its own context. A lead agent (you or a
dedicated orchestrator session) reviews, resolves conflicts, and merges to main
via squash merge.

### tmux Layout

```
┌─────────────────────────┬─────────────────────────┐
│  Pane 0: LEAD           │  Pane 1: Agent A         │
│  (review, merge, plan)  │  (worktree + branch)     │
│  Branch: main           │  Branch: phase-X-topic    │
│  Dir: ~/proyectos/      │  Dir: ~/proyectos/        │
│       portfolio/         │       portfolio/           │
│       fashion-techpack-  │       fashion-techpack-    │
│       ai/                │       ai-wt-A/             │
├─────────────────────────┼─────────────────────────┤
│  Pane 2: Agent B        │  Pane 3: Agent C         │
│  (worktree + branch)    │  (worktree + branch)     │
│  Branch: phase-X-other   │  Branch: phase-X-etc      │
│  Dir: .../ai-wt-B/      │  Dir: .../ai-wt-C/        │
└─────────────────────────┴─────────────────────────┘
```

### Worktree Setup Script

```bash
#!/bin/bash
# scripts/setup-worktrees.sh — run from main repo root

REPO_ROOT=$(pwd)
PARENT_DIR=$(dirname "$REPO_ROOT")
PROJECT_NAME=$(basename "$REPO_ROOT")

# Create worktrees for parallel agents
create_worktree() {
    local suffix=$1
    local branch=$2
    local worktree_path="${PARENT_DIR}/${PROJECT_NAME}-wt-${suffix}"

    git branch "$branch" 2>/dev/null || true
    git worktree add "$worktree_path" "$branch"
    echo "Created worktree: $worktree_path → branch $branch"

    # Copy shared config files that agents need
    cp .env "$worktree_path/.env" 2>/dev/null || true
}

# Phase-specific worktree creation (call per phase)
# Example for Phase 1:
# create_worktree "models" "phase1/models"
# create_worktree "services" "phase1/services"

echo "Worktrees ready. Use 'git worktree list' to see all."
```

### Worktree Cleanup Script

```bash
#!/bin/bash
# scripts/cleanup-worktrees.sh — after merge, remove worktrees

REPO_ROOT=$(pwd)
PARENT_DIR=$(dirname "$REPO_ROOT")
PROJECT_NAME=$(basename "$REPO_ROOT")

for wt in "${PARENT_DIR}/${PROJECT_NAME}-wt-"*; do
    if [ -d "$wt" ]; then
        branch=$(cd "$wt" && git branch --show-current)
        cd "$REPO_ROOT"
        git worktree remove "$wt" --force
        git branch -D "$branch" 2>/dev/null
        echo "Removed worktree: $wt ($branch)"
    fi
done
```

---

## 11. Phase Breakdown — Multi-Agent Build

### Phase 0: Scaffolding (Single Agent — LEAD on main)

**Branch**: `main` (direct commits)
**Agent**: Lead only

```
Tasks:
1. git init + gh repo create fashion-techpack-ai --public
2. PLAN.md (this file) into repo root
3. docker-compose.yml skeleton (orchestrator + redis)
4. .gitignore (includes initiatives/, .env, __pycache__, node_modules)
5. .env.example
6. orchestrator/ directory scaffold (empty __init__.py files, requirements.txt)
7. gateway/ directory scaffold (package.json, tsconfig.json)
8. docs/ scaffold (empty ARCHITECTURE.md, DECISIONS.md)
9. initiatives/ directory with overview.md + phase folders
10. Initial README.md stub

Commits:
  chore: initial project scaffolding
  chore: docker-compose skeleton with orchestrator and redis
  docs: plan.md and project documentation structure
```

**CLAUDE.md for lead agent:**
```markdown
# Fashion Tech Pack AI — Lead Agent Context

You are the lead orchestrator for this project. Your responsibilities:
- Review PRs and merges from parallel agent branches
- Resolve merge conflicts
- Maintain PLAN.md, docs/ARCHITECTURE.md, docs/DECISIONS.md
- Update initiatives/overview.md after each phase
- Squash merge feature branches to main with conventional commits
- Run integration tests after merges

Project conventions:
- Conventional commits (feat:, fix:, test:, docs:, chore:)
- Squash merge to main — clean linear history
- initiatives/ is .gitignored — local dev orchestration only
- Each phase has its own branch prefix: phase0/, phase1/, etc.
```

---

### Phase 1: Services + Models (2 Parallel Agents)

**Worktrees:**
- Agent A: `fashion-techpack-ai-wt-models` → branch `phase1/models`
- Agent B: `fashion-techpack-ai-wt-services` → branch `phase1/services`

**Agent A — Domain Models:**
```
Tasks:
1. All Pydantic models in orchestrator/app/models/
   - brief.py (DesignBrief, GarmentType)
   - measurements.py (Measurements)
   - fabric.py (FabricSpec)
   - bom.py (BOMItem)
   - techpack.py (TechPack, ConstructionDetail)
   - state.py (TechPackState for LangGraph)
2. Seed data: seed/fabrics.json (50+ fabric entries)
3. Unit tests for model validation

Prompt for agent:
  "Read PLAN.md sections 4 (Domain Models) and 9 (Project Structure).
   Build ALL Pydantic domain models in orchestrator/app/models/.
   Create seed/fabrics.json with 50+ realistic fabric entries.
   Write unit tests in orchestrator/tests/test_models/.
   Commit after each model file."
```

**Agent B — Infrastructure Services:**
```
Tasks:
1. orchestrator/app/config.py (env vars, model routing config)
2. orchestrator/app/services/llm_client.py (OpenRouter wrapper)
3. orchestrator/app/services/embedding_service.py (OpenRouter embeddings)
4. orchestrator/app/services/rag_service.py (Supabase pgvector)
5. orchestrator/app/services/redis_service.py (cache layer)
6. seed/seed_embeddings.py (script to embed fabrics into Supabase)
7. Unit tests for each service (mock external calls)

Prompt for agent:
  "Read PLAN.md sections 2 (Tech Stack), 8 (Database Schema), 11 (Env Vars).
   Build ALL infrastructure services in orchestrator/app/services/.
   The LLM client must support model routing via config (different models
   per task type). The RAG service must use Supabase pgvector with cosine
   similarity. Write unit tests with mocked external calls.
   Commit after each service file."
```

**Lead merges:**
```bash
# After both agents complete:
git checkout main
git merge --squash phase1/models
git commit -m "feat(models): pydantic domain models and fabric seed data"
git merge --squash phase1/services
git commit -m "feat(services): openrouter, supabase, embedding, redis services"
```

---

### Phase 2: CrewAI Prototype (1-2 Agents)

**Worktrees:**
- Agent A: `fashion-techpack-ai-wt-crew` → branch `phase2/crewai`
- Agent B (optional): `fashion-techpack-ai-wt-tools` → branch `phase2/tools`

**Agent A — CrewAI Crew:**
```
Tasks:
1. orchestrator/app/crews/tools.py (shared tool functions for RAG, LLM)
2. orchestrator/app/crews/techpack_crew.py (4 agents + 4 tasks + crew)
3. orchestrator/app/api/crew_endpoint.py (POST /crew/techpacks)
4. Test: run crew against a sample brief, validate TechPack output
5. Document prompt iterations in initiatives/phase2-crewai-prototype/findings.md

Prompt for agent:
  "Read PLAN.md sections 3 (Architecture — CrewAI layer), 5 (Agent Definitions).
   Build the CrewAI prototype in orchestrator/app/crews/.
   Define 4 agents (Design Analyst, Fabric Specialist, Production Planner,
   Technical Writer) with roles, goals, backstories, and tool bindings.
   Use the shared services from app/services/ (llm_client, rag_service).
   The crew output must validate against TechPack Pydantic model.
   Add a FastAPI endpoint POST /crew/techpacks that runs the crew.
   Test against a sample brief. Commit after each agent definition."
```

**Lead merges:**
```bash
git checkout main
git merge --squash phase2/crewai
git commit -m "feat(crews): crewai techpack prototype with 4 agents"
```

---

### Phase 3: LangGraph Production (2-3 Parallel Agents)

**Worktrees:**
- Agent A: `fashion-techpack-ai-wt-agents` → branch `phase3/agents`
- Agent B: `fashion-techpack-ai-wt-graph` → branch `phase3/graph`
- Agent C (optional): `fashion-techpack-ai-wt-api` → branch `phase3/api`

**Agent A — LangGraph Node Functions:**
```
Tasks:
1. orchestrator/app/agents/brief_analyzer.py
2. orchestrator/app/agents/spec_extractor.py
3. orchestrator/app/agents/fabric_matcher.py
4. orchestrator/app/agents/bom_builder.py
5. orchestrator/app/agents/tech_pack_writer.py
6. Each agent: async function taking TechPackState, returning updated state
7. Unit tests per agent with mocked LLM responses

Prompt for agent:
  "Read PLAN.md sections 5 (Agent Definitions) and 4 (Domain Models — State).
   Build each LangGraph agent node as an async function in orchestrator/app/agents/.
   Each agent takes TechPackState and returns updated TechPackState.
   Reuse prompts validated in the CrewAI prototype (check app/crews/techpack_crew.py).
   Use services from app/services/ for LLM calls and RAG.
   Every agent output must Pydantic-validate before writing to state.
   Commit after each agent file."
```

**Agent B — LangGraph Workflow + API:**
```
Tasks:
1. orchestrator/app/graphs/techpack_graph.py (StateGraph definition)
2. Conditional edges (retry on validation failure)
3. Checkpointing with MemorySaver
4. orchestrator/app/api/techpacks.py (POST + GET endpoints)
5. WebSocket progress callback integration
6. Integration test: full pipeline with real LLM calls

Prompt for agent:
  "Read PLAN.md sections 6 (LangGraph Workflow) and 7 (API Design).
   Build the LangGraph state machine in orchestrator/app/graphs/techpack_graph.py.
   Wire all agent nodes from app/agents/ with proper edges.
   Add conditional retry edge on validation node.
   Add checkpointing with MemorySaver.
   Build FastAPI endpoints in app/api/techpacks.py.
   Include WebSocket progress callback that emits agent status updates.
   Commit after graph definition, then after API endpoints."
```

**Lead merges:**
```bash
git checkout main
git merge --squash phase3/agents
git commit -m "feat(agents): langgraph node functions for all 5 agents"
git merge --squash phase3/graph
git commit -m "feat(graphs): langgraph workflow with conditional retry and checkpointing"
```

---

### Phase 4: Node.js Gateway (2 Parallel Agents)

**Worktrees:**
- Agent A: `fashion-techpack-ai-wt-gateway-core` → branch `phase4/gateway-core`
- Agent B: `fashion-techpack-ai-wt-gateway-ws` → branch `phase4/gateway-ws`

**Agent A — Express Core:**
```
Tasks:
1. gateway/src/index.ts (Express app with middleware)
2. gateway/src/routes/techpacks.ts (proxy to FastAPI)
3. gateway/src/routes/fabrics.ts (proxy to FastAPI)
4. gateway/src/routes/health.ts
5. gateway/src/middleware/auth.ts (JWT)
6. gateway/src/middleware/rateLimit.ts
7. gateway/src/middleware/validation.ts (Zod schemas)
8. gateway/src/types/index.ts

Prompt for agent:
  "Read PLAN.md sections 7 (API Design) and 9 (Project Structure — gateway/).
   Build the Node.js Express gateway in TypeScript.
   All endpoints proxy to the FastAPI orchestrator at ORCHESTRATOR_URL.
   Implement JWT auth, rate limiting, and Zod request validation middleware.
   Use axios or fetch for proxying. Commit after each route file."
```

**Agent B — WebSocket + Integration:**
```
Tasks:
1. gateway/src/ws/techpackStream.ts (WebSocket handler)
2. Integration tests (gateway → orchestrator → agents)
3. gateway/Dockerfile

Prompt for agent:
  "Read PLAN.md section 7 (API Design — WebSocket endpoint).
   Build the WebSocket handler in gateway/src/ws/techpackStream.ts.
   It should connect to the orchestrator and relay agent progress events
   to the client in real-time. Write integration tests that verify the
   full flow: gateway receives request → orchestrator processes → WS
   streams progress. Build the gateway Dockerfile."
```

**Lead merges:**
```bash
git checkout main
git merge --squash phase4/gateway-core
git commit -m "feat(gateway): express typescript gateway with auth and routing"
git merge --squash phase4/gateway-ws
git commit -m "feat(gateway): websocket streaming and integration tests"
```

---

### Phase 5: Integration + Polish (1-2 Agents + LEAD)

**Worktrees:**
- Agent A: `fashion-techpack-ai-wt-infra` → branch `phase5/infra`
- LEAD: main (docs, README, final review)

**Agent A — Docker + CI:**
```
Tasks:
1. docker-compose.yml (gateway + orchestrator + redis, with Supabase hosted)
2. orchestrator/Dockerfile (multi-stage: deps → runtime)
3. .github/workflows/ci.yml (lint + test on push for both services)
4. Verify full stack starts and processes a request end-to-end

Prompt for agent:
  "Read PLAN.md sections 9 (Project Structure), 11 (Env Vars).
   Build docker-compose.yml that runs gateway, orchestrator, and redis.
   Build orchestrator Dockerfile (multi-stage, lean runtime).
   Build GitHub Actions CI workflow that lints and tests both services.
   Verify the full stack works: docker-compose up → POST brief → get tech pack."
```

**LEAD — Documentation:**
```
Tasks:
1. README.md (architecture overview, setup, API docs, demo walkthrough)
2. docs/ARCHITECTURE.md (system design document)
3. docs/DECISIONS.md (all ADRs from section 12)
4. Framework comparison table in README (CrewAI vs LangGraph results)
5. Final review of all code, cleanup, version tag

Lead does this directly on main after all merges.
```

---

## 12. Key ADRs to Document

### ADR-001: Hybrid Node.js + Python Architecture
**Decision**: Node.js gateway for API surface, Python/FastAPI for AI orchestration.
**Rationale**: Node.js provides the performance and ecosystem expected for a
production API gateway (auth, rate limiting, WebSocket). Python provides the AI/ML
ecosystem (LangGraph, LangChain, Pydantic) without fighting the tooling. Same
pattern used at scale: API gateway in one language, domain services in another.

### ADR-002: CrewAI for Prototyping, LangGraph for Production
**Decision**: Use CrewAI to validate agent roles, prompts, and tool chains. Then
migrate to LangGraph for the production implementation.
**Rationale**: CrewAI's role-based design (agent + goal + backstory) is the fastest
way to iterate on prompt engineering and validate tool bindings. But CrewAI lacks
typed state, conditional edges, checkpointing, and WebSocket-compatible progress
callbacks. LangGraph adds these production requirements. Keeping both implementations
lets us benchmark and provides an ADR backed by empirical data, not opinion.

### ADR-003: OpenRouter for Model Routing
**Decision**: Use OpenRouter as unified LLM gateway instead of direct API calls.
**Rationale**: Different agents have different cost/capability needs. OpenRouter
provides a single API with automatic fallbacks and unified billing. Switching models
is a config change, not a code change.

### ADR-004: Supabase pgvector over ChromaDB/FAISS
**Decision**: Use Supabase managed PostgreSQL with pgvector for vector storage.
**Rationale**: The fabric catalog is relational data with an embedding column.
pgvector lets us combine vector similarity with SQL filters in a single query.

### ADR-005: Structured Outputs with Pydantic Validation
**Decision**: Every agent produces Pydantic-validated JSON, not free text.
**Rationale**: Pydantic enforces type safety at every handoff between agents.
Same pattern as API request/response validation — applied to agent I/O.

### ADR-006: Git Worktrees for Parallel Agent Development
**Decision**: Use git worktrees with per-phase branches for parallel Claude Code
agent development, squash-merged to main by the lead.
**Rationale**: Each agent needs its own filesystem context and branch to avoid
conflicts. Worktrees share the same .git directory so branches are immediately
available across all checkouts. Squash merging keeps main history clean and linear.

---

## 13. Interview Talking Points

### "Walk me through the architecture."
"It's a hybrid system — Node.js gateway for the API surface, Python/FastAPI for AI
orchestration. I built it with two agent frameworks side by side: CrewAI for rapid
prototyping of agent roles and prompts, then LangGraph for the production pipeline
with typed state, conditional routing, and checkpointing. Five specialized agents
collaborate through a LangGraph state machine, each producing Pydantic-validated
output. The fabric matcher uses RAG against a Supabase pgvector catalog. The gateway
streams agent progress to clients via WebSocket."

### "Why both CrewAI AND LangGraph?"
"CrewAI is the fastest way to iterate on agent design — you define a role, goal,
backstory, and tools, and you can test a full pipeline in minutes. But for production
you need typed state, conditional edges, error recovery, and WebSocket-compatible
progress callbacks. LangGraph provides all of that. I use CrewAI to validate my
prompts and tool chains, then migrate the validated agents into LangGraph nodes.
Both implementations produce the same TechPack schema, so I can benchmark them
against each other — execution time, token cost, output quality."

### "How does the RAG pipeline work?"
"The fabric catalog lives in Supabase with pgvector. Each fabric's description is
embedded using text-embedding-3-small via OpenRouter and stored as a 1536-dimension
vector. When the fabric matcher agent runs, it embeds the design brief's fabric
preferences, does a cosine similarity search against the catalog, and a reranker
(GPT-4o-mini) scores the top results against the full context. The top 3 fabrics
flow into the next agent via the typed state dict."

### "How would you adapt this to Mango's conversational AI?"
"The pattern transfers directly. Replace fashion agents with customer service agents:
an intent classifier (my brief analyzer), specialist agents for order status, returns,
and styling (my fabric matcher and spec extractor), and a response composer (my tech
pack writer). The LangGraph state machine handles routing between them. The Node.js
gateway handles multi-channel delivery — web, WhatsApp, Instagram — same Express +
WebSocket pattern I use for agent progress streaming. The CrewAI layer would be how
you prototype new agent capabilities before promoting them to production."

---

## 14. Environment Variables

```env
# OpenRouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Redis
REDIS_URL=redis://localhost:6379

# Gateway
GATEWAY_PORT=3000
ORCHESTRATOR_URL=http://localhost:8000
JWT_SECRET=your-secret-here

# Orchestrator
ORCHESTRATOR_PORT=8000

# Model routing
MODEL_REASONING=anthropic/claude-sonnet-4
MODEL_EXTRACTION=openai/gpt-4o-mini
MODEL_EMBEDDING=openai/text-embedding-3-small
```

---

## 15. Lead Agent — Master Prompt

This is the prompt you paste into the LEAD Claude Code session on main.
The lead reads this plan, creates the initiative docs, and then instructs
you on which parallel agents to spawn and what prompts to give them.

```
Read PLAN.md for the complete project spec.

You are the LEAD agent for this project. Your responsibilities:
1. Create the initiatives/ directory structure per PLAN.md section 9
2. Execute Phase 0 (scaffolding) directly on main
3. After Phase 0, tell me which worktrees to create and what prompts
   to paste into each parallel agent session
4. After each phase, I will switch to your pane and you will:
   - Review the branches (git log, git diff main..branch-name)
   - Squash merge each branch to main with a conventional commit
   - Run tests to verify integration
   - Update initiatives/overview.md with phase status
   - Clean up worktrees
5. Maintain docs/ARCHITECTURE.md and docs/DECISIONS.md

Project conventions:
- Conventional commits, squash merge to main
- initiatives/ is .gitignored — local orchestration only
- Each phase branch prefix: phase0/, phase1/, phase2/, etc.
- Tests must pass before merge
- Use the model routing config from PLAN.md section 2
- All LLM calls go through OpenRouter — never direct provider APIs
```