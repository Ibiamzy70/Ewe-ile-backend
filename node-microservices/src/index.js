import express from "express";
import http from "http";
import { Server as IOServer } from "socket.io";
import dotenv from "dotenv";
import jobsRouter from "./routes/jobs.js";
import redis from "./redis/client.js";           
import { createAdapter } from "@socket.io/redis-adapter";
import jwt from "jsonwebtoken";
import { verifyDjangoToken } from "./auth/djangoJwtVerify.js"; 
import { rateLimiter } from "./redis/rateLimiter.js";

dotenv.config();

const app = express();
app.use(express.json());


app.get("/health", (req, res) => res.json({ ok: true }));


app.get("/protected", rateLimiter, async (req, res) => {
  try {
    const auth = req.headers.authorization || "";
    const token = auth.split(" ")[1];
    if (!token) return res.status(401).json({ error: "Missing token" });

    const payload = await verifyDjangoToken(token);
    
    res.json({ ok: true, payload });
  } catch (err) {
    return res.status(401).json({ error: "Invalid token", details: err.message });
  }
});


app.use("/jobs", jobsRouter);


const server = http.createServer(app);
const io = new IOServer(server, {
  cors: { origin: true, credentials: true }, 
  pingTimeout: 20000,
});


const subClient = redis.duplicate();
const pubClient = redis.duplicate();

Promise.all([pubClient.connect?.(), subClient.connect?.()]) 
  .catch(() => {}) 

io.adapter(createAdapter(pubClient, subClient));


io.use(async (socket, next) => {
  try {
    const token = socket.handshake.auth?.token;
    if (!token) return next(new Error("Authentication error: missing token"));
    const payload = await verifyDjangoToken(token);
    
    socket.data.user = payload;
    next();
  } catch (err) {
    next(new Error("Authentication error: " + err.message));
  }
});

io.on("connection", (socket) => {
  console.log("socket connected:", socket.id, "user:", socket.data.user?.sub || socket.data.user?.user_id);

  socket.on("ping", (d) => {
    socket.emit("pong", { id: socket.id, echo: d });
  });

  socket.on("disconnect", (reason) => {
    console.log("socket disconnected", socket.id, reason);
  });
});

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
  console.log(` API + Socket.IO running on port ${PORT}`);
});

const shutdown = async () => {
  console.log("Shutting down gracefully...");
  try {
    await io.close();
    if (redis) await redis.quit();
    process.exit(0);
  } catch (err) {
    console.error("Error during shutdown:", err);
    process.exit(1);
  }
};

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);