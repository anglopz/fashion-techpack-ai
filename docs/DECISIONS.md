# Architecture Decision Records

## ADR-001: Hybrid Node.js + Python Architecture

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Node.js gateway for API surface, Python/FastAPI for AI orchestration.

**Rationale**: _To be documented._

---

## ADR-002: CrewAI for Prototyping, LangGraph for Production

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use CrewAI to validate agent roles, prompts, and tool chains. Then migrate to LangGraph for the production implementation.

**Rationale**: _To be documented._

---

## ADR-003: OpenRouter for Model Routing

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use OpenRouter as unified LLM gateway instead of direct API calls.

**Rationale**: _To be documented._

---

## ADR-004: Supabase pgvector over ChromaDB/FAISS

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use Supabase managed PostgreSQL with pgvector for vector storage.

**Rationale**: _To be documented._

---

## ADR-005: Structured Outputs with Pydantic Validation

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Every agent produces Pydantic-validated JSON, not free text.

**Rationale**: _To be documented._

---

## ADR-006: Git Worktrees for Parallel Agent Development

**Status**: Accepted
**Date**: 2026-03-25

**Decision**: Use git worktrees with per-phase branches for parallel Claude Code agent development, squash-merged to main by the lead.

**Rationale**: _To be documented._
