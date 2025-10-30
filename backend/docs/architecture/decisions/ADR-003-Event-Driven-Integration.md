# ADR-003: Event-Driven Integration Pattern

**Status**: Accepted  
**Date**: 2025-10-20  
**Deciders**: Arquitetura Backend Team  
**Related**: ADR-001 (DDD), ADR-002 (CQRS)

---

## Context

Com a adoção de DDD e separação em 12 domínios independentes, precisamos de um mecanismo de integração entre domínios que:

1. **Preserve a autonomia dos domínios**: Cada domínio deve ser independente e não conhecer detalhes internos de outros
2. **Mantenha baixo acoplamento**: Mudanças em um domínio não devem quebrar outros
3. **Suporte workflows complexos**: Processos como "Cotação → Aprovação → Pedido → Financiamento" envolvem múltiplos domínios
4. **Garanta consistência eventual**: Sistema distribuído precisa lidar com falhas e retries
5. **Seja auditável**: Rastreamento completo de eventos para compliance e debugging

### Cenários Críticos

**Fluxo de Cotação Completo**:
```
quotes → pricing (calcular valores)
      → approvals (análise de crédito)
      → orders (conversão em pedido)
      → financing (aprovação de crédito)
      → integrations (envio para distribuidoras)
```

**Catálogo e Preços**:
```
catalog (produto atualizado) → pricing (recalcular matrizes)
pricing (tabela alterada) → quotes (invalidar cache)
```

**Observabilidade**:
```
* (qualquer evento) → observability (métricas, logs, alertas)
```

---

## Decision

Adotamos **Event-Driven Architecture** usando o EventBus do Medusa como backbone, com:

### 1. Padrão Publish-Subscribe

**Publishers**: Domínios publicam eventos quando algo relevante acontece  
**Subscribers**: Domínios se inscrevem em eventos de outros domínios  
**Event Bus**: Medusa EventBus gerencia pub/sub (Redis como transport)

```typescript
// Publisher (domains/quotes/application/commands/handlers/CreateQuoteHandler.ts)
const quote = await this.repository.create(data);
await this.eventBus.emit(EventTypes.QUOTE_CREATED, {
  quoteId: quote.id,
  customerId: quote.customer_id,
  totalValue: quote.total_value,
  // ... payload
});

// Subscriber (domains/approvals/infrastructure/subscribers/QuoteCreatedSubscriber.ts)
@Subscriber(EventTypes.QUOTE_CREATED)
class QuoteCreatedSubscriber {
  async handle(event: DomainEvent<QuoteCreatedPayload>) {
    // Criar aprovação automaticamente se valor > R$ 50k
    if (event.data.totalValue > 50000) {
      await this.approvalService.createApproval({
        quoteId: event.data.quoteId,
        type: 'HIGH_VALUE_QUOTE'
      });
    }
  }
}
```

### 2. Event Contracts (Schema & Versioning)

**Todos os eventos seguem contrato fixo**:
```typescript
interface DomainEvent<T> {
  eventId: string;           // UUID único
  eventType: string;         // "quote.created" (30+ tipos definidos)
  version: string;           // "1.0", "2.0" (versionamento)
  timestamp: Date;           // ISO-8601
  aggregateId: string;       // ID da entidade principal (quote, product, etc)
  aggregateType: string;     // "Quote", "Product"
  data: T;                   // Payload tipado
  metadata?: {
    userId?: string;
    correlationId?: string;  // Rastreamento de fluxo
    causationId?: string;    // Evento que causou este
    origin?: string;         // "quotes", "catalog"
  };
}
```

**Versionamento de Eventos**:
- Eventos têm `version` explícita
- Subscribers especificam versões aceitas
- Breaking changes = nova versão (ex: `quote.created.v2`)
- Manter retrocompatibilidade por 6 meses

### 3. Subscriber Patterns (Idempotency & Ordering)

**Idempotência**: Processar mesmo evento 2x = mesmo resultado
```typescript
class ApprovalCreatedSubscriber {
  async handle(event: DomainEvent<ApprovalCreatedPayload>) {
    // 1. Check se já processou este evento
    const processed = await this.cache.exists(
      `event:processed:${event.eventId}`
    );
    if (processed) return; // Já processado
    
    // 2. Processar (com transaction)
    await this.db.transaction(async (tx) => {
      await this.orderService.createOrder(event.data, tx);
      
      // 3. Marcar como processado (TTL 7 dias)
      await this.cache.set(
        `event:processed:${event.eventId}`,
        'true',
        7 * 24 * 60 * 60
      );
    });
  }
}
```

