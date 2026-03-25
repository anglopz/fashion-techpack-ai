# Phase 1: Services + Models — Findings

- TeamCreate with 2 agents in separate worktrees worked well for parallel development
- Merge order matters: models must land on main before services (import dependency)
- 55 seed fabrics provide good variety for RAG testing
- AsyncOpenAI SDK works seamlessly with OpenRouter's /api/v1 endpoint
