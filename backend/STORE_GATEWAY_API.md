# 🚀 YSH B2B Store - API Gateway

> Gateway unificado para acesso da loja com precificação dinâmica e comparação de distribuidores

## 📋 Visão Geral

O **YSH B2B Store API Gateway** consolida todos os endpoints necessários para operação da loja, integrando:

- ✅ **Catálogo de produtos** com 1.138 SKUs enriquecidos
- ✅ **Precificação dinâmica** com markup de 25% e margem líquida de 11%
- ✅ **Comparação entre distribuidores** com análise de variação de preços
- ✅ **Estatísticas por categoria** e análise de cobertura
- ✅ **Estratégia de pricing** com cenários e recomendações

---

## 🎯 Endpoints Disponíveis

### 1. Gateway Overview
```http
GET /store/gateway
```

**Descrição:** Retorna informações sobre o gateway, endpoints disponíveis e estatísticas gerais.

**Response:**
```json
{
  "name": "YSH B2B Store API Gateway",
  "version": "1.0.0",
  "status": "operational",
  "data": {
    "total_skus": 1138,
    "last_update": "2025-01-29T...",
    "cache_ttl": "300s"
  },
  "endpoints": { ... },
  "features": [ ... ],
  "pricing_info": {
    "avg_markup": "25%",
    "avg_gross_margin": "20%",
    "avg_net_margin": "11%"
  }
}
```

---

### 2. Lista de Produtos
```http
GET /store/gateway/products
```

**Descrição:** Lista produtos com precificação dinâmica e filtros avançados.

**Query Parameters:**
| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `category` | string | Filtrar por categoria | `kits`, `panels`, `inverters` |
| `manufacturer` | string | Filtrar por fabricante | `FOTUS`, `CANADIAN` |
| `min_price` | number | Preço mínimo | `1000` |
| `max_price` | number | Preço máximo | `10000` |
| `limit` | number | Resultados por página (max: 200) | `50` |
| `offset` | number | Offset para paginação | `0` |
| `sort` | string | Campo de ordenação | `price`, `margin`, `sku` |
| `order` | string | Ordem | `asc`, `desc` |
| `scenario` | string | Cenário de pricing | `neutro`, `agressivo`, `premium` |

**Response:**
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "sku": "FOTUSKP021704KWPCERAMICOKITS",
        "cost_price": 5324.30,
        "final_price": 6654.99,
        "pricing": {
          "base_markup": 28,
          "adjustment": -3,
          "final_markup": 25,
          "gross_margin": 20,
          "net_margin": 11,
          "scenario": "neutro"
        },
        "channel": {
          "channel": "b2c",
          "discount": 0,
          "channel_price": 6654.99
        },
        "features": {
          "charm_pricing": true,
          "has_adjustments": false
        },
        "images": [...],
        "project_splits": {...}
      }
    ],
    "count": 1138,
    "limit": 50,
    "offset": 0,
    "has_more": true,
    "stats": {
      "avg_price": 6543.21,
      "avg_margin": 11.0,
      "price_range": {
        "min": 180.00,
        "max": 35935.00
      }
    }
  },
  "query": {...},
  "timestamp": "2025-01-29T..."
}
```

---

### 3. Detalhes do Produto
```http
GET /store/gateway/products/:sku
```

**Descrição:** Retorna detalhes completos de um produto incluindo estratégia de precificação.

**Path Parameters:**
- `sku` (string, required): SKU do produto (ex: `FOTUSKP021704KWPCERAMICOKITS`)

**Response:**
```json
{
  "success": true,
  "data": {
    "sku": "FOTUSKP021704KWPCERAMICOKITS",
    "category": "kits",
    "cost_price": 5324.30,
    "final_price": 6654.99,
    "pricing_strategy": {
      "dynamic_markup": {
        "cost_price": 5324.30,
        "base_markup": 28,
        "adjustment": -3,
        "final_markup": 25,
        "selling_price": 6655.38,
        "gross_margin": 20,
        "net_margin": 11,
        "scenario": "neutro"
      },
      "adjustments": {
        "time": 0,
        "inventory": 0,
        "competition": 0,
        "segment": 0,
        "urgency": 0,
        "total": 0,
        "active": false
      },
      "channel_pricing": {
        "base_price": 6655.38,
        "channel": "b2c",
        "discount": 0,
        "channel_price": 6655.38
      },
      "psychological": {
        "charm_applied": true,
        "original_price": 6655.38,
        "charm_price": 6654.99
      }
    },
    "price_score": {
      "category": "average",
      "delta": 0,
      "best_price": 5324.30,
      "explanation": "Sem dados competitivos"
    },
    "project_splits": {...},
    "kpis": {...},
    "images": [...],
    "metadata": {...}
  }
}
```

---

### 4. Comparação de Preços
```http
GET /store/gateway/products/:sku/pricing
```

**Descrição:** Compara preços de um SKU entre diferentes distribuidores.

**Path Parameters:**
- `sku` (string, required): SKU do produto

**Response:**
```json
{
  "success": true,
  "data": {
    "sku": "FOTUSKP021704KWPCERAMICOKITS",
    "category": "kits",
    "manufacturer": "FOTUS",
    "comparison": {
      "total_offers": 3,
      "best_price": 5324.30,
      "worst_price": 6654.99,
      "average_price": 6000.00,
      "variation_pct": 25.0,
      "savings_potential": 1330.69
    },
    "offers": [
      {
        "distributor": "YSH Internal",
        "price": 5324.30,
        "source": "cost",
        "rank": 1,
        "is_best": true,
        "is_worst": false,
        "diff_from_best_pct": 0,
        "diff_from_avg_pct": -11.26
      },
      {
        "distributor": "YSH B2C",
        "price": 6654.99,
        "source": "final",
        "rank": 2,
        "is_best": false,
        "is_worst": true,
        "diff_from_best_pct": 25.0,
        "diff_from_avg_pct": 10.92
      }
    ],
    "recommendation": {
      "best_offer": {...},
      "savings": "20% ao escolher melhor oferta"
    }
  }
}
```

**Note:** Requer que o arquivo `distributor-price-comparison.json` tenha sido gerado previamente com o script `generate-distributor-price-comparison.js`.

---

### 5. Lista de Distribuidores
```http
GET /store/gateway/distributors
```

**Descrição:** Lista distribuidores com estatísticas de produtos e preços.

**Response:**
```json
{
  "success": true,
  "data": {
    "distributors": [
      {
        "name": "FOTUS",
        "total_products": 1138,
        "categories": ["kits", "panels", "inverters", "batteries"],
        "price_range": {
          "min": 180.00,
          "max": 35935.00,
          "avg": 6543.21
        },
        "margins": {
          "avg_net_margin": 11.0,
          "avg_gross_margin": 20.0
        }
      }
    ],
    "summary": {
      "total_distributors": 1,
      "total_products": 1138,
      "avg_products_per_distributor": 1138.0
    }
  }
}
```

---

### 6. Estatísticas de Categorias
```http
GET /store/gateway/categories
```

**Descrição:** Retorna estatísticas detalhadas por categoria de produto.

**Response:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "name": "kits",
        "total_products": 856,
        "price_range": {
          "min": 2500.00,
          "max": 35935.00,
          "avg": 8234.56
        },
        "margins": {
          "avg_net_margin": 11.0,
          "avg_gross_margin": 20.0
        },
        "coverage": {
          "with_images": 856,
          "image_coverage_pct": 100.0,
          "with_adjustments": 0,
          "adjustments_pct": 0.0
        }
      },
      {
        "name": "panels",
        "total_products": 150,
        "...": "..."
      }
    ],
    "summary": {
      "total_categories": 8,
      "total_products": 1138,
      "avg_products_per_category": 142.25
    }
  }
}
```

