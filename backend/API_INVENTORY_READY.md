# 📋 YSH B2B - Inventário de APIs Prontas

> **Última atualização:** 21 de outubro de 2025  
> **Total de endpoints:** 183+ rotas implementadas

---

## 🎯 Resumo Executivo

Este documento cataloga **todas as APIs REST prontas** do backend YSH B2B, organizadas por funcionalidade e domínio.

### Estatísticas Globais

- **183+ endpoints** ativos
- **12 domínios principais** de negócio
- **Versão da API:** v2.0.0
- **Rate limiting:** Implementado em endpoints críticos
- **Autenticação:** JWT + Session-based
- **Documentação:** Swagger disponível em `/docs`

---

## 📦 1. CATÁLOGO E PRODUTOS

### 1.1 Catálogo Unificado (Internal Catalog)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/catalog` | Overview do catálogo completo | ✅ Ready |
| `GET` | `/store/catalog/:category` | Produtos por categoria | ✅ Ready |
| `GET` | `/store/catalog/:category/:id` | Detalhes de produto específico | ✅ Ready |
| `GET` | `/store/catalog/search` | Busca de produtos | ✅ Ready |
| `GET` | `/store/catalog/skus` | Lista de SKUs | ✅ Ready |
| `GET` | `/store/catalog/skus/:id` | Detalhes de SKU | ✅ Ready |
| `GET` | `/store/catalog/skus/:id/compare` | Comparação de SKUs | ✅ Ready |
| `GET` | `/store/catalog/manufacturers` | Lista de fabricantes | ✅ Ready |
| `GET` | `/store/catalog/metrics` | Métricas do catálogo | ✅ Ready |
| `GET` | `/store/catalog/kits` | Kits pré-montados | ✅ Ready |
| `GET` | `/store/catalog/kits/:id` | Detalhes de kit específico | ✅ Ready |

**Características:**

- ✅ 861 imagens pré-carregadas
- ✅ Cache em memória (~94% hit rate)
- ✅ Paginação otimizada (até 200/página)
- ✅ Resposta < 50ms
- ✅ Independente do Unified Catalog

### 1.2 Produtos Unificados

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/products` | Lista unificada de produtos | ✅ Ready |
| `GET` | `/store/products.custom` | Produtos customizados | ✅ Ready |
| `GET` | `/store/products.custom/:id` | Detalhes produto customizado | ✅ Ready |
| `GET` | `/store/products/by-sku/:sku` | Busca por SKU | ✅ Ready |
| `GET` | `/store/produtos_melhorados` | Produtos com enriquecimento | ✅ Ready |
| `GET` | `/store/produtos_melhorados/:id` | Detalhes produto enriquecido | ✅ Ready |
| `GET` | `/store/produtos_melhorados/:handle` | Busca por handle | ✅ Ready |

**Query Parameters:**

- `source`: `internal|external|all`
- `enhanced`: `true|false`
- `custom`: `true|false`
- `category`: filtro por categoria
- `manufacturer`: filtro por fabricante
- `min_price`, `max_price`: filtro de preço
- `q`: busca textual

### 1.3 Catálogo Interno (Legacy)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/catalogo_interno` | Overview catálogo interno | ✅ Ready |
| `GET` | `/store/catalogo_interno/:category` | Categoria específica | ✅ Ready |
| `GET` | `/store/catalogo_interno/health` | Health check do catálogo | ✅ Ready |
| `GET` | `/store/catalogo_interno/images/:sku` | Imagens por SKU | ✅ Ready |
| `POST` | `/store/catalogo_interno/preload` | Pré-carregamento de cache | ✅ Ready |
| `GET` | `/store/catalogo_interno/cdn/:category/:filename` | Imagens via CDN | ✅ Ready |

### 1.4 Fallback API (Redundância)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/fallback/products` | Produtos fallback | ✅ Ready |
| `GET` | `/store/fallback/products/:category` | Categoria fallback | ✅ Ready |
| `GET` | `/store/fallback/products/:category/:id` | Produto fallback | ✅ Ready |

---

