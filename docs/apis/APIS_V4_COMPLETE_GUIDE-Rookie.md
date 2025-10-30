# ✅ APIS V4 - Guia Completo de Contratos e Fallbacks

**Data:** 2025-01-XX  
**Escopo:** Backend + Storefront (Contratos, Versionamento, Fallbacks, Preloaders)  
**Status:** ✅ **IMPLEMENTADO**

---

## 🎯 Visão Geral

Este guia unifica padrões de contratos, versionamento, fallbacks e preloaders para garantir resiliência (SLOs estáveis) e UX suave.

---

## 📋 Contratos e Versionamento

### Envelopes Padrão

#### Sucesso (200-299)

```typescript
{
  success: true,
  data: T,
  meta?: {
    limit?: number,
    offset?: number,
    page?: number,
    count: number,
    total?: number,
    stale?: boolean  // true quando dados vêm de cache/fallback
  }
}
```

#### Erro (400-599)

```typescript
{
  success: false,
  error: {
    code: string,           // "PRODUCT_NOT_FOUND", "RATE_LIMIT_EXCEEDED"
    message: string,        // Mensagem legível
    details?: any,          // Detalhes adicionais
    request_id?: string,    // Para rastreamento
    timestamp: string       // ISO 8601
  }
}
```

### Rate Limiting (429)

**Headers de Resposta:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 2025-01-15T10:30:00Z
Retry-After: 60
```

**Body:**

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please retry after 60 seconds.",
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T10:29:00Z"
  }
}
```

### Versionamento

**Request (Header ou Query):**
```
X-API-Version: v2.0
# ou
?api_version=v2.0
```

**Response (Header):**
```
X-API-Version: v2.0
```

**Tolerância entre versões:**
- v2.0 aceita requests de v1.x (com warnings)
- Breaking changes requerem nova major version
- Deprecation notices com 6 meses de antecedência

---

## 🔄 Fallbacks e Resiliência

### Backend

#### 1. Timeouts e Retries

**Configuração:**
```typescript
// src/lib/http.ts (backend)
const DEFAULT_OPTIONS = {
  timeout: 5000,        // 5s
  maxRetries: 3,
  baseDelay: 1000,      // 1s
  maxDelay: 10000,      // 10s
  retryOn: [408, 429, 500, 502, 503, 504],
};
```

**Exponential Backoff com Jitter:**
```typescript
function calculateBackoff(attempt: number, baseDelay: number, maxDelay: number): number {
  const exponentialDelay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
  const jitter = Math.random() * 0.3 * exponentialDelay; // ±30%
  return Math.floor(exponentialDelay + jitter);
}
```

#### 2. Circuit Breaker

**Estados:**
- **CLOSED:** Normal operation
- **OPEN:** Falhas consecutivas ≥ threshold (rejeita requests)
- **HALF_OPEN:** Timeout expirado, testando recuperação

**Configuração:**
```typescript
circuit_breaker: {
  enabled: true,
  failure_threshold: 3,      // Abrir após 3 falhas
  success_threshold: 2,      // Fechar após 2 sucessos em HALF_OPEN
  timeout_ms: 60000,         // 1 min para tentar HALF_OPEN
}
```

#### 3. Cache com Stale-if-Error

**Redis TTL + GRACE:**
```typescript
// Exemplo: ANEEL Tariffs
const CACHE_CONFIG = {
  ttl: 86400,        // 24h (dados frescos)
  grace: 604800,     // 7 dias (stale-if-error)
};

// Ao buscar:
const cached = await redis.get(key);
if (cached) {
  const { data, expires_at, grace_until } = JSON.parse(cached);
  const now = Date.now();
  
  if (now < expires_at) {
    // Dados frescos
    return { data, meta: { stale: false } };
  } else if (now < grace_until) {
    // Dados stale, mas válidos em caso de erro
    try {
      const fresh = await fetchFromAPI();
      await redis.set(key, JSON.stringify({ data: fresh, expires_at: now + ttl, grace_until: now + ttl + grace }));
      return { data: fresh, meta: { stale: false } };
    } catch (error) {
      console.warn('[Cache] Using stale data due to error:', error);
      return { data, meta: { stale: true } };
    }
  }
}
```

#### 4. Fallbacks por Endpoint

**ANEEL Tariffs:**
```typescript
// 1. Tentar API ANEEL
// 2. Fallback: snapshot Redis (último conhecido)
// 3. Fallback: arquivo local (dados históricos)
// 4. Marcar meta.stale = true
```

**Solar Calculator:**
```typescript
// 1. Tentar PVLib + ANEEL
// 2. Fallback: snapshot tarifário + irradiância média
// 3. Marcar como "estimativa" no response
// 4. meta.stale = true
```

