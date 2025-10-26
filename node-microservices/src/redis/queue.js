import { Queue } from "bullmq";
import dotenv from "dotenv";
dotenv.config();

import redis from "./client.js";

export const jobQueue = new Queue("jobs", { connection: redis });


export async function enqueueJob(data) {
  await jobQueue.add("new-job", data);
}
