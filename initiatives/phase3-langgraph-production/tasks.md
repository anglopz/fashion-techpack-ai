# Phase 3: LangGraph Production — Tasks

## Agent A — Node Functions
- [ ] agents/brief_analyzer.py
- [ ] agents/spec_extractor.py
- [ ] agents/fabric_matcher.py
- [ ] agents/bom_builder.py
- [ ] agents/tech_pack_writer.py
- [ ] Unit tests for all agents

## Agent B — Graph + API
- [ ] graphs/techpack_graph.py: StateGraph with conditional edges
- [ ] api/techpack_endpoint.py: POST /api/v1/techpacks (LangGraph version)
- [ ] WebSocket progress streaming
- [ ] Redis checkpointing integration
- [ ] Unit + integration tests

## Lead — Merge & Verify
- [ ] Squash merge phase3/agents → main
- [ ] Squash merge phase3/graph → main
- [ ] All tests passing
- [ ] Worktree cleanup
