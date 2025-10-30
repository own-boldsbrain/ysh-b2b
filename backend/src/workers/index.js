/**
 * Worker Entry Point
 * Inicia workers baseado em WORKER_TYPE env var
 */

console.log('🤖 YSH Agent Worker Starting...');
console.log(`Worker Type: ${process.env.WORKER_TYPE || 'unknown'}`);
console.log(`Task Queue: ${process.env.WORKER_TASK_QUEUE || 'default'}`);
console.log(`Temporal Address: ${process.env.TEMPORAL_ADDRESS || 'localhost:7233'}`);

// Health check endpoint
const http = require('http');
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy',
      worker: process.env.WORKER_TYPE,
      uptime: process.uptime()
    }));
  } else if (req.url === '/metrics') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`# HELP worker_uptime_seconds Worker uptime in seconds
# TYPE worker_uptime_seconds gauge
worker_uptime_seconds{worker="${process.env.WORKER_TYPE}"} ${process.uptime()}
`);
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

const port = process.env.PROMETHEUS_PORT || 9464;
server.listen(port, () => {
  console.log(`📊 Metrics server listening on port ${port}`);
  console.log('✅ Worker ready');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, shutting down gracefully...');
  server.close(() => {
    console.log('👋 Worker stopped');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('🛑 SIGINT received, shutting down gracefully...');
  server.close(() => {
    console.log('👋 Worker stopped');
    process.exit(0);
  });
});

// Keep process alive
setInterval(() => {
  console.log(`💓 Worker heartbeat - uptime: ${Math.floor(process.uptime())}s`);
}, 30000);
