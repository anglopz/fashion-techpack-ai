import { Router } from "express";
import jwt from "jsonwebtoken";

export function authRouter(jwtSecret: string): Router {
  const router = Router();

  router.get("/demo-token", (_req, res) => {
    const token = jwt.sign({ sub: "demo-user" }, jwtSecret, {
      algorithm: "HS256",
      expiresIn: "24h",
    });
    res.json({ token });
  });

  return router;
}