**Catalog/Kits:**
```typescript
// 1. Tentar database
// 2. Fallback: internal catalog (pre-loaded)
// 3. Fallback: cache minimalista
// 4. meta.stale = true se não for database
```

#### 5. Health Endpoint

**GET /api/health**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "services": {
    "database": { "status": "up", "latency_ms": 12 },
    "redis": { "status": "up", "latency_ms": 3 },
    "pvlib": { "status": "degraded", "latency_ms": 5200, "circuit": "OPEN" },
    "aneel": { "status": "up", "latency_ms": 450 }
  },
  "metrics": {
    "cache_hit_rate": 0.937,
    "fallback_count_24h": 42,
    "p95_response_time_ms": 87,
    "p99_response_time_ms": 234
  }
}
```

---

### Storefront

#### 1. fetchWithFallbacks

**Já implementado em `src/lib/http.ts`:**
```typescript
export class HttpClient {
  async fetch<T>(url: string, options?: FetchOptions): Promise<T> {
    // 1. Timeout com AbortController
    // 2. Retries com exponential backoff + jitter
    // 3. 429 handling com Retry-After
    // 4. Erro normalizado (HttpError)
  }
}
```

#### 2. Preloaders e Suspense

**Loading States:**
```typescript
// app/[countryCode]/(main)/loading.tsx
export default function Loading() {
  return <GridSkeleton />;
}

// app/[countryCode]/(main)/products/[handle]/loading.tsx
export default function ProductLoading() {
  return <ProductSkeleton />;
}
```

**Skeleton Components:**
```typescript
// src/components/ui/skeleton.tsx
export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse rounded-md bg-gray-200", className)} />
  );
}
```

#### 3. Degraded State

**Banner quando meta.stale = true:**
```typescript
// src/components/ui/degraded-banner.tsx
<DegradedBanner 
  message="Exibindo dados em cache. Alguns preços podem estar desatualizados."
  onRetry={() => router.refresh()}
/>
```

**Uso em Server Components:**
```typescript
export default async function ProductPage({ params }: Props) {
  const product = await getProductByHandle(params.handle, region.id);
  
  // Se meta.stale, mostrar banner
  const isStale = product.meta?.stale;
  
  return (
    <>
      {isStale && <DegradedBanner />}
      <ProductTemplate product={product} />
    </>
  );
}
```

#### 4. Error Boundaries

**PDP Error Boundary:**
```typescript
// app/[countryCode]/(main)/products/[handle]/error.tsx
export default function ProductError({ error, reset }: ErrorProps) {
  return (
    <div>
      <h2>Erro ao carregar produto</h2>
      <button onClick={reset}>Tentar novamente</button>
      <a href="/">Voltar para home</a>
    </div>
  );
}
```

#### 5. A11y de Estados

**Loading:**
```typescript
<div role="status" aria-live="polite" aria-busy="true">
  <Skeleton />
  <span className="sr-only">Carregando produto...</span>
</div>
```

**Error:**
```typescript
<div role="alert" aria-live="assertive">
  <ExclamationTriangleIcon aria-hidden="true" />
  <p>Erro ao carregar produto</p>
</div>
```

**Degraded:**
```typescript
<div role="alert" aria-live="polite">
  <ExclamationTriangleIcon aria-hidden="true" />
  <p>Exibindo dados em cache</p>
