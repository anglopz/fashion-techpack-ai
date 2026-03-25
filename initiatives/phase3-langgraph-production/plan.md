# Phase 3: LangGraph Production — Plan

## Objective
Replace CrewAI prototype with production LangGraph orchestration: typed state, conditional edges, checkpointing, WebSocket streaming.

## Approach
Two parallel agents via worktrees:
- **Agent A** (phase3/agents): 5 LangGraph node functions in orchestrator/app/agents/
- **Agent B** (phase3/graph): StateGraph definition + API endpoints + WebSocket progress

## Merge Order
Agents FIRST (graph imports agent nodes).

## Agent Node Functions (PLAN.md section 5)
1. brief_analyzer.py — Parse unstructured brief → DesignBrief
2. spec_extractor.py — Extract measurements + construction details
3. fabric_matcher.py — RAG search for matching fabrics
4. bom_builder.py — Generate bill of materials
5. tech_pack_writer.py — Compile final TechPack document

## Graph (PLAN.md section 6)
- StateGraph with TechPackState
- Conditional edges based on validation results
- Redis checkpointing for resume
- WebSocket progress updates per node completion
