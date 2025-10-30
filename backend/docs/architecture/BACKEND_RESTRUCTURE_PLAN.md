# Plano de Reestruturacao Backend End-to-End

**Data:** 20 de outubro de 2025  
**Versao:** 1.1  
**Status:** Em planejamento

---

## Visao Geral

Reestruturacao completa do backend YSH Solar Hub adotando **Domain-Driven Design (DDD)**, **CQRS leve** e **arquitetura orientada a eventos** para ganhar desempenho, clareza arquitetural e governanca operacional 360 graus.

- Performance alvo: listagem de catalogo <150 ms (P95), calculo de preco <50 ms, simulacao solar <1 s (cache hit) / <5 s (miss)
- Claridade de dominio: JTBD, inputs/outputs e outcomes definidos por dominio, contratos versionados
- Escalabilidade: workflows persistentes, cache distribuido, materialized views para consultas pesadas
- Observabilidade: SLIs/SLOs por dominio, auditoria completa, MTTR <30 min

---

## Principios Arquitetonicos

- **Dominios primeiro**: cada dominio com camadas `domain`, `application`, `infrastructure`, `interfaces`
- **Rotas finas**: `src/api/*` apenas delega casos de uso; validadores isolados
- **Eventos como integracao**: publish/subscribe entre dominios (quotes -> approvals -> orders)
- **CQRS pragmatica**: comandos gravam no modelo canonico; queries leem materialized views ou caches
- **Observabilidade nativa**: eventos de dominio com metadados para auditoria, metrics e tracing
- **Idempotencia**: comandos POST e steps de workflow com chaves idempotentes
- **Seguranca B2B**: policies por dominio, segregacao multi-tenant, auditoria imutavel

---

## Dominios Centrais

### 1. Catalog

- **Responsabilidade:** ingestao, normalizacao, enriquecimento e disponibilidade de SKUs
- **JTBD:** "Unificar SKUs multi-distribuidor com dados confiaveis e imagens otimizadas"
- **Inputs:** feeds JSON/CSV, webhooks parceiros, comandos admin
- **Outputs:** produtos normalizados, imagens otimizadas, eventos `catalog.*`
- **Outcomes:** TTFB <150 ms, sincronizacao <15 min, 0 erro critico de mapeamento
- **KPIs:** TTFB, tempo de sync, taxa de falha de normalizacao
- **Touchpoints:** `src/modules/unified-catalog`, `src/modules/ysh-catalog`, rotas `/admin/import-catalog`, `/store/catalog/*`

### 2. Pricing

- **Responsabilidade:** precificacao por canal/grupo, promoções e regras comerciais
- **JTBD:** "Calcular preco final consistente por contexto"
- **Inputs:** regras comerciais, grupos de clientes, promoções, eventos `catalog.product.updated`
- **Outputs:** precos resolvidos, eventos `pricing.*`
- **Outcomes:** consistencia 100%, latencia <50 ms
- **KPIs:** latencia de calculo, divergencias de preco, cobertura de regras
- **Touchpoints:** `src/modules/ysh-pricing`, workflows de promocao, rotas `/admin/solar/promotions`

### 3. Quotes

- **Responsabilidade:** criacao, negociacao e ciclo de vida de RFQs
- **JTBD:** "Gerenciar cotacoes com snapshot imutavel, mensagens e anexos"
- **Inputs:** itens, mensagens, anexos, politicas de cliente
- **Outputs:** cotacoes, mensagens, eventos `quote.*`
- **Outcomes:** TTM <5 min, taxa de aceite >30%, SLA mensagens <2 h
- **KPIs:** tempo ciclo, taxa de aceite, aging
- **Touchpoints:** `src/modules/quote`, `src/api/admin|store/quotes/*`

### 4. Approvals

- **Responsabilidade:** workflows de aprovacao multi-etapas com auditoria
- **JTBD:** "Orquestrar aprovacoes condicionais garantido rastreabilidade"
- **Inputs:** politicas por empresa, eventos de quote/order, excecoes
- **Outputs:** decisoes, pendencias, auditoria, eventos `approval.*`
- **Outcomes:** lead time <24 h, bypass indevido 0%
- **KPIs:** ciclo por etapa, taxa de escalonamento, aging pendente
- **Touchpoints:** `src/workflows/approval`, rotas `/store/approvals`, `/admin/approvals/*`

### 5. Company

