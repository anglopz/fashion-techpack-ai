import express from "express";
import request from "supertest";
import { createRateLimiter } from "../../src/middleware/rateLimit";

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
