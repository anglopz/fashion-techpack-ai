# Phase 4: Node.js API Gateway — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Node.js/Express/TypeScript API gateway that proxies requests to the FastAPI orchestrator, with JWT auth, rate limiting, Zod validation, and WebSocket streaming relay.

**Architecture:** Express gateway at `gateway/src/` with middleware chain (CORS → rate-limit → JWT auth → Zod validation → route handler → axios proxy). WebSocket handler relays agent progress from orchestrator to client. All business logic stays in the orchestrator.

**Tech Stack:** Express 4, TypeScript 5, axios, ws, zod, jsonwebtoken, express-rate-limit, Jest + supertest for testing.

**Existing infrastructure (do NOT recreate):**
- `gateway/package.json` — dependencies already declared (express, axios, ws, zod, jsonwebtoken, express-rate-limit, cors, dotenv)
- `gateway/tsconfig.json` — configured for ES2022, strict, commonjs
- `gateway/Dockerfile` — stub, needs full multi-stage build
- `gateway/src/routes/`, `gateway/src/middleware/`, `gateway/src/ws/`, `gateway/src/types/` — empty dirs with .gitkeep

**Orchestrator endpoints (gateway proxies to these):**
- `POST /api/v1/techpacks` — creates tech pack job, returns 202 with `{ id, status, engine, ws_url }`
- `GET /api/v1/techpacks/:id` — returns job status/result
- `WS /api/v1/techpacks/:id/stream` — streams agent messages until done
- `GET /health` — returns `{ status: "ok" }`

**Merge strategy:** Stream A (gateway-core) merged to main first, then Stream B (gateway-ws). WS handler imports from types defined in Stream A.

---

## File Structure

### Stream A — Gateway Core

| File | Responsibility |
|------|---------------|
| `gateway/src/types/index.ts` | Shared TypeScript interfaces |
| `gateway/src/middleware/auth.ts` | JWT verification, req.user extraction |
| `gateway/src/middleware/rateLimit.ts` | express-rate-limit config |
| `gateway/src/middleware/validation.ts` | Zod schema validation factory |
| `gateway/src/routes/health.ts` | Health check with orchestrator ping |
| `gateway/src/routes/techpacks.ts` | Tech pack CRUD proxy |
| `gateway/src/routes/fabrics.ts` | Fabric catalog proxy |
| `gateway/src/index.ts` | Express app factory, middleware wiring |
| `gateway/__tests__/middleware/auth.test.ts` | Auth middleware tests |
| `gateway/__tests__/middleware/rateLimit.test.ts` | Rate limit tests |
| `gateway/__tests__/middleware/validation.test.ts` | Validation tests |
| `gateway/__tests__/routes/health.test.ts` | Health route tests |
| `gateway/__tests__/routes/techpacks.test.ts` | Techpacks route tests |
| `gateway/__tests__/routes/fabrics.test.ts` | Fabrics route tests |

### Stream B — WebSocket + Dockerfile

| File | Responsibility |
|------|---------------|
| `gateway/src/ws/techpackStream.ts` | WS relay between client and orchestrator |
| `gateway/__tests__/ws/techpackStream.test.ts` | WS handler tests |
| `gateway/Dockerfile` | Multi-stage production build |

---

## Stream A: Gateway Core

### Task 1: Project setup — install dependencies and configure Jest

**Files:**
- Modify: `gateway/package.json`
- Create: `gateway/jest.config.ts`

- [ ] **Step 1: Install dependencies**

```bash
cd gateway
npm install
npm install --save-dev jest ts-jest @types/jest supertest @types/supertest
```

- [ ] **Step 2: Create Jest config**

```typescript
// gateway/jest.config.ts
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/__tests__"],
  moduleFileExtensions: ["ts", "js", "json"],
  testMatch: ["**/*.test.ts"],
};

export default config;
```

- [ ] **Step 3: Add test script to package.json**

Add to `scripts` in `package.json`:
```json
"test": "jest --verbose",
"test:watch": "jest --watch"
```

- [ ] **Step 4: Verify Jest runs (no tests yet)**

Run: `npm test`
Expected: "No tests found" (not an error)

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json jest.config.ts
git commit -m "chore(gateway): install dependencies and configure jest"
```

---

### Task 2: TypeScript types

**Files:**
- Create: `gateway/src/types/index.ts`
- Test: `gateway/__tests__/types/index.test.ts`

- [ ] **Step 1: Write the type test**

```typescript
// gateway/__tests__/types/index.test.ts
import {
  CreateTechPackRequest,
  CreateTechPackResponse,
  CreateFabricRequest,
  FabricSearchResult,
  WSMessage,
  AuthPayload,
} from "../src/types";

