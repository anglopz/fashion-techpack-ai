import express from "express";
import request from "supertest";
import axios from "axios";
import { fabricsRouter } from "../../src/routes/fabrics";

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
