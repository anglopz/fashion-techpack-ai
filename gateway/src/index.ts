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

  // Techpacks: validation only on POST, then delegate to router
  app.use("/api/v1/techpacks", (req, res, next) => {
    if (req.method === "POST") {
      return validate(CreateTechPackSchema)(req, res, next);
    }
    next();
  }, techpacksRouter(config.orchestratorUrl));

  // Fabrics: validation only on POST, then delegate to router
  app.use("/api/v1/fabrics", (req, res, next) => {
    if (req.method === "POST") {
      return validate(CreateFabricSchema)(req, res, next);
    }
    next();
  }, fabricsRouter(config.orchestratorUrl));

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