**Ordenação**: Eventos do mesmo aggregate devem processar em ordem
```typescript
// Redis streams mantém ordem por aggregate
// Consumers usam consumer groups para paralelismo
await eventBus.emit(EventTypes.QUOTE_UPDATED, {
  // correlationId vincula eventos do mesmo fluxo
  metadata: { correlationId: quote.id }
});
```

### 4. Integration Flows (Exemplos)

**Fluxo 1: Cotação → Aprovação → Pedido**
```
1. quotes emite: quote.created
2. approvals escuta: quote.created → cria approval automática
3. approvals emite: approval.approved
4. orders escuta: approval.approved → cria order
5. orders emite: order.created
6. financing escuta: order.created → inicia processo de crédito
```

**Fluxo 2: Produto Atualizado → Invalidar Cache**
```
1. catalog emite: product.updated
2. pricing escuta: product.updated → recalcula matrizes
3. pricing emite: price.updated
4. quotes escuta: price.updated → invalida cache de cotações
```

**Fluxo 3: Observabilidade Global**
```
1. * (qualquer domínio) emite: *.* (qualquer evento)
2. observability escuta: *.* → registra métricas
3. observability detecta anomalias → emite: alert.triggered
4. integrations escuta: alert.triggered → envia email/Slack
```

### 5. Error Handling (Dead Letter Queue & Retries)

**Retry Strategy**: Exponential backoff com 5 tentativas
```typescript
const RETRY_CONFIG = {
  maxRetries: 5,
  delays: [1000, 5000, 15000, 60000, 300000], // 1s, 5s, 15s, 1min, 5min
  backoffMultiplier: 1.5
};

class ResilientSubscriber {
  async handle(event: DomainEvent<T>) {
    let attempt = 0;
    while (attempt < RETRY_CONFIG.maxRetries) {
      try {
        await this.process(event);
        return; // Sucesso
      } catch (error) {
        attempt++;
        if (attempt >= RETRY_CONFIG.maxRetries) {
          // Última tentativa falhou → DLQ
          await this.sendToDeadLetterQueue(event, error);
          throw error;
        }
        await sleep(RETRY_CONFIG.delays[attempt - 1]);
      }
    }
  }
}
```

**Dead Letter Queue (DLQ)**: Eventos que falharam após N retries
```typescript
// Tabela no DB
table events_dlq {
  id: uuid
  event_id: uuid (original)
  event_type: string
  event_payload: jsonb
  subscriber_name: string
  error_message: text
  retry_count: int
  failed_at: timestamp
  status: 'pending' | 'retrying' | 'resolved' | 'ignored'
}

// Dashboard Grafana: alertar se DLQ > 10 eventos
```

### 6. Compensating Transactions (Saga Pattern)

**Problema**: Fluxo multi-domínio pode falhar no meio
```
quote.created → approval.created → [FALHA] → order.created (não executou)
```

**Solução**: Compensating transactions para rollback
```typescript
class CreateOrderSaga {
  async execute(quoteId: string) {
    const steps = [];
    
    try {
      // Step 1: Criar approval
      const approval = await this.approvalService.create(quoteId);
      steps.push({ name: 'approval', id: approval.id });
      
      // Step 2: Criar order
      const order = await this.orderService.create(approval.id);
      steps.push({ name: 'order', id: order.id });
      
      // Step 3: Reservar estoque
      await this.inventoryService.reserve(order.id);
      steps.push({ name: 'inventory', id: order.id });
      
    } catch (error) {
      // Rollback na ordem inversa
      for (const step of steps.reverse()) {
        await this.compensate(step);
      }
      throw error;
    }
  }
  
  async compensate(step: { name: string; id: string }) {
    switch (step.name) {
      case 'inventory':
        await this.inventoryService.release(step.id);
        break;
      case 'order':
        await this.orderService.cancel(step.id);
        break;
      case 'approval':
        await this.approvalService.cancel(step.id);
        break;
    }
  }
}
```

### 7. Event Types Definidos (30+)

Já mapeados em `src/shared/events/index.ts`:
```typescript
// Catalog
catalog.product.created
catalog.product.updated
catalog.product.deleted
catalog.sku.stockChanged

// Pricing
pricing.price.updated
pricing.discount.applied
pricing.tariff.changed

// Quotes
quote.created
quote.updated
quote.submitted
quote.approved
quote.rejected

// Approvals
approval.created
approval.approved
approval.rejected
approval.escalated

// Orders
order.created
order.confirmed
order.shipped
order.delivered
order.cancelled

// Financing
financing.application.submitted
financing.application.approved
financing.application.rejected

// Solar
solar.simulation.completed
solar.design.generated

// Integrations
distributor.order.sent
distributor.order.confirmed
distributor.order.failed
```

---

## Consequences

### Positivas

