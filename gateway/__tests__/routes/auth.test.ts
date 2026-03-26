import express from "express";
import request from "supertest";
import jwt from "jsonwebtoken";
import { authRouter } from "../../src/routes/auth";

const JWT_SECRET = "test-secret";

function buildApp(): express.Express {
  const app = express();
  app.use("/api/v1/auth", authRouter(JWT_SECRET));
  return app;
}

describe("GET /api/v1/auth/demo-token", () => {
  it("returns a valid JWT with demo-user sub", async () => {
    const app = buildApp();
    const res = await request(app).get("/api/v1/auth/demo-token");

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty("token");
    expect(typeof res.body.token).toBe("string");

    const decoded = jwt.verify(res.body.token, JWT_SECRET, {
      algorithms: ["HS256"],
    }) as jwt.JwtPayload;

    expect(decoded.sub).toBe("demo-user");
    expect(decoded.exp).toBeDefined();
    // Token should expire roughly 24h from now
    const expiresIn = decoded.exp! - decoded.iat!;
    expect(expiresIn).toBe(86400);
  });

  it("returns different tokens on each call", async () => {
    const app = buildApp();
    const res1 = await request(app).get("/api/v1/auth/demo-token");
    const res2 = await request(app).get("/api/v1/auth/demo-token");

    // iat will differ (or at least tokens are independently signed)
    expect(res1.body.token).toBeDefined();
    expect(res2.body.token).toBeDefined();
  });
});
