# Phase 1: Services + Models — Plan

## Objective
Build all Pydantic domain models and infrastructure services per PLAN.md sections 2, 4, 8, 14.

## Approach
Two parallel agents via TeamCreate, each in its own git worktree:
- **Agent A** (phase1/models): Domain models + seed data
- **Agent B** (phase1/services): Config, LLM client, embedding, RAG, Redis services + FastAPI main

## Merge Order
Models FIRST (services import from models).

## Key Decisions
- OpenRouter via openai SDK (OpenAI-compatible API)
- Model routing by task type (reasoning→claude-sonnet-4, extraction→gpt-4o-mini, embedding→text-embedding-3-small)
- Supabase pgvector for RAG with cosine similarity
- All external calls mocked in tests