## 💰 2. COTAÇÕES E ORÇAMENTOS

### 2.1 Cotações Store

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/quotes` | Lista cotações do cliente | ✅ Ready |
| `POST` | `/store/quotes` | Criar cotação | ✅ Ready |
| `GET` | `/store/quotes/:id` | Detalhes da cotação | ✅ Ready |
| `POST` | `/store/quotes/:id/accept` | Aceitar cotação | ✅ Ready |
| `POST` | `/store/quotes/:id/reject` | Rejeitar cotação | ✅ Ready |
| `GET` | `/store/quotes/:id/preview` | Preview da cotação | ✅ Ready |
| `POST` | `/store/quotes/:id/messages` | Adicionar mensagem | ✅ Ready |

### 2.2 Cotações Admin

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/quotes` | Lista todas cotações | ✅ Ready |
| `GET` | `/admin/quotes/:id` | Detalhes cotação (admin) | ✅ Ready |
| `POST` | `/admin/quotes/:id/send` | Enviar cotação ao cliente | ✅ Ready |
| `POST` | `/admin/quotes/:id/reject` | Rejeitar cotação | ✅ Ready |
| `POST` | `/admin/quotes/:id/messages` | Mensagens (admin) | ✅ Ready |

### 2.3 Cotações Comparativas

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/comparative-quotes` | Lista cotações comparativas | ✅ Ready |
| `POST` | `/store/comparative-quotes` | Criar cotação comparativa | ✅ Ready |
| `GET` | `/store/comparative-quotes/:id` | Detalhes | ✅ Ready |
| `POST` | `/store/comparative-quotes/:id` | Atualizar | ✅ Ready |
| `DELETE` | `/store/comparative-quotes/:id` | Deletar | ✅ Ready |
| `POST` | `/store/comparative-quotes/:id/publish` | Publicar para cliente | ✅ Ready |
| `POST` | `/store/comparative-quotes/:id/select` | Selecionar opção | ✅ Ready |
| `GET` | `/store/comparative-quotes/:id/select` | Ver seleção | ✅ Ready |
| `GET` | `/store/comparative-quotes/:id/comparison` | Comparar opções | ✅ Ready |
| `POST` | `/store/comparative-quotes/:id/comparison` | Adicionar comparação | ✅ Ready |

### 2.4 Cotações Solares (Draft Orders)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/solar-quotes` | Criar cotação solar | ✅ Ready |

**Features:**

- ✅ Preços customizados por tipo de telhado/construção
- ✅ Validação automática de viabilidade técnica
- ✅ Cálculo de ROI e payback
- ✅ Estimativa de geração anual
- ✅ Multiplicadores de complexidade

---

## ☀️ 3. SOLAR E FOTOVOLTAICA

### 3.1 Calculadora Solar

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/solar/calculate` | Cálculo de dimensionamento | ✅ Ready |
| `POST` | `/store/solar/calculator` | Calculadora avançada | ✅ Ready |
| `GET` | `/store/solar/calculator` | Info da calculadora | ✅ Ready |
| `GET` | `/store/solar/viability` | Análise de viabilidade | ✅ Ready |
| `POST` | `/store/solar/validate-feasibility` | Validar viabilidade | ✅ Ready |

### 3.2 Cálculos Solares (Saved)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/calculos_solares` | Lista cálculos salvos | ✅ Ready |
| `POST` | `/store/calculos_solares` | Criar novo cálculo | ✅ Ready |
| `GET` | `/store/calculos_solares/:id` | Detalhes do cálculo | ✅ Ready |
| `PATCH` | `/store/calculos_solares/:id` | Atualizar cálculo | ✅ Ready |
| `DELETE` | `/store/calculos_solares/:id` | Deletar cálculo | ✅ Ready |

