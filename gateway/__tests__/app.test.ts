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
