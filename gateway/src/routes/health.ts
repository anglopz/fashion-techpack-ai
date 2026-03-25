import { Router } from "express";
import axios from "axios";

export function healthRouter(orchestratorUrl: string): Router {
  const router = Router();

  router.get("/", async (_req, res) => {
    let orchestratorStatus = "unreachable";
    try {
      await axios.get(`${orchestratorUrl}/health`, { timeout: 2000 });
      orchestratorStatus = "ok";
    } catch {
      // orchestrator is down — still report gateway as ok
    }

    res.json({
      status: "ok",
      orchestrator: orchestratorStatus,
    });
  });

  return router;
}