### 3.3 Computer Vision Solar

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/deteccao_solar` | Detecção de painéis em imagem | ✅ Ready |
| `GET` | `/store/deteccao_solar` | Info do serviço | ✅ Ready |
| `POST` | `/store/analise_termica` | Análise térmica (infrared) | ✅ Ready |
| `GET` | `/store/analise_termica` | Info análise térmica | ✅ Ready |
| `POST` | `/store/photogrammetry` | Reconstrução 3D (OpenDroneMap) | ✅ Ready |
| `GET` | `/store/photogrammetry` | Info photogrammetry | ✅ Ready |

**Capacidades CV:**

- ✅ Detecção de painéis solares
- ✅ Análise térmica (hotspots)
- ✅ Reconstrução 3D de telhados
- ✅ Medição de áreas
- ✅ Análise de sombreamento
- ✅ Cálculo de viabilidade solar

### 3.4 PVLib Integration

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/pvlib/panels` | Lista painéis certificados | ✅ Ready |
| `GET` | `/pvlib/inverters` | Lista inversores certificados | ✅ Ready |
| `POST` | `/pvlib/validate-mppt` | Validar compatibilidade MPPT | ✅ Ready |
| `GET` | `/pvlib/stats` | Estatísticas do banco de dados | ✅ Ready |

### 3.5 Solar Admin

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/solar/orders` | Pedidos solares | ✅ Ready |
| `POST` | `/admin/solar/promotions` | Criar promoção | ✅ Ready |
| `POST` | `/admin/solar/promotions/free-shipping` | Frete grátis | ✅ Ready |
| `GET` | `/admin/solar/fleet-analysis` | Análise de frota | ✅ Ready |
| `GET` | `/admin/view-configurations/solar-projects` | Configurações projeto | ✅ Ready |

---

## 💳 4. FINANCIAMENTO

### 4.1 Simulação de Financiamento

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/financing/simulate` | Simular SAC ou PRICE | ✅ Ready |
| `GET` | `/financing/rates` | Taxas atuais | ✅ Ready |

**Sistemas suportados:**

- ✅ SAC (Sistema de Amortização Constante)
- ✅ PRICE (Sistema Francês)
- ✅ Taxa SELIC + spread
- ✅ Taxas customizadas

### 4.2 Financiamento Store

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/financiamento` | Opções de financiamento | ✅ Ready |
| `POST` | `/store/financiamento` | Criar financiamento | ✅ Ready |
| `POST` | `/store/financiamento/calculate` | Calcular parcelas | ✅ Ready |

### 4.3 Aplicações de Financiamento

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/aplicacoes_financiamento` | Aplicar para financiamento | ✅ Ready |
| `GET` | `/store/aplicacoes_financiamento` | Lista aplicações | ✅ Ready |

### 4.4 Financiamento Admin

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/financing` | Lista financiamentos | ✅ Ready |
| `POST` | `/admin/financing` | Criar financiamento | ✅ Ready |
| `GET` | `/admin/financing/:id` | Detalhes | ✅ Ready |
| `POST` | `/admin/financing/:id` | Atualizar | ✅ Ready |
| `GET` | `/admin/financing/companies/:company_id` | Por empresa | ✅ Ready |

---

## 🏢 5. EMPRESAS E B2B

### 5.1 Empresas Store

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/companies` | Criar empresa | ✅ Ready |
| `GET` | `/store/companies/:id` | Detalhes da empresa | ✅ Ready |
| `POST` | `/store/companies/:id` | Atualizar empresa | ✅ Ready |
| `DELETE` | `/store/companies/:id` | Deletar empresa | ✅ Ready |
| `POST` | `/store/companies/:id/approval-settings` | Config aprovações | ✅ Ready |
| `POST` | `/store/companies/:id/invite-employee` | Convidar funcionário | ✅ Ready |

### 5.2 Funcionários

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/companies/:id/employees` | Lista funcionários | ✅ Ready |
| `POST` | `/store/companies/:id/employees` | Adicionar funcionário | ✅ Ready |
| `GET` | `/store/companies/:id/employees/:employeeId` | Detalhes | ✅ Ready |
| `POST` | `/store/companies/:id/employees/:employeeId` | Atualizar | ✅ Ready |
| `DELETE` | `/store/companies/:id/employees/:employeeId` | Remover | ✅ Ready |

### 5.3 Aprovações

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/approvals` | Lista aprovações pendentes | ✅ Ready |
| `POST` | `/store/approvals/:id` | Aprovar/rejeitar | ✅ Ready |
| `POST` | `/store/carts/:id/approvals` | Solicitar aprovação | ✅ Ready |