---

### 7. Estratégia de Precificação
```http
GET /store/gateway/pricing-strategy
```

**Descrição:** Análise completa da estratégia de precificação dinâmica com KPIs e recomendações.

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_products": 1138,
      "avg_final_markup": 25.0,
      "avg_gross_margin": 20.0,
      "avg_net_margin": 11.0,
      "with_charm_pricing": 1127,
      "charm_pricing_pct": 99.0,
      "with_adjustments": 0,
      "adjustments_pct": 0.0
    },
    "scenarios": {
      "analysis": [
        {
          "scenario": "neutro",
          "products": 1138,
          "percentage": 100.0,
          "avg_markup": 25.0,
          "avg_gross_margin": 20.0,
          "avg_net_margin": 11.0
        }
      ],
      "distribution": {
        "total_scenarios": 1,
        "most_used": "neutro"
      }
    },
    "price_positioning": {
      "competitive": 0,
      "average": 1138,
      "premium": 0,
      "distribution_pct": {
        "competitive": 0.0,
        "average": 100.0,
        "premium": 0.0
      }
    },
    "top_performers": {
      "highest_margin": [...],
      "lowest_margin": [...]
    },
    "dynamic_adjustments": {
      "usage": {
        "time": 0,
        "inventory": 0,
        "competition": 0,
        "segment": 0,
        "urgency": 0
      },
      "total_active": 0,
      "recommendations": [
        "Considere ativar ajustes dinâmicos para otimizar margens",
        "Implemente ajustes de inventário para produtos de baixo giro",
        "Configure ajustes de competição para produtos sensíveis a preço"
      ]
    },
    "recommendations": [
      "Ative ajustes dinâmicos para otimização automática",
      "Implemente múltiplos cenários (agressivo/premium) para segmentação"
    ]
  }
}
```

---

## 🏗️ Arquitetura

### Fonte de Dados
Todos os endpoints utilizam o arquivo `enriched-skus-for-dynamodb-images-fixed.json` como fonte de dados:

- **Total de SKUs:** 1.138 produtos
- **Cobertura de imagens:** 100%
- **Precificação dinâmica:** Ativa em todos os produtos
- **Cache:** 5 minutos (300s)

### Cache Strategy
```typescript
// Cache em memória
let enrichedCache: any = null;
let cacheTimestamp = 0;
const CACHE_TTL = 300000; // 5 minutos
```

### Categorias Suportadas
- `kits` - Kits completos de energia solar
- `panels` - Painéis fotovoltaicos
- `inverters` - Inversores solares
- `batteries` - Baterias e sistemas de armazenamento
- `structures` - Estruturas de fixação
- `cables` - Cabos e conectores
- `stringboxes` - String boxes
- `accessories` - Acessórios diversos

---

## 📊 Dados de Precificação

### Estrutura de Pricing
Cada produto contém:

```typescript
{
  dynamic_markup: {
    costPrice: number,
    baseMarkup: number,      // 28%
    adjustment: number,       // -3%
    finalMarkup: number,      // 25%
    sellingPrice: number,
    grossMargin: number,      // 20%
    netMargin: number,        // 11%
    scenario: "neutro" | "agressivo" | "premium"
  },
  dynamic_adjustments: {
    time_adjustment: number,
    inventory_adjustment: number,
    competition_adjustment: number,
    segment_adjustment: number,
    urgency_adjustment: number,
    total_adjustment: number
  },
  channel_pricing: {
    basePrice: number,
    channel: "b2c" | "b2b",
    discount: number,
    channelPrice: number,
    commission: number
  },
  psychological_pricing: {
    charm_applied: boolean
  }
}
```

### KPIs Atuais
- **Markup Médio:** 25%
- **Margem Bruta:** 20%
- **Margem Líquida:** 11%
- **Charm Pricing:** 99% de adoção
- **Ajustes Dinâmicos:** 0% (oportunidade de otimização)

---

## 🔧 Como Usar

### 1. Listar Produtos Filtrados
```bash
# Listar kits com preço entre R$ 5.000 e R$ 10.000
curl "http://localhost:9000/store/gateway/products?category=kits&min_price=5000&max_price=10000&limit=20"
```

### 2. Obter Detalhes de um Produto
```bash
# Detalhes completos do SKU
curl "http://localhost:9000/store/gateway/products/FOTUSKP021704KWPCERAMICOKITS"
```

### 3. Comparar Preços entre Distribuidores
```bash
# Comparação de preços
curl "http://localhost:9000/store/gateway/products/FOTUSKP021704KWPCERAMICOKITS/pricing"
```

### 4. Ver Estratégia de Pricing
```bash
# Análise completa da estratégia
curl "http://localhost:9000/store/gateway/pricing-strategy"
```

---

## 🚨 Notas Importantes

### Pré-requisitos
1. **Arquivo de dados enriquecidos:**
   ```
   backend/enriched-skus-for-dynamodb-images-fixed.json
   ```

2. **Arquivo de comparação de preços (opcional):**
   ```bash
   # Gerar comparação antes de usar endpoint /pricing
   node scripts/generate-distributor-price-comparison.js
   ```

### Limitações
- **Paginação máxima:** 200 produtos por request
- **Cache TTL:** 5 minutos
- **Comparação de preços:** Requer arquivo JSON pré-gerado

### Recomendações
1. ✅ **Ativar ajustes dinâmicos** para otimização automática de margens
2. ✅ **Implementar cenários múltiplos** (agressivo/premium) para segmentação
3. ✅ **Aumentar charm pricing** para 100% de adoção
4. ✅ **Monitorar produtos com baixa margem** e ajustar markup

---

## 📝 Exemplos de Integração

### React/Next.js
```typescript
// Listar produtos
const response = await fetch('/store/gateway/products?category=kits&limit=50');
const { data } = await response.json();

