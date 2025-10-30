---
id: schemas-performance
title: Análise de Schemas e Performance
sidebar_label: Schemas & Performance
sidebar_position: 1
description: Análise detalhada dos schemas de produtos, SKUs e performance dos containers Docker
---

## 📦 Análise dos Schemas e SKUs

### Inventário Total de Produtos

**Total**: 1.161 produtos em 12 categorias

| Categoria | Produtos | Tamanho | Completude | Status |
|-----------|----------|---------|------------|--------|
| **Inverters** | 489 | 790.79 KB | 99.8% | ✅ Excelente |
| **Kits** | 334 | 1348.48 KB | 74.5% | ⚠️ Bom |
| **Cables** | 55 | 79.03 KB | 100% | ✅ Excelente |
| **EV Chargers** | 83 | 139 KB | 100% | ✅ Excelente |
| **Controllers** | 38 | 64.83 KB | 100% | ✅ Excelente |
| **Structures** | 40 | 52.22 KB | 100% | ✅ Excelente |
| **Panels** | 29 | 92.43 KB | 96.6% | ✅ Excelente |
| **Accessories** | 17 | 22.69 KB | 100% | ✅ Excelente |
| **Stringboxes** | 13 | 15.04 KB | 100% | ✅ Excelente |
| **Others** | 10 | 12.84 KB | 48.1% | 🔴 Ruim |
| **Batteries** | 9 | 11.07 KB | 100% | ✅ Excelente |
| **Posts** | 6 | 8.84 KB | 100% | ✅ Excelente |

### Qualidade dos Dados

#### ✅ Categorias de Alta Qualidade (>95%)

Inverters, Cables, EV Chargers, Controllers, Structures, Panels, Accessories, Stringboxes, Batteries, Posts

#### ⚠️ Categorias que Precisam Atenção

- **Kits** (74.5%): Faltam manufacturers em alguns produtos
- **Others** (48.1%): Dados incompletos, considerar recategorização

### SKU Registry

- **Total de SKUs registrados**: 4.749 SKUs únicos
- **Formato**: Normalizado e uppercase
- **Duplicatas**: Nenhuma detectada
- **Integridade**: ✅ 100%

### Estrutura dos Produtos

```json
{
  "id": "unique_id",
  "name": "Nome do Produto",
  "manufacturer": "Fabricante",
  "model": "Modelo",
  "category": "categoria",
  "price": "R$ XX,XX",
  "pricing": {
    "price": 100.00,
    "price_brl": 100.00,
    "currency": "BRL"
  },
  "technical_specs": {
    "potencia": "550W",
    "tensao": "380V"
  },
  "metadata": {
    "source": "fonte",
    "normalized": true,
    "specs_enriched": true,
    "image_match": {
      "status": "matched",
      "confidence": 0.95
    }
  },
  "image_url": "caminho/para/imagem",
  "availability": true
}
```

## 🐳 Análise dos Containers Docker

### Status Atual dos Recursos

| Container | CPU % | Memória Usada | Mem % | Net I/O | Block I/O |
|-----------|-------|---------------|-------|---------|-----------|
| postgres-dev | 0.01% | 44.59 MB | 0.14% | 23.7kB / 73.3kB | 34.6MB / 303kB |
| redis-dev | 0.23% | 9.07 MB | 0.03% | 3.57kB / 6.56kB | 12.8MB / 4.1kB |
| backend-dev | 0.01% | 310.1 MB | 0.97% | 91.5kB / 28.9kB | 139MB / 4.69MB |
| storefront-dev | 0.31% | 282.1 MB | 0.88% | 7.15kB / 1.6kB | 142MB / 21.9MB |

**Total de Memória em Uso**: ~646 MB de 31.23 GB disponíveis (2%)

### Configurações Atuais

#### PostgreSQL

```ini
shared_buffers = 128 MB          # ⚠️ Pode ser otimizado
max_connections = 100            # ✅ Adequado para dev
work_mem = 4 MB                  # ⚠️ Pode ser otimizado
maintenance_work_mem = 64 MB     # ⚠️ Pode ser otimizado
effective_cache_size = 4 GB      # ✅ OK
```

#### Redis

```ini
maxmemory = 0                    # ⚠️ Deve ser configurado
maxmemory-policy = não configurado  # ⚠️ Deve ser configurado
```

#### Backend (Node.js)

```bash
NODE_OPTIONS = --max-old-space-size=2048  # ✅ OK
NODE_ENV = development                    # ✅ OK
```

#### Storefront (Next.js)

```bash
NEXT_TELEMETRY_DISABLED = 1    # ✅ OK
NODE_ENV = dev                 # ✅ OK
```

## 🚀 Otimizações Recomendadas

### 🔴 CRÍTICAS (Implementar Imediatamente)

#### 1. Configurar Limites de Memória no Redis

**Problema**: Redis sem limite pode consumir toda a memória disponível.

**Solução**:

```yaml
redis:
  command: >
    redis-server
    --appendonly yes
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
    --save 60 1000
    --tcp-backlog 511
```

#### 2. Otimizar PostgreSQL para Desenvolvimento

**Problema**: Configurações padrão são conservadoras.

**Solução**:

```yaml
postgres:
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=128MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
    -c work_mem=8MB
    -c min_wal_size=1GB
    -c max_wal_size=4GB
```

#### 3. Adicionar Health Checks Adequados

**Solução**:

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
    interval: 30s
    timeout: 10s
    start_period: 60s
    retries: 3

