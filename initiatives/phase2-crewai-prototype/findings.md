# Phase 2: CrewAI Prototype — Findings

- **litellm is required for CrewAI + OpenRouter**: CrewAI's `openrouter/` model prefix routes through litellm, not native providers
- **Team agents unreliable for single-agent phases**: Both attempts (MCP permission block + Germinating hang) failed. Direct execution in worktree worked immediately.
- **@tool decorator is the modern CrewAI API**: `from crewai.tools import tool` — cleaner than subclassing BaseTool
- **_run_async helper needed**: CrewAI tools are sync but services are async; bridge with `asyncio.get_event_loop().run_until_complete()`