// Detalhes do produto
const product = await fetch(`/store/gateway/products/${sku}`);
const { data: productData } = await product.json();
```

### TypeScript Types
```typescript
interface Product {
  sku: string;
  cost_price: number;
  final_price: number;
  pricing: {
    base_markup: number;
    adjustment: number;
    final_markup: number;
    gross_margin: number;
    net_margin: number;
    scenario: string;
  };
  channel: {
    channel: string;
    discount: number;
    channel_price: number;
  };
  features: {
    charm_pricing: boolean;
    has_adjustments: boolean;
  };
  images: string[];
  project_splits: any;
}
```

---

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique os logs do servidor: `console.log('[Gateway] ...')`
- Confirme que o arquivo `enriched-skus-for-dynamodb-images-fixed.json` existe
- Execute `generate-distributor-price-comparison.js` se usar endpoint `/pricing`

---

## ✅ Status

| Endpoint | Status | Cache | Dependências |
|----------|--------|-------|--------------|
| `/store/gateway` | ✅ Operacional | 5min | `enriched-skus-*.json` |
| `/store/gateway/products` | ✅ Operacional | 5min | `enriched-skus-*.json` |
| `/store/gateway/products/:sku` | ✅ Operacional | 5min | `enriched-skus-*.json` |
| `/store/gateway/products/:sku/pricing` | ✅ Operacional | - | `distributor-price-comparison.json` |
| `/store/gateway/distributors` | ✅ Operacional | 5min | `enriched-skus-*.json` |
| `/store/gateway/categories` | ✅ Operacional | 5min | `enriched-skus-*.json` |
| `/store/gateway/pricing-strategy` | ✅ Operacional | 5min | `enriched-skus-*.json` |

**Última atualização:** 29/10/2025
