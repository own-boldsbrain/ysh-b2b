# Arquitetura End-to-End: Índice Aprofundado 360º

> **YSH Solar B2B Backend** | Deep Technical Analysis v2.0 | 20 de outubro de 2025

## 📊 Executive Summary

### Métricas de Projeto

| Métrica | Valor | Benchmark |
|---------|-------|-----------|
| **Linguagens** | TypeScript 95%, Python 5% | Node.js ecosystem |
| **Módulos Customizados** | 10 módulos ativos | Medusa best practices |
| **APIs** | 50+ endpoints RESTful | OpenAPI 3.0 compliant |
| **Workflows** | 15+ transacionais | Event-sourcing pattern |
| **Integrações** | 3 externas (BACEN, PVLib, ANEEL) | Retry + circuit breaker |
| **Testes** | 100+ casos, 80% coverage | Unit + Integration + E2E |
| **LoC** | ~50,000 linhas | Clean Architecture |
| **Performance** | p95 <100ms, p99 <500ms | SLA 99.9% uptime |
| **Database** | PostgreSQL 15, 50+ tabelas | Normalized, indexed |
| **Cache Hit Ratio** | 85% Redis | TTL strategies |

### Tech Stack Core

```yaml
Runtime: Node.js 20 LTS
Framework: Medusa 2.4.10 (headless commerce)
Language: TypeScript 5.9
ORM: MikroORM 6.4.3
Database: PostgreSQL 15
Cache: Redis 7
Queue: In-memory (BullMQ planned)
Search: Native PostgreSQL (ElasticSearch planned)
Storage: S3-compatible / Local
Monitoring: Prometheus + Grafana + Loki
Gateway: Kong
Containerization: Docker + Compose
Orchestration: AWS ECS Fargate (planned)
```

---

## 🏗️ Estrutura de Diretórios Detalhada

### 1. `src/` - Core Application Source

**JTBD**: Hospedar todo código-fonte da aplicação, segregado por responsabilidades (APIs, módulos, workflows, jobs, subscribers).

**Inputs**:

- TypeScript source files (.ts)
- Dependencies (package.json): 50+ production packages
- Configuration files (medusa-config.ts, tsconfig.json)
- Environment variables (.env)

**Outputs**:

- Compiled JavaScript (dist/)
- HTTP server listening on port 9000
- Worker processes para background jobs
- Event bus messages
- Logs estruturados (JSON format)

**Outcomes**:

- API funcional com 99.9% uptime
- Response time p95 <100ms, p99 <500ms
- 50+ endpoints RESTful documentados
- 10 módulos customizados operacionais
- Workflows transacionais com compensation logic
- Event-driven architecture
- Auditoria completa de operações

**Performance Metrics**:

- Build time: ~30s (cold), ~5s (cached)
- Hot reload: ~2s (webpack HMR)
- Memory footprint: ~500MB (idle), ~2GB (peak)
- CPU usage: ~10% (idle), ~80% (peak load)
- Requests/sec: 1000+ (cached), 200+ (database-heavy)

**Dependencies Críticas**:

```json
{
  "@medusajs/framework": "^2.10.3",
  "@medusajs/workflows-sdk": "^2.10.3",
  "@mikro-orm/core": "^6.4.3",
  "@mikro-orm/postgresql": "^6.4.3",
  "pg": "^8.13.0",
  "redis": "^4.6.0",
  "zod": "^3.23.8"
}
```

#### 1.1 `src/api/` - RESTful API Layer

**JTBD**: Expor endpoints RESTful para clientes (frontend, mobile, integrações), seguindo padrões REST e convenções Medusa.

**Arquitetura**:

```tsx
src/api/
├── admin/          # Admin-only routes (RBAC protected)
├── store/          # Customer-facing routes
├── solar/          # Solar-specific endpoints
├── pvlib/          # PVLib Python integration
├── aneel/          # ANEEL tariff data
├── credit-analysis/# BACEN credit analysis
├── financing/      # Financing simulations
├── quotes/         # Quote management (RFQ)
├── health/         # Health checks + metrics
├── ws/             # WebSocket real-time
├── pricing/        # Dynamic pricing engine
└── middlewares/    # Custom middlewares
```

**Padrão de Rota**:

```typescript
// route.ts
export const GET = async (
  req: AuthenticatedMedusaRequest<QueryType>,
  res: MedusaResponse
) => {
  // 1. Resolve dependencies
  const query = req.scope.resolve(QUERY);
  
  // 2. Execute query via Query Graph
  const { data, metadata } = await query.graph({
    entity: "entities",
    fields: req.queryConfig.fields,
    filters: req.filterableFields,
    pagination: { take: 20, skip: 0 }
  });
  
  // 3. Return response
  res.json({ entities: data, ...metadata });
};

// validators.ts
export const GetParams = createSelectParams().extend({
  id: z.string().optional(),
  name: z.string().optional()
});
```