### 5.4 Empresas Admin

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/companies` | Lista empresas | ✅ Ready |
| `POST` | `/admin/companies` | Criar empresa | ✅ Ready |
| `GET` | `/admin/companies/:id` | Detalhes | ✅ Ready |
| `POST` | `/admin/companies/:id` | Atualizar | ✅ Ready |
| `DELETE` | `/admin/companies/:id` | Deletar | ✅ Ready |
| `GET` | `/admin/companies/:id/approval-settings` | Config aprovações | ✅ Ready |
| `POST` | `/admin/companies/:id/approval-settings` | Atualizar config | ✅ Ready |
| `POST` | `/admin/companies/:id/customer-group` | Associar customer group | ✅ Ready |
| `DELETE` | `/admin/companies/:id/customer-group/:customerGroupId` | Desassociar | ✅ Ready |
| `GET` | `/admin/companies/:id/employees` | Funcionários (admin) | ✅ Ready |
| `POST` | `/admin/companies/:id/employees` | Adicionar funcionário | ✅ Ready |
| `GET` | `/admin/companies/:id/employees/:employeeId` | Detalhes funcionário | ✅ Ready |
| `POST` | `/admin/companies/:id/employees/:employeeId` | Atualizar funcionário | ✅ Ready |
| `DELETE` | `/admin/companies/:id/employees/:employeeId` | Remover funcionário | ✅ Ready |
| `GET` | `/admin/approvals` | Todas aprovações | ✅ Ready |
| `POST` | `/admin/approvals/:id` | Processar aprovação | ✅ Ready |

---

## 💰 6. PRICING E PAGAMENTOS

### 6.1 Pricing

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/pricing/calculate` | Calcular preço | ✅ Ready |
| `POST` | `/pricing/calculate/batch` | Cálculo em lote | ✅ Ready |
| `GET` | `/store/frete_gratis/prices` | Preços frete grátis | ✅ Ready |

### 6.2 Payment

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/payment/calculate` | Calcular condições pagamento | ✅ Ready |
| `GET` | `/payment/calculate` | Info condições | ✅ Ready |
| `POST` | `/payment/split` | Split de pagamento | ✅ Ready |
| `GET` | `/payment/split` | Info split | ✅ Ready |

### 6.3 Regras de Pricing por Distribuidor

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/distributors/:code/pricing-rules` | Regras do distribuidor | ✅ Ready |
| `POST` | `/distributors/:code/pricing-rules` | Criar/atualizar regras | ✅ Ready |
| `GET` | `/distributors/:code/pricing-rules/tiers` | Tiers de desconto | ✅ Ready |
| `GET` | `/distributors/:code/pricing-rules/stats` | Estatísticas | ✅ Ready |

---

## 🤖 7. RAG E IA

### 7.1 Hélio Copiloto Solar

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/rag/ask-helio` | Pergunta ao Hélio (GPT-4 + RAG) | ✅ Ready |
| `POST` | `/store/helio` | Alias para ask-helio | ✅ Ready |

**Features:**

- ✅ GPT-4o integrado
- ✅ RAG sobre 4 collections (catálogo, regulações, tarifas, técnico)
- ✅ Embeddings text-embedding-3-large
- ✅ Rate limiting (10 req/min)
- ✅ Timeout 30s
- ✅ Contextual com CEP e consumo

### 7.2 RAG Search

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/rag/search` | Busca semântica vetorial | ✅ Ready |
| `GET` | `/store/rag/search` | Info do serviço | ✅ Ready |
| `POST` | `/store/rag/recommend-products` | Recomendação de produtos | ✅ Ready |

