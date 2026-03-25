import express from "express";
import request from "supertest";
import axios from "axios";
import { techpacksRouter } from "../../src/routes/techpacks";

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