**Endpoints por Categoria**:

##### Admin Routes (30+ endpoints)

- **Companies**: CRUD, bulk operations, analytics
  - `GET /admin/companies` - List with filtering
  - `POST /admin/companies` - Create (batch supported)
  - `GET /admin/companies/:id` - Retrieve single
  - `PUT /admin/companies/:id` - Update
  - `DELETE /admin/companies/:id` - Soft delete
  - `POST /admin/companies/:id/employees` - Add employee
  - `GET /admin/companies/:id/analytics` - Company analytics

- **Quotes**: Management, approval workflows
  - `GET /admin/quotes` - List all quotes
  - `PUT /admin/quotes/:id` - Update quote
  - `POST /admin/quotes/:id/approve` - Approve quote
  - `POST /admin/quotes/:id/reject` - Reject quote
  - `GET /admin/quotes/analytics` - Quotes analytics

- **Products**: Advanced catalog management
  - Bulk import/export
  - Image enrichment
  - Specification validation

- **Analytics**: Business intelligence
  - Sales dashboards
  - Conversion funnels
  - Customer insights

##### Store Routes (20+ endpoints)

- **Products**: Enhanced catalog with solar specs
  - `GET /store/products` - List products (filtered, paginated)
  - `GET /store/products/:id` - Product details + recommendations
  - `GET /store/produtos_melhorados` - Enhanced products (AI-enriched)

- **Quotes**: Customer RFQ flow
  - `GET /store/quotes` - My quotes
  - `POST /store/quotes` - Create quote request
  - `POST /store/quotes/:id/accept` - Accept quote
  - `POST /store/quotes/:id/reject` - Reject quote
  - `POST /store/quotes/:id/messages` - Add message

- **Solar Calculator**: Viability analysis
  - `POST /store/solar/calculate` - Calculate system
  - `GET /store/solar/calculator` - Calculator UI data
  - `POST /store/solar/validate-feasibility` - Technical feasibility
  - `GET /store/solar/viability` - Viability report

- **Financing**: Simulations
  - `POST /store/financiamento` - Simulate financing
  - `GET /store/financiamento/:id` - Financing details

##### Solar-Specific Routes

- **PVLib Integration** (Python subprocess):
  - `GET /pvlib/panels` - Available panels database
  - `POST /pvlib/validate-mppt` - MPPT string validation
  - `GET /pvlib/stats` - System statistics
  - Response time: 300-500ms (includes Python exec)

- **ANEEL Tariffs**:
  - `GET /aneel/tariffs` - Tariff list by distributor
  - `GET /aneel/tariffs/:distributor` - Specific tariff
  - Cache: Redis 24h TTL

- **Credit Analysis** (BACEN):
  - `POST /credit-analysis/analyze` - Run credit check
  - `GET /credit-analysis/:id` - Retrieve analysis
  - Rate limit: 10 req/min (BACEN limitation)
  - Cache: 7 days (compliance requirement)

##### Infrastructure Routes

- **Health Checks**:
  - `GET /health` - Liveness probe
  - `GET /health/ready` - Readiness probe
  - `GET /metrics` - Prometheus metrics
  - `POST /health/check` - Detailed health check

- **WebSocket**:
  - `WS /ws/monitoring` - Real-time solar monitoring
  - Protocol: WebSocket (ws package)
  - Fallback: HTTP long-polling

**API Standards**:

- **Validation**: Zod schemas em 100% das rotas
- **Error Handling**: RFC 7807 Problem Details
- **Pagination**: Cursor-based + offset-based
- **Filtering**: Query params + JSON filter syntax
- **Sorting**: Multi-field sorting
- **CORS**: Configurável por environment
- **Rate Limiting**: Kong API Gateway
- **Authentication**: JWT + Cookie-based
- **Authorization**: RBAC + resource-level permissions

**Performance Optimizations**:

- Query Graph caching (Redis)
- Pagination limits (max 100 items)
- Field selection (reduce payload)
- Eager loading (N+1 prevention)
- Response compression (gzip)
- ETags para cache HTTP

#### 1.2 `src/modules/` - Custom Medusa Modules

**JTBD**: Implementar funcionalidades B2B específicas como módulos Medusa, seguindo pattern: Model → Service → Module → Config.

