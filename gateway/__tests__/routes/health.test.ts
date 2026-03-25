import express from "express";
import request from "supertest";
import axios from "axios";
import { healthRouter } from "../../src/routes/health";

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