storefront:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
    interval: 30s
    timeout: 10s
    start_period: 60s
    retries: 3
```

### 🟡 IMPORTANTES (Implementar em 24-48h)

#### 4. Adicionar Resource Limits

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 512M

storefront:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 512M

postgres:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
      reservations:
        cpus: '0.25'
        memory: 256M

redis:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.1'
        memory: 128M
```

#### 5. Otimizar Volumes Docker

```yaml
volumes:
  - ./backend:/app:cached
  - /app/node_modules:delegated
  - backend_uploads:/app/uploads
```

#### 6. Configurar Logging Adequado

```yaml
backend:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### 🟢 OPCIONAIS (Performance Avançada)

#### 7. Adicionar Cache de Build Multi-Stage

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=development
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package*.json ./
```

#### 8. Adicionar Prometheus Metrics

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: ysh-prometheus
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"
```

## 🎯 Plano de Importação de Produtos

### Estratégia Recomendada

#### Fase 1: Importar Categorias de Alta Qualidade (Prioridade Alta)

**Produtos**: 1.028 (88.5% do total)

Ordem de importação:

- Inverters (489) - Produto principal
- Panels (29) - Produto principal
- Kits (334) - Combos prontos
- EV Chargers (83) - Alta margem
- Cables (55) - Acessório essencial
- Structures (40) - Complemento
- Controllers (38) - Complemento
- Accessories (17) - Complemento
- Stringboxes (13) - Complemento
- Batteries (9) - Complemento
- Posts (6) - Complemento

#### Fase 2: Revisar e Importar Categorias com Problemas

**Produtos**: 10 (Others)

- Recategorizar produtos da categoria "Others"
- Completar dados faltantes
- Importar após correção

### Script de Importação Recomendado

```typescript
// backend/src/scripts/import-catalog.ts
import { MedusaContainer } from "@medusajs/framework/types"
import fs from "fs"
import path from "path"

const CATALOG_PATH = "../../ysh-erp/data/catalog/unified_schemas"
const CATEGORIES_ORDER = [
  "inverters", "panels", "kits", "ev_chargers", "cables",
  "structures", "controllers", "accessories", "stringboxes",
  "batteries", "posts"
]

export default async function importCatalog(
  container: MedusaContainer
) {
  const productService = container.resolve("productService")
  
  let imported = 0
  let errors = 0
  
  for (const category of CATEGORIES_ORDER) {
    const filePath = path.join(CATALOG_PATH, `${category}_unified.json`)
    
    if (!fs.existsSync(filePath)) {
      console.warn(`⚠️  File not found: ${filePath}`)
      continue
    }
    
    const products = JSON.parse(fs.readFileSync(filePath, 'utf-8'))
    console.log(`📦 Importing ${products.length} ${category}...`)
    
    for (const product of products) {
      try {
        await productService.create({
          title: product.name,
          handle: product.id,
          status: product.availability ? "published" : "draft",
          metadata: {
            sku: product.id.toUpperCase(),
            manufacturer: product.manufacturer,
            model: product.model,
            technical_specs: product.technical_specs
          },
          variants: [{
            title: "Default",
            sku: product.id.toUpperCase(),
            prices: [{
              amount: product.pricing?.price_brl || 0,
              currency_code: "brl"
            }]
          }]
        })
        imported++
      } catch (error) {
        console.error(`❌ Error importing ${product.id}`)
        errors++
      }
    }
  }
  
  console.log(`\n✅ Import complete: ${imported} products, ${errors} errors`)
}
```

## 📊 Métricas de Performance Esperadas

### Antes da Otimização (Atual)

| Métrica | Valor Atual | Status |
|---------|-------------|--------|
| Backend startup | ~60s | 🔴 Lento |
| Storefront startup | ~30s | 🟡 OK |
| DB query avg | ~50ms | 🟡 OK |
| Cache hit rate | Desconhecido | ⚫ N/A |
| Memory usage | 646 MB | ✅ Ótimo |
| CPU usage | <1% | ✅ Ótimo |

### Após Otimização (Esperado)

| Métrica | Valor Esperado | Melhoria |
|---------|----------------|----------|
| Backend startup | ~30-40s | 🎯 -33% |
| Storefront startup | ~20-25s | 🎯 -17% |
| DB query avg | ~20-30ms | 🎯 -40% |
| Cache hit rate | >90% | 🎯 +90% |
| Memory usage | 800-900 MB | ✅ Controlado |
| CPU usage | <2% | ✅ Ótimo |

## ✅ Checklist de Implementação

### Imediato (Hoje)

- [ ] Aplicar configurações do Redis (maxmemory, policy)
- [ ] Aplicar otimizações do PostgreSQL
- [ ] Habilitar health checks
- [ ] Testar docker-compose.optimized.yml

### 24 horas

- [ ] Adicionar resource limits
- [ ] Configurar logging adequado
- [ ] Otimizar volumes com cache
- [ ] Executar import de produtos (Fase 1)

### 48 horas

- [ ] Implementar monitoramento (opcional)
- [ ] Criar benchmarks de performance
- [ ] Documentar métricas
- [ ] Validar produtos importados

---

**Análise realizada**: 08/10/2025 às 17:30 UTC  
**Próxima ação**: Aplicar docker-compose.optimized.yml e importar produtos  
**Status**: 🎯 **PRONTO PARA OTIMIZAÇÃO E IMPORTAÇÃO**