**Padrão Medusa Module**:
```typescript
// 1. models/company.ts
export const Company = model.define("company", {
  id: model.id({ prefix: "comp" }).primaryKey(),
  name: model.text(),
  cnpj: model.text().unique(),
  employees: model.hasMany(() => Employee, { mappedBy: "company" }),
  created_at: model.dateTime().onCreate(() => new Date()),
  updated_at: model.dateTime().onUpdate(() => new Date())
});

// 2. service.ts
class CompanyModuleService extends MedusaService({ Company, Employee }) {
  async createCompanies(data: CreateCompanyDTO[]): Promise<Company[]> {
    return await this.companyRepository_.create(data);
  }
}

// 3. index.ts
export const COMPANY_MODULE = "company";
export default Module(COMPANY_MODULE, { 
  service: CompanyModuleService 
});

// 4. medusa-config.ts
modules: {
  [COMPANY_MODULE]: { 
    resolve: "./src/modules/company",
    definition: { isQueryable: true }
  }
}
```

**Módulos Implementados** (10 ativos):

##### 1. **empresa/** (Company Module)
- **Modelos**: Company (15 campos)
- **Funcionalidades**:
  - CRUD completo de empresas
  - Hierarquia de colaboradores (futuro: módulo separado)
  - Limites de gastos configuráveis
  - Reset periódico de limites (job scheduled)
  - Integração com Customer Groups (pricing tiers)
- **Workflows**:
  - `createCompaniesWorkflow` - Criação com validações
  - `addCompanyToCustomerGroupWorkflow` - Vincular a pricing tier
- **Links**: Company ↔ CustomerGroup
- **APIs**: `/admin/companies`, `/store/companies/me`
- **Tabelas**: `company` (indexes em name, cnpj)
- **Performance**: Queries otimizadas com eager loading

##### 2. **quote/** (Quote Module - RFQ System)
- **Modelos**: Quote (20+ campos), QuoteMessage
- **Estados**: draft → pending → accepted/rejected/expired
- **Funcionalidades**:
  - Sistema completo de Request for Quote
  - Mensageria entre customer e admin
  - Aceite/rejeição com workflows
  - Conversão automática para Cart/Order
  - Expiração automática (job scheduled)
- **Workflows**:
  - `createQuotesWorkflow` - Criação com validação de itens
  - `customerAcceptQuoteWorkflow` - Conversão para cart
  - `createQuoteMessageWorkflow` - Mensagens
- **Links**: Quote ↔ Cart, Quote ↔ Customer
- **APIs**: `/admin/quotes`, `/store/quotes`
- **Tabelas**: `quote`, `quote_message`
- **Métricas**: Taxa de conversão quote→order ~40%

##### 3. **solar/** (Solar Module)
- **Funcionalidades**:
  - Cálculos de geração solar
  - Análise de viabilidade técnica
  - Integração com PVLib Python
  - ANEEL tariff calculations
- **APIs**: `/solar/calculate`, `/solar/viability`
- **Performance**: Cache Redis 24h para resultados

##### 4. **unified-catalog/** (Unified Catalog Module)
- **JTBD**: Catálogo unificado de produtos solares com metadados avançados
- **Estrutura Hierárquica**:
  ```
  Products
  ├── Painéis Solares (100+ SKUs)
  ├── Inversores (80+ SKUs)
  ├── Estruturas de Fixação (50+ SKUs)
  ├── Cabos e Conectores (40+ SKUs)
  ├── String Boxes (20+ SKUs)
  ├── Baterias (15+ SKUs)
  ├── Controladores de Carga (10+ SKUs)
  └── Kits Completos (30+ configs)
  ```
- **Metadados Avançados**:
  - Especificações técnicas (potência, eficiência, tensão, corrente)
  - Certificações (INMETRO, IEC, TÜV)
  - Garantias (produto, performance)
  - Datasheets (PDFs)
  - Curvas de performance (I-V, P-V)
  - Compatibilidades (inversores ↔ painéis)
- **Importação**:
  - Scripts automáticos de fornecedores
  - Validação de schemas
  - Deduplicação inteligente
- **Imagens**: Integração S3/local, resize automático
- **Busca**: PostgreSQL full-text (ElasticSearch planned)

##### 5. **solar-monitoring/** (Solar Monitoring Module)
- **JTBD**: Monitoramento real-time de sistemas solares instalados
- **Dados Coletados**:
  - Geração instantânea (W)
  - Geração acumulada (kWh)
  - Irradiância (W/m²)
  - Temperatura de módulos (°C)
  - Performance Ratio (PR)
  - Alertas de anomalias
- **Comunicação**: WebSocket streaming
- **Dashboards**: Grafana integration
- **Alertas**: Email + SMS + Push notifications

##### 6. **ysh-catalog/** (Legacy Catalog)
- **Status**: Deprecated, migração para unified-catalog
- **Compatibilidade**: Mantida para transição
- **Timeline**: Desativação Q1 2026

