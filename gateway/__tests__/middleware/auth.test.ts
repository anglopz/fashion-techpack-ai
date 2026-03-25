import express from "express";
import request from "supertest";
import jwt from "jsonwebtoken";
import { authMiddleware } from "../../src/middleware/auth";

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
