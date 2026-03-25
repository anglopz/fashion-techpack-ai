# Phase 2: CrewAI Prototype — Tasks

## Tools
- [x] crews/tools.py: brief_parser_tool (keyword-based garment/fabric/color extraction)
- [x] crews/tools.py: fabric_search_tool (RAGService wrapper)
- [x] crews/tools.py: embedding_tool (EmbeddingService wrapper)

## Agents & Crew
- [x] crews/techpack_crew.py: Design Analyst agent (gpt-4o-mini, brief_parser_tool)
- [x] crews/techpack_crew.py: Fabric Specialist agent (gpt-4o-mini, fabric_search + embedding tools)
- [x] crews/techpack_crew.py: Production Planner agent (gpt-4o-mini, no tools)
- [x] crews/techpack_crew.py: Technical Writer agent (claude-sonnet-4, no tools)
- [x] crews/techpack_crew.py: Sequential crew with 4 tasks

## API
- [x] api/crew_endpoint.py: POST /crew/techpacks returning 202
- [x] main.py: Register crew router

## Infrastructure
- [x] Added litellm to requirements.txt

## Tests
- [x] 28 new tests (tools, agents, crew, endpoint)
- [x] 107 total tests passing

## Lead — Merge & Verify
- [x] Squash merge phase2/crewai → main
- [x] All 107 tests passing
- [x] Worktree cleanup