describe("types", () => {
  it("CreateTechPackRequest has required fields", () => {
    const req: CreateTechPackRequest = {
      description: "Organic cotton t-shirt",
    };
    expect(req.description).toBe("Organic cotton t-shirt");
    expect(req.engine).toBeUndefined();
  });

  it("CreateTechPackRequest accepts all optional fields", () => {
    const req: CreateTechPackRequest = {
      description: "test",
      garment_type: "top",
      target_season: "SS26",
      fabric_preferences: ["cotton"],
      color_palette: ["#000"],
      style_references: ["ref1"],
      engine: "langgraph",
    };
    expect(req.engine).toBe("langgraph");
  });

  it("CreateTechPackResponse has all fields", () => {
    const res: CreateTechPackResponse = {
      id: "tp_abc123",
      status: "processing",
      engine: "langgraph",
      ws_url: "/api/v1/techpacks/tp_abc123/stream",
    };
    expect(res.id).toBe("tp_abc123");
  });

  it("CreateFabricRequest has required fields", () => {
    const req: CreateFabricRequest = {
      name: "Organic Cotton Jersey",
      composition: "100% Organic Cotton",
      weight_gsm: 180,
      width_cm: 150,
      color: "Natural White",
      care_instructions: ["Machine wash 30°C"],
    };
    expect(req.name).toBe("Organic Cotton Jersey");
  });

  it("WSMessage represents agent progress", () => {
    const msg: WSMessage = {
      agent: "brief_analyzer",
      status: "running",
      message: "Parsing design brief...",
    };
    expect(msg.agent).toBe("brief_analyzer");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/types/index.test.ts --verbose`
Expected: FAIL — cannot find module `../src/types`

- [ ] **Step 3: Write the types**

```typescript
// gateway/src/types/index.ts

export interface CreateTechPackRequest {
  description: string;
  garment_type?: string;
  target_season?: string;
  fabric_preferences?: string[];
  color_palette?: string[];
  style_references?: string[];
  engine?: "langgraph" | "crewai";
}

export interface CreateTechPackResponse {
  id: string;
  status: string;
  engine: string;
  ws_url: string;
}

export interface TechPackResult {
  id: string;
  status: string;
  engine: string;
  tech_pack?: Record<string, unknown>;
  created_at?: string;
  processing_time_ms?: number;
}

export interface CreateFabricRequest {
  name: string;
  composition: string;
  weight_gsm: number;
  width_cm: number;
  color: string;
  care_instructions: string[];
}

export interface FabricSearchResult {
  results: Array<{
    id: string;
    name: string;
    similarity: number;
    [key: string]: unknown;
  }>;
}

export interface WSMessage {
  agent?: string;
  status: string;
  message?: string;
  data?: Record<string, unknown>;
  event?: string;
}

export interface AuthPayload {
  sub: string;
  iat: number;
  exp: number;
  [key: string]: unknown;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/types/index.test.ts --verbose`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/types/index.ts __tests__/types/index.test.ts
git commit -m "feat(gateway): typescript type definitions"
```

---

### Task 3: Auth middleware

**Files:**
- Create: `gateway/src/middleware/auth.ts`
- Test: `gateway/__tests__/middleware/auth.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/middleware/auth.test.ts
import express from "express";
import request from "supertest";
import jwt from "jsonwebtoken";
import { authMiddleware } from "../src/middleware/auth";

const TEST_SECRET = "test-jwt-secret";

function buildApp(): express.Express {
  const app = express();
  app.use(authMiddleware(TEST_SECRET));
  app.get("/protected", (req, res) => {
    res.json({ user: (req as any).user });
  });
  app.get("/health", (_req, res) => {
    res.json({ status: "ok" });
  });
  return app;
}

describe("authMiddleware", () => {
  const app = buildApp();

  it("returns 401 when no Authorization header", async () => {
    const res = await request(app).get("/protected");
    expect(res.status).toBe(401);
    expect(res.body.error).toBe("Missing or invalid token");
  });

  it("returns 401 for invalid token", async () => {
    const res = await request(app)
      .get("/protected")
      .set("Authorization", "Bearer invalid-token");
    expect(res.status).toBe(401);
    expect(res.body.error).toBe("Missing or invalid token");
  });

  it("passes with valid token and sets req.user", async () => {
    const token = jwt.sign({ sub: "user-123" }, TEST_SECRET, {
      algorithm: "HS256",
      expiresIn: "1h",
    });
    const res = await request(app)
      .get("/protected")
      .set("Authorization", `Bearer ${token}`);
    expect(res.status).toBe(200);
    expect(res.body.user.sub).toBe("user-123");
  });

  it("skips auth for /health", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });

  it("returns 401 for expired token", async () => {
    const token = jwt.sign({ sub: "user-123" }, TEST_SECRET, {
      algorithm: "HS256",
      expiresIn: "-1s",
    });
    const res = await request(app)
      .get("/protected")
      .set("Authorization", `Bearer ${token}`);
    expect(res.status).toBe(401);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/middleware/auth.test.ts --verbose`
Expected: FAIL — cannot find module `../src/middleware/auth`

- [ ] **Step 3: Implement auth middleware**

```typescript
// gateway/src/middleware/auth.ts
import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { AuthPayload } from "../types";

declare global {
  namespace Express {
    interface Request {
      user?: AuthPayload;
    }
  }
}

const SKIP_AUTH_PATHS = ["/health"];

export function authMiddleware(secret: string) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (SKIP_AUTH_PATHS.includes(req.path)) {
      next();
      return;
    }

    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      res.status(401).json({ error: "Missing or invalid token" });
      return;
    }

    const token = authHeader.slice(7);
    try {
      const decoded = jwt.verify(token, secret, {
        algorithms: ["HS256"],
      }) as AuthPayload;
      req.user = decoded;
      next();
    } catch {
      res.status(401).json({ error: "Missing or invalid token" });
    }
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/middleware/auth.test.ts --verbose`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/middleware/auth.ts __tests__/middleware/auth.test.ts
git commit -m "feat(gateway): jwt auth middleware"
```

---

### Task 4: Rate limit middleware

**Files:**
- Create: `gateway/src/middleware/rateLimit.ts`
- Test: `gateway/__tests__/middleware/rateLimit.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/middleware/rateLimit.test.ts
import express from "express";
import request from "supertest";
import { createRateLimiter } from "../src/middleware/rateLimit";

function buildApp(max: number, windowMs: number): express.Express {
  const app = express();
  app.use(createRateLimiter(max, windowMs));
  app.get("/test", (_req, res) => {
    res.json({ ok: true });
  });
  return app;
}

describe("createRateLimiter", () => {
  it("allows requests under the limit", async () => {
    const app = buildApp(5, 60000);
    const res = await request(app).get("/test");
    expect(res.status).toBe(200);
  });

  it("blocks requests over the limit with 429", async () => {
    const app = buildApp(2, 60000);
    await request(app).get("/test");
    await request(app).get("/test");
    const res = await request(app).get("/test");
    expect(res.status).toBe(429);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/middleware/rateLimit.test.ts --verbose`
Expected: FAIL — cannot find module

- [ ] **Step 3: Implement rate limiter**

```typescript
// gateway/src/middleware/rateLimit.ts
import rateLimit from "express-rate-limit";

export function createRateLimiter(
  max: number = 100,
  windowMs: number = 15 * 60 * 1000,
) {
  return rateLimit({
    windowMs,
    max,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests, please try again later" },
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/middleware/rateLimit.test.ts --verbose`
Expected: PASS — both tests pass

- [ ] **Step 5: Commit**

```bash
git add src/middleware/rateLimit.ts __tests__/middleware/rateLimit.test.ts
git commit -m "feat(gateway): rate limit middleware"
```

---

### Task 5: Validation middleware with Zod schemas

**Files:**
- Create: `gateway/src/middleware/validation.ts`
- Test: `gateway/__tests__/middleware/validation.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/middleware/validation.test.ts
import express from "express";
import request from "supertest";
import {
  validate,
  CreateTechPackSchema,
  CreateFabricSchema,
} from "../src/middleware/validation";

function buildApp(schema: any): express.Express {
  const app = express();
  app.use(express.json());
  app.post("/test", validate(schema), (_req, res) => {
    res.json({ ok: true });
  });
  return app;
}

describe("validate middleware", () => {
  describe("CreateTechPackSchema", () => {
    const app = buildApp(CreateTechPackSchema);

    it("passes with valid minimal body", async () => {
      const res = await request(app)
        .post("/test")
        .send({ description: "A cotton t-shirt" });
      expect(res.status).toBe(200);
    });

    it("passes with all optional fields", async () => {
      const res = await request(app).post("/test").send({
        description: "A cotton t-shirt",
        garment_type: "top",
        target_season: "SS26",
        fabric_preferences: ["cotton"],
        color_palette: ["#000"],
        style_references: ["ref"],
        engine: "langgraph",
      });
      expect(res.status).toBe(200);
    });

    it("rejects missing description", async () => {
      const res = await request(app).post("/test").send({});
      expect(res.status).toBe(400);
      expect(res.body.error).toBe("Validation failed");
      expect(res.body.details).toBeDefined();
    });

    it("rejects invalid engine value", async () => {
      const res = await request(app)
        .post("/test")
        .send({ description: "test", engine: "invalid" });
      expect(res.status).toBe(400);
    });
  });

  describe("CreateFabricSchema", () => {
    const app = buildApp(CreateFabricSchema);

    it("passes with valid body", async () => {
      const res = await request(app).post("/test").send({
        name: "Organic Cotton Jersey",
        composition: "100% Organic Cotton",
        weight_gsm: 180,
        width_cm: 150,
        color: "Natural White",
        care_instructions: ["Machine wash 30°C"],
      });
      expect(res.status).toBe(200);
    });

    it("rejects negative weight_gsm", async () => {
      const res = await request(app).post("/test").send({
        name: "Test",
        composition: "Test",
        weight_gsm: -1,
        width_cm: 150,
        color: "White",
        care_instructions: [],
      });
      expect(res.status).toBe(400);
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/middleware/validation.test.ts --verbose`
Expected: FAIL — cannot find module

- [ ] **Step 3: Implement validation middleware**

```typescript
// gateway/src/middleware/validation.ts
import { Request, Response, NextFunction } from "express";
import { ZodSchema, z } from "zod";

export function validate(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({
        error: "Validation failed",
        details: result.error.issues,
      });
      return;
    }
    req.body = result.data;
    next();
  };
}

export const CreateTechPackSchema = z.object({
  description: z.string().min(1),
  garment_type: z.string().optional(),
  target_season: z.string().optional(),
  fabric_preferences: z.array(z.string()).default([]),
  color_palette: z.array(z.string()).default([]),
  style_references: z.array(z.string()).default([]),
  engine: z.enum(["langgraph", "crewai"]).default("langgraph"),
});

export const CreateFabricSchema = z.object({
  name: z.string().min(1),
  composition: z.string().min(1),
  weight_gsm: z.number().positive(),
  width_cm: z.number().positive(),
  color: z.string().min(1),
  care_instructions: z.array(z.string()),
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/middleware/validation.test.ts --verbose`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/middleware/validation.ts __tests__/middleware/validation.test.ts
git commit -m "feat(gateway): zod validation middleware with schemas"
```

---

### Task 6: Health route

**Files:**
- Create: `gateway/src/routes/health.ts`
- Test: `gateway/__tests__/routes/health.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/routes/health.test.ts
import express from "express";
import request from "supertest";
import axios from "axios";
import { healthRouter } from "../src/routes/health";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

function buildApp(): express.Express {
  const app = express();
  app.use("/health", healthRouter("http://localhost:8000"));
  return app;
}

describe("GET /health", () => {
  it("returns ok with orchestrator reachable", async () => {
    mockedAxios.get.mockResolvedValue({ data: { status: "ok" } });
    const app = buildApp();
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
    expect(res.body.orchestrator).toBe("ok");
  });

  it("returns ok with orchestrator unreachable", async () => {
    mockedAxios.get.mockRejectedValue(new Error("ECONNREFUSED"));
    const app = buildApp();
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
    expect(res.body.orchestrator).toBe("unreachable");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/routes/health.test.ts --verbose`
Expected: FAIL — cannot find module

- [ ] **Step 3: Implement health route**

```typescript
// gateway/src/routes/health.ts
import { Router } from "express";
import axios from "axios";

export function healthRouter(orchestratorUrl: string): Router {
  const router = Router();

  router.get("/", async (_req, res) => {
    let orchestratorStatus = "unreachable";
    try {
      await axios.get(`${orchestratorUrl}/health`, { timeout: 2000 });
      orchestratorStatus = "ok";
    } catch {
      // orchestrator is down — still report gateway as ok
    }

    res.json({
      status: "ok",
      orchestrator: orchestratorStatus,
    });
  });

  return router;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/routes/health.test.ts --verbose`
Expected: PASS — both tests pass

- [ ] **Step 5: Commit**

```bash
git add src/routes/health.ts __tests__/routes/health.test.ts
git commit -m "feat(gateway): health check route with orchestrator ping"
```

---

### Task 7: Techpacks route

**Files:**
- Create: `gateway/src/routes/techpacks.ts`
- Test: `gateway/__tests__/routes/techpacks.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/routes/techpacks.test.ts
import express from "express";
import request from "supertest";
import axios from "axios";
import { techpacksRouter } from "../src/routes/techpacks";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

function buildApp(): express.Express {
  const app = express();
  app.use(express.json());
  app.use("/api/v1/techpacks", techpacksRouter("http://localhost:8000"));
  return app;
}

describe("techpacks routes", () => {
  afterEach(() => jest.clearAllMocks());

  describe("POST /api/v1/techpacks", () => {
    it("proxies to orchestrator and returns 202", async () => {
      const orchestratorResponse = {
        id: "tp_abc123",
        status: "processing",
        engine: "langgraph",
        ws_url: "/api/v1/techpacks/tp_abc123/stream",
      };
      mockedAxios.post.mockResolvedValue({
        status: 202,
        data: orchestratorResponse,
      });

      const app = buildApp();
      const res = await request(app)
        .post("/api/v1/techpacks")
        .send({ description: "Organic cotton t-shirt for SS26" });

      expect(res.status).toBe(202);
      expect(res.body.id).toBe("tp_abc123");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/techpacks",
        expect.objectContaining({ description: "Organic cotton t-shirt for SS26" }),
      );
    });

    it("returns 502 when orchestrator is down", async () => {
      mockedAxios.post.mockRejectedValue(new Error("ECONNREFUSED"));
      const app = buildApp();
      const res = await request(app)
        .post("/api/v1/techpacks")
        .send({ description: "test" });
      expect(res.status).toBe(502);
      expect(res.body.error).toBe("Orchestrator unavailable");
    });
  });

  describe("GET /api/v1/techpacks/:id", () => {
    it("proxies to orchestrator and returns result", async () => {
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: { id: "tp_abc123", status: "completed" },
      });

      const app = buildApp();
      const res = await request(app).get("/api/v1/techpacks/tp_abc123");

      expect(res.status).toBe(200);
      expect(res.body.id).toBe("tp_abc123");
      expect(mockedAxios.get).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/techpacks/tp_abc123",
      );
    });

    it("returns 404 when orchestrator returns 404", async () => {
      const err: any = new Error("Not found");
      err.response = { status: 404, data: { detail: "Tech pack not found" } };
      mockedAxios.get.mockRejectedValue(err);

      const app = buildApp();
      const res = await request(app).get("/api/v1/techpacks/tp_nonexistent");
      expect(res.status).toBe(404);
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/routes/techpacks.test.ts --verbose`
Expected: FAIL — cannot find module

- [ ] **Step 3: Implement techpacks route**

```typescript
// gateway/src/routes/techpacks.ts
import { Router } from "express";
import axios from "axios";

export function techpacksRouter(orchestratorUrl: string): Router {
  const router = Router();

  router.post("/", async (req, res) => {
    try {
      const response = await axios.post(
        `${orchestratorUrl}/api/v1/techpacks`,
        req.body,
      );
      res.status(response.status).json(response.data);
    } catch (err: any) {
      if (err.response) {
        res.status(err.response.status).json(err.response.data);
      } else {
        res.status(502).json({ error: "Orchestrator unavailable" });
      }
    }
  });

  router.get("/:id", async (req, res) => {
    try {
      const response = await axios.get(
        `${orchestratorUrl}/api/v1/techpacks/${req.params.id}`,
      );
      res.status(response.status).json(response.data);
    } catch (err: any) {
      if (err.response) {
        res.status(err.response.status).json(err.response.data);
      } else {
        res.status(502).json({ error: "Orchestrator unavailable" });
      }
    }
  });

  return router;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/routes/techpacks.test.ts --verbose`
Expected: PASS — all 4 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/routes/techpacks.ts __tests__/routes/techpacks.test.ts
git commit -m "feat(gateway): techpacks route with orchestrator proxy"
```

---

### Task 8: Fabrics route

**Files:**
- Create: `gateway/src/routes/fabrics.ts`
- Test: `gateway/__tests__/routes/fabrics.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/routes/fabrics.test.ts
import express from "express";
import request from "supertest";
import axios from "axios";
import { fabricsRouter } from "../src/routes/fabrics";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

function buildApp(): express.Express {
  const app = express();
  app.use(express.json());
  app.use("/api/v1/fabrics", fabricsRouter("http://localhost:8000"));
  return app;
}

describe("fabrics routes", () => {
  afterEach(() => jest.clearAllMocks());

  describe("POST /api/v1/fabrics", () => {
    it("proxies to orchestrator and returns 201", async () => {
      mockedAxios.post.mockResolvedValue({
        status: 201,
        data: { id: "fab_xyz789", name: "Organic Cotton Jersey", embedded: true },
      });

      const app = buildApp();
      const res = await request(app).post("/api/v1/fabrics").send({
        name: "Organic Cotton Jersey",
        composition: "100% Organic Cotton",
        weight_gsm: 180,
        width_cm: 150,
        color: "Natural White",
        care_instructions: ["Machine wash 30°C"],
      });

      expect(res.status).toBe(201);
      expect(res.body.id).toBe("fab_xyz789");
    });

    it("returns 502 when orchestrator is down", async () => {
      mockedAxios.post.mockRejectedValue(new Error("ECONNREFUSED"));
      const app = buildApp();
      const res = await request(app).post("/api/v1/fabrics").send({
        name: "Test",
        composition: "Test",
        weight_gsm: 180,
        width_cm: 150,
        color: "White",
        care_instructions: [],
      });
      expect(res.status).toBe(502);
    });
  });

  describe("GET /api/v1/fabrics/search", () => {
    it("proxies search query to orchestrator", async () => {
      mockedAxios.get.mockResolvedValue({
        status: 200,
        data: {
          results: [
            { id: "fab_001", name: "Organic Cotton Jersey", similarity: 0.92 },
          ],
        },
      });

      const app = buildApp();
      const res = await request(app).get(
        "/api/v1/fabrics/search?q=lightweight+cotton&limit=5",
      );

      expect(res.status).toBe(200);
      expect(res.body.results).toHaveLength(1);
      expect(mockedAxios.get).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/fabrics/search",
        { params: expect.objectContaining({ q: "lightweight cotton" }) },
      );
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/routes/fabrics.test.ts --verbose`
Expected: FAIL — cannot find module

- [ ] **Step 3: Implement fabrics route**

```typescript
// gateway/src/routes/fabrics.ts
import { Router } from "express";
import axios from "axios";

export function fabricsRouter(orchestratorUrl: string): Router {
  const router = Router();

  router.post("/", async (req, res) => {
    try {
      const response = await axios.post(
        `${orchestratorUrl}/api/v1/fabrics`,
        req.body,
      );
      res.status(response.status).json(response.data);
    } catch (err: any) {
      if (err.response) {
        res.status(err.response.status).json(err.response.data);
      } else {
        res.status(502).json({ error: "Orchestrator unavailable" });
      }
    }
  });

  router.get("/search", async (req, res) => {
    try {
      const response = await axios.get(
        `${orchestratorUrl}/api/v1/fabrics/search`,
        { params: req.query },
      );
      res.status(response.status).json(response.data);
    } catch (err: any) {
      if (err.response) {
        res.status(err.response.status).json(err.response.data);
      } else {
        res.status(502).json({ error: "Orchestrator unavailable" });
      }
    }
  });

  return router;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/routes/fabrics.test.ts --verbose`
Expected: PASS — all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/routes/fabrics.ts __tests__/routes/fabrics.test.ts
git commit -m "feat(gateway): fabrics route with catalog proxy and search"
```

---

### Task 9: Express app entry point

**Files:**
- Create: `gateway/src/index.ts`
- Test: `gateway/__tests__/app.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/app.test.ts
import request from "supertest";
import jwt from "jsonwebtoken";
import { createApp } from "../src/index";

// Mock axios to prevent real orchestrator calls
jest.mock("axios");

const TEST_SECRET = "test-secret-for-app";

describe("Express app", () => {
  const app = createApp({
    orchestratorUrl: "http://localhost:8000",
    jwtSecret: TEST_SECRET,
    rateLimitMax: 1000,
    rateLimitWindowMs: 60000,
  });

  function makeToken(payload: object = { sub: "user-1" }): string {
    return jwt.sign(payload, TEST_SECRET, { algorithm: "HS256", expiresIn: "1h" });
  }

  it("GET /health works without auth", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });

  it("POST /api/v1/techpacks requires auth", async () => {
    const res = await request(app)
      .post("/api/v1/techpacks")
      .send({ description: "test" });
    expect(res.status).toBe(401);
  });

  it("POST /api/v1/techpacks with auth passes to route", async () => {
    const axios = require("axios");
    axios.post.mockResolvedValue({
      status: 202,
      data: { id: "tp_1", status: "processing", engine: "langgraph", ws_url: "/ws" },
    });

    const res = await request(app)
      .post("/api/v1/techpacks")
      .set("Authorization", `Bearer ${makeToken()}`)
      .send({ description: "test" });
    expect(res.status).toBe(202);
  });

  it("returns 400 for invalid request body", async () => {
    const res = await request(app)
      .post("/api/v1/techpacks")
      .set("Authorization", `Bearer ${makeToken()}`)
      .send({});
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("Validation failed");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/app.test.ts --verbose`
Expected: FAIL — cannot find module `../src/index`

- [ ] **Step 3: Implement the app factory**

```typescript
// gateway/src/index.ts
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { authMiddleware } from "./middleware/auth";
import { createRateLimiter } from "./middleware/rateLimit";
import { validate, CreateTechPackSchema, CreateFabricSchema } from "./middleware/validation";
import { healthRouter } from "./routes/health";
import { techpacksRouter } from "./routes/techpacks";
import { fabricsRouter } from "./routes/fabrics";

dotenv.config();

export interface AppConfig {
  orchestratorUrl: string;
  jwtSecret: string;
  rateLimitMax?: number;
  rateLimitWindowMs?: number;
  corsOrigins?: string;
}

export function createApp(config: AppConfig): express.Express {
  const app = express();

  // Body parsing
  app.use(express.json());

  // CORS
  const origins = config.corsOrigins ? config.corsOrigins.split(",") : "*";
  app.use(cors({ origin: origins, credentials: true }));

  // Rate limiting
  app.use(
    createRateLimiter(config.rateLimitMax ?? 100, config.rateLimitWindowMs ?? 900000),
  );

  // Auth (skips /health)
  app.use(authMiddleware(config.jwtSecret));

  // Routes
  app.use("/health", healthRouter(config.orchestratorUrl));

  app.use(
    "/api/v1/techpacks",
    validate(CreateTechPackSchema),
    techpacksRouter(config.orchestratorUrl),
  );
  app.use("/api/v1/fabrics", fabricsRouter(config.orchestratorUrl));

  return app;
}

// Start server when run directly (not imported for tests)
if (require.main === module) {
  const config: AppConfig = {
    orchestratorUrl: process.env.ORCHESTRATOR_URL ?? "http://localhost:8000",
    jwtSecret: process.env.JWT_SECRET ?? "",
    rateLimitMax: Number(process.env.RATE_LIMIT_MAX) || 100,
    rateLimitWindowMs: Number(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
    corsOrigins: process.env.CORS_ORIGINS,
  };

  if (!config.jwtSecret) {
    console.error("JWT_SECRET is required");
    process.exit(1);
  }

  const port = Number(process.env.GATEWAY_PORT) || 3000;
  const server = app.listen(port, () => {
    console.log(`Gateway listening on port ${port}`);
  });

  const app = createApp(config);

  // Graceful shutdown
  for (const signal of ["SIGTERM", "SIGINT"] as const) {
    process.on(signal, () => {
      console.log(`Received ${signal}, shutting down...`);
      server.close(() => process.exit(0));
    });
  }
}
```

**Note:** There is a bug in the above — `app` is used before declaration. The agent must fix the ordering: declare `const app = createApp(config);` before `const server = app.listen(...)`. The correct order:

```typescript
if (require.main === module) {
  const config: AppConfig = {
    orchestratorUrl: process.env.ORCHESTRATOR_URL ?? "http://localhost:8000",
    jwtSecret: process.env.JWT_SECRET ?? "",
    rateLimitMax: Number(process.env.RATE_LIMIT_MAX) || 100,
    rateLimitWindowMs: Number(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
    corsOrigins: process.env.CORS_ORIGINS,
  };

  if (!config.jwtSecret) {
    console.error("JWT_SECRET is required");
    process.exit(1);
  }

  const app = createApp(config);
  const port = Number(process.env.GATEWAY_PORT) || 3000;
  const server = app.listen(port, () => {
    console.log(`Gateway listening on port ${port}`);
  });

  for (const signal of ["SIGTERM", "SIGINT"] as const) {
    process.on(signal, () => {
      console.log(`Received ${signal}, shutting down...`);
      server.close(() => process.exit(0));
    });
  }
}
```

- [ ] **Step 4: Fix validation middleware placement**

The `validate(CreateTechPackSchema)` is applied to ALL techpacks routes including GET. It should only apply to POST. Refactor the app to apply validation per-method:

```typescript
// In createApp, change the techpacks route mounting to:
const techpacks = techpacksRouter(config.orchestratorUrl);
app.post("/api/v1/techpacks", validate(CreateTechPackSchema), techpacks);
app.get("/api/v1/techpacks/:id", techpacks);

// And for fabrics:
const fabrics = fabricsRouter(config.orchestratorUrl);
app.post("/api/v1/fabrics", validate(CreateFabricSchema), fabrics);
app.get("/api/v1/fabrics/search", fabrics);
```

Actually, the cleaner approach is to mount routes directly and apply validation inside the router. Alternatively, mount routers and apply validation to specific sub-paths. The agent should find the cleanest approach that passes the tests. The key requirement: validation only on POST, not GET.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/app.test.ts --verbose`
Expected: PASS — all 4 tests pass

- [ ] **Step 6: Run full test suite**

Run: `cd gateway && npm test`
Expected: All tests pass (types, middleware, routes, app)

- [ ] **Step 7: Commit**

```bash
git add src/index.ts __tests__/app.test.ts
git commit -m "feat(gateway): express app factory with middleware wiring"
```

---

## Stream B: WebSocket + Dockerfile

### Task 10: WebSocket relay handler

**Files:**
- Create: `gateway/src/ws/techpackStream.ts`
- Test: `gateway/__tests__/ws/techpackStream.test.ts`

**Important context:** This task runs in a separate worktree. It depends on types from Stream A. Since Stream A may not be merged yet, this agent should define a minimal local type for `WSMessage` if the import from `../types` fails, OR copy the types file. The merge will reconcile.

- [ ] **Step 1: Write the failing tests**

```typescript
// gateway/__tests__/ws/techpackStream.test.ts
import http from "http";
import express from "express";
import WebSocket, { WebSocketServer } from "ws";
import { setupWebSocketHandler } from "../src/ws/techpackStream";

// Helper: create a mock orchestrator WS server
function createMockOrchestrator(
  port: number,
  messages: object[],
): Promise<http.Server> {
  return new Promise((resolve) => {
    const server = http.createServer();
    const wss = new WebSocketServer({ server });
    wss.on("connection", (ws) => {
      for (const msg of messages) {
        ws.send(JSON.stringify(msg));
      }
      ws.send(JSON.stringify({ event: "done", status: "completed" }));
      ws.close();
    });
    server.listen(port, () => resolve(server));
  });
}

function waitForMessages(ws: WebSocket, count: number): Promise<object[]> {
  return new Promise((resolve) => {
    const received: object[] = [];
    ws.on("message", (data) => {
      received.push(JSON.parse(data.toString()));
      if (received.length >= count) resolve(received);
    });
  });
}

describe("WebSocket techpack stream relay", () => {
  let gatewayServer: http.Server;
  let orchestratorServer: http.Server;
  let gatewayPort: number;
  const orchestratorPort = 19876;

  afterEach((done) => {
    const servers = [gatewayServer, orchestratorServer].filter(Boolean);
    let closed = 0;
    if (servers.length === 0) return done();
    servers.forEach((s) =>
      s.close(() => {
        closed++;
        if (closed === servers.length) done();
      }),
    );
  });

  it("relays messages from orchestrator to client", async () => {
    const agentMessages = [
      { agent: "brief_analyzer", status: "running", message: "Parsing..." },
      { agent: "brief_analyzer", status: "completed", data: { garment_type: "top" } },
    ];

    orchestratorServer = await createMockOrchestrator(
      orchestratorPort,
      agentMessages,
    );

    const app = express();
    gatewayServer = http.createServer(app);
    setupWebSocketHandler(gatewayServer, `ws://localhost:${orchestratorPort}`);

    await new Promise<void>((resolve) =>
      gatewayServer.listen(0, () => resolve()),
    );
    gatewayPort = (gatewayServer.address() as any).port;

    const client = new WebSocket(
      `ws://localhost:${gatewayPort}/api/v1/techpacks/tp_test/stream`,
    );

    await new Promise<void>((resolve) => client.on("open", () => resolve()));

    // Expect 2 agent messages + 1 done message = 3
    const messages = await waitForMessages(client, 3);
    expect(messages[0]).toMatchObject({ agent: "brief_analyzer", status: "running" });
    expect(messages[1]).toMatchObject({ agent: "brief_analyzer", status: "completed" });
    expect(messages[2]).toMatchObject({ event: "done", status: "completed" });

    client.close();
  });

  it("sends error when orchestrator is unreachable", async () => {
    const app = express();
    gatewayServer = http.createServer(app);
    // Point to a port where nothing is listening
    setupWebSocketHandler(gatewayServer, "ws://localhost:19999");

    await new Promise<void>((resolve) =>
      gatewayServer.listen(0, () => resolve()),
    );
    gatewayPort = (gatewayServer.address() as any).port;

    const client = new WebSocket(
      `ws://localhost:${gatewayPort}/api/v1/techpacks/tp_test/stream`,
    );

    await new Promise<void>((resolve) => client.on("open", () => resolve()));

    const messages = await waitForMessages(client, 1);
    expect(messages[0]).toMatchObject({ error: expect.any(String) });

    client.close();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd gateway && npx jest __tests__/ws/techpackStream.test.ts --verbose`
Expected: FAIL — cannot find module

- [ ] **Step 3: Implement WebSocket handler**

```typescript
// gateway/src/ws/techpackStream.ts
import http from "http";
import WebSocket, { WebSocketServer } from "ws";
import { URL } from "url";

export function setupWebSocketHandler(
  server: http.Server,
  orchestratorWsUrl: string,
): void {
  const wss = new WebSocketServer({ noServer: true });

  server.on("upgrade", (request, socket, head) => {
    const pathname = new URL(request.url ?? "", "http://localhost").pathname;
    const match = pathname.match(
      /^\/api\/v1\/techpacks\/([^/]+)\/stream$/,
    );

    if (!match) {
      socket.destroy();
      return;
    }

    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit("connection", ws, request, match[1]);
    });
  });

  wss.on("connection", (clientWs: WebSocket, _request: http.IncomingMessage, techpackId: string) => {
    const orchestratorPath = `/api/v1/techpacks/${techpackId}/stream`;
    // Convert http(s) URL to ws URL for orchestrator
    const wsUrl = `${orchestratorWsUrl}${orchestratorPath}`;

    let orchestratorWs: WebSocket;
    try {
      orchestratorWs = new WebSocket(wsUrl);
    } catch (err) {
      clientWs.send(JSON.stringify({ error: "Failed to connect to orchestrator" }));
      clientWs.close();
      return;
    }

    orchestratorWs.on("open", () => {
      // Relay: orchestrator → client
      orchestratorWs.on("message", (data) => {
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.send(data.toString());
        }
      });
    });

    orchestratorWs.on("close", () => {
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.close();
      }
    });

    orchestratorWs.on("error", (err) => {
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.send(
          JSON.stringify({ error: `Orchestrator connection failed: ${err.message}` }),
        );
        clientWs.close();
      }
    });

    // If client disconnects, close orchestrator connection
    clientWs.on("close", () => {
      if (orchestratorWs.readyState === WebSocket.OPEN) {
        orchestratorWs.close();
      }
    });
  });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd gateway && npx jest __tests__/ws/techpackStream.test.ts --verbose`
Expected: PASS — both tests pass

- [ ] **Step 5: Commit**

```bash
git add src/ws/techpackStream.ts __tests__/ws/techpackStream.test.ts
git commit -m "feat(gateway): websocket relay handler for techpack streaming"
```

---

### Task 11: Dockerfile

**Files:**
- Modify: `gateway/Dockerfile`

- [ ] **Step 1: Write the Dockerfile**

```dockerfile
# gateway/Dockerfile

# --- Build stage ---
FROM node:20-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src/ ./src/
RUN npx tsc

# --- Runtime stage ---
FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist

ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", "dist/index.js"]
```

- [ ] **Step 2: Verify Dockerfile builds**

Run: `cd gateway && docker build -t techpack-gateway:test .`
Expected: Build succeeds (may fail if Stream A code isn't present yet — that's OK, just verify the Dockerfile syntax is correct)

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "feat(gateway): multi-stage docker build"
```

---

### Task 12: Run full test suite and final verification

- [ ] **Step 1: Run all tests**

Run: `cd gateway && npm test`
Expected: All tests pass

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd gateway && npx tsc --noEmit`
Expected: No errors

- [ ] **Step 3: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix(gateway): test and compilation fixes"
```
