import { Worker } from "bullmq";
import dotenv from "dotenv";
import redis from "../redis/client.js";


dotenv.config();

const worker = new Worker(
  "jobs", 
  async (job) => {
    console.log("Processing job:", job.id, job.name, job.data);

    try {
      
      if (job.data.action === "notify_new_job") {
        console.log("Sending notification for job:", job.data.job.id);
        
      }

      
      await new Promise((resolve) => setTimeout(resolve, 1000));

      console.log("Job finished successfully:", job.id);
      return { ok: true };
    } catch (err) {
      console.error("Job processing error:", job.id, err);
      throw err; 
    }
  },
  { connection: redis }
);




worker.on("completed", (job) => console.log(`Job ${job.id} completed`));
worker.on("failed", (job, err) =>
  console.error(` Job ${job?.id} failed:`, err?.message)
);

console.log("Job Worker started and listening for jobs...");

process.on("SIGINT", async () => {
  console.log("Worker shutting down...");
  await worker.close();
  await redis.quit();
  process.exit(0);
});
