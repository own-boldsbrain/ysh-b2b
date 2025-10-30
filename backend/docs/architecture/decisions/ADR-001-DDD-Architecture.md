# ADR-001: Adoção de Domain-Driven Design (DDD)

**Status:** Aceito  
**Data:** 20 de Outubro de 2025  
**Decisores:** Time YSH B2B Backend

---

## Contexto

O backend YSH Solar Hub cresceu organicamente com lógica de negócio misturada nas rotas, acoplamento entre módulos, e falta de clareza sobre responsabilidades de cada componente. Com 278+ rotas, 12 módulos customizados e 21 workflows, a complexidade está dificultando:

- Manutenção e evolução do código
- Onboarding de novos desenvolvedores
- Testes unitários e de integração
- Performance e escalabilidade
- Clareza sobre fluxos de negócio

## Decisão

Adotamos **Domain-Driven Design (DDD)** como princípio arquitetural principal, reorganizando o backend em **12 domínios centrais** com separação clara de responsabilidades em 4 camadas:

```
src/domains/<domínio>/
├── domain/           # Entidades, Value Objects, Domain Events
├── application/      # Use Cases, Application Services, DTOs
├── infrastructure/   # Repositories, Adapters, External APIs
└── interfaces/       # Controllers, Validators, Request/Response DTOs
```

### 12 Domínios Identificados

1. **Catalog** - Gestão de produtos e SKUs
2. **Pricing** - Precificação dinâmica e promoções
3. **Quotes** - Cotações B2B (RFQ)
4. **Approvals** - Workflows de aprovação
5. **Company** - Empresas e colaboradores B2B
6. **Orders** - Pedidos e checkout
7. **Financing** - Financiamento e crédito
8. **Energy ANEEL** - Tarifas e dados ANEEL
9. **Solar Simulations** - Cálculos solares (PVLib)
10. **Integrations** - Integrações com distribuidores
11. **Platform** - Infraestrutura transversal
12. **Observability** - Métricas, logs, auditoria

### Shared Layer

Utilitários comuns a todos os domínios:

```
src/shared/
├── errors/       # Classes de erro customizadas
├── auth/         # Autenticação e autorização
├── validation/   # Schemas Zod e validators
├── events/       # Sistema de eventos de domínio
├── cache/        # Redis wrapper
├── utils/        # Helpers comuns
└── types/        # TypeScript types compartilhados
```

### Compatibilidade com Medusa

Mantemos compatibilidade 100% com Medusa 2.4:

- `src/modules/<domínio>` - Wrappers Medusa (DI container)
- `src/api/<admin|store>/<domínio>` - Rotas finas delegando para use cases
- Migração incremental com feature flags

## Consequências

### Positivas

✅ **Clareza de Negócio**
- Linguagem ubíqua entre dev e negócio
- JTBDs explícitos por domínio
- Bounded contexts claros

✅ **Manutenibilidade**
- Código organizado por domínio
- Separação de concerns (camadas)
- Testes mais simples

✅ **Escalabilidade**
- Domínios independentes
- Potencial para microserviços futuros
- Cache e otimização por domínio

✅ **Onboarding**
- Estrutura previsível
- Documentação por domínio
- Exemplos claros

### Negativas

⚠️ **Complexidade Inicial**
- Curva de aprendizado DDD
- Mais arquivos e abstrações
- Setup inicial trabalhoso

⚠️ **Migração Gradual**
- Coexistência de código legado
- Feature flags necessários
- Documentação dupla temporária

⚠️ **Overhead de Boilerplate**
- Mais interfaces e DTOs
- Camadas adicionais
- Mitigado com generators

## Alternativas Consideradas

### 1. Manter Arquitetura Atual
- ❌ Não resolve problemas de manutenção
- ❌ Complexidade continua crescendo
- ✅ Zero custo de migração

### 2. Microserviços Imediatos
- ❌ Overhead operacional alto
- ❌ Complexidade de rede
- ❌ Não temos experiência operacional
- ✅ Escalabilidade máxima

### 3. Clean Architecture (sem DDD)
- ✅ Separação de concerns
- ❌ Menos foco em domínio de negócio
- ❌ Não resolve problema de linguagem ubíqua

## Implementação

### Fase 1 (2 semanas) - Atual
- ✅ Estrutura de domínios criada
- ✅ Shared utilities implementados
- 🔄 ADRs e coding standards
- ⏳ Rota piloto (Catálogo)

### Fase 2 (3 semanas)
- Migrar Catalog + Pricing
- CQRS leve implementado
- Cache Redis configurado

### Fases 3-6 (9 semanas)
- Migrar domínios restantes
- Event-Driven entre domínios
- Observabilidade completa

## Referências

- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Implementing DDD - Vaughn Vernon](https://vaughnvernon.com/)
- [BACKEND_RESTRUCTURE_PLAN.md](../BACKEND_RESTRUCTURE_PLAN.md)
- [REESTRUTURACAO_360.md](../../REESTRUTURACAO_360.md)

## Aprovação

- **Autor:** Time Backend YSH
- **Revisores:** Arquitetos, Tech Leads
- **Data de Aprovação:** 20/10/2025