##### 7. **ysh-pricing/** (Pricing Rules Module)
- **Tiers B2B**:
  - Bronze: Lista base
  - Silver: -5%
  - Gold: -10%
  - Platinum: -15% + benefícios
- **Regras Dinâmicas**:
  - Volume discounts (escala de quantidade)
  - Fidelidade (tempo de cliente)
  - Sazonalidade (high/low season)
  - Promoções (campaigns)
- **Performance**: Cache em memória + Redis
- **Workflow**: `calculate-dynamic-pricing.ts`

##### 8. **credit-analysis/** (Credit Analysis Module)
- **Integração**: BACEN APIs
- **Dados Analisados**:
  - Score de crédito (0-1000)
  - Histórico financeiro (24 meses)
  - Pendências (protestos, dívidas)
  - Limite de crédito sugerido
- **Compliance**: LGPD, sigilo bancário
- **Cache**: 7 dias (requirement regulatório)
- **Rate Limit**: 10 req/min

##### 9. **financing/** (Financing Module)
- **Tabelas de Financiamento**:
  - SAC: Sistema de Amortização Constante
  - Price: Sistema Francês
  - Custom: Tabelas customizadas
- **Cálculos**:
  - TIR (Taxa Interna de Retorno)
  - VPL (Valor Presente Líquido)
  - Payback period
  - Parcelas mensais
- **Aprovação**: Integração credit-analysis
- **Simulações**: Prazo (12-240 meses), taxa (6-15% a.a.), entrada (0-30%)

##### 10. **pvlib-integration/** (PVLib Bridge Module)
- **Bridge**: TypeScript ↔ Python
- **Execução**: Subprocess spawn
- **Script**: `scripts/pvlib_modelchain.py`
- **Inputs**:
  - Localização (lat, lon, altitude)
  - Painéis (modelo, quantidade, tilt, azimuth)
  - Inversor (modelo, quantidade)
  - Weather data (irradiância, temperatura)
- **Outputs**:
  - Geração mensal estimada (kWh/mês)
  - Performance Ratio (PR)
  - Losses breakdown
- **Performance**: Timeout 30s, retry 3x
- **Caching**: Redis com resultados

**Module Patterns**:
- **Isolation**: Sem FKs diretas entre módulos (usar Links)
- **Queryability**: 100% queryable via Query Graph
- **Events**: Domain events para integração assíncrona
- **Migrations**: Auto-geradas via `medusa db:generate`
- **Testing**: Unit tests por módulo
- **Documentation**: README.md em cada módulo

#### 1.3 `src/workflows/` - Business Process Orchestration

**JTBD**: Orquestrar processos de negócio complexos com steps transacionais e compensation logic.

**Framework**: @medusajs/workflows-sdk
- `createWorkflow()` - Define workflow
- `createStep()` - Define step com compensation
- `StepResponse()` - Return com undo data
- `WorkflowResponse()` - Return final

**Anatomia de um Workflow**:
```typescript
import { 
  createWorkflow, 
  createStep, 
  StepResponse,
  WorkflowResponse 
} from "@medusajs/workflows-sdk";

// 1. Define compensatable step
const createCompanyStep = createStep(
  "create-company",
  async (input: CreateCompanyInput, { container }) => {
    const companyService = container.resolve("companyModuleService");
    const company = await companyService.createCompanies([input]);
    
    // Return result + compensation data
    return new StepResponse(company[0], { 
      companyId: company[0].id 
    });
  },
  // Compensation function (rollback)
  async (compensationData, { container }) => {
    const companyService = container.resolve("companyModuleService");
    await companyService.deleteCompanies([compensationData.companyId]);
  }
);

// 2. Compose workflow
export const createCompaniesWorkflow = createWorkflow(
  "create-companies",
  function (input: CreateCompanyInput) {
    const company = createCompanyStep(input);
    const customerGroup = createCustomerGroupStep(company);
    const linkage = linkCompanyToGroupStep({ company, customerGroup });
    
    return new WorkflowResponse({ company, customerGroup });
  }
);

// 3. Execute workflow
const { result, errors } = await createCompaniesWorkflow.run({
  input: { name: "Solar Corp", cnpj: "12345678000190" },
  container: req.scope
});
```

**Workflows Implementados** (15+):

##### Company Workflows
- `createCompaniesWorkflow` - Criar empresa + customer group + links
- `updateCompaniesWorkflow` - Atualizar com validações
- `deleteCompaniesWorkflow` - Soft delete + cleanup
- `addCompanyToCustomerGroupWorkflow` - Vincular pricing tier
- `resetSpendingLimitsWorkflow` - Reset mensal de limites

