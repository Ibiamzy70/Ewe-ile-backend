import redis from "./client.js";
import { promisify } from "util";

const DEFAULT_TTL = parseInt(process.env.CACHE_TTL || "60", 10);

export async function cacheGet(key) {
  const val = await redis.get(key);
  return val ? JSON.parse(val) : null;
}

export async function cacheSet(key, value, ttl = DEFAULT_TTL) {
  await redis.set(key, JSON.stringify(value), "EX", ttl);
}

export async function cacheDel(key) {
  await redis.del(key);
}


export function cacheMiddleware(cacheKeyFn, ttl = DEFAULT_TTL) {
  return async (req, res, next) => {
    try {
      const key = cacheKeyFn(req);
      const cached = await cacheGet(key);
      if (cached) {
        return res.json(cached);
      }

      // Monkey-patch res.json to store the response
      const originalJson = res.json.bind(res);
      res.json = async (data) => {
        try {
          await cacheSet(key, data, ttl);
        } catch (err) {
          console.error("Cache set failed:", err.message);
        }
        return originalJson(data);
      };

      next();
    } catch (err) {
      console.error("Cache middleware error:", err.message);
      next();
    }
  };
}
