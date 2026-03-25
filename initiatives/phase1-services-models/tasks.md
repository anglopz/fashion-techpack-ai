# Phase 1: Services + Models — Tasks

## Agent A — Domain Models
- [x] brief.py: GarmentType enum + DesignBrief model
- [x] measurements.py: Measurements model with size ranges
- [x] fabric.py: FabricSpec model
- [x] bom.py: BOMItem model
- [x] techpack.py: TechPack + ConstructionDetail models
- [x] state.py: TechPackState TypedDict for LangGraph
- [x] seed/fabrics.json: 55 realistic fabric entries
- [x] Unit tests for all models (54 tests)

## Agent B — Infrastructure Services
- [x] config.py: Settings dataclass with ModelRouting, env loading
- [x] llm_client.py: AsyncOpenAI wrapper for OpenRouter
- [x] embedding_service.py: Text embedding via OpenRouter
- [x] rag_service.py: Supabase pgvector fabric search
- [x] redis_service.py: Async Redis with JSON serialization
- [x] main.py: FastAPI app with health endpoint
- [x] Unit tests with mocked externals (25 tests)

## Lead — Merge & Verify
- [x] Squash merge phase1/models → main
- [x] Squash merge phase1/services → main
- [x] All 79 tests passing
- [x] Clean up worktrees and branches