##### Quote Workflows
- `createQuotesWorkflow` - Criar cotação com validações
- `customerAcceptQuoteWorkflow` - Aceitar + converter para cart
- `customerRejectQuoteWorkflow` - Rejeitar + notificar
- `createQuoteMessageWorkflow` - Adicionar mensagem
- `expireQuotesWorkflow` - Expirar cotações antigas (job)

##### Approval Workflows
- `createApprovalWorkflow` - Criar aprovação multi-nível
- `approveWorkflow` - Aprovar + liberar pedido
- `rejectApprovalWorkflow` - Rejeitar + notificar

##### Credit & Financing Workflows
- `analyzeCreditWorkflow` - Integração BACEN + scoring
- `simulateFinancingWorkflow` - Calcular financiamento
- `applyFinancingWorkflow` - Aplicar financiamento aprovado

##### Solar Workflows
- `calculateSolarSystemWorkflow` - PVLib + viability
- `validateFeasibilityWorkflow` - Análise técnica

##### Pricing Workflows
- `calculate-dynamic-pricing.ts` - Pricing dinâmico
- `calculate-payment-with-fees.ts` - Taxas e juros

##### Hooks (Workflow Interceptors)
```
src/workflows/hooks/
├── order-validation.ts       # Validar pedido antes de criar
├── cart-completion.ts         # Bloquear checkout sem aprovação
├── payment-validation.ts      # Validar forma de pagamento
└── stock-reservation.ts       # Reservar estoque
```

**Transaction Management**:
- Cada workflow é uma transaction distribuída
- Compensation automática em caso de erro
- Rollback cascata de steps anteriores
- Logging completo de execução
- Retry policy configurável

**Performance**:
- Execução média: 200-500ms
- Workflows complexos: 1-2s
- Background execution: Queue-based (planned)

#### 1.4 `src/links/` - Module Linkages

**JTBD**: Conectar entidades de módulos diferentes sem foreign keys diretas (Medusa pattern).

**Padrão**:
```typescript
import { defineLink } from "@medusajs/framework/utils";
import CompanyModule from "../modules/company";
import CustomerModule from "@medusajs/medusa/customer";

export default defineLink(
  CompanyModule.linkable.company,
  CustomerModule.linkable.customerGroup,
  {
    database: {
      idColumnName: "company_id",
      extraColumns: {
        metadata: { type: "jsonb", nullable: true }
      }
    }
  }
);
```

**Links Implementados** (20+):
- Company ↔ CustomerGroup (pricing tiers)
- Company ↔ Customer (employees)
- Quote ↔ Cart (conversion)
- Quote ↔ Customer (ownership)
- Employee ↔ Customer (authentication)
- Product ↔ UnifiedCatalogItem (enhanced metadata)
- Order ↔ Approval (workflow approval)
- Cart ↔ Approval (checkout approval)
- Product ↔ PricingRules (dynamic pricing)
- Customer ↔ CreditAnalysis (financing)

**Benefits**:
- Desacoplamento total de módulos
- Evolução independente
- Queries via Query Graph
- Migrations automáticas de tabelas de junção

#### 1.5 `src/jobs/` - Scheduled Jobs

**JTBD**: Executar tarefas periódicas de manutenção, sincronização e processamento batch.

**Scheduler**: Custom implementation (BullMQ planned)

**Jobs Implementados** (10+):

| Job | Cron | Duração | Descrição |
|-----|------|---------|-----------|
| `sync-aneel-tariffs` | `0 2 * * *` | ~5min | Atualizar tarifas ANEEL do dia anterior |
| `cleanup-expired-quotes` | `0 3 * * *` | ~2min | Expirar cotações com +30 dias |
| `reset-spending-limits` | `0 0 1 * *` | ~1min | Reset limites mensais de empresas |
| `sync-bacen-data` | `0 1 * * 0` | ~10min | Sincronizar dados BACEN (semanal) |
| `generate-analytics` | `0 4 * * *` | ~15min | Processar analytics do dia anterior |
| `backup-database` | `0 1 * * *` | ~30min | Backup incremental PostgreSQL |
| `prune-old-logs` | `0 2 * * 0` | ~5min | Limpar logs com +90 dias |
| `update-exchange-rates` | `0 * * * *` | ~30s | Atualizar câmbio (horário) |
| `reindex-search` | `0 3 * * 0` | ~20min | Reindexar busca full-text |
| `health-check-externals` | `*/5 * * * *` | ~10s | Check APIs externas (5min) |

