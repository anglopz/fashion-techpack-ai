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
