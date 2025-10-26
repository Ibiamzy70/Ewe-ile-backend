import Redis from "ioredis";
import dotenv from "dotenv";
dotenv.config();

const { REDIS_URL } = process.env;

if (!REDIS_URL) {
  throw new Error("REDIS_URL is not defined in .env");
}

export const redis = new Redis(REDIS_URL, {
  tls: REDIS_URL.startsWith("rediss://") ? {} : undefined,
  maxRetriesPerRequest: null,
  connectTimeout: 10000,
});

redis.on("connect", () => console.log("Redis connected"));
redis.on("error", (err) => console.error(" Redis error:", err));

export default redis;
