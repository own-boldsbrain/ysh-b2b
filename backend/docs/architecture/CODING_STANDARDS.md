# Coding Standards - YSH Solar B2B Platform

**Versão**: 1.0  
**Data**: 2025-10-20  
**Escopo**: Backend (Medusa 2.4 + DDD + CQRS + Event-Driven)

---

## Table of Contents

1. [Princípios Gerais](#princípios-gerais)
2. [Estrutura de Diretórios](#estrutura-de-diretórios)
3. [Naming Conventions](#naming-conventions)
4. [Import/Export Patterns](#importexport-patterns)
5. [TypeScript Guidelines](#typescript-guidelines)
6. [DDD Patterns](#ddd-patterns)
7. [CQRS Patterns](#cqrs-patterns)
8. [Event-Driven Patterns](#event-driven-patterns)
9. [Error Handling](#error-handling)
10. [Testing Standards](#testing-standards)
11. [Documentation](#documentation)
12. [Git Commit Conventions](#git-commit-conventions)
13. [Code Review Guidelines](#code-review-guidelines)
14. [ESLint Rules](#eslint-rules)

---

## Princípios Gerais

### SOLID Principles

**S - Single Responsibility**: Cada classe/função tem uma única responsabilidade
```typescript
// ❌ Ruim: Classe faz validação + persistência + email
class QuoteService {
  validateQuote() { /* ... */ }
  saveQuote() { /* ... */ }
  sendEmail() { /* ... */ }
}

// ✅ Bom: Responsabilidades separadas
class QuoteValidator { validate() { /* ... */ } }
class QuoteRepository { save() { /* ... */ } }
class EmailService { send() { /* ... */ } }
```

**O - Open/Closed**: Aberto para extensão, fechado para modificação
```typescript
// ✅ Bom: Nova estratégia sem modificar existente
interface PricingStrategy {
  calculate(product: Product): Money;
}

class RetailPricingStrategy implements PricingStrategy { /* ... */ }
class WholesalePricingStrategy implements PricingStrategy { /* ... */ }
```

**L - Liskov Substitution**: Subtipos substituíveis por tipos base
**I - Interface Segregation**: Interfaces específicas, não genéricas
**D - Dependency Inversion**: Dependa de abstrações, não implementações

### DRY (Don't Repeat Yourself)

- Se copiar código 2x, extrair para função
- Se copiar código 3x, extrair para utilitário compartilhado (`src/shared/`)

### KISS (Keep It Simple, Stupid)

- Preferir simplicidade a cleverness
- Se precisar de comentário, considere renomear/refatorar

### YAGNI (You Aren't Gonna Need It)

- Não implementar funcionalidades "que podem ser úteis no futuro"
- Implementar apenas o necessário para o requisito atual

---

## Estrutura de Diretórios

### Convenção Raiz

```
backend/
├── src/
│   ├── domains/              # 12 domínios DDD
│   │   ├── catalog/
│   │   ├── pricing/
│   │   ├── quotes/
│   │   ├── approvals/
│   │   ├── company/
│   │   ├── orders/
│   │   ├── financing/
│   │   ├── energy-aneel/
│   │   ├── solar-simulations/
│   │   ├── integrations/
│   │   ├── platform/
│   │   └── observability/
│   ├── shared/               # Utilitários compartilhados
│   │   ├── errors/
│   │   ├── validation/
│   │   ├── events/
│   │   ├── cache/
│   │   ├── utils/
│   │   ├── types/
│   │   └── auth/
│   ├── api/                  # Rotas HTTP (Medusa)
│   └── migrations/           # Database migrations
├── docs/                     # Documentação
├── tests/                    # Testes E2E
└── scripts/                  # Scripts utilitários
```

### Estrutura de Domínio (4 Camadas)

```
domains/<domain-name>/
├── domain/                   # Camada de domínio (lógica de negócio)
│   ├── entities/             # Entidades do domínio
│   ├── value-objects/        # Value Objects (imutáveis)
│   ├── repositories/         # Interfaces de repositórios
│   ├── services/             # Domain Services (lógica complexa)
│   └── events/               # Domain Events específicos
├── application/              # Camada de aplicação (casos de uso)
│   ├── commands/             # Commands (CQRS)
│   │   └── handlers/         # Command Handlers
│   ├── queries/              # Queries (CQRS)
│   │   └── handlers/         # Query Handlers
│   └── services/             # Application Services (orquestração)
├── infrastructure/           # Camada de infraestrutura (detalhes técnicos)
│   ├── repositories/         # Implementações de repositórios
│   ├── subscribers/          # Event Subscribers
│   ├── cache/                # Cache strategies
│   └── external/             # Integrações externas
└── interfaces/               # Camada de interface (adaptadores)
    ├── controllers/          # HTTP Controllers
    ├── dto/                  # Data Transfer Objects
    └── mappers/              # Mappers (entity <-> DTO)
```

---

## Naming Conventions

### Arquivos

**Padrão**: `kebab-case.ts` (tudo minúsculo, hífens)

```
✅ Bom:
- list-skus-query.ts
- create-quote-handler.ts
- quote-repository.ts

❌ Ruim:
- ListSKUsQuery.ts (PascalCase)
- createQuoteHandler.ts (camelCase)
- QuoteRepository.ts (PascalCase)
```

### Classes

**Padrão**: `PascalCase` + sufixo descritivo

```typescript
// Entities
class Quote { /* ... */ }
class Product { /* ... */ }

// Value Objects
class Money { /* ... */ }
class Address { /* ... */ }

// Services
class QuoteService { /* ... */ }
class PricingCalculator { /* ... */ }

// Repositories
class QuoteRepository { /* ... */ }
class ProductRepository { /* ... */ }

// Commands/Queries
class CreateQuoteCommand { /* ... */ }
class ListSKUsQuery { /* ... */ }

// Handlers
class CreateQuoteHandler { /* ... */ }
class ListSKUsHandler { /* ... */ }

// Controllers
class QuoteController { /* ... */ }
class CatalogController { /* ... */ }

// Subscribers
class QuoteCreatedSubscriber { /* ... */ }
class ApprovalApprovedSubscriber { /* ... */ }

// DTOs
class CreateQuoteDTO { /* ... */ }
class QuoteResponseDTO { /* ... */ }

// Mappers
class QuoteMapper { /* ... */ }
```

### Interfaces

**Padrão**: `I + PascalCase` para interfaces de serviço, sem prefixo para DTOs

```typescript
// Interfaces de serviço/repositório
interface IQuoteRepository { /* ... */ }
interface IEventBusService { /* ... */ }

// DTOs (sem I)
interface CreateQuoteDTO { /* ... */ }
interface QuoteResponseDTO { /* ... */ }

// Contratos de eventos
interface QuoteCreatedPayload { /* ... */ }
```

### Variáveis e Funções

**Padrão**: `camelCase`

```typescript
// Variáveis
const quoteId = '123';
const totalValue = 50000;
const customerEmail = 'user@example.com';

// Funções
function calculateTotalPrice(items: Item[]): Money { /* ... */ }
async function createQuote(data: CreateQuoteDTO): Promise<Quote> { /* ... */ }

// Booleans: usar is/has/should
const isActive = true;
const hasPermission = false;
const shouldRetry = true;
```

### Constantes

**Padrão**: `UPPER_SNAKE_CASE` para globais, `camelCase` para locais

```typescript
// Constantes globais (exportadas)
export const MAX_RETRY_ATTEMPTS = 5;
export const DEFAULT_CACHE_TTL = 3600;
export const API_VERSION = '2.4';

// Constantes locais (não exportadas)
const defaultPagination = { page: 1, limit: 20 };
const retryDelays = [1000, 5000, 15000];
```

### Enums

**Padrão**: `PascalCase` para nome, `UPPER_SNAKE_CASE` para valores

```typescript
// ❌ Evitar: enum tradicional
enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed'
}

// ✅ Preferir: const object (type safety)
export const OrderStatus = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  SHIPPED: 'shipped',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled'
} as const;

export type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus];
```

---

## Import/Export Patterns

### Order de Imports

**Padrão**: Externos → Medusa → Shared → Domínios → Relativos

```typescript
// 1. Node.js built-ins
import { promises as fs } from 'fs';
import path from 'path';

// 2. External packages
import { z } from 'zod';
import Redis from 'ioredis';

// 3. Medusa
import { MedusaRequest, MedusaResponse } from '@medusajs/medusa';
import { IEventBusService } from '@medusajs/types';

// 4. Shared utilities
import { AppError, ValidationError } from '@shared/errors';
import { validateSchema } from '@shared/validation';
import { EventTypes } from '@shared/events';

// 5. Domínios (outros)
import { PricingService } from '@domains/pricing/application/services';

// 6. Domínio atual (relativos)
import { Quote } from '../entities/quote';
import { IQuoteRepository } from '../repositories/quote-repository';
```

### Exports

**Padrão**: Exports explícitos no final do arquivo ou via `index.ts`

```typescript
// ❌ Evitar: export inline
export class QuoteService { /* ... */ }
export interface IQuoteService { /* ... */ }

// ✅ Preferir: exports no final
class QuoteService { /* ... */ }
interface IQuoteService { /* ... */ }

export { QuoteService, IQuoteService };

// ✅ Ou via index.ts (barrel export)
// domains/quotes/domain/index.ts
export * from './entities/quote';
export * from './value-objects/quote-status';
export * from './repositories/quote-repository';
```

### Path Aliases

**Configuração**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "paths": {
      "@shared/*": ["./src/shared/*"],
      "@domains/*": ["./src/domains/*"],
      "@api/*": ["./src/api/*"]
    }
  }
}
```

**Uso**:
```typescript
// ✅ Bom: Path alias (limpo)
import { AppError } from '@shared/errors';
import { QuoteService } from '@domains/quotes/application/services';

// ❌ Ruim: Paths relativos longos
import { AppError } from '../../../../../shared/errors';
```

---

## TypeScript Guidelines

### Strict Mode

**Obrigatório**: `tsconfig.json` com strict mode

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true
  }
}
```

### Type Annotations

**Regra**: Sempre tipar parâmetros e retornos de funções

```typescript
// ❌ Ruim: Sem tipos
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ✅ Bom: Tipado
function calculateTotal(items: Item[]): Money {
  return items.reduce((sum, item) => sum + item.price, Money.zero());
}
```

### Type vs Interface

**Regra**: `interface` para objetos, `type` para unions/intersections

```typescript
// ✅ Interface para objetos
interface CreateQuoteDTO {
  customerId: string;
  items: QuoteItem[];
  metadata?: Record<string, unknown>;
}

// ✅ Type para unions/intersections
type EntityStatus = 'active' | 'inactive' | 'archived';
type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;
```

### Generics

**Regra**: Usar nomes descritivos para generics complexos

```typescript
// ❌ Ruim: Genérico vago
function process<T>(data: T): T { /* ... */ }

// ✅ Bom: Genérico descritivo
function mapEntity<TEntity, TDTO>(
  entity: TEntity,
  mapper: (e: TEntity) => TDTO
): TDTO {
  return mapper(entity);
}
```

### Avoid `any`

**Regra**: Usar `unknown` quando tipo for realmente desconhecido

```typescript
// ❌ Ruim: any desabilita type checking
function processData(data: any) { /* ... */ }

// ✅ Bom: unknown força validação
function processData(data: unknown) {
  if (typeof data === 'object' && data !== null) {
    // Type guard antes de usar
  }
}

// ✅ Melhor: Type específico
function processData(data: CreateQuoteDTO) { /* ... */ }
```

---

## DDD Patterns

### Entities

**Regra**: Identidade única, métodos de negócio, imutabilidade quando possível

```typescript
// ✅ Bom: Entity com lógica de negócio
class Quote {
  private constructor(
    public readonly id: string,
    public readonly customerId: string,
    private status: QuoteStatus,
    private items: QuoteItem[],
    public readonly createdAt: Date,
    private updatedAt: Date
  ) {}

  // Factory method
  static create(data: CreateQuoteData): Quote {
    // Validações de negócio
    if (data.items.length === 0) {
      throw new DomainError('Quote must have at least one item');
    }
    
    return new Quote(
      generateId(),
      data.customerId,
      QuoteStatus.DRAFT,
      data.items,
      new Date(),
      new Date()
    );
  }

  // Métodos de negócio (não getters/setters)
  submit(): void {
    if (this.status !== QuoteStatus.DRAFT) {
      throw new DomainError('Only draft quotes can be submitted');
    }
    this.status = QuoteStatus.SUBMITTED;
    this.updatedAt = new Date();
  }

  approve(): void {
    if (this.status !== QuoteStatus.SUBMITTED) {
      throw new DomainError('Only submitted quotes can be approved');
    }
    this.status = QuoteStatus.APPROVED;
    this.updatedAt = new Date();
  }

  calculateTotal(): Money {
    return this.items.reduce(
      (sum, item) => sum.add(item.total),
      Money.zero()
    );
  }

  // Getters (sem setters públicos)
  getStatus(): QuoteStatus {
    return this.status;
  }

  getItems(): readonly QuoteItem[] {
    return Object.freeze([...this.items]);
  }
}
```

### Value Objects

**Regra**: Sem identidade, imutáveis, validação no construtor

```typescript
// ✅ Bom: Value Object imutável
class Money {
  private constructor(
    public readonly amount: number,
    public readonly currency: string
  ) {
    if (amount < 0) {
      throw new ValidationError('Amount cannot be negative');
    }
    if (!['BRL', 'USD'].includes(currency)) {
      throw new ValidationError('Invalid currency');
    }
  }

  static of(amount: number, currency: string = 'BRL'): Money {
    return new Money(amount, currency);
  }

  static zero(currency: string = 'BRL'): Money {
    return new Money(0, currency);
  }

  add(other: Money): Money {
    this.ensureSameCurrency(other);
    return new Money(this.amount + other.amount, this.currency);
  }

  multiply(factor: number): Money {
    return new Money(this.amount * factor, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }

  private ensureSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new DomainError('Cannot operate on different currencies');
    }
  }
}
```

### Domain Services

**Regra**: Lógica que não pertence a uma única entidade

```typescript
// ✅ Bom: Domain Service com lógica complexa
class PricingCalculator {
  constructor(
    private readonly tariffRepository: ITariffRepository,
    private readonly discountRepository: IDiscountRepository
  ) {}

  async calculatePrice(
    product: Product,
    quantity: number,
    context: PricingContext
  ): Promise<Money> {
    // Lógica complexa envolvendo múltiplas entidades
    const basePric = product.getBasePrice();
    const tariff = await this.tariffRepository.findByRegion(context.region);
    const discount = await this.discountRepository.findApplicable(
      product,
      quantity,
      context
    );

    let finalPrice = basePrice.multiply(quantity);
    finalPrice = this.applyTariff(finalPrice, tariff);
    finalPrice = this.applyDiscount(finalPrice, discount);

    return finalPrice;
  }

  private applyTariff(price: Money, tariff: Tariff): Money {
    // Lógica de aplicação de tarifa
    return price.multiply(1 + tariff.rate);
  }

  private applyDiscount(price: Money, discount: Discount | null): Money {
    if (!discount) return price;
    return price.multiply(1 - discount.percentage);
  }
}
```

### Repositories (Interfaces)

**Regra**: Definir contrato no domínio, implementar na infraestrutura

```typescript
// domains/quotes/domain/repositories/quote-repository.ts
export interface IQuoteRepository {
  findById(id: string): Promise<Quote | null>;
  findByCustomerId(customerId: string): Promise<Quote[]>;
  save(quote: Quote): Promise<void>;
  delete(id: string): Promise<void>;
}

// domains/quotes/infrastructure/repositories/quote-repository.ts
class QuoteRepository implements IQuoteRepository {
  constructor(private readonly db: any) {}

  async findById(id: string): Promise<Quote | null> {
    const row = await this.db.quote.findUnique({ where: { id } });
    return row ? QuoteMapper.toDomain(row) : null;
  }

  async save(quote: Quote): Promise<void> {
    const data = QuoteMapper.toPersistence(quote);
    await this.db.quote.upsert({ where: { id: quote.id }, data });
  }

  // ... outras implementações
}
```

---

## CQRS Patterns

### Commands

**Regra**: Representam intenções de mudar estado

```typescript
// domains/quotes/application/commands/create-quote-command.ts
export class CreateQuoteCommand {
  constructor(
    public readonly customerId: string,
    public readonly items: CreateQuoteItemDTO[],
    public readonly metadata?: Record<string, unknown>
  ) {}
}

// domains/quotes/application/commands/handlers/create-quote-handler.ts
export class CreateQuoteHandler {
  constructor(
    private readonly repository: IQuoteRepository,
    private readonly eventBus: IEventBusService,
    private readonly pricingService: PricingService
  ) {}

  async execute(command: CreateQuoteCommand): Promise<Quote> {
    // 1. Validação
    await this.validateCommand(command);

    // 2. Criar entidade
    const quote = Quote.create({
      customerId: command.customerId,
      items: command.items
    });

    // 3. Calcular preços (domain service)
    const itemsWithPrices = await Promise.all(
      command.items.map(item => this.pricingService.calculateItemPrice(item))
    );
    quote.setItems(itemsWithPrices);

    // 4. Persistir
    await this.repository.save(quote);

    // 5. Emitir evento
    await this.eventBus.emit(EventTypes.QUOTE_CREATED, {
      quoteId: quote.id,
      customerId: quote.customerId,
      totalValue: quote.calculateTotal().amount
    });

    return quote;
  }

  private async validateCommand(command: CreateQuoteCommand): Promise<void> {
    if (!command.customerId) {
      throw new ValidationError('Customer ID is required');
    }
    if (command.items.length === 0) {
      throw new ValidationError('At least one item is required');
    }
  }
}
```

### Queries

**Regra**: Apenas leitura, usar cache quando possível

```typescript
// domains/catalog/application/queries/list-skus-query.ts
export class ListSKUsQuery {
  constructor(
    public readonly filters?: {
      categoryId?: string;
      search?: string;
      inStock?: boolean;
    },
    public readonly pagination?: PaginationParams,
    public readonly sort?: SortParams
  ) {}
}

// domains/catalog/application/queries/handlers/list-skus-handler.ts
export class ListSKUsHandler {
  constructor(
    private readonly repository: IProductRepository,
    private readonly cache: CacheService
  ) {}

  async execute(query: ListSKUsQuery): Promise<PaginatedResponse<ProductSKU>> {
    // 1. Gerar cache key
    const cacheKey = this.cache.generateKey('catalog', 'product:list', query);

    // 2. Tentar cache primeiro
    const cached = await this.cache.get<PaginatedResponse<ProductSKU>>(cacheKey);
    if (cached) {
      return cached;
    }

    // 3. Query no DB (read-only)
    const result = await this.repository.listSKUs(
      query.filters,
      query.pagination,
      query.sort
    );

    // 4. Cachear resultado (TTL: 1 hora)
    await this.cache.set(cacheKey, result, CacheTTL.CATALOG);

    return result;
  }
}
```

---

## Event-Driven Patterns

### Event Publishing

**Regra**: Emitir após persistência bem-sucedida

```typescript
// ✅ Bom: Evento após salvar
async execute(command: CreateQuoteCommand): Promise<Quote> {
  const quote = Quote.create(command);
  
  // 1. Persistir PRIMEIRO
  await this.repository.save(quote);
  
  // 2. Emitir evento DEPOIS
  await this.eventBus.emit(EventTypes.QUOTE_CREATED, {
    quoteId: quote.id,
    customerId: quote.customerId,
    totalValue: quote.calculateTotal().amount,
    metadata: {
      userId: this.context.userId,
      correlationId: this.context.correlationId
    }
  });
  
  return quote;
}

// ❌ Ruim: Evento antes de salvar (pode falhar)
await this.eventBus.emit(EventTypes.QUOTE_CREATED, { /* ... */ });
await this.repository.save(quote); // Se falhar, evento já foi emitido!
```

### Event Subscribers

**Regra**: Idempotentes, com retry e error handling

```typescript
// domains/approvals/infrastructure/subscribers/quote-created-subscriber.ts
import { Subscriber } from '@medusajs/medusa';
import { EventTypes } from '@shared/events';
import type { DomainEvent, QuoteCreatedPayload } from '@shared/events';

@Subscriber(EventTypes.QUOTE_CREATED)
export class QuoteCreatedSubscriber {
  constructor(
    private readonly approvalService: ApprovalService,
    private readonly cache: CacheService
  ) {}

  async handle(event: DomainEvent<QuoteCreatedPayload>): Promise<void> {
    // 1. Check idempotência (já processou este evento?)
    const processedKey = `event:processed:${event.eventId}`;
    const alreadyProcessed = await this.cache.exists(processedKey);
    
    if (alreadyProcessed) {
      console.log(`Event ${event.eventId} already processed, skipping`);
      return;
    }

    try {
      // 2. Processar evento
      if (event.data.totalValue > 50000) {
        await this.approvalService.createApproval({
          quoteId: event.data.quoteId,
          type: 'HIGH_VALUE_QUOTE',
          reason: `Quote value (${event.data.totalValue}) exceeds R$ 50k threshold`,
          metadata: {
            correlationId: event.metadata?.correlationId
          }
        });
      }

      // 3. Marcar como processado (TTL: 7 dias)
      await this.cache.set(processedKey, 'true', 7 * 24 * 60 * 60);

    } catch (error) {
      console.error(`Error processing event ${event.eventId}:`, error);
      throw error; // Retry automático via Medusa
    }
  }
}
```

---

## Error Handling

### Error Types

**Regra**: Usar hierarquia de erros do `@shared/errors`

```typescript
import {
  AppError,
  DomainError,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError
} from '@shared/errors';

// ✅ Bom: Erro específico
class QuoteService {
  async getQuote(id: string): Promise<Quote> {
    const quote = await this.repository.findById(id);
    
    if (!quote) {
      throw new NotFoundError('Quote', id);
    }
    
    return quote;
  }

  async submitQuote(id: string): Promise<void> {
    const quote = await this.getQuote(id);
    
    if (quote.getStatus() !== QuoteStatus.DRAFT) {
      throw new DomainError(
        'Only draft quotes can be submitted',
        { quoteId: id, currentStatus: quote.getStatus() }
      );
    }
    
    quote.submit();
    await this.repository.save(quote);
  }
}
```

### Error Handling em Controllers

**Regra**: Deixar errors bubbling, middleware global captura

```typescript
// ✅ Bom: Deixar erro subir
class QuoteController {
  async createQuote(req: MedusaRequest, res: MedusaResponse): Promise<void> {
    const command = new CreateQuoteCommand(
      req.body.customerId,
      req.body.items
    );
    
    // Se handler lançar erro, middleware global captura
    const quote = await this.handler.execute(command);
    
    res.status(201).json({
      quote: QuoteMapper.toDTO(quote)
    });
  }
}

// ❌ Ruim: Try-catch desnecessário
class QuoteController {
  async createQuote(req: MedusaRequest, res: MedusaResponse): Promise<void> {
    try {
      const quote = await this.handler.execute(command);
      res.status(201).json({ quote });
    } catch (error) {
      // Middleware já faz isso!
      res.status(500).json({ error: error.message });
    }
  }
}
```

---

## Testing Standards

### Estrutura de Testes

```
tests/
├── unit/                     # Testes unitários (isolados)
│   ├── domains/
│   │   ├── quotes/
│   │   │   ├── entities/
│   │   │   ├── value-objects/
│   │   │   └── services/
│   └── shared/
├── integration/              # Testes de integração (DB, Redis)
│   ├── domains/
│   │   ├── quotes/
│   │   │   ├── commands/
│   │   │   └── queries/
└── e2e/                      # Testes end-to-end (HTTP)
    ├── api/
    │   ├── store/
    │   └── admin/
```

### Unit Tests

**Regra**: Testar lógica de negócio, mockar dependências

```typescript
// tests/unit/domains/quotes/entities/quote.spec.ts
import { Quote, QuoteStatus } from '@domains/quotes/domain/entities/quote';
import { DomainError } from '@shared/errors';

describe('Quote Entity', () => {
  describe('create', () => {
    it('should create quote in DRAFT status', () => {
      const quote = Quote.create({
        customerId: 'cust-123',
        items: [{ productId: 'prod-1', quantity: 2 }]
      });

      expect(quote.getStatus()).toBe(QuoteStatus.DRAFT);
      expect(quote.customerId).toBe('cust-123');
    });

    it('should throw error if no items provided', () => {
      expect(() => {
        Quote.create({
          customerId: 'cust-123',
          items: []
        });
      }).toThrow(DomainError);
    });
  });

  describe('submit', () => {
    it('should change status from DRAFT to SUBMITTED', () => {
      const quote = Quote.create({
        customerId: 'cust-123',
        items: [{ productId: 'prod-1', quantity: 2 }]
      });

      quote.submit();

      expect(quote.getStatus()).toBe(QuoteStatus.SUBMITTED);
    });

    it('should throw error if not in DRAFT status', () => {
      const quote = Quote.create({
        customerId: 'cust-123',
        items: [{ productId: 'prod-1', quantity: 2 }]
      });
      quote.submit(); // DRAFT -> SUBMITTED

      expect(() => {
        quote.submit(); // Tentar submeter novamente
      }).toThrow(DomainError);
    });
  });
});
```

### Integration Tests

**Regra**: Testar interação com DB/Redis/Services reais

```typescript
// tests/integration/domains/quotes/commands/create-quote-handler.spec.ts
import { CreateQuoteHandler } from '@domains/quotes/application/commands/handlers';
import { QuoteRepository } from '@domains/quotes/infrastructure/repositories';
import { setupTestDatabase, cleanupTestDatabase } from '../../../helpers';

describe('CreateQuoteHandler Integration', () => {
  let handler: CreateQuoteHandler;
  let repository: QuoteRepository;
  let db: any;

  beforeAll(async () => {
    db = await setupTestDatabase();
    repository = new QuoteRepository(db);
    handler = new CreateQuoteHandler(repository, eventBus, pricingService);
  });

  afterAll(async () => {
    await cleanupTestDatabase(db);
  });

  it('should create quote and persist to database', async () => {
    const command = new CreateQuoteCommand(
      'cust-123',
      [{ productId: 'prod-1', quantity: 2 }]
    );

    const quote = await handler.execute(command);

    // Verificar persistência
    const saved = await repository.findById(quote.id);
    expect(saved).toBeDefined();
    expect(saved?.customerId).toBe('cust-123');
  });
});
```

### E2E Tests

**Regra**: Testar fluxos completos via HTTP

```typescript
// tests/e2e/api/store/quotes/create-quote.spec.ts
import request from 'supertest';
import { app } from '../../../helpers/app';

describe('POST /store/quotes', () => {
  it('should create quote and return 201', async () => {
    const response = await request(app)
      .post('/store/quotes')
      .send({
        customerId: 'cust-123',
        items: [
          { productId: 'prod-1', quantity: 2 }
        ]
      })
      .expect(201);

    expect(response.body.quote).toMatchObject({
      customerId: 'cust-123',
      status: 'DRAFT'
    });
  });

  it('should return 400 if items are empty', async () => {
    const response = await request(app)
      .post('/store/quotes')
      .send({
        customerId: 'cust-123',
        items: []
      })
      .expect(400);

    expect(response.body.error).toBeDefined();
  });
});
```

### Test Coverage

**Meta**: Mínimo 80% coverage

```bash
# Rodar testes com coverage
npm run test:coverage

# Coverage por tipo
- Unit tests: 90%+ (lógica de negócio crítica)
- Integration tests: 80%+ (casos de uso)
- E2E tests: 70%+ (happy paths + edge cases)
```

---

## Documentation

### README Files

**Obrigatório**: Cada domínio e camada tem README.md

```markdown
# Quotes Domain

## Responsabilidades

- Gerenciar ciclo de vida de cotações (criar, editar, submeter, aprovar, rejeitar)
- Calcular preços de produtos com descontos e tarifas
- Integrar com sistema de aprovações para cotações de alto valor

## Estrutura

- `domain/`: Entidades, Value Objects, Domain Services
- `application/`: Commands, Queries, Handlers
- `infrastructure/`: Repositories, Subscribers, Cache
- `interfaces/`: Controllers, DTOs, Mappers

## Comandos

- `CreateQuoteCommand`: Criar nova cotação
- `UpdateQuoteCommand`: Atualizar cotação existente
- `SubmitQuoteCommand`: Submeter cotação para aprovação

## Queries

- `ListQuotesQuery`: Listar cotações com filtros
- `GetQuoteQuery`: Buscar cotação por ID

## Eventos

- `quote.created`: Cotação criada
- `quote.submitted`: Cotação submetida para aprovação
- `quote.approved`: Cotação aprovada
- `quote.rejected`: Cotação rejeitada

## Dependências

- `pricing`: Calcular preços de produtos
- `approvals`: Criar aprovações para cotações de alto valor
```

### JSDoc Comments

**Regra**: Documentar classes públicas e funções complexas

```typescript
/**
 * Service responsible for calculating product prices based on context.
 * 
 * Pricing calculation considers:
 * - Base product price
 * - Regional tariffs (ANEEL)
 * - Volume discounts
 * - Customer-specific discounts
 * - Seasonal promotions
 * 
 * @example
 * ```typescript
 * const calculator = new PricingCalculator(tariffRepo, discountRepo);
 * const price = await calculator.calculatePrice(product, 100, context);
 * ```
 */
export class PricingCalculator {
  /**
   * Calculates the final price for a product considering all factors.
   * 
   * @param product - The product to price
   * @param quantity - Quantity being purchased
   * @param context - Pricing context (region, customer, date)
   * @returns Final calculated price
   * @throws {NotFoundError} If tariff for region is not found
   * @throws {DomainError} If product is not available for sale
   */
  async calculatePrice(
    product: Product,
    quantity: number,
    context: PricingContext
  ): Promise<Money> {
    // Implementation...
  }
}
```

---

## Git Commit Conventions

### Commit Message Format

**Padrão**: Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

```
feat:     Nova funcionalidade
fix:      Correção de bug
refactor: Refatoração (sem mudança de comportamento)
test:     Adicionar/modificar testes
docs:     Documentação
style:    Formatação (sem mudança de lógica)
perf:     Melhoria de performance
chore:    Tarefas de build, CI, dependências
```

### Examples

```bash
# Nova feature
git commit -m "feat(quotes): add high-value approval workflow"

# Bug fix
git commit -m "fix(pricing): correct tariff calculation for commercial customers"

# Refactoring
git commit -m "refactor(catalog): extract SKU filtering to separate service"

# Breaking change
git commit -m "feat(auth)!: migrate to JWT-based authentication

BREAKING CHANGE: API now requires JWT tokens instead of session cookies.
Migration guide: docs/migration/jwt-auth.md"
```

### Scope

```
catalog       - Catálogo de produtos
pricing       - Precificação
quotes        - Cotações
approvals     - Aprovações
company       - Empresas
orders        - Pedidos
financing     - Financiamento
energy-aneel  - Dados de energia (ANEEL)
solar         - Simulações solares
integrations  - Integrações externas
platform      - Plataforma (infra)
observability - Observabilidade
shared        - Utilitários compartilhados
```

---

## Code Review Guidelines

### Checklist

**Antes de abrir PR**:
- [ ] Código compila sem erros TypeScript
- [ ] Testes unitários passam (`npm run test:unit`)
- [ ] Testes de integração passam (`npm run test:integration`)
- [ ] Coverage mínimo 80% nas novas linhas
- [ ] ESLint sem erros (`npm run lint`)
- [ ] Prettier aplicado (`npm run format`)
- [ ] README atualizado (se aplicável)
- [ ] ADR criado para decisões arquiteturais (se aplicável)

**Durante review**:
- [ ] Código segue padrões do projeto
- [ ] Nomes de variáveis/funções são descritivos
- [ ] Lógica de negócio está no domínio (não em controllers)
- [ ] Erros são tratados apropriadamente
- [ ] Sem código comentado (exceto TODOs justificados)
- [ ] Sem console.log() desnecessários
- [ ] Performance considerada (N+1 queries, cache, etc.)
- [ ] Segurança considerada (SQL injection, XSS, etc.)

### PR Description Template

```markdown
## Descrição

[Descrever o que foi implementado e por quê]

## Tipo de Mudança

- [ ] Nova feature
- [ ] Bug fix
- [ ] Refactoring
- [ ] Breaking change
- [ ] Documentação

## Checklist

- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Coverage >= 80%
- [ ] ESLint sem erros
- [ ] Prettier aplicado

## Screenshots (se aplicável)

[Imagens de telas, logs, etc.]

## Notas Adicionais

[Informações adicionais para reviewers]
```

---

## ESLint Rules

### Configuração Base

```javascript
// eslint.config.js
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'prettier'
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    project: './tsconfig.json'
  },
  rules: {
    // TypeScript
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/strict-boolean-expressions': 'error',
    
    // Domain Boundaries (custom rule)
    'no-restricted-imports': ['error', {
      patterns: [
        {
          group: ['**/domains/*/infrastructure/*'],
          message: 'Do not import infrastructure details across domains'
        },
        {
          group: ['**/domains/*/application/*'],
          message: 'Do not import application layer across domains'
        }
      ]
    }],
    
    // Code Quality
    'complexity': ['error', 10],
    'max-lines-per-function': ['error', { max: 50, skipBlankLines: true }],
    'max-depth': ['error', 3],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'error',
    
    // Best Practices
    'eqeqeq': ['error', 'always'],
    'no-var': 'error',
    'prefer-const': 'error',
    'prefer-arrow-callback': 'error'
  }
};
```

### Custom Rules

```javascript
// eslint-plugin-local/domain-boundaries.js
module.exports = {
  create(context) {
    return {
      ImportDeclaration(node) {
        const importPath = node.source.value;
        const currentFile = context.getFilename();
        
        // Proibir import de infrastructure de outros domínios
        if (
          currentFile.includes('/domains/') &&
          importPath.includes('/domains/') &&
          importPath.includes('/infrastructure/') &&
          !currentFile.includes(importPath.split('/domains/')[1].split('/')[0])
        ) {
          context.report({
            node,
            message: 'Cannot import infrastructure from other domains'
          });
        }
      }
    };
  }
};
```

---

## Conclusão

Este guia é um documento vivo e deve ser atualizado conforme o projeto evolui. Dúvidas ou sugestões devem ser discutidas com a equipe de arquitetura.

**Versões**:
- 1.0 (2025-10-20): Versão inicial

**Referências**:
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [CQRS Pattern (Martin Fowler)](https://martinfowler.com/bliki/CQRS.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
