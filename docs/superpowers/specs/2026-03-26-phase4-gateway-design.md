# Phase 4: Node.js API Gateway — Design Spec

**Date:** 2026-03-26
**Status:** Approved
**Depends on:** Phase 3 (LangGraph production) — complete

## Goal

Build a Node.js/Express/TypeScript API gateway that sits in front of the FastAPI orchestrator. The gateway handles auth, rate limiting, request validation, and WebSocket streaming relay. All business logic stays in the orchestrator — the gateway is a thin proxy layer.

## Architecture

```
Client → Express Gateway (Node.js) → FastAPI Orchestrator (Python)
              ↕ WebSocket relay ↕
```

Middleware chain per request: `CORS → rate-limit → JWT auth → Zod validation → route handler → axios proxy → response`

## Components

### Entry Point: `src/index.ts`

Express app factory with:
- CORS middleware (configurable origins via `CORS_ORIGINS` env, defaults to `*`)
- Middleware wiring in order: rate-limit, auth, routes
- WebSocket upgrade handling via `ws` library on the same HTTP server
- Graceful shutdown (SIGTERM/SIGINT close server + active connections)
- Reads config from env: `GATEWAY_PORT` (default 3000), `ORCHESTRATOR_URL` (default `http://localhost:8000`)

### Routes

#### `src/routes/techpacks.ts`
- `POST /api/v1/techpacks` — Validate body with Zod, proxy to `POST ORCHESTRATOR_URL/api/v1/techpacks`, return 202 with job ID + WS URL
- `GET /api/v1/techpacks/:id` — Proxy to `GET ORCHESTRATOR_URL/api/v1/techpacks/:id`, return result

#### `src/routes/fabrics.ts`
- `POST /api/v1/fabrics` — Validate body with Zod, proxy to orchestrator, return 201
- `GET /api/v1/fabrics/search` — Forward query params `?q=...&limit=...` to orchestrator, return results

#### `src/routes/health.ts`
- `GET /health` — Return `{ status: "ok", orchestrator: "ok"|"unreachable" }`. Pings orchestrator `/health` with a 2s timeout.

### Middleware

#### `src/middleware/auth.ts`
- JWT verification using `jsonwebtoken.verify()` against `JWT_SECRET` env var
- Extracts decoded payload to `req.user` (extends Express Request type)
- Skips auth for: `GET /health`
- Returns 401 with `{ error: "Missing or invalid token" }` on failure
- Algorithm: HS256

#### `src/middleware/rateLimit.ts`
- Uses `express-rate-limit`
- Default: 100 requests per 15-minute window
- Configurable via `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW_MS` env vars
- Returns standard 429 response

#### `src/middleware/validation.ts`
- Exports a `validate(schema: ZodSchema)` middleware factory
- Parses `req.body` against the Zod schema
- Returns 400 with `{ error: "Validation failed", details: zodErrors }` on failure
- Zod schemas defined in-file for each request type:
  - `CreateTechPackSchema` — description (required string), garment_type (optional), target_season (optional), fabric_preferences (string[]), color_palette (string[]), style_references (string[]), engine (enum "langgraph"|"crewai", default "langgraph")
  - `CreateFabricSchema` — name (required), composition (required), weight_gsm (positive number), width_cm (positive number), color (required), care_instructions (string[])

### WebSocket

#### `src/ws/techpackStream.ts`
- Handles WS upgrade at path `/api/v1/techpacks/:id/stream`
- On client connect: opens a WS connection to `ORCHESTRATOR_URL/api/v1/techpacks/:id/stream`
- Relays messages from orchestrator → client in real-time
- On orchestrator `done` event: forwards to client, closes both connections
- On orchestrator disconnect/error: sends error frame to client, closes
- On client disconnect: closes orchestrator connection
- JWT auth on WS: client must send token as first message or via `?token=` query param

### Types

#### `src/types/index.ts`
- `CreateTechPackRequest` — mirrors Zod schema
- `CreateTechPackResponse` — `{ id, status, engine, ws_url }`
- `TechPackResult` — `{ id, status, engine, tech_pack?, created_at, processing_time_ms }`
- `CreateFabricRequest` — mirrors Zod schema
- `FabricSearchResult` — `{ results: { id, name, similarity, ... }[] }`
- `WSMessage` — `{ agent?, status, message?, data?, event? }`
- `AuthPayload` — decoded JWT payload on `req.user`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_PORT` | `3000` | Gateway listen port |
| `ORCHESTRATOR_URL` | `http://localhost:8000` | FastAPI orchestrator base URL |
| `JWT_SECRET` | (required) | HS256 signing secret |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `RATE_LIMIT_MAX` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW_MS` | `900000` | Rate limit window (15 min) |

## Testing Strategy

- **Framework:** Jest + supertest + ts-jest
- **Mocking:** axios mocked for all proxy tests (no real orchestrator needed), `ws` mocked for WebSocket tests
- **Structure:** One test file per source file in `__tests__/` directory
- **Coverage targets:** All routes, middleware skip/block paths, validation pass/fail, WS relay lifecycle

### Test files
- `__tests__/routes/techpacks.test.ts`
- `__tests__/routes/fabrics.test.ts`
- `__tests__/routes/health.test.ts`
- `__tests__/middleware/auth.test.ts`
- `__tests__/middleware/rateLimit.test.ts`
- `__tests__/middleware/validation.test.ts`
- `__tests__/ws/techpackStream.test.ts`

## Dockerfile

Multi-stage build:
1. **Build stage:** `node:20-slim`, `npm ci`, `npx tsc`
2. **Runtime stage:** `node:20-slim`, copy `dist/` + `node_modules/` (production only via `npm ci --omit=dev`), expose `GATEWAY_PORT`, `CMD ["node", "dist/index.js"]`

## Stream Split for Parallel Development

### Stream A: gateway-core (branch `phase4/gateway-core`)
- `src/index.ts`
- `src/routes/techpacks.ts`, `src/routes/fabrics.ts`, `src/routes/health.ts`
- `src/middleware/auth.ts`, `src/middleware/rateLimit.ts`, `src/middleware/validation.ts`
- `src/types/index.ts`
- All `__tests__/routes/` and `__tests__/middleware/` tests

### Stream B: gateway-ws (branch `phase4/gateway-ws`)
- `src/ws/techpackStream.ts`
- `__tests__/ws/techpackStream.test.ts`
- `Dockerfile`

**Merge order:** gateway-core first, then gateway-ws (WS handler imports from types).