- **Responsabilidade:** estrutura B2B (empresas, colaboradores, limites, grupos)
- **JTBD:** "Configurar contas corporativas com governanca de gastos"
- **Inputs:** convites, mudancas de papel, limites, integrações ERP/CRM
- **Outputs:** memberships, limites, eventos `company.*`
- **Outcomes:** provisionamento <1 min, 0 divergencia de limite
- **KPIs:** tempo de onboarding, inconsistencias de limite, adherencia a policy
- **Touchpoints:** `src/modules/empresa`, rotas `/admin/companies/*`

### 6. Orders

- **Responsabilidade:** conversao de RFQ em pedido, checkout B2B, pagamentos e fulfillment
- **JTBD:** "Concluir pedidos B2B com aprovacao integrada"
- **Inputs:** carrinho, aprovacao concedida, status pagamento/entrega
- **Outputs:** pedidos, faturas, eventos `order.*`
- **Outcomes:** taxa de erro checkout <0.5%, previsibilidade de fulfillment
- **KPIs:** taxa sucesso checkout, tempo ciclo, reprocessamentos
- **Touchpoints:** `@medusajs/order`, workflows customizados, rotas `/store/orders`

### 7. Financing

- **Responsabilidade:** simulacoes, credit scoring, consentimentos regulatorios
- **JTBD:** "Simular e aprovar financiamentos com conformidade BACEN"
- **Inputs:** dados cliente, consentimentos, tabelas parceiras
- **Outputs:** simulacoes, limites aprovados/negados, eventos `financing.*`
- **Outcomes:** latencia simulacao <2 s, conformidade 100%
- **KPIs:** latencia, taxa de aprovacao, alertas compliance
- **Touchpoints:** `src/modules/financing`, rotas `/admin/financing/*`

### 8. Energy-ANEEL

- **Responsabilidade:** tarifas/regioes ANEEL e aplicacao em simulacoes/billing
- **JTBD:** "Manter tabelas tarifarias e aplica-las corretamente"
- **Inputs:** bases ANEEL, atualizacoes regionais, ajustes reguladores
- **Outputs:** tarifas resolvidas, eventos `aneel.tariff.updated`
- **Outcomes:** acerto 100%, atualizacao <48 h
- **KPIs:** latencia resolucao tarifa, divergencias encontradas
- **Touchpoints:** `src/modules/tarifa-aneel`, rotas `/admin/aneel/*`

### 9. Solar-Simulations

- **Responsabilidade:** calculos PVLib, cenarios de viabilidade, caching distribuido
- **JTBD:** "Estimativas confiaveis de geracao e retorno"
- **Inputs:** coordenadas, equipamentos, irradiancia, parametros de consumo
- **Outputs:** metricas de geracao, relatórios, eventos `solar.simulation.completed`
- **Outcomes:** latencia cache hit <1 s / miss <5 s, acuracia validada
- **KPIs:** cache hit rate, latencia, variacao vs medicao real
- **Touchpoints:** `src/modules/solar`, `src/modules/pvlib-integration`, scripts Python

### 10. Integrations

- **Responsabilidade:** ingestao distribuidores, reconciliacao de estoque/preco/imagens
- **JTBD:** "Sincronizar dados externos com confianca e alertas proativos"
- **Inputs:** cron jobs, webhooks, scraping fallback, APIs parceiras
- **Outputs:** normalizacoes, diffs, alertas, eventos `integration.*`
- **Outcomes:** erro <1%, latencia <15 min
- **KPIs:** divergencia por distribuidor, tempo de resolucao, erros de integracao
- **Touchpoints:** `data/products-inventory`, scripts de pipeline, jobs `src/jobs/*`

### 11. Observability

- **Responsabilidade:** metrics, logs estruturados, tracing, auditoria e SLOs
- **JTBD:** "Medir e explicar o comportamento do sistema end-to-end"
- **Inputs:** eventos de dominio, logs, traces, configuracoes de alerta
- **Outputs:** dashboards, alertas, auditoria, relatórios
- **Outcomes:** MTTR <30 min, SLO 99.9% APIs criticas
- **KPIs:** disponibilidade, tempo de deteccao, tempo de resolucao
- **Touchpoints:** `src/domains/observability`, configuracoes Grafana/Alertmanager

---

## Arquitetura Alvo

