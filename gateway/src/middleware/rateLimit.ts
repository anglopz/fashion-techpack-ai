import rateLimit from "express-rate-limit";

export function createRateLimiter(
  max: number = 100,
  windowMs: number = 15 * 60 * 1000,
) {
  return rateLimit({
    windowMs,
    max,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests, please try again later" },
  });
}
