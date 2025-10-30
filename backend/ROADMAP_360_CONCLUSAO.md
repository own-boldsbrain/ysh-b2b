# 🎯 YSH Solar B2B - Plano de Conclusão 360º

## 📊 Status Executivo

### ✅ Fase 1 Concluída: Infraestrutura Unificada

**Problema Resolvido**: Havia duplicação e conflitos entre `docker-compose.yml` (antigo) e `.deploy/docker-compose.agents.yml` (novo).

**Solução Implementada**: Criado `docker-compose.unified.yml` que consolida:

#### 🗄️ Camada de Dados
- **PostgreSQL Temporal** (porta 5433) - Dedicado ao Temporal
- **PostgreSQL Supabase** (porta 5432) - Banco principal da aplicação
- **Redis Stack** (6379 + RedisInsight 8001) - Cache, sessions, Bull queues
- **Redpanda** (19092) - Event streaming (substitui RabbitMQ)

#### ⚡ Camada de Orquestração
- **Temporal Server** (7233 gRPC + 8080 UI) - Workflow orchestration
- **Temporal Workers** (catalog-extractor, price-intelligence, product-enricher, sku-governor)

#### 🤖 Camada de Inteligência
- **Huginn** (porta 3001) - Price tracking & automation
- **Ollama** (11434) - Local LLM para enrichment

#### 📊 Camada de Observabilidade
- **Grafana** (3000) - Dashboards
- **Prometheus** (9090) - Metrics
- **Loki** (3100) - Logs centralizados
- **Promtail** - Log collection

#### 🌐 Camada de Suporte
- **Kong** (8000) - API Gateway
- **Supabase Studio** (54321) - DB Admin
- **Redpanda Console** (8082) - Kafka UI
- **Browserless Chrome** (3333) - Browser automation

### 📦 Arquivos Criados

1. **docker-compose.unified.yml** (530 linhas)
   - Consolida todos os serviços necessários
   - Resolve conflitos de porta
   - Define workers com replicas e resource limits
   - Healthchecks para todos os serviços críticos

2. **start-unified-infra.ps1** (180 linhas)
   - Script de bootstrap automatizado
   - Cria arquivos de configuração mínimos
   - Inicia serviços em ordem correta (infra → temporal → support → observability)
   - Aguarda health checks entre etapas
   - Exibe URLs de acesso ao final

3. **init-scripts/supabase-init.sql** (automático via script)
   - Schema `distributor_data` com tabelas:
     - `distributors` - 7 distribuidores pré-cadastrados
     - `products` - Catálogo unificado
     - `product_prices` - Histórico de preços
     - `sync_runs` - Rastreamento de sincronizações
   - Índices otimizados para queries

---

## 🎯 Roadmap 360º - Próximas Fases

### **Fase 2: Validação Fortlev** (2-3h)
**Status**: Script criado, aguardando execução

```powershell
cd mcp-servers
npx tsx extract-fortlev-full.ts
```

**Objetivo**: Extrair catálogo completo (100+ produtos) com infinite scroll, validar estrutura de dados, gerar baseline para replicação.

**Entregáveis**:
- ✅ `fortlev-catalog-full.json` - Catálogo completo
- ✅ `fortlev-catalog-full.csv` - Formato CSV para análise
- ✅ Estatísticas por categoria
- ✅ Análise de preços (min/max/avg)

---

### **Fase 3-4: Implementação dos 6 Agentes Restantes** (2-3 dias)

| Distribuidor | URL Base | Estratégia | Complexidade |
|-------------|----------|-----------|--------------|
| **Neosolar** | loja.neosolar.com.br | Scraping direto | Média |
| **Solfácil** | marketplace.solfacil.com.br | Marketplace API | Baixa |
| **Fotus** | fotusenergia.com.br | Scraping + AJAX | Alta |
| **Odex** | odexdistribuidora.com.br | Scraping direto | Média |
| **Edeltec** | edeltecsolar.com.br | Scraping direto | Baixa |
| **Dynamis** | dynamissolar.com.br | Scraping + SPA | Alta |

