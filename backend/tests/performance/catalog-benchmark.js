/**
 * K6 Load Test - Catalog SKU List
 * 
 * Performance benchmark for GET /store/catalog/skus
 * Target: P95 < 150ms
 * 
 * Usage:
 *   k6 run catalog-benchmark.js
 * 
 * Custom options:
 *   k6 run -e BASE_URL=http://localhost:9000 catalog-benchmark.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const cacheHitLatency = new Trend('cache_hit_latency');
const cacheMissLatency = new Trend('cache_miss_latency');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:9000';
const ENDPOINT = `${BASE_URL}/store/catalog/skus`;

export const options = {
  stages: [
    { duration: '10s', target: 5 },   // Ramp-up to 5 VUs
    { duration: '30s', target: 10 },  // Stable load with 10 VUs
    { duration: '20s', target: 20 },  // Peak load with 20 VUs
    { duration: '10s', target: 0 },   // Ramp-down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<150'],    // 95% of requests under 150ms
    http_req_duration: ['p(99)<300'],    // 99% of requests under 300ms
    http_req_failed: ['rate<0.01'],      // Error rate < 1%
    errors: ['rate<0.01'],               // Custom error rate < 1%
  },
};

export default function () {
  // Test scenarios with different parameters
  const scenarios = [
    { name: 'Basic List', params: 'limit=20' },
    { name: 'Paginated', params: 'page=2&limit=10' },
    { name: 'Category Filter', params: 'category=inverters&limit=10' },
    { name: 'Search', params: 'search=solar&limit=10' },
  ];

  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  const url = `${ENDPOINT}?${scenario.params}`;

  const startTime = Date.now();
  const response = http.get(url);
  const duration = Date.now() - startTime;

  // Check response
  const checkResult = check(response, {
    'status is 200': (r) => r.status === 200,
    'response has success field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.success === true;
      } catch (e) {
        return false;
      }
    },
    'response has skus': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.data?.skus);
      } catch (e) {
        return false;
      }
    },
    'response has pagination': (r) => {
      try {
        const body = JSON.parse(r.body);
        return typeof body.data?.pagination?.total === 'number';
      } catch (e) {
        return false;
      }
    },
  });

  if (!checkResult) {
    errorRate.add(1);
    console.error(`[${scenario.name}] Request failed:`, response.status, response.body.substring(0, 200));
  } else {
    errorRate.add(0);
    
    // Estimate if this was cache hit (fast response) or miss (slower)
    if (duration < 50) {
      cacheHitLatency.add(duration);
    } else {
      cacheMissLatency.add(duration);
    }
  }

  // Think time (simulates user reading results)
  sleep(1);
}

export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const p99 = data.metrics.http_req_duration.values['p(99)'];
  const errorRate = data.metrics.errors.values.rate;

  console.log('\n========================================');
  console.log('Performance Benchmark Results');
  console.log('========================================');
  console.log(`P95 Latency: ${p95.toFixed(2)}ms ${p95 < 150 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`P99 Latency: ${p99.toFixed(2)}ms ${p99 < 300 ? '✓ PASS' : '✗ FAIL'}`);
  console.log(`Error Rate: ${(errorRate * 100).toFixed(2)}% ${errorRate < 0.01 ? '✓ PASS' : '✗ FAIL'}`);
  console.log('========================================\n');

  return {
    'stdout': JSON.stringify(data, null, 2),
  };
}
