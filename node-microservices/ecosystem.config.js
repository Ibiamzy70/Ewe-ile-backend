export default {
  apps: [
    {
      name: "node-microservice",
      script: "./src/index.js",
      instances: "max",               
      exec_mode: "cluster",           
      watch: false,                  
      autorestart: true,              
      max_memory_restart: "500M",     
      env: {
        NODE_ENV: "production",
      },
    },
    {
      name: "job-worker",
      script: "./src/workers/jobWorker.js",
      instances: process.env.WORKER_CONCURRENCY || 2, 
      exec_mode: "fork",               
      autorestart: true,
      max_memory_restart: "500M",
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