</div>
```

---

## 🧪 Pact Contract Testing

### Consumer (Storefront)

**Isolado de test:unit:**
```json
{
  "scripts": {
    "test:unit": "jest --testPathIgnorePatterns=pact",
    "test:pact:consumer": "jest --testMatch='**/*.pact.test.ts'"
  }
}
```

**Exemplo de Contrato:**
```typescript
// storefront/src/lib/__tests__/products.pact.test.ts
describe("Products API", () => {
  it("should get product by handle", async () => {
    await provider.addInteraction({
      state: "product kit-solar-5kw exists",
      uponReceiving: "a request for product by handle",
      withRequest: {
        method: "GET",
        path: "/store/products_enhanced",
        query: { handle: "kit-solar-5kw", limit: "1" },
        headers: { "x-publishable-api-key": like("pk_...") },
      },
      willRespondWith: {
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: {
          products: eachLike({
            id: like("prod_123"),
            handle: "kit-solar-5kw",
            title: like("Kit Solar 5kW"),
            thumbnail: like("https://..."),
          }),
        },
      },
    });

    const product = await getProductByHandle("kit-solar-5kw", "region_br");
    expect(product.handle).toBe("kit-solar-5kw");
  });
});
```

### Provider (Backend)

**Fixtures Estáveis:**
```typescript
// backend/pact/fixtures/catalog.ts
export const CATALOG_FIXTURES = {
  products: [
    {
      id: "prod_kit_5kw",
      handle: "kit-solar-5kw",
      title: "Kit Solar 5kW",
      thumbnail: "https://example.com/kit-5kw.jpg",
      variants: [{ sku: "KIT-5KW-001", price: 15000 }],
    },
  ],
};
```

**Verificação:**
```typescript
// backend/pact/provider.pact.test.ts
describe("Pact Provider Verification", () => {
  it("should verify contracts", async () => {
    const opts = {
      provider: "ysh-backend",
      providerBaseUrl: "http://localhost:9000",
      pactUrls: ["./pacts/storefront-ysh-backend.json"],
      stateHandlers: {
        "product kit-solar-5kw exists": async () => {
          await seedDatabase(CATALOG_FIXTURES);
        },
      },
    };

    await new Verifier(opts).verifyProvider();
  });
});
```

---

## 📊 Observabilidade

### Backend (Pino Logs)

**Formato:**
```json
{
  "level": "info",
  "time": 1705315800000,
  "request_id": "req_abc123",
  "method": "GET",
  "url": "/store/products_enhanced",
  "status": 200,
  "duration_ms": 87,
  "cache_hit": true,
  "stale": false
}
```

**Métricas no Health:**
```json
{
  "cache_hit_rate": 0.937,
  "fallback_count_24h": 42,
  "p95_response_time_ms": 87,
  "p99_response_time_ms": 234,
  "rate_limit_429_count": 3,
  "circuit_breaker_open_count": 1
}
```

### Storefront (PostHog)

**Eventos (sem PII):**
```typescript
posthog.capture('api_error', {
  endpoint: '/store/products_enhanced',
  status: 500,
  error_code: 'INTERNAL_ERROR',
  retry_count: 3,
  // Sem request_id (pode conter PII)
});

posthog.capture('degraded_state', {
  component: 'ProductPage',
  reason: 'stale_cache',
  duration_ms: 5000,
});
```

**Web Vitals:**
```typescript
posthog.capture('web_vitals', {
  lcp: 1234,
  fid: 45,
  cls: 0.05,
  ttfb: 234,
});
```

---

## ✅ Checklist de Implementação

### Backend
- [x] APIResponse + X-API-Version em 12/12 rotas custom
- [x] Rate limiting com X-RateLimit-* headers
- [x] HTTP client com timeout/retry/circuit breaker
- [x] Cache Redis com stale-if-error
- [ ] Snapshots Redis para fallbacks (ANEEL, Solar)
- [ ] Health endpoint com métricas
- [x] Pact Provider com fixtures
- [x] Logs Pino com request_id

### Storefront
- [x] HTTP client unificado (timeout/backoff/jitter/429)
- [x] Data layer com retry logic
- [x] Loading states (skeletons)
- [x] Error boundaries
- [x] Degraded state banner (criado)
- [x] JSON-LD em PDP
- [x] Metadata/OG/Twitter
- [x] CSP headers
- [x] A11y (skip links, roles, aria-*)
- [ ] Pact Consumer isolado
- [ ] PostHog sem PII

---

## 🚀 Próximos Passos

### Imediato (Hoje - 2h)
1. **Testar PDP com fallback de imagem** (30min)
   ```bash
   # Verificar se placeholder funciona
   curl http://localhost:8000/br/products/kit-solar-5kw
   ```

2. **Validar error boundary** (30min)
   ```bash
   # Simular erro 500
   # Verificar UI de erro
   # Testar retry button
   ```

3. **Build e deploy** (1h)
   ```bash
   cd storefront
   npm run type-check && npm run build
   ```

### Curto Prazo (Esta Semana - 4h)
1. **Implementar snapshots Redis** (2h)
   - ANEEL tariffs snapshot
   - Solar calculator fallback
   - Catalog cache minimalista

2. **Health endpoint com métricas** (1h)
   - Cache hit rate
   - Fallback count
   - p95/p99 response times

3. **Pact Consumer isolado** (1h)
   - Separar de test:unit
   - Fixtures estáveis
   - CI/CD integration

---

## 📚 Documentação Relacionada

- [Backend V7 Complete Summary](./backend/BACKEND_V7_COMPLETE_SUMMARY.md)
- [Storefront V7 Summary](./storefront/STOREFRONT_V7_SUMMARY.md)
- [V7 Complete Summary](./V7_COMPLETE_SUMMARY.md)
- [Análise APIs Produtos/Imagens](./ANALISE_APIS_PRODUTOS_IMAGENS_360.md)

---

**Status:** ✅ **INFRAESTRUTURA COMPLETA**  
**Próximo:** Testar PDP, validar fallbacks, implementar snapshots Redis  
**Tempo Estimado:** 6h (2h imediato + 4h curto prazo)
