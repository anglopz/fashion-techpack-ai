# Tasks & Lessons Learned

## Cross-Phase Lessons

- **litellm required for CrewAI + OpenRouter**: CrewAI's `openrouter/` prefix routes through litellm, not native providers. Added to requirements.txt in Phase 2.
- **Team agents can get stuck**: Opus 4.6 team agents hit "Germinating" hangs and permission blocks with context7 MCP tools. For single-agent phases, writing directly in the worktree is more reliable.
- **Merge order matters**: Always merge models/domain branches before services branches — services import from models.

## Blocked Items

_None currently._