✅ **Baixo acoplamento**: Domínios não conhecem uns aos outros, apenas eventos  
✅ **Escalabilidade**: Subscribers podem processar em paralelo  
✅ **Auditabilidade**: Event log completo de todas as operações  
✅ **Resiliência**: Retry automático e DLQ para falhas  
✅ **Extensibilidade**: Adicionar novo subscriber não quebra existentes  
✅ **Consistência eventual**: Sistema funciona mesmo com falhas temporárias  

### Negativas

❌ **Complexidade**: Debugging de fluxos multi-domínio mais difícil  
❌ **Consistência eventual**: Dados podem estar temporariamente inconsistentes  
❌ **Monitoramento**: Precisa de observabilidade robusta (Grafana, logs)  
❌ **Testes**: Testes end-to-end precisam simular eventos assíncronos  
❌ **Latência**: Fluxos síncronos se tornam assíncronos (pode ser +200ms)  

### Mitigações

- **Grafana dashboards**: Visualização de fluxos de eventos em tempo real
- **Correlation IDs**: Rastreamento completo de requests multi-domínio
- **Circuit breaker**: Evitar cascata de falhas entre domínios
- **Feature flags**: Rollback fácil de integrações problemáticas
- **Testes de contrato**: Validar schemas de eventos entre domínios

---

## Alternatives Considered

### 1. Chamadas HTTP Diretas (Rejected)

**Como seria**:
```typescript
// domains/quotes/application/CreateQuoteHandler.ts
const quote = await this.quoteRepo.create(data);
await this.httpClient.post('http://approvals/api/approvals', {
  quoteId: quote.id
});
```

**Por que não**:
- ❌ Alto acoplamento (quotes conhece URL de approvals)
- ❌ Falha síncrona (se approvals cair, quotes falha)
- ❌ Dificulta testes (precisa mockar HTTP)
- ❌ Sem retry automático

### 2. Message Queue Externo (RabbitMQ/Kafka) (Rejected)

**Como seria**:
- Instalar RabbitMQ/Kafka separadamente
- Domínios publicam/consomem de filas/tópicos

**Por que não**:
- ❌ Infraestrutura adicional (mais complexidade operacional)
- ❌ Medusa já tem EventBus com Redis (redundância)
- ❌ Overkill para escala atual (278 routes, não milhões)
- ✅ Pode ser migrado no futuro se necessário

### 3. Shared Database (Rejected)

**Como seria**:
- Todos os domínios leem/escrevem nas mesmas tabelas

**Por que não**:
- ❌ Acoplamento máximo (viola DDD)
- ❌ Conflitos de schema entre domínios
- ❌ Impossível escalar domínios independentemente

---

## Implementation Plan

### Fase 1 (Atual): Fundação
- ✅ Definir EventTypes em `src/shared/events/`
- ✅ Criar DomainEvent interface
- ✅ Criar EventPublisher helper

### Fase 2: Primeiro Subscriber (Semana 3-4)
- Criar `domains/approvals/infrastructure/subscribers/QuoteCreatedSubscriber.ts`
- Registrar subscriber no Medusa
- Testar fluxo: quote.created → approval.created

### Fase 3: Dead Letter Queue (Semana 5)
- Criar tabela `events_dlq`
- Implementar retry strategy
- Dashboard Grafana para DLQ

### Fase 4: Correlation IDs (Semana 6)
- Adicionar correlationId em todos os eventos
- Implementar rastreamento em logs
- Dashboard de fluxos no Grafana

### Fase 5: Sagas (Fase 3 do projeto)
- Implementar Saga Orchestrator
- Compensating transactions para fluxos críticos

---

## Monitoring & Metrics

**Métricas Críticas** (Prometheus + Grafana):
```
# Total de eventos publicados por tipo
events_published_total{event_type="quote.created"}

# Latência de processamento de subscribers
subscriber_processing_duration_seconds{subscriber="QuoteCreatedSubscriber"}

# Taxa de falha de subscribers
subscriber_failures_total{subscriber="ApprovalCreatedSubscriber"}

# Tamanho da DLQ
events_dlq_size{status="pending"}

# Tempo médio de saga
saga_duration_seconds{saga="CreateOrderSaga"}
```

**Alertas**:
- DLQ > 50 eventos → PagerDuty
- Subscriber com >5% de falhas → Slack
- Latência de subscriber >10s → Slack

---

## References

- [Medusa EventBus Documentation](https://docs.medusajs.com/development/events/create-subscriber)
- [Event-Driven Architecture Patterns (Martin Fowler)](https://martinfowler.com/articles/201701-event-driven.html)
- [Saga Pattern (microservices.io)](https://microservices.io/patterns/data/saga.html)
- ADR-001: DDD Architecture
- ADR-002: CQRS Implementation
- `src/shared/events/index.ts` (EventTypes e interfaces)