- `src/domains/<dominio>/{domain,application,infrastructure,interfaces}` para logica principal
- `src/modules/<dominio>` encapsula integracao Medusa (registries, di container)
- Rotas em `src/api/admin|store/<dominio>` apenas orquestram validacao + chamada do caso de uso
- Eventos publicados via subscribers (`src/subscribers/<dominio>`) e workflows (`src/workflows/<dominio>`)
- Redis para cache (catalogo, simulacoes, listas) com versionamento de chave
- Postgres com indices por filtros frequentes e materialized views em `database/views/<dominio>`
- Jobs assíncronos em `src/jobs/<dominio>` com filas segregadas
- Observabilidade nativa (OpenTelemetry + Prometheus + Grafana)

---

## Roadmap de Migracao

### Fase 0 – Inventario (concluida)

- Mapear rotas, workflows, subscribers, jobs, migrações e dados vivos
- Catalogar dependencias externas e contratos atuais

### Fase 1 – Fundacao DDD (2 semanas)

- Criar skeleton `src/domains/*` (completo)
- Extrair casos de uso prioritarios para camadas `application`
- Configurar validadores/DTOs em `interfaces`

### Fase 2 – Catalogo & Quotes (3 semanas)

- Separar comandos/queries com CQRS leve
- Implementar caches Redis e materialized views
- Atualizar rotas `/admin/import-catalog` e `/store/quotes` para usar novos casos de uso

### Fase 3 – Approvals & Orders (3 semanas)

- Introduzir eventos `quote.*` -> `approval.*` -> `order.*`
- Centralizar trilha de auditoria
- Ajustar workflows customizados de pedido

### Fase 4 – Financing & Energy (3 semanas)

- Consolidar integrações BACEN/ANEEL com consent store unificado
- Normalizar tarifas por regiao e expor API de consulta

### Fase 5 – Observability (2 semanas)

- Criar builders de metricas por dominio e SLO dashboards
- Instrumentar workflows e jobs com tracing

### Fase 6 – Hardening Prod (2 semanas)

- Migrar workflow engine para backend persistente (Redis/DB)
- Implementar rate limiting multi-tenant, idempotency keys e testes de carga

Cada fase com rollout progressivo, feature flags e planos de rollback.

---

## Entregaveis Principais

- Catalogo de dominios 360 graus com JTBD/inputs/outputs/outcomes
- Arquitetura alvo documentada e skeletons criados (`src/domains/*`)
- Plano de migracao incremental com riscos e mitigacoes
- Conjunto de KPIs + dashboards de monitoramento (Grafana)
- Documentacao operacional em `docs/REESTRUTURACAO_360.md` e anexos

---

## Riscos e Mitigacoes

| Risco | Mitigacao |
|-------|-----------|
| Acoplamento legado em rotas | Introduzir camada `application` antes de mover, refatorar incrementalmente, usar feature flags |
| Sobre carga em importacoes | Jobs particionados por distribuidor, backpressure, limites de concorrencia |
| Consistencia eventual em eventos | Contratos versionados, idempotencia em subscribers, repositorio de eventos com dedup |
| Crescimento de cache | TTLs por dominio, invalidacao via eventos, monitorar consumo |
| Compliance e auditoria | Consent store central, logs imutaveis, revisao periodica |

---

## KPIs e Dashboards

- **Catalogo:** TTFB, tempo de sync, erros de normalizacao
- **Pricing:** latencia de calculo, divergencias, aplicacao de promocao
- **Quotes:** tempo ciclo, taxa de aceite, aging
- **Approvals:** tempo por etapa, escalonamentos, aging
- **Orders:** taxa sucesso checkout, tempo ciclo, reprocessamentos
- **Financing:** latencia simulacao, taxa aprovacao, alertas compliance
- **Solar-Simulations:** cache hit rate, latencia hit/miss, acuracia
- **Observability:** SLO APIs criticas, MTTR, cobertura de logs/traces

Dashboards recomendados: API Performance, Cache Efficiency, Workflow Health, Database Health, Business Conversion.

---

## Proximos Passos Imediatos

1. Validar mapa de dominios e prioridades com stakeholders.
2. Escolher rotas piloto (ex.: import catalogo, send quote) para migrar para camada `application`.
3. Configurar caches Redis + indices críticos (catalogo, quotes, approvals).
4. Definir dashboards iniciais e coletores de metricas.
5. Planejar cronograma de treinamentos internos sobre novo modelo de dominios.

---

**Ultima atualizacao:** 20/10/2025

