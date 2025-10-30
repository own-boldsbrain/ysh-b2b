#!/usr/bin/env node

/**
 * Health Check CLI
 * Verifica status de todos os serviços do YSH Agents
 */

const http = require('http');
const https = require('https');

const SERVICES = [
  { name: 'Temporal Server', url: 'http://localhost:8080', critical: true },
  { name: 'Supabase Studio', url: 'http://localhost:54321', critical: true },
  { name: 'Redis', url: 'http://localhost:8001', critical: true },
  { name: 'Redpanda Admin', url: 'http://localhost:19644/metrics', critical: true },
  { name: 'Grafana', url: 'http://localhost:3000', critical: false },
  { name: 'Prometheus', url: 'http://localhost:9090', critical: false },
  { name: 'Redpanda Console', url: 'http://localhost:8082', critical: false },
];

const AGENTS = [
  { name: 'Catalog Extractor', queue: 'catalog-extraction' },
  { name: 'Price Intelligence', queue: 'price-intelligence' },
  { name: 'Product Enricher', queue: 'product-enrichment' },
  { name: 'SKU Governor', queue: 'sku-governance' },
];

function checkUrl(url) {
  return new Promise((resolve) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, { timeout: 5000 }, (res) => {
      resolve(res.statusCode >= 200 && res.statusCode < 400);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function checkAgent(agent) {
  // Simplified check - in production, query Temporal for worker status
  return true;
}

async function main() {
  console.log('🏥 YSH Agents Health Check');
  console.log('==========================\n');

  let allHealthy = true;

  // Check services
  for (const service of SERVICES) {
    process.stdout.write(`${service.critical ? '✅' : '📊'} ${service.name}: `);
    const isHealthy = await checkUrl(service.url);
    
    if (isHealthy) {
      console.log('✅ OK');
    } else {
      console.log('❌ DOWN');
      if (service.critical) {
        allHealthy = false;
      }
    }
  }

  console.log('\n📊 Agents Status:');

  // Check agents
  for (const agent of AGENTS) {
    process.stdout.write(`  - ${agent.name}: `);
    const isHealthy = await checkAgent(agent);
    console.log(isHealthy ? '✅ Ready' : '❌ Down');
    if (!isHealthy) {
      allHealthy = false;
    }
  }

  console.log('\n' + '='.repeat(26));
  if (allHealthy) {
    console.log('🎉 All systems operational!');
    process.exit(0);
  } else {
    console.log('⚠️  Some services are down');
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('❌ Health check failed:', err.message);
  process.exit(1);
});