### 7.3 RAG Admin

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/admin/rag/seed-collections` | Popular collections | ✅ Ready |

---

## 📊 8. ANEEL E TARIFAS

### 8.1 Tarifas

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/aneel/tariffs` | Buscar tarifas | ✅ Ready |
| `GET` | `/aneel/tariffs` | Tarifas (endpoint alternativo) | ✅ Ready |

**Query Parameters:**

- `distributor`: código da distribuidora
- `consumer_class`: B1, B2, B3, A4, etc.
- `subgroup`: subgrupo tarifário

### 8.2 Concessionárias

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/aneel/concessionarias` | Lista concessionárias | ✅ Ready |

### 8.3 Cálculo de Economia

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/aneel/calculate-savings` | Calcular economia FV | ✅ Ready |

---

## 🔍 9. ANÁLISE DE CRÉDITO

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/credit-analysis` | Criar análise | ✅ Ready |
| `GET` | `/credit-analysis` | Lista análises | ✅ Ready |
| `POST` | `/credit-analysis/:id/analyze` | Executar análise | ✅ Ready |
| `PATCH` | `/credit-analysis/:id/status` | Atualizar status | ✅ Ready |
| `GET` | `/credit-analysis/customer/:customer_id` | Por cliente | ✅ Ready |
| `GET` | `/credit-analysis/quote/:quote_id` | Por cotação | ✅ Ready |
| `POST` | `/store/analises_credito` | Análise store | ✅ Ready |
| `GET` | `/store/analises_credito` | Lista (store) | ✅ Ready |

---

## 🛒 10. CARRINHO E PEDIDOS

### 10.1 Carrinho

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/carts/:id/line-items/bulk` | Adicionar múltiplos itens | ✅ Ready |

### 10.2 Pedidos

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/orders/:id/fulfillment` | Status de fulfillment | ✅ Ready |

### 10.3 Kits

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/kits` | Lista kits pré-montados | ✅ Ready |

---

## 📱 11. FACEBOOK CATALOG

### 11.1 Sync

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/admin/facebook-catalog/sync` | Sincronizar catálogo | ✅ Ready |
| `GET` | `/admin/facebook-catalog/syncs` | Histórico de syncs | ✅ Ready |

### 11.2 Mappings

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/facebook-catalog/mappings` | Ver mapeamentos | ✅ Ready |

### 11.3 Platforms

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/facebook-catalog/platforms/status` | Status plataformas | ✅ Ready |
| `POST` | `/admin/facebook-catalog/platforms/connect` | Conectar plataforma | ✅ Ready |

### 11.4 WhatsApp

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/admin/facebook-catalog/whatsapp/send-catalog` | Enviar catálogo | ✅ Ready |
| `POST` | `/admin/facebook-catalog/whatsapp/send-product` | Enviar produto | ✅ Ready |

---

## 🏥 12. HEALTH E MONITORING

### 12.1 Health Checks

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/health` | Health geral da API | ✅ Ready |
| `GET` | `/store/health` | Health store (detalhado) | ✅ Ready |
| `POST` | `/store/health` | Trigger health checks | ✅ Ready |

### 12.2 Monitoring

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/ws/monitoring` | WebSocket monitoring | ✅ Ready |

---

## 📚 13. DOCUMENTAÇÃO E UTILIDADES

### 13.1 Docs

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/docs` | Documentação interativa | ✅ Ready |
| `GET` | `/docs.json` | OpenAPI spec JSON | ✅ Ready |

### 13.2 Events e Leads

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/store/events` | Registrar evento | ✅ Ready |
| `POST` | `/store/leads` | Criar lead | ✅ Ready |

### 13.3 Imagens

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/store/images` | Serviço de imagens | ✅ Ready |
| `POST` | `/admin/internal/media/presign` | Presigned URL S3 | ✅ Ready |

### 13.4 Admin Internal

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/internal/products` | Lista produtos internos | ✅ Ready |
| `POST` | `/admin/internal/products` | Criar produto interno | ✅ Ready |
| `POST` | `/admin/internal/products/:id/images` | Upload imagem | ✅ Ready |
| `PATCH` | `/admin/internal/products/:id/images` | Atualizar imagem | ✅ Ready |
| `DELETE` | `/admin/internal/products/:id/images` | Deletar imagem | ✅ Ready |

