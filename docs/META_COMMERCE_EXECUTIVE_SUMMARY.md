# Meta Commerce Platform Integration - Executive Summary

## 🎯 Visão Geral

Integração de alta performance entre o inventário YSH B2B (2.914 produtos fotovoltaicos) e a Meta Commerce Platform (Facebook Shops & Instagram Shopping), usando padrões Meta como referência core em substituição ao Medusa.js.

---

## 📊 Números do Projeto

### Inventário YSH

- **2.914** produtos base
- **16.532** SKUs totais (com variantes)
- **7** categorias de produtos
- **32** fabricantes
- **5** distribuidores ativos

### Cobertura da Integração

- **100%** dos produtos mapeados para Meta Catalog
- **99%+** de precisão de inventário
- **< 0.5%** taxa de sobrevenda alvo
- **< 5s** latência de Batch API (p95)

---

## 🏗️ Arquitetura de Integração

```tsx
┌─────────────────────────────────────────────────────────┐
│                YSH B2B Platform                          │
│                                                          │
│  Inventory    Catalog       Orders                      │
│  Manager  →   Manager   →   Manager                     │
│     │            │              │                        │
│     └────────────┼──────────────┘                        │
│                  │                                       │
│         Meta Commerce Integration Layer                 │
│  ┌───────────────┼────────────────────────┐             │
│  │   Catalog Sync   Inventory Sync   Orders│             │
│  └───────────────┼────────────────────────┘             │
└──────────────────┼──────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  Meta Commerce API   │
        │  (Graph API v18.0)   │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ Facebook Shops &     │
        │ Instagram Shopping   │
        └──────────────────────┘
```

### Componentes Principais

#### 1. **Catalog Sync** (Sincronização de Catálogo)

- **Feed API**: Sincronização programada (diária)
- **Batch API**: Atualizações em tempo real
- **Mapeamento**: YSH Schema → Meta Product Schema

#### 2. **Inventory Sync** (Sincronização de Inventário)

- **Real-time updates**: Batch API para produtos de alta rotação
- **Scheduled updates**: Feed API para produtos regulares
- **Anti-overselling**: Pré-alocação + buffers dinâmicos

#### 3. **Order Management** (Gestão de Pedidos)

- **Webhooks**: Recebimento de pedidos Meta
- **Acknowledgement**: Confirmação automática ou manual (B2B approvals)
- **Fulfillment**: Envio e tracking

---

## 🔄 Fluxos Principais

### Fluxo 1: Sincronização de Produto

```tsx
YSH Product Created/Updated
           │
           ▼
    Product Transformer
    (YSH → Meta Schema)
           │
           ▼
  ┌────────┴────────┐
  │                 │
  ▼                 ▼
Feed API        Batch API
(Scheduled)    (Real-time)
  │                 │
  └────────┬────────┘
           ▼
    Meta Catalog
           │
           ▼
 Facebook/Instagram
     Surfaces
```

### Fluxo 2: Pedido de Cliente

```tsx
Customer Places Order
(Facebook/Instagram)
           │
           ▼
    Webhook Received
    (orders.created)
           │
           ▼
  Create YSH Order
           │
           ▼
  ┌────────┴────────┐
  │   B2B Approval  │
  │     Needed?     │
  └────────┬────────┘
           │
     ┌─────┴─────┐
     │           │
    Yes          No
     │           │
     ▼           ▼
  Wait for   Acknowledge
  Approval   Immediately
     │           │
     └─────┬─────┘
           ▼
     Process Order
           │
           ▼
    Send Shipment
    (Fulfillment)
```

### Fluxo 3: Atualização de Inventário

```tsx
Inventory Changed
(Order, Restock, Admin)
           │
           ▼
  Calculate Meta Quantity
  (Pre-allocation + Buffer)
           │
           ▼
    Batch API Update
    (Real-time < 5s)
           │
           ▼
    Meta Inventory
      Synchronized
           │
           ▼
  Displayed on Facebook/
    Instagram Shops
```

---

## 🗺️ Mapeamento de Dados

### Produto YSH → Meta Product Schema

| Campo YSH | Campo Meta | Transformação |
|-----------|------------|---------------|
| `id` / `external_id` | `id` (retailer_id) | Direto |
| `name` | `title` | Direto |
| `description` | `description` + `rich_text_description` | Enriquecido com specs |
| `status` | `availability` | `published` → `in stock` |
| `price.amount` | `price` | `7850.00 BRL` |
| `images[0]` | `image_link` | URL principal |
| `images[1..n]` | `additional_image_link` | Galeria |
| `manufacturer.name` | `brand` | Direto |
| `category` | `google_product_category` | Mapeamento fixo |
| `inventory.quantity` | `quantity_to_sell_on_fb` | Com pré-alocação + buffer |
| `product_base_id` | `item_group_id` | Agrupamento de variantes |

### Categorias YSH → Google Product Categories

| Categoria YSH | Google Product Category |
|---------------|-------------------------|
| Kits Solares | Electronics > Power > Power Inverters |
| Painéis Solares | Electronics > Solar Energy Equipment > Solar Panels |
| Inversores | Electronics > Power > Power Inverters |
| Baterias | Electronics > Power > Batteries |
| Estruturas | Hardware > Hardware Accessories > Mounting Hardware |
| Cabos | Electronics > Electronics Accessories > Cables |
| Acessórios | Electronics > Electronics Accessories |

---

## 🛡️ Estratégias Anti-Sobrevenda