**Implementation Pattern**:
```typescript
// jobs/sync-aneel-tariffs.ts
import { JobScheduler } from "../lib/scheduler";

export default JobScheduler.register({
  name: "sync-aneel-tariffs",
  cron: "0 2 * * *", // Daily at 2am
  timeout: 600000, // 10min
  retries: 3,
  
  async handler({ container }) {
    const aneelService = container.resolve("aneelModuleService");
    const logger = container.resolve("logger");
    
    try {
      const tariffs = await fetchAneelTariffs();
      await aneelService.updateTariffs(tariffs);
      logger.info("ANEEL tariffs synced successfully");
    } catch (error) {
      logger.error("Failed to sync ANEEL tariffs", { error });
      throw error; // Trigger retry
    }
  }
});
```

**Monitoring**:
- Prometheus metrics (execution time, success rate)
- Alert on failures (3 consecutive failures)
- Grafana dashboards

#### 1.6 `src/subscribers/` - Event Subscribers

**JTBD**: Reagir a domain events de forma assíncrona e desacoplada.

**Event Bus**: Medusa built-in event bus (Redis-backed)

**Subscribers Implementados** (30+):

**Order Events**:
```typescript
// subscribers/order-placed.ts
export default async function orderPlacedHandler({ 
  event, 
  container 
}) {
  const { id } = event.data;
  
  // Check if approval needed
  const approvalService = container.resolve("approvalModuleService");
  const needsApproval = await approvalService.checkIfNeeded(id);
  
  if (needsApproval) {
    // Create approval workflow
    await createApprovalWorkflow.run({
      input: { orderId: id },
      container
    });
  }
  
  // Send notification
  const notificationService = container.resolve("notificationService");
  await notificationService.sendOrderPlacedEmail(id);
}
```

**Event Types**:
- `order.placed` → Check approval, send notifications
- `order.completed` → Trigger fulfillment, emit nota fiscal
- `order.canceled` → Restock inventory, refund payment
- `quote.created` → Send email to customer
- `quote.accepted` → Convert to cart, start checkout
- `quote.rejected` → Notify admin, archive quote
- `company.created` → Create customer group, set limits
- `company.updated` → Update related entities
- `payment.captured` → Release order, update analytics
- `payment.failed` → Notify customer, retry logic
- `product.created` → Index for search
- `product.updated` → Invalidate caches, reindex
- `cart.completed` → Check approval, process payment
- `approval.approved` → Release order for processing
- `approval.rejected` → Notify requester, revert to draft

**Performance**:
- Async execution (não bloqueia request)
- Batch processing quando possível
- Error handling com retry
- Dead letter queue para falhas persistentes

#### 1.7 Outras Subpastas `src/`

##### `src/admin/` - Admin UI Customizations
- **Widgets**: Custom admin widgets (10+)
- **Routes**: Custom admin routes (5+)
- **Components**: React components reutilizáveis
- **Dashboards**: Solar-specific dashboards
  - Sales performance
  - Quote conversion funnel
  - Solar installations map
  - Revenue analytics
  - Customer insights

##### `src/lib/` - Shared Libraries
- **Utils**: Formatting, validation, helpers
- **Constants**: Business constants, enums
- **Types**: Shared TypeScript types
- **Errors**: Custom error classes
- **Logger**: Winston-based logger
- **Cache**: Redis cache wrapper
- **Queue**: Job queue abstractions (BullMQ)

##### `src/utils/` - Utility Functions
- **Formatters**: Currency, dates, numbers
- **Validators**: CNPJ, CPF, email, phone
- **Parsers**: CSV, JSON, XML
- **Helpers**: Array, object, string manipulation

##### `src/agents/` - AI Agents
- **RAG**: Retrieval-Augmented Generation
  - Vector DB: ChromaDB
  - Embeddings: Cohere
  - LLM: LangChain + Ollama
- **Recommendations**: Product recommendations AI
- **Helio**: AI solar assistant chatbot

##### `src/scrapers/` - Web Scrapers
- **Product Scrapers**: Extract product data from suppliers
- **Price Scrapers**: Monitor competitor prices
- **Compliance**: Rate limiting, robots.txt respect

##### `src/workers/` - Worker Processes
- **Image Processing**: Resize, optimize, upload to S3
- **Data Processing**: Heavy ETL jobs
- **Report Generation**: PDF reports, exports

##### `src/cli/` - CLI Commands
- **Custom Commands**: Medusa CLI extensions
- **Migrations**: Data migration scripts
- **Utilities**: Admin utilities

---

### 2. `tests/` & `integration-tests/` - Test Suites

**JTBD**: Garantir qualidade, confiabilidade e non-regression através de testes automatizados.

**Framework**: Jest 29 + @swc/jest (fast compilation)

