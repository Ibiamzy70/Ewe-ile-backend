import express from "express";
import { cacheMiddleware, cacheDel } from "../redis/cache.js";
import { rateLimiter } from "../redis/rateLimiter.js";
import { enqueueJob } from "../redis/queue.js";

const router = express.Router();


let jobs = [];
let id = 1;


const jobCacheKey = () => "jobs:list";

router.get(
  "/",
  rateLimiter,
  cacheMiddleware(() => jobCacheKey()),
  (req, res) => {
    res.json(jobs);
  }
);

router.post("/", async (req, res) => {
  const { title, company } = req.body;
  const newJob = { id: id++, title, company };
  jobs.push(newJob);

  
  await cacheDel(jobCacheKey());

  
  await enqueueJob({ action: "notify_new_job", job: newJob });

  res.status(201).json(newJob);
});

router.delete("/:id", async (req, res) => {
  const jobId = parseInt(req.params.id, 10);
  jobs = jobs.filter((j) => j.id !== jobId);
  await cacheDel(jobCacheKey());
  res.status(204).send();
});

export default router;