### 1. **Pré-Alocação por Canal**

```tsx
Total Inventory: 100 units
├─ Facebook/Instagram: 30 units (30%)
├─ B2B Website: 50 units (50%)
└─ Other Marketplaces: 20 units (20%)
```

### 2. **Buffers Dinâmicos**

```tsx
High Velocity Products (>50 sales/month):
  Buffer: 20% → Display 80% of allocated

Medium Velocity (10-50 sales/month):
  Buffer: 10% → Display 90% of allocated

Low Velocity (<10 sales/month):
  Buffer: 5% → Display 95% of allocated
```

### 3. **Ciclo de Vida do Inventário**

```tsx
Inventário Disponível = Inventário Fornecido - Pedidos Não Confirmados

Order Created → Reduce "Available" (cache)
Order Confirmed (30 min) → Remove from counter
Order Canceled → Restore "Provided" (if restock=true)
```

---

## 🔐 Autenticação & Segurança

### Setup de Autenticação

1. **Criar Developer App** no Meta for Developers
2. **Criar System User** no Business Manager
3. **Atribuir Assets**:
   - App (API Access)
   - Commerce Account
   - Facebook Page
   - Product Catalog
4. **Gerar Access Token** com permissões:
   - `catalog_management`
   - `business_management`
   - `commerce_manage_accounts`
   - `commerce_account_manage_orders`
   - `commerce_account_read_reports`

### Segurança

- ✅ Access tokens em secrets manager
- ✅ Rotação automática a cada 60 dias
- ✅ Rate limiting: 200 req/min
- ✅ Logs com PII mascarado
- ✅ HTTPS apenas

---

## 📈 KPIs & Métricas

### Performance

| Métrica | Alvo |
|---------|------|
| Latency Batch API | < 5s (p95) |
| Feed Upload Time | < 30 min (catálogo completo) |
| Order Acknowledgement | < 2 min após webhook |

### Acurácia

| Métrica | Alvo |
|---------|------|
| Precisão de Inventário | > 99% |
| Taxa de Sobrevenda | < 0.5% |
| Mapeamento de Produtos | 100% |

### Business

| Métrica | Alvo |
|---------|------|
| Taxa de Conversão | > 2% |
| Ticket Médio | > R$ 5.000 |
| Taxa de Cancelamento | < 3% |
| NPS | > 8.0 |

---

## 🚀 Roadmap de Implementação

### Fase 1: Setup & Autenticação (Semana 1-2)

- ✅ Criar Developer App
- ✅ Configurar System User
- ✅ Gerar access tokens
- ✅ Testes de autenticação

### Fase 2: Mapeamento de Catálogo (Semana 3-4)

- 🔄 Implementar Product Transformer
- 🔄 Mapear categorias YSH → Google
- 🔄 Sistema de variantes
- 🔄 Feed CSV de teste

### Fase 3: Sincronização de Inventário (Semana 5-6)

- ⏳ Feed API Service
- ⏳ Batch API Service
- ⏳ Workflows de sincronização
- ⏳ Estratégias anti-sobrevenda

### Fase 4: Gestão de Pedidos (Semana 7-8)

- ⏳ Order Acknowledgement API
- ⏳ Order Fulfillment API
- ⏳ Webhooks de pedidos
- ⏳ Integração com aprovações B2B

### Fase 5: Checkout URL (Semana 9)

- ⏳ Rota `/checkout/meta-commerce`
- ⏳ Parser de produtos URL
- ⏳ Aplicação de cupons
- ⏳ Tracking UTM

### Fase 6: Testes & Go-Live (Semana 10-12)

- ⏳ Testes end-to-end
- ⏳ Testes de carga
- ⏳ App Review
- ⏳ Deploy gradual

---

## 📚 Documentação

### Documentos do Projeto

- **[Blueprint Completo](../docs/META_COMMERCE_INTEGRATION_BLUEPRINT.md)**: Arquitetura detalhada de integração
- **[Module README](../backend/src/meta-commerce/README.md)**: Guia de desenvolvimento do módulo
- **[Inventory Blueprint 360º](../backend/data/products-inventory/INVENTORY_BLUEPRINT_360.md)**: Análise completa do inventário YSH

### Recursos Meta

- [Commerce Platform Overview](https://developers.facebook.com/docs/commerce-platform)
- [Catalog & Inventory Guide](https://developers.facebook.com/docs/commerce-platform/catalog)
- [Batch API Reference](https://developers.facebook.com/docs/commerce-platform/catalog/batch-api)
- [Order Management API](https://developers.facebook.com/docs/commerce-platform/order-management)

---

## 👥 Equipe & Contatos

**Tech Lead**: fernando@yellosolarhub.com  
**Meta Developer Support**: https://developers.facebook.com/support  
**Business Manager**: [YSH Business Manager ID]  

---

## ✨ Próximos Passos

1. **Imediato**: Criar Developer App no Meta for Developers
2. **Esta Semana**: Configurar System User e access tokens
3. **Próxima Semana**: Iniciar implementação do Product Transformer
4. **Este Mês**: Primeira sincronização de teste com 100 produtos

---

**Versão**: 1.0.0  
**Data**: 2025-01-13  
**Status**: ✅ Blueprint Completo - Pronto para Implementação  

> 💡 **Nota**: Este documento é um resumo executivo. Para detalhes técnicos completos, consulte o [Blueprint de Integração](../docs/META_COMMERCE_INTEGRATION_BLUEPRINT.md).
