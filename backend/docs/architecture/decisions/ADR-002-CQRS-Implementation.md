# ADR-002: Implementação de CQRS Leve

**Status:** Aceito  
**Data:** 20 de Outubro de 2025  
**Decisores:** Time YSH B2B Backend

---

## Contexto

Após adotar DDD (ADR-001), precisamos definir como separar operações de leitura (queries) e escrita (commands) para otimizar performance e clareza do código.

### Problemas Atuais

- Queries pesadas bloqueiam escritas
- Listagens sem cache ou índices adequados
- Projeções calculadas em tempo real
- Modelos de leitura = modelos de escrita

### Requisitos

- Latência listagem catálogo: <150ms (P95)
- Latência cálculo preço: <50ms (P95)
- Cache hit rate: >70%
- Backward compatibility: 100%

## Decisão

Implementamos **CQRS Leve** (sem Event Sourcing completo):

### Commands (Escrita)

```typescript
// Comandos gravam no modelo canônico
src/domains/<domínio>/application/
├── commands/
│   ├── CreateProductCommand.ts
│   ├── UpdatePriceCommand.ts
│   └── handlers/
│       ├── CreateProductHandler.ts
│       └── UpdatePriceHandler.ts
```

**Características:**
- Gravam diretamente no PostgreSQL (modelo normalizado)
- Validação completa
- Emitem eventos de domínio
- Transacionais

### Queries (Leitura)

```typescript
// Queries leem de caches, views materializadas ou DB otimizado
src/domains/<domínio>/application/
├── queries/
│   ├── ListProductsQuery.ts
│   ├── GetPriceQuery.ts
│   └── handlers/
│       ├── ListProductsHandler.ts
│       └── GetPriceHandler.ts
```

**Características:**
- Lêem de Redis cache (TTL por domínio)
- Fallback para materialized views (PostgreSQL)
- Fallback final para modelo canônico
- Paginação cursor-based

### Fluxo de Dados

```
Command → Handler → Repository → DB (write)
                 ↓
              Event Bus
                 ↓
        Cache Invalidation

Query → Handler → Cache? → Materialized View? → DB (read)
```

### Materialized Views

Criamos views para queries pesadas:

```sql
-- Catalog search view
CREATE MATERIALIZED VIEW catalog_search AS
SELECT 
  p.id, p.title, p.description, p.category_id,
  v.sku, v.price, v.stock, v.distributor_id
FROM products p
JOIN product_variants v ON p.id = v.product_id
WHERE p.deleted_at IS NULL;

CREATE INDEX idx_catalog_search_category ON catalog_search(category_id);
CREATE INDEX idx_catalog_search_price ON catalog_search(price);

-- Refresh strategy: on-demand via event
REFRESH MATERIALIZED VIEW CONCURRENTLY catalog_search;
```

### Cache Strategy

TTLs por domínio:

```typescript
export const DomainTTLs = {
  catalog: 3600,    // 1 hour
  pricing: 300,     // 5 minutes (dados mais voláteis)
  quotes: 1800,     // 30 minutes
  solar: 86400,     // 24 hours (cálculos pesados)
} as const;
```

Invalidação precisa:

```typescript
// Event handler example
class ProductUpdatedHandler {
  async handle(event: DomainEvent<ProductUpdatedPayload>) {
    // Invalida cache específico
    await cache.delete(`product:${event.payload.productId}`);
    await cache.deleteByPattern(`product:list:*`);
    
    // Refresh materialized view
    await db.query('REFRESH MATERIALIZED VIEW CONCURRENTLY catalog_search');
  }
}
```

## Consequências

### Positivas

✅ **Performance**
- Queries otimizadas independentemente
- Cache distribuído (Redis)
- Materialized views para agregações

✅ **Escalabilidade**
- Read replicas potenciais
- Cache warming estratégico
- Backpressure em writes

✅ **Manutenibilidade**
- Lógica de read/write separada
- Validação apenas em commands
- Queries simples e diretas

### Negativas

⚠️ **Consistência Eventual**
- Cache pode estar desatualizado (TTL)
- Materialized views atrasadas
- Mitigado: TTLs curtos em dados críticos

⚠️ **Complexidade**
- Mais código (commands + queries)
- Cache invalidation logic
- Mitigado: Abstrações em shared/

⚠️ **Storage Overhead**
- Materialized views duplicam dados
- Cache Redis consome memória
- Mitigado: TTLs + eviction policies

## Alternativas Consideradas

### 1. CQRS Completo com Event Sourcing
- ✅ Auditoria completa
- ✅ Time travel debugging
- ❌ Complexidade extrema
- ❌ Storage overhead alto
- ❌ Não temos expertise

### 2. Sem CQRS (Modelo Único)
- ✅ Simplicidade
- ❌ Performance ruim em queries pesadas
- ❌ Não atende requisitos (<150ms)
- ❌ Dificulta cache

### 3. Read Replicas sem CQRS
- ✅ Escalabilidade de leitura
- ❌ Replicação lag
- ❌ Não resolve problema de cache
- ❌ Overhead operacional

## Implementação

### Fase 2 (3 semanas) - Próxima
- [ ] Migrar Catalog para CQRS
  - Commands: CreateProduct, UpdateProduct, DeleteProduct
  - Queries: ListProducts, GetProduct, SearchProducts
  - Cache: catalog:product:*, catalog:list:*
  - Materialized view: catalog_search

- [ ] Migrar Pricing para CQRS
  - Commands: CreateRule, UpdateRule
  - Queries: GetPrice, GetActivePromotions
  - Cache: pricing:*, promotion:*
  - View: pricing_matrix

### Monitoramento

Métricas Grafana:

```typescript
// Cache hit rate
sum(rate(cache_hits_total[5m])) / 
sum(rate(cache_requests_total[5m]))

// Query latency P95
histogram_quantile(0.95, 
  rate(query_duration_seconds_bucket[5m])
)

// Command latency P95
histogram_quantile(0.95, 
  rate(command_duration_seconds_bucket[5m])
)
```

## Referências

- [CQRS Pattern - Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [ADR-001: DDD Architecture](./ADR-001-DDD-Architecture.md)
- [ADR-003: Event-Driven Integration](./ADR-003-Event-Driven-Integration.md)

## Aprovação

- **Autor:** Time Backend YSH
- **Revisores:** Arquitetos, Tech Leads
- **Data de Aprovação:** 20/10/2025
