# Architecture Decision Records

## ADR-001: Hybrid Node.js + Python Architecture

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Node.js gateway for API surface, Python/FastAPI for AI orchestration.

**Rationale**: Node.js provides the performance and ecosystem expected for a production API gateway (auth, rate limiting, WebSocket). Python provides the AI/ML ecosystem (LangGraph, LangChain, Pydantic) without fighting the tooling. Same pattern used at scale: API gateway in one language, domain services in another.

---

## ADR-002: CrewAI for Prototyping, LangGraph for Production

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use CrewAI to validate agent roles, prompts, and tool chains. Then migrate to LangGraph for the production implementation.

**Rationale**: CrewAI's role-based design (agent + goal + backstory) is the fastest way to iterate on prompt engineering and validate tool bindings. But CrewAI lacks typed state, conditional edges, checkpointing, and WebSocket-compatible progress callbacks. LangGraph adds these production requirements. Keeping both implementations lets us benchmark and provides an ADR backed by empirical data, not opinion.

---

## ADR-003: OpenRouter for Model Routing

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use OpenRouter as unified LLM gateway instead of direct API calls.

**Rationale**: Different agents have different cost/capability needs. OpenRouter provides a single API with automatic fallbacks and unified billing. Switching models is a config change, not a code change.

---

## ADR-004: Supabase pgvector over ChromaDB/FAISS

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use Supabase managed PostgreSQL with pgvector for vector storage.

**Rationale**: The fabric catalog is relational data with an embedding column. pgvector lets us combine vector similarity with SQL filters in a single query.

---

## ADR-005: Structured Outputs with Pydantic Validation

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Every agent produces Pydantic-validated JSON, not free text.

**Rationale**: Pydantic enforces type safety at every handoff between agents. Same pattern as API request/response validation — applied to agent I/O.

---

## ADR-006: Git Worktrees for Parallel Agent Development

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use git worktrees with per-phase branches for parallel Claude Code agent development, squash-merged to main by the lead.

**Rationale**: Each agent needs its own filesystem context and branch to avoid conflicts. Worktrees share the same .git directory so branches are immediately available across all checkouts. Squash merging keeps main history clean and linear.