**Template de Implementação** (por agente):
1. ✅ Debug script (`debug-[distributor].ts`) - 30min
2. ✅ HTML structure mapping - 45min
3. ✅ Authentication implementation - 1h
4. ✅ MCP server (`distributors/[name]/server.ts`) - 2h
5. ✅ Test script (`test-[distributor]-simple.ts`) - 30min
6. ✅ Full extraction script (`extract-[distributor]-full.ts`) - 1h

**Total Estimado**: ~6h por agente = 36h (~4.5 dias com 8h/dia)

---

### **Fase 5: Temporal Workflows** (1 dia)

**Estrutura de Workflows**:

```typescript
// src/workflows/distributor-sync.workflow.ts
export async function syncDistributorWorkflow(
  distributorSlug: string,
  fullSync: boolean = false
): Promise<SyncResult> {
  const activities = proxyActivities<DistributorActivities>({
    startToCloseTimeout: '30 minutes',
    retry: { maximumAttempts: 3 }
  });

  // 1. Authenticate
  const session = await activities.authenticate(distributorSlug);
  
  // 2. List products
  const products = await activities.listProducts(session, fullSync);
  
  // 3. Enrich with LLM
  const enriched = await activities.enrichProducts(products);
  
  // 4. Persist to PostgreSQL
  const saved = await activities.persistProducts(enriched);
  
  // 5. Publish events to Redpanda
  await activities.publishProductEvents(saved);
  
  return { productsProcessed: saved.length };
}
```

**Workflows a Criar**:
1. ✅ `syncDistributorWorkflow` - Sync individual
2. ✅ `syncAllDistributorsWorkflow` - Sync paralelo (7 agentes)
3. ✅ `priceMonitoringWorkflow` - Monitoramento contínuo
4. ✅ `enrichmentWorkflow` - LLM batch processing

---

### **Fase 6: Scheduler com Node-Cron** (4h)

**Arquivo**: `src/scheduler/cron-scheduler.ts`

```typescript
import cron from 'node-cron';
import { Connection, Client } from '@temporalio/client';

// Daily full sync - 00:00 BRT
cron.schedule('0 0 * * *', async () => {
  await client.workflow.start('syncAllDistributorsWorkflow', {
    args: [{ fullSync: true }]
  });
});

// Hourly incremental - Every hour
cron.schedule('0 * * * *', async () => {
  await client.workflow.start('syncAllDistributorsWorkflow', {
    args: [{ fullSync: false }]
  });
});

// Price monitoring - Every 4 hours
cron.schedule('0 */4 * * *', async () => {
  await client.workflow.start('priceMonitoringWorkflow', {
    args: [{ distributors: 'all' }]
  });
});
```

**Schedules**:
- ✅ **00:00** - Full sync (todos distribuidores)
- ✅ **A cada hora** - Incremental sync
- ✅ **A cada 4h** - Price monitoring
- ✅ **06:00** - LLM enrichment batch

---

### **Fase 7: Huginn Price Intelligence** (1 dia)

**Scenarios a Configurar**:

1. **Price Change Detection**
   - WebhookAgent ← Recebe events do Redpanda
   - TriggerAgent → Detecta variação > 5%
   - EmailAgent → Alerta equipe de compras

2. **New Product Notifications**
   - WebhookAgent ← Novos produtos via Temporal
   - DataOutputAgent → Dashboard em tempo real

3. **Stock Monitoring**
   - HttpStatusAgent → Polling de availability
   - EventFormattingAgent → Normaliza dados
   - PostAgent → Webhook para Slack/Teams

4. **Competitor Analysis**
   - DataOutputAgent → Agrega preços por categoria
   - JavaScriptAgent → Calcula médias e outliers
   - DashboardAgent → Visualização comparativa

**Integrações**:
- ✅ Redpanda → Huginn (eventos de produtos)
- ✅ Huginn → PostgreSQL (queries de preços)
- ✅ Huginn → Slack/Teams (alertas)

---

### **Fase 8: LLM Enrichment com Ollama** (1 dia)

