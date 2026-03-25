import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { AuthPayload } from "../types";

declare global {
  namespace Express {
    interface Request {
      user?: AuthPayload;
    }
  }
}

const SKIP_AUTH_PATHS = ["/health"];

export function authMiddleware(secret: string) {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (SKIP_AUTH_PATHS.includes(req.path)) {
      next();
      return;
    }

    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      res.status(401).json({ error: "Missing or invalid token" });
      return;
    }

    const token = authHeader.slice(7);
    try {
      const decoded = jwt.verify(token, secret, {
        algorithms: ["HS256"],
      }) as AuthPayload;
      req.user = decoded;
      next();
    } catch {
      res.status(401).json({ error: "Missing or invalid token" });
    }
  };
}