### 13.5 Import Catalog

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `GET` | `/admin/import-catalog` | Status import | ✅ Ready |

### 13.6 Viability (Solar)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| `POST` | `/solar/viability` | Análise de viabilidade | ✅ Ready |
| `GET` | `/solar/viability` | Info viabilidade | ✅ Ready |

---

## 🔐 Autenticação e Segurança

### Headers Requeridos

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
X-API-Version: v2.0.0  # Opcional
```

### Rate Limiting

| Endpoint | Limite | Janela |
|----------|--------|--------|
| `/store/rag/ask-helio` | 10 req | 1 min |
| Outros endpoints | 100 req | 1 min |

---

## 📊 Métricas de Performance

### Tempos de Resposta Médios

| Tipo | Tempo |
|------|-------|
| Catalog queries | < 50ms |
| Product searches | < 100ms |
| Solar calculations | < 200ms |
| RAG queries | < 2s |
| Photogrammetry | < 30s |

### Cache Hit Rates

| Serviço | Hit Rate |
|---------|----------|
| Internal Catalog | ~94% |
| Product Images | ~87% |
| Tariff Data | ~92% |

---

## 🚀 Exemplos de Uso

### 1. Buscar produtos de uma categoria

```bash
curl -X GET "https://api.yellosolarhub.com/store/catalog/panels?limit=50&page=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Criar cotação solar

```bash
curl -X POST "https://api.yellosolarhub.com/store/solar-quotes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_123",
    "region_id": "reg_456",
    "solar_project": {
      "capacity_kwp": 10.5,
      "irradiation_kwh_m2_day": 5.2,
      "roof_type": "metalico",
      "building_type": "commercial",
      "roof_area_m2": 80,
      "address": {
        "street": "Rua Solar 123",
        "city": "São Paulo",
        "state": "SP",
        "postal_code": "01310-100"
      }
    },
    "items": [...]
  }'
```

### 3. Perguntar ao Hélio

```bash
curl -X POST "https://api.yellosolarhub.com/store/rag/ask-helio" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual o melhor inversor para um sistema de 10kWp?",
    "context": {
      "cep": "01310-100",
      "consumo_kwh_mes": 800
    }
  }'
```

### 4. Simular financiamento

```bash
curl -X POST "https://api.yellosolarhub.com/financing/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "principal": 50000,
    "periods": 60,
    "system": "SAC",
    "spread": 3.5
  }'
```

---

## 📝 Notas Importantes

1. **API Versioning:** Todas as respostas incluem header `X-API-Version`
2. **Backward Compatibility:** APIs legacy ainda funcionam mas estão marcadas como deprecated
3. **Error Handling:** Erros seguem padrão RFC 7807 (Problem Details)
4. **Pagination:** Padrão `limit`/`offset` ou `page`/`limit`
5. **Cache Headers:** Respostas incluem `Cache-Control` e `ETag`

---

## 🔄 Endpoints Deprecated (mas ainda funcionais)

| Endpoint | Substituto | Deprecado em |
|----------|-----------|---------------|
| `/store/catalog` (old) | `/store/products` | v2.0.0 |
| `/store/internal-catalog` | `/store/catalog` | v2.0.0 |
| `/store/products_enhanced` | `/store/products?enhanced=true` | v2.0.0 |

---

## 📦 Próximas Features (Roadmap)

- [ ] GraphQL endpoint
- [ ] WebSocket real-time updates
- [ ] Batch operations API
- [ ] Advanced analytics endpoints
- [ ] Mobile-optimized responses
- [ ] Multi-language support

---

## 📞 Contato e Suporte

- **Documentação completa:** https://docs.yellosolarhub.com
- **Swagger UI:** https://api.yellosolarhub.com/docs
- **Status Page:** https://status.yellosolarhub.com

---

**Gerado automaticamente em:** 21 de outubro de 2025  
**Versão do backend:** 2.10.0  
**Framework:** Medusa.js v2