**Modelos a Baixar**:
```bash
docker exec ysh-ollama ollama pull llama3     # 4.7GB - General purpose
docker exec ysh-ollama ollama pull mistral    # 4.1GB - Fast inference
docker exec ysh-ollama ollama pull phi3       # 2.3GB - Lightweight
```

**Pipeline de Enrichment**:

```typescript
// src/services/llm-enricher.service.ts
export class LLMEnricherService {
  async enrichProduct(product: Product): Promise<EnrichedProduct> {
    // 1. Semantic categorization
    const category = await this.categorize(product.title);
    
    // 2. Technical specs extraction
    const specs = await this.extractSpecs(product.description);
    
    // 3. SEO content generation
    const seo = await this.generateSEO(product);
    
    // 4. Comparison table generation
    const comparison = await this.generateComparison(product);
    
    return { ...product, category, specs, seo, comparison };
  }
}
```

**Use Cases**:
- ✅ Categorização semântica (ex: "Inversor Growatt 3kW" → "Inversor Solar / String / 3-5kW")
- ✅ Extração de specs técnicas (potência, tensão, corrente, eficiência)
- ✅ Geração de descrições SEO-friendly
- ✅ Tabelas comparativas automáticas

---

### **Fase 9: Grafana Dashboards** (4h)

**Dashboards a Criar**:

#### 1. **Agent Health Dashboard**
- ✅ Success rate por distribuidor (últimas 24h)
- ✅ Duração média de sync (linha temporal)
- ✅ Errors por tipo (pie chart)
- ✅ Products extracted (gauge)

#### 2. **Coverage 360º Dashboard**
- ✅ Products per distributor (bar chart)
- ✅ Category distribution (treemap)
- ✅ Growth timeline (área stacked)
- ✅ Data freshness (heatmap)

#### 3. **Price Intelligence Dashboard**
- ✅ Price trends por categoria (multi-line)
- ✅ Competitor comparison (radar chart)
- ✅ Alert history (table)
- ✅ Price volatility (candlestick)

#### 4. **System Metrics Dashboard**
- ✅ CPU/Memory usage (gauges)
- ✅ Temporal workflow status (pie)
- ✅ Redis cache hit rate (gauge)
- ✅ Redpanda throughput (line)

**Alertas**:
- ❌ Sync failure rate > 20%
- ❌ Data staleness > 48h
- ❌ Price spike > 30%
- ❌ Worker CPU > 90%

---

### **Fase 10: Validação End-to-End** (4h)

**Checklist de Validação**:

1. ✅ **7 Agentes Operacionais**
   - [ ] Fortlev - Full extraction OK
   - [ ] Neosolar - Full extraction OK
   - [ ] Solfácil - Full extraction OK
   - [ ] Fotus - Full extraction OK
   - [ ] Odex - Full extraction OK
   - [ ] Edeltec - Full extraction OK
   - [ ] Dynamis - Full extraction OK

2. ✅ **PostgreSQL Persistence**
   - [ ] Tabela `distributors` - 7 registros
   - [ ] Tabela `products` - 1000+ registros
   - [ ] Tabela `product_prices` - 7000+ registros (histórico)
   - [ ] Tabela `sync_runs` - Log completo

3. ✅ **Temporal Workflows**
   - [ ] `syncDistributorWorkflow` - 7/7 sucesso
   - [ ] `syncAllDistributorsWorkflow` - Execução paralela OK
   - [ ] `priceMonitoringWorkflow` - Detecta mudanças
   - [ ] Scheduler - Cron jobs ativos

4. ✅ **Huginn Price Tracking**
   - [ ] 7 scenarios configurados
   - [ ] Alertas de preço funcionando
   - [ ] Dashboard de competitor analysis

5. ✅ **LLM Enrichment**
   - [ ] Ollama operacional (llama3)
   - [ ] Categorização semântica - 95%+ accuracy
   - [ ] Specs extraction - 80%+ recall
   - [ ] SEO content gerado para todos produtos

6. ✅ **Grafana Observability**
   - [ ] 4 dashboards criados e funcionais
   - [ ] Alertas configurados
   - [ ] Métricas em tempo real

