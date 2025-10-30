# Local Testing Guide - Catalog Pilot Route

## Prerequisites

1. **PostgreSQL** - Database with `ysh_catalog` schema
2. **Redis** - Cache layer (port 6379 default)
3. **Node.js 18+** - Runtime environment
4. **k6** (optional) - For load testing

## Setup Steps

### 1. Start Redis

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Verify:**
```bash
redis-cli ping
# Expected: PONG
```

### 2. Configure Environment

Create or update `.env` file:

```env
# Enable DDD pilot route
CATALOG_DDD_ENABLED=true

# Redis configuration
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Database (ensure ysh_catalog schema exists)
DATABASE_URL=postgresql://user:pass@localhost:5432/ysh_solar
```

### 3. Verify Database Schema

Ensure `ysh_catalog.products` and `ysh_catalog.manufacturers` tables exist:

```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'ysh_catalog';

-- Expected: products, manufacturers, skus, etc.
```

### 4. Start Medusa Server

```bash
npm run dev
```

Check logs for:
```
[ListSKUsHandler] Handler initialized with cache
```

## Testing

### Smoke Test (Quick Validation)

**PowerShell (Windows):**
```powershell
.\tests\local\catalog-smoke-test.ps1
```

**Bash (Linux/Mac):**
```bash
chmod +x tests/local/catalog-smoke-test.sh
./tests/local/catalog-smoke-test.sh
```

**Manual curl:**
```bash
# Basic list
curl "http://localhost:9000/store/catalog/skus?limit=10"

# With filters
curl "http://localhost:9000/store/catalog/skus?category=inverters&limit=5"

# Pagination
curl "http://localhost:9000/store/catalog/skus?page=2&limit=10"
```

### Load Test (Performance Validation)

**Prerequisite:** Install k6
```bash
# Windows (Chocolatey)
choco install k6

# Mac (Homebrew)
brew install k6

# Linux (Binary)
wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz
tar -xzf k6-v0.47.0-linux-amd64.tar.gz
sudo mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/
```

**Run benchmark:**
```bash
k6 run tests/performance/catalog-benchmark.js
```

**Expected results:**
- P95 latency < 150ms ✓
- P99 latency < 300ms ✓
- Error rate < 1% ✓

## Monitoring

### Check Metrics

**Add metrics endpoint to catalog route** (in `src/api/store/catalog/metrics/route.ts`):

```typescript
import { getHandlerMetrics } from '@domains/catalog/application/queries/handlers/list-skus-handler';

export async function GET(req: Request) {
  const metrics = getHandlerMetrics();
  
  return Response.json({
    success: true,
    data: metrics,
    timestamp: new Date().toISOString()
  });
}
```

**Query metrics:**
```bash
curl http://localhost:9000/store/catalog/metrics
```

### Check Cache

**Redis CLI:**
```bash
redis-cli

# List all catalog keys
KEYS catalog:skus:*

# Check specific key
GET catalog:skus:list:abc123

# Monitor cache operations in real-time
MONITOR
```

### Check Logs

Look for these log messages:

```
[ListSKUsHandler] Cache HIT - 12ms
[ListSKUsHandler] Cache MISS - querying DB
[ListSKUsHandler] Query completed - 85ms (20 items, P95: 120ms)
```

## Troubleshooting

### Issue: No data returned

**Solution:** Check if database has products:
```sql
SELECT COUNT(*) FROM ysh_catalog.products WHERE is_active = true;
```

### Issue: Cache not working

**Solution 1:** Verify Redis connection:
```bash
redis-cli ping
```

**Solution 2:** Check Redis URL in `.env`:
```env
REDIS_URL=redis://localhost:6379
```

**Solution 3:** Clear cache:
```bash
redis-cli FLUSHDB
```

### Issue: High latency (>150ms P95)

**Possible causes:**
1. Database not indexed - Add indexes:
   ```sql
   CREATE INDEX idx_products_category ON ysh_catalog.products(category);
   CREATE INDEX idx_products_manufacturer ON ysh_catalog.products(manufacturer_id);
   ```

2. Cold cache - Warm up with requests:
   ```bash
   for i in {1..10}; do curl -s "http://localhost:9000/store/catalog/skus?limit=20" > /dev/null; done
   ```

3. Large result set - Reduce limit or add filters

### Issue: Feature flag not working

**Solution:** Ensure `CATALOG_DDD_ENABLED=true` in `.env` and restart server.

Check route is using DDD handler:
```typescript
// In src/api/store/catalog/skus/route.ts
console.log('DDD enabled:', dddCatalogHandlers.isEnabled);
```

## Success Criteria

✅ **Functional**:
- All smoke tests pass (5/5)
- Response format matches specification
- Filters (category, search, pagination) work correctly

✅ **Performance**:
- P95 latency < 150ms
- P99 latency < 300ms
- Cache hit rate > 80% after warmup

✅ **Reliability**:
- Error rate < 1%
- No memory leaks (stable memory usage over time)
- Cache invalidation works (test by updating product)

## Next Steps

After successful local testing:

1. **Run integration tests:** `npm run test:integration`
2. **Deploy to staging:** Test with production-like data
3. **Monitor metrics:** Set up Grafana dashboard
4. **Gradual rollout:** Start with 10% traffic, increase to 100%