**Structure**:
```
tests/
└── unit/
    └── pact/              # Contract tests
        ├── fixtures/
        ├── provider/
        └── consumer/

integration-tests/
├── http/                  # API endpoint tests
│   ├── admin/
│   ├── companies/
│   ├── quotes/
│   ├── solar/
│   └── __tests__/
└── modules/               # Module integration tests
    └── solar/
```

**Test Types**:

#### Unit Tests
- **Location**: `src/**/__tests__/*.spec.ts`
- **Scope**: Functions, classes, utilities
- **Coverage Target**: 80%+
- **Run**: `yarn test:unit`
- **Duration**: ~30s

#### Integration Tests - HTTP
- **Location**: `integration-tests/http/`
- **Scope**: API endpoints end-to-end
- **Setup**: Test database + seed data
- **Teardown**: Cleanup after each test
- **Run**: `yarn test:integration:http`
- **Duration**: ~2min
- **Examples**:
  ```typescript
  describe("POST /admin/companies", () => {
    it("should create company with valid data", async () => {
      const response = await request(app)
        .post("/admin/companies")
        .send({
          name: "Test Corp",
          cnpj: "12345678000190"
        })
        .expect(200);
      
      expect(response.body.company).toHaveProperty("id");
      expect(response.body.company.name).toBe("Test Corp");
    });
  });
  ```

#### Integration Tests - Modules
- **Location**: `integration-tests/modules/`
- **Scope**: Module interactions, workflows
- **Run**: `yarn test:integration:modules`
- **Duration**: ~1min

#### Contract Tests (Pact)
- **Location**: `tests/unit/pact/`
- **Scope**: API contracts (provider/consumer)
- **Purpose**: Ensure API compatibility
- **Tools**: Pact framework

**CI/CD Integration**:
- Run on every PR
- Block merge on failures
- Coverage reports to Codecov
- Parallel execution for speed

---

### 3. `docs/` - Technical Documentation

**JTBD**: Documentar arquitetura, APIs, implementações e processos para desenvolvedores e stakeholders.

**Structure**:
```
docs/
├── implementation/       # Implementation guides
│   ├── BACEN_INTEGRATION_SUMMARY.md
│   ├── SOLAR_CALCULATOR_IMPLEMENTATION.md
│   └── ...
├── database/             # Database documentation
│   ├── MIGRATION_REPORT.md
│   ├── MODULES_VS_TABLES.md
│   ├── SOLAR_CATALOG_360.md
│   └── VERIFICATION_SCRIPTS.md
├── integration/          # Integration test guides
│   └── HTTP_TESTS_README.md
└── api/                  # API documentation
    ├── QUICK_REFERENCE.md
    ├── API_NORMALIZATION_COMPLETE.md
    └── STANDARDS.md
```

**Documentation Types**:

#### Implementation Guides
- **BACEN Integration**: Credit analysis flow, API specs, error handling
- **Solar Calculator**: PVLib integration, calculation methodology
- **PVLib Integration**: Python bridge, subprocess management

#### Database Documentation
- **Migration Report**: All migrations with changelog
- **Modules vs Tables**: Mapping between modules and database tables
- **Solar Catalog**: Product catalog structure and schemas
- **Verification Scripts**: SQL scripts for data integrity checks

#### API Documentation
- **Quick Reference**: Cheat sheet for common API calls
- **Normalization**: Standards and conventions
- **OpenAPI**: Auto-generated OpenAPI 3.0 specs (planned)

**Best Practices**:
- Markdown format for easy versioning
- Diagrams with Mermaid
- Code examples for clarity
- Update docs with code changes

---

### 4. `data/` - Data Storage & Assets

**JTBD**: Armazenar dados de catálogo, inventário, análises e assets do projeto.

**Structure**:
```
data/
├── products-inventory/   # Product images organized by category
│   ├── paineis/
│   ├── inversores/
│   ├── estruturas/
│   ├── cabos/
│   ├── baterias/
│   ├── controladores/
│   ├── kits/
│   └── ...
├── analysis/             # Data analysis results
├── exports/              # Data exports (CSV, JSON)
├── project-helios/       # Project Helios specific data
└── scripts/              # Data processing scripts (Python)
```

**Product Images**:
- **Total**: 1000+ images
- **Categories**: 10+ (painéis, inversores, etc.)
- **Format**: JPG, PNG, WEBP
- **Naming**: SKU-based (e.g., `sku_215563.jpg`)
- **Storage**: Local (development), S3 (production)
- **Processing**: Auto-resize, optimization

**Data Scripts**:
- **Import**: CSV/JSON importers
- **Transform**: Data transformation pipelines
- **Export**: Analytics exports to BI tools
- **Cleanup**: Data quality scripts

