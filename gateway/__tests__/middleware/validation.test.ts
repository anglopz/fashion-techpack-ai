import express from "express";
import request from "supertest";
import {
  validate,
  CreateTechPackSchema,
  CreateFabricSchema,
} from "../../src/middleware/validation";

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
