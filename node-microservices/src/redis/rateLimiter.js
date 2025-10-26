import redis from "./client.js";

const WINDOW = parseInt(process.env.RATE_LIMIT_WINDOW || "60", 10);
const LIMIT = parseInt(process.env.RATE_LIMIT_MAX || "60", 10);

export async function rateLimiter(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress;
  const key = `ratelimit:${ip}:${req.path}`;
  const count = await redis.incr(key);

  if (count === 1) await redis.expire(key, WINDOW);

  if (count > LIMIT) {
    return res.status(429).json({
      error: "Too many requests. Try again later.",
    });
  }

  next();
}