---

## 🚀 Execução Imediata

### Passo 1: Iniciar Infraestrutura (5min)

```powershell
cd C:\Users\fjuni\OneDrive\Documentos\GitHub\ysh-b2b\backend
.\start-unified-infra.ps1
```

**Aguardar**: ~2-3 minutos para todos os serviços subirem

### Passo 2: Baixar Modelos LLM (10min)

```powershell
docker exec ysh-ollama ollama pull llama3
docker exec ysh-ollama ollama pull mistral
```

### Passo 3: Validar Fortlev (5min)

```powershell
cd mcp-servers
npx tsx extract-fortlev-full.ts
```

**Expectativa**: 100-150 produtos extraídos, JSON + CSV gerados

### Passo 4: Iniciar Workers Temporal (2min)

```powershell
docker-compose -f docker-compose.unified.yml up -d `
    catalog-extractor-worker `
    price-intelligence-worker `
    product-enricher-worker `
    sku-governor-worker
```

---

## 📈 Métricas de Sucesso 360º

| Métrica | Baseline | Target 360º | Status |
|---------|----------|-------------|--------|
| **Distribuidores Ativos** | 1 (Fortlev) | 7 | 🟡 14% |
| **Produtos Catalogados** | 20 | 1000+ | 🟡 2% |
| **Cobertura de Preços** | 0% | 100% | 🔴 0% |
| **Accuracy Categorização** | Manual | 95%+ LLM | 🔴 0% |
| **Freshness de Dados** | N/A | < 1h | 🔴 0% |
| **Alertas de Preço** | 0 | Tempo real | 🔴 0% |
| **Dashboards Operacionais** | 0 | 4 | 🔴 0% |
| **Success Rate Sync** | 100% | > 95% | 🟢 100% |

---

## 🎯 Prioridades Imediatas

### Hoje (2-3h):
1. ✅ Executar `start-unified-infra.ps1` → Validar todos serviços UP
2. ✅ Executar `extract-fortlev-full.ts` → Baseline de 100+ produtos
3. ✅ Verificar PostgreSQL → Confirmar persist das tabelas iniciais

### Esta Semana (20-30h):
1. ✅ Implementar 6 agentes restantes (6h cada = 36h)
2. ✅ Criar Temporal workflows básicos (8h)
3. ✅ Setup scheduler com cron (4h)
4. ✅ Configurar Huginn scenarios (8h)

### Próxima Semana (15h):
1. ✅ Integração LLM enrichment (8h)
2. ✅ Dashboards Grafana (4h)
3. ✅ Validação end-to-end (3h)
4. ✅ Documentação final (2h)

---

## 🔗 Links Rápidos

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Temporal UI** | http://localhost:8080 | - |
| **Supabase Studio** | http://localhost:54321 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Huginn** | http://localhost:3001 | - |
| **Redpanda Console** | http://localhost:8082 | - |
| **Prometheus** | http://localhost:9090 | - |
| **RedisInsight** | http://localhost:8001 | - |

---

## 📚 Documentação de Referência

- ✅ **FORTLEV_AGENT_360_REPORT.md** - Fortlev implementation details
- ✅ **docker-compose.unified.yml** - Infrastructure as Code
- ✅ **start-unified-infra.ps1** - Bootstrap automation
- ✅ **init-scripts/supabase-init.sql** - Database schema

---

## ⚡ Comando de Validação Rápida

```powershell
# 1. Verificar containers ativos
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Verificar logs de erro
docker-compose -f docker-compose.unified.yml logs --tail=50 --follow

# 3. Testar Temporal
curl http://localhost:8080/api/v1/namespaces

# 4. Testar PostgreSQL
docker exec ysh-postgres-supabase psql -U supabase_admin -d postgres -c "\dt distributor_data.*"

# 5. Testar Ollama
curl http://localhost:11434/api/tags
```

---

**Última Atualização**: 2025-01-XX  
**Versão**: 1.0.0  
**Status**: ✅ Fase 1 Completa | 🟡 Fases 2-10 Pendentes