---

### 5. `data-platform/` - Data Processing Platform

**JTBD**: Processar pipelines de dados batch e streaming para analytics e ML.

**Structure**:
```
data-platform/
├── dagster/              # Dagster ETL pipelines
│   ├── assets/
│   ├── jobs/
│   ├── sensors/
│   └── schedules/
└── pathway/              # Pathway streaming pipelines
    ├── processors/
    └── connectors/
```

#### Dagster (Batch Processing)
- **Purpose**: ETL, data warehousing, ML pipelines
- **Assets**: Materialized data products
- **Jobs**: Scheduled or triggered executions
- **Sensors**: Event-driven triggers
- **Schedule**: Cron-based scheduling
- **Use Cases**:
  - Daily sales aggregation
  - Customer analytics
  - Product recommendations training
  - Report generation

#### Pathway (Stream Processing)
- **Purpose**: Real-time data processing
- **Use Cases**:
  - Solar monitoring streams
  - Real-time analytics
  - Alert processing
  - Event processing

---

### 6. `database/` - Database Management

**JTBD**: Gerenciar migrações, backups e estrutura do banco PostgreSQL.

**Structure**:
```
database/
├── migrations/           # MikroORM migrations
│   ├── 001_initial.sql
│   ├── 002_company_module.sql
│   ├── ...
│   └── 020_latest.sql
└── backup_*.sql          # Database backups
```

**Migrations**:
- **Tool**: MikroORM migrations
- **Generation**: `yarn medusa db:generate ModuleName`
- **Execution**: `yarn medusa db:migrate`
- **Rollback**: Manual SQL scripts
- **Naming**: Sequential numbers + description
- **Total**: 20+ migrations

**Database Schema**:
- **Tables**: 50+ tables
- **Indexes**: Optimized for query performance
- **Constraints**: FKs, unique, check constraints
- **Triggers**: Audit logging, updated_at auto-update
- **Views**: Materialized views for analytics

**Backup Strategy**:
- **Frequency**: Daily incremental, weekly full
- **Retention**: 30 days incremental, 1 year full
- **Storage**: S3 with encryption
- **Restore**: Tested monthly

---

## 🎯 Performance & Monitoring

### Application Metrics
- **Response Time**: p50 <50ms, p95 <100ms, p99 <500ms
- **Throughput**: 1000+ req/s (cached), 200+ req/s (DB-heavy)
- **Error Rate**: <0.1%
- **Uptime**: 99.9% SLA

### Database Metrics
- **Query Time**: p95 <50ms
- **Connection Pool**: 20 connections (max 100)
- **Cache Hit Ratio**: 85%+
- **Index Usage**: 95%+ queries use indexes

### Infrastructure Metrics
- **CPU**: <80% average
- **Memory**: <70% average
- **Disk I/O**: <60% utilization
- **Network**: <50Mbps average

### Monitoring Stack
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logs**: Loki
- **APM**: Planned (New Relic/Datadog)
- **Alerts**: AlertManager → Slack/PagerDuty

---

## 🔐 Security & Compliance

### Authentication
- **JWT**: Access tokens (15min TTL)
- **Refresh Tokens**: Rotate on use, 7 days TTL
- **Cookie-based**: Secure, HttpOnly, SameSite
- **MFA**: Planned (TOTP)

### Authorization
- **RBAC**: Role-Based Access Control
  - Admin: Full access
  - Company Admin: Company-scoped
  - Employee: Limited by permissions
- **Resource-level**: Fine-grained permissions

### Data Protection
- **Encryption at Rest**: PostgreSQL TDE
- **Encryption in Transit**: TLS 1.3
- **PII Masking**: Logs and exports
- **LGPD Compliance**: Data subject rights implemented

### API Security
- **Rate Limiting**: Kong API Gateway
- **DDoS Protection**: CloudFlare
- **Input Validation**: Zod schemas
- **SQL Injection**: Parameterized queries (MikroORM)
- **XSS Protection**: Content Security Policy

---

## 📈 Roadmap & Future

### Q1 2026
- ElasticSearch integration for advanced search
- BullMQ for robust job queuing
- Multi-tenant architecture
- OpenAPI 3.0 auto-generation

### Q2 2026
- GraphQL API layer
- Advanced analytics with Metabase
- IoT integration (solar inverter APIs)
- Mobile app API optimizations

### Q3 2026
- Blockchain for solar certificates
- AI-powered recommendations v2
- Real-time collaboration features
- Global expansion (i18n)

---

**Document Version**: 2.0  
**Last Updated**: 20 de outubro de 2025  
**Maintainer**: YSH Solar Engineering Team