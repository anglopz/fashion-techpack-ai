# Phase 2: CrewAI Prototype — Plan

## Objective
Build a CrewAI-based tech pack generation crew to validate prompts, tools, and agent roles before LangGraph production build.

## Approach
Single agent in git worktree (phase2/crewai branch). Originally planned as TeamCreate but switched to direct execution due to agent reliability issues.

## Key Decisions
- 4 CrewAI agents: Design Analyst, Fabric Specialist, Production Planner, Technical Writer
- Sequential process (each agent's output feeds the next)
- @tool decorator for CrewAI tools (modern API)
- litellm required for CrewAI + OpenRouter integration
- POST /api/v1/crew/techpacks endpoint (async, returns 202)
