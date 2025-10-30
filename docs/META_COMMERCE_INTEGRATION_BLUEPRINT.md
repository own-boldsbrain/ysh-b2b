# Meta Commerce Platform - Blueprint de Integração YSH B2B

## Arquitetura de Alta Performance & Acurácia

> **Status**: Design Phase  
> **Data**: 2025-01-13  
> **Versão**: 1.0.0  
> **Core Reference**: Meta Commerce Platform Standards  

---

## 📋 Sumário Executivo

Este blueprint define a arquitetura de integração entre o inventário YSH (2.914 produtos base, 16.532 SKUs) e a Meta Commerce Platform, usando padrões Meta como referência core em substituição ao Medusa.js.

### Objetivos Estratégicos

1. **Alta Performance**: Batch API para atualizações em tempo real + Feed API para sincronizações programadas
2. **Acurácia Máxima**: Mapeamento preciso de 7 categorias de produtos fotovoltaicos para Google Product Categories
3. **Escalabilidade**: Suporte para 32 fabricantes e 5 distribuidores
4. **Redução de Sobrevenda**: Estratégias de inventário pré-alocado e limitações dinâmicas

---

## 🏗️ Arquitetura de Integração

### Visão Geral do Sistema

```tsx
┌─────────────────────────────────────────────────────────────────┐
│                    YSH B2B Platform (Backend)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Inventory   │  │   Catalog    │  │   Orders     │          │
│  │   Manager     │  │   Manager    │  │   Manager    │          │
│  └───────┬──────┘  └───────┬──────┘  └───────┬──────┘          │
│          │                  │                  │                  │
│  ┌───────▼──────────────────▼──────────────────▼──────┐         │
│  │         Meta Commerce Integration Layer            │         │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │         │
│  │  │   Catalog  │  │ Inventory  │  │   Orders   │   │         │
│  │  │   Sync     │  │   Sync     │  │   Sync     │   │         │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘   │         │
│  └────────┼───────────────┼───────────────┼──────────┘         │
└───────────┼───────────────┼───────────────┼────────────────────┘
            │               │               │
            ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Meta Commerce Platform (Graph API)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Batch API  │  │   Feed API   │  │  Order Mgmt  │          │
│  │  (Real-time) │  │  (Scheduled) │  │     APIs     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Product    │  │   Inventory  │  │   Orders     │          │
│  │   Catalog    │  │   Tracking   │  │  Lifecycle   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Facebook Shops & Instagram  │
        │        Shopping Surfaces      │
        └───────────────────────────────┘
```

---

## 🔐 Autenticação & Autorização

### Arquitetura de Autenticação

```tsx
┌─────────────────────────────────────────────────────┐
│           Business Manager (YSH)                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  System User │  │  Facebook App│                │
│  │  (API Token) │◄─┤  (OAuth)     │                │
│  └──────┬───────┘  └──────────────┘                │
│         │                                            │
│  ┌──────▼───────────────────────────────┐          │
│  │         Assigned Assets:             │          │
│  │  • App (API Access)                  │          │
│  │  • Commerce Account (Test & Prod)    │          │
│  │  • Facebook Page                     │          │
│  │  • Product Catalog                   │          │
│  └──────────────────────────────────────┘          │
└─────────────────────────────────────────────────────┘
```

### Configuração Step-by-Step

#### 1. Criar Developer App

```bash
# Meta for Developers Console
1. Acesse: https://developers.facebook.com/apps
2. Criar App → Type: Business
3. Nome: "YSH B2B Commerce Integration"
4. Salvar App ID e App Secret
```

#### 2. Criar System User

```bash
# Business Manager → Business Settings → Users → System Users
1. Criar System User: "ysh-commerce-api"
2. Role: Admin
3. Gerar Access Token com permissões:
   - catalog_management
   - business_management
   - commerce_manage_accounts
   - commerce_account_manage_orders
   - commerce_account_read_reports
```

#### 3. Atribuir Assets

```typescript
// backend/src/config/meta-commerce.config.ts
export const MetaCommerceConfig = {
  app: {
    id: process.env.META_APP_ID,
    secret: process.env.META_APP_SECRET,
  },
  systemUser: {
    id: process.env.META_SYSTEM_USER_ID,
    accessToken: process.env.META_SYSTEM_USER_TOKEN,
  },
  commerce: {
    accountId: process.env.META_COMMERCE_ACCOUNT_ID,
    catalogId: process.env.META_CATALOG_ID,
    pageId: process.env.META_PAGE_ID,
  },
  api: {
    baseUrl: 'https://graph.facebook.com/v18.0',
    timeout: 30000,
    retryAttempts: 3,
  }
};
```

---

## 📦 Mapeamento de Catálogo

### YSH Categories → Meta Product Schema

#### Campos Obrigatórios (Universal)

| Campo Meta | Campo YSH | Transformação | Exemplo |
|-----------|-----------|---------------|---------|
| `id` | `retailer_id` | SKU único | `"NEO-INV-DEYE-SUN-8K-SG04LP3-EU"` |
| `title` | `name` | Nome comercial | `"Inversor Deye SUN-8K-SG04LP3-EU"` |
| `description` | `description` | Descrição comercial + specs | `"Inversor híbrido 8kW..."` |
| `availability` | `status` | Mapeamento: `published` → `in stock` | `"in stock"` |
| `condition` | - | Sempre `new` | `"new"` |
| `price` | `price.amount` | Converter para `{valor} {moeda}` | `"7850.00 BRL"` |
| `link` | `storefront_url` | URL produto storefront | `"https://ysh.com.br/products/inv-deye-sun-8k"` |
| `image_link` | `images[0].url` | URL imagem principal | `"https://cdn.ysh.com.br/inv-deye-8k.jpg"` |
| `brand` | `manufacturer.name` | Nome fabricante | `"Deye"` |
| `google_product_category` | `category` | Mapeamento fixo (ver tabela) | `"Electronics > Power"` |

#### Campos Obrigatórios (Checkout Facebook/Instagram - US)

| Campo Meta | Campo YSH | Nota |
|-----------|-----------|------|
| `quantity_to_sell_on_fb` | `inventory.quantity` | Substituir `inventory` (deprecated) |
| `checkout_url` | - | URL backend checkout: `https://ysh.com.br/checkout` |

#### Campos Opcionais Recomendados

| Campo Meta | Campo YSH | Benefício |
|-----------|-----------|-----------|
| `additional_image_link` | `images[1..n].url` | Galeria de imagens |
| `sale_price` | `promotional_price` | Preço promocional |
| `sale_price_effective_date` | `promotion_period` | Período da promoção |
| `item_group_id` | `product_base_id` | Agrupar variantes |
| `color` | `variants.color` | Filtro de variantes |
| `size` | `variants.power_rating` | Ex: "8kW", "10kW" |
| `rich_text_description` | `description_html` | HTML formatado |
| `custom_label_0` | `category` | "Inversor", "Painel", etc |
| `custom_label_1` | `manufacturer.name` | "Deye", "DAH Solar" |
| `custom_label_2` | `distributor.name` | "Neosolar", "Fortlev" |
| `custom_label_3` | `technology` | "Híbrido", "On-Grid" |
| `custom_label_4` | `series` | "SUN-K-SG", "DHN-Series" |

### Mapeamento de Categorias YSH → Google Product Categories

```typescript
// backend/src/meta-commerce/mappings/categories.ts
export const YSH_TO_GOOGLE_CATEGORIES: Record<string, string> = {
  // Categoria YSH → Google Product Category ID
  'kits-solares': 'Electronics > Power > Power Inverters',
  'paineis-solares': 'Electronics > Solar Energy Equipment > Solar Panels',
  'inversores': 'Electronics > Power > Power Inverters',
  'baterias': 'Electronics > Power > Batteries',
  'estruturas': 'Hardware > Hardware Accessories > Mounting Hardware',
  'cabos': 'Electronics > Electronics Accessories > Cables',
  'acessorios': 'Electronics > Electronics Accessories',
};
```

### Sistema de Variantes

Meta Commerce usa `item_group_id` para agrupar variantes:

```json
{
  "requests": [
    {
      "method": "CREATE",
      "retailer_id": "NEO-INV-DEYE-SUN-8K-BASE",
      "data": {
        "item_group_id": "DEYE-SUN-K-SG-SERIES",
        "title": "Inversor Deye SUN-K-SG",
        "size": "8kW",
        "color": "Standard",
        "price": "7850.00 BRL",
        "quantity_to_sell_on_fb": 45
      }
    },
    {
      "method": "CREATE",
      "retailer_id": "NEO-INV-DEYE-SUN-10K-BASE",
      "data": {
        "item_group_id": "DEYE-SUN-K-SG-SERIES",
        "title": "Inversor Deye SUN-K-SG",
        "size": "10kW",
        "color": "Standard",
        "price": "9200.00 BRL",
        "quantity_to_sell_on_fb": 32
      }
    }
  ]
}
```

**Estratégia YSH**:

- 2.914 produtos base → `item_group_id`
- 16.532 SKUs totais → produtos individuais com `item_group_id` apontando para base
- Usar `size` para potência (8kW, 10kW, 550W, etc)
- Usar `color` para variações visuais (se aplicável)
- `additional_variant_attribute` para specs técnicas (tensão, corrente, etc)

---

## 🔄 Sincronização de Inventário

### Arquitetura Dual-Mode

#### 1. Feed API (Scheduled) - Produtos de Venda Lenta

**Quando usar**: Produtos com alta disponibilidade, vendas previsíveis

```typescript
// backend/src/meta-commerce/services/feed-sync.service.ts
export class FeedSyncService {
  async scheduledFullSync(): Promise<void> {
    // Executar diariamente às 3h AM
    const products = await this.getProductsForFullSync();
    
    const feed = {
      version: '1.0',
      items: products.map(p => ({
        id: p.retailer_id,
        title: p.name,
        description: p.description,
        availability: this.mapAvailability(p.status),
        condition: 'new',
        price: `${p.price.amount} ${p.price.currency}`,
        link: `https://ysh.com.br/products/${p.handle}`,
        image_link: p.images[0]?.url,
        brand: p.manufacturer.name,
        google_product_category: YSH_TO_GOOGLE_CATEGORIES[p.category],
        quantity_to_sell_on_fb: p.inventory.quantity,
        // Omitir campos voláteis como 'quantity_to_sell_on_fb'
        // para gerenciar via Batch API
        ...this.getOptionalFields(p),
      })),
    };
    
    await this.uploadFeed(feed);
  }
}
```

**Formato CSV**:

```csv
id,title,description,availability,condition,price,link,image_link,brand,google_product_category,item_group_id,size,custom_label_0,custom_label_1
NEO-INV-DEYE-SUN-8K,Inversor Deye SUN-8K-SG04LP3-EU,Inversor híbrido 8kW com backup,in stock,new,7850.00 BRL,https://ysh.com.br/products/inv-deye-sun-8k,https://cdn.ysh.com.br/inv-deye-8k.jpg,Deye,Electronics > Power > Power Inverters,DEYE-SUN-K-SG-SERIES,8kW,Inversor,Deye
```

**Frequência**:

- Produtos regulares: 1x dia (3h AM)
- Produtos com promoções: 6x dia (a cada 4h)

#### 2. Batch API (Real-time) - Produtos de Venda Rápida

**Quando usar**: Produtos com baixo estoque, alto giro, inventário compartilhado

```typescript
// backend/src/meta-commerce/services/batch-sync.service.ts
export class BatchSyncService {
  async updateInventoryRealtime(updates: InventoryUpdate[]): Promise<void> {
    const batchRequest = {
      access_token: MetaCommerceConfig.systemUser.accessToken,
      item_type: 'PRODUCT_ITEM',
      requests: updates.map(u => ({
        method: 'UPDATE',
        retailer_id: u.sku,
        data: {
          quantity_to_sell_on_fb: u.quantity,
          availability: u.quantity > 0 ? 'in stock' : 'out of stock',
        }
      }))
    };
    
    const response = await this.postBatch(batchRequest);
    await this.checkBatchStatus(response.handle);
  }
  
  async postBatch(request: BatchRequest): Promise<BatchResponse> {
    const url = `${MetaCommerceConfig.api.baseUrl}/${MetaCommerceConfig.commerce.catalogId}/batch`;
    return axios.post(url, request);
  }
  
  async checkBatchStatus(handle: string): Promise<void> {
    const url = `${MetaCommerceConfig.api.baseUrl}/${MetaCommerceConfig.commerce.catalogId}/check_batch_request_status`;
    const response = await axios.get(url, {
      params: { handle }
    });
    
    if (response.data.status === 'ERROR') {
      throw new Error(`Batch failed: ${response.data.errors}`);
    }
  }
}
```

**Triggers de Sincronização em Tempo Real**:

```typescript
// backend/src/workflows/hooks/inventory-changed.ts
export const inventoryChangedHook = createStep(
  'inventory-changed-meta-sync',
  async ({ product_id, new_quantity }) => {
    const batchService = new BatchSyncService();
    
    await batchService.updateInventoryRealtime([
      {
        sku: product_id,
        quantity: new_quantity,
      }
    ]);
    
    return new StepResponse({ synced: true });
  }
);
```

**Gatilhos**:

- Pedido confirmado → Reduzir estoque
- Pedido cancelado → Restaurar estoque (se `restock_items: true`)
- Admin atualiza inventário → Sincronizar imediatamente
- Webhook de distribuidor → Atualizar disponibilidade

### Estratégias Anti-Sobrevenda

#### 1. Inventário Pré-Alocado

```typescript
// backend/src/meta-commerce/strategies/pre-allocated-inventory.ts
export class PreAllocatedInventoryStrategy {
  async allocateInventory(product: Product): Promise<number> {
    const totalInventory = product.inventory.quantity;
    const channelAllocation = {
      'facebook_instagram': 0.30, // 30% para Meta
      'website_b2b': 0.50,         // 50% para B2B direto
      'marketplace': 0.20,         // 20% para outros
    };
    
    return Math.floor(totalInventory * channelAllocation['facebook_instagram']);
  }
}
```

#### 2. Limitações Dinâmicas

```typescript
// backend/src/meta-commerce/strategies/dynamic-limits.ts
export class DynamicLimitsStrategy {
  async applyBuffer(product: Product): Promise<number> {
    const velocity = await this.calculateSalesVelocity(product.id);
    
    if (velocity === 'high') {
      // Produtos de venda rápida: buffer de 20%
      return Math.floor(product.inventory.quantity * 0.80);
    } else if (velocity === 'medium') {
      // Produtos médios: buffer de 10%
      return Math.floor(product.inventory.quantity * 0.90);
    } else {
      // Produtos lentos: buffer de 5%
      return Math.floor(product.inventory.quantity * 0.95);
    }
  }
  
  async calculateSalesVelocity(productId: string): Promise<'high' | 'medium' | 'low'> {
    const sales = await this.getSalesLast30Days(productId);
    if (sales > 50) return 'high';
    if (sales > 10) return 'medium';
    return 'low';
  }
}
```

#### 3. Ciclo de Vida do Inventário

```tsx
Inventário Disponível = Inventário Fornecido - Pedidos Não Confirmados

┌─────────────────────────────────────────────────────────┐
│ Pedido Criado → Reduz "Inventário Disponível" (cache)  │
│ Pedido Confirmado (30 min) → Remove do balcão          │
│ Pedido Cancelado → Restaura "Inventário Fornecido"     │
└─────────────────────────────────────────────────────────┘
```

---

## 🛒 Gestão de Pedidos

### Fluxo de Ordem (Order Lifecycle)

```tsx
┌─────────────────────────────────────────────────────────────┐
│              Facebook/Instagram Checkout                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  Order Created  │ ◄── Webhook: orders.created
        │   (CREATED)     │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ YSH Backend     │
        │ Acknowledges    │ ──► POST /{order_id}/acknowledge
        │   (IN_PROGRESS) │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Order Approved  │
        │ (B2B Workflow)  │ ◄── Approval Module valida limite
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ YSH Fulfills    │ ──► POST /{order_id}/shipments
        │  (FULFILLED)    │      { tracking_number, carrier }
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Order Completed │
        │  (COMPLETED)    │
        └─────────────────┘
```

### APIs de Gestão de Pedidos

#### 1. Order Acknowledgement API

```typescript
// backend/src/meta-commerce/services/order-acknowledgement.service.ts
export class OrderAcknowledgementService {
  async acknowledgeOrder(orderId: string): Promise<void> {
    // Após receber webhook orders.created
    const url = `${MetaCommerceConfig.api.baseUrl}/${orderId}/acknowledge`;
    
    await axios.post(url, {
      access_token: MetaCommerceConfig.systemUser.accessToken,
    });
    
    // Move ordem de CREATED → IN_PROGRESS
  }
}
```

#### 2. Order Fulfillment API

```typescript
// backend/src/meta-commerce/services/order-fulfillment.service.ts
export class OrderFulfillmentService {
  async createShipment(orderId: string, fulfillment: FulfillmentData): Promise<void> {
    const url = `${MetaCommerceConfig.api.baseUrl}/${orderId}/shipments`;
    
    await axios.post(url, {
      access_token: MetaCommerceConfig.systemUser.accessToken,
      items: fulfillment.items.map(i => ({
        retailer_id: i.sku,
        quantity: i.quantity,
      })),
      tracking_info: {
        tracking_number: fulfillment.trackingNumber,
        carrier: fulfillment.carrier, // 'correios', 'jamef', etc
      },
      shipment_origin_postal_code: fulfillment.originZipCode,
    });
  }
}
```

#### 3. Order Cancellation API

```typescript
// backend/src/meta-commerce/services/order-cancellation.service.ts
export class OrderCancellationService {
  async cancelOrder(orderId: string, reason: CancellationReason): Promise<void> {
    const url = `${MetaCommerceConfig.api.baseUrl}/${orderId}/cancellations`;
    
    await axios.post(url, {
      access_token: MetaCommerceConfig.systemUser.accessToken,
      cancel_reason: {
        reason_code: this.mapReasonCode(reason),
        reason_description: reason.description,
      },
      restock_items: reason.shouldRestock, // true para OUT_OF_STOCK
    });
  }
  
  mapReasonCode(reason: CancellationReason): string {
    // OUT_OF_STOCK, CUSTOMER_REQUESTED, FRAUDULENT_ORDER, etc
    const mapping = {
      'sobrevenda': 'OUT_OF_STOCK',
      'cliente_solicitou': 'CUSTOMER_REQUESTED',
      'fraude': 'FRAUDULENT_ORDER',
      'produto_descontinuado': 'NO_LONGER_AVAILABLE',
    };
    return mapping[reason.type] || 'UNKNOWN';
  }
}
```

### Webhooks Configuration

```typescript
// backend/src/meta-commerce/webhooks/orders.webhook.ts
export class OrdersWebhook {
  @Post('/webhooks/meta-commerce/orders')
  async handleOrderWebhook(@Body() payload: MetaWebhookPayload) {
    const event = payload.entry[0].changes[0];
    
    switch (event.field) {
      case 'orders.created':
        await this.handleOrderCreated(event.value);
        break;
      case 'orders.updated':
        await this.handleOrderUpdated(event.value);
        break;
      case 'orders.canceled':
        await this.handleOrderCanceled(event.value);
        break;
    }
  }
  
  async handleOrderCreated(order: MetaOrder): Promise<void> {
    // 1. Criar ordem no sistema YSH
    const yshOrder = await createOrdersWorkflow.run({
      input: this.mapMetaOrderToYsh(order),
      container: this.container,
    });
    
    // 2. Verificar aprovações B2B
    const needsApproval = await this.checkApprovalNeeded(yshOrder);
    
    if (!needsApproval) {
      // 3. Acknowledge automaticamente
      await this.acknowledgementService.acknowledgeOrder(order.id);
    } else {
      // 3. Aguardar aprovação manual
      await this.notifyApprovers(yshOrder);
    }
  }
}
```

---

## 🔗 Checkout URL Configuration

### Arquitetura de Checkout

```tsx
Facebook/Instagram Cart
       │
       │ User clicks "Buy"
       ▼
┌─────────────────────────────────────────────────────┐
│  Checkout URL:                                       │
│  https://ysh.com.br/checkout                        │
│  ?products=SKU1%3A2%2CSKU2%3A1                      │
│  &coupon=SOLAR2025                                  │
│  &cart_origin=instagram                             │
│  &utm_source=IGShopping&utm_medium=Social           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  YSH Storefront (Next.js)                           │
│  /checkout/meta-commerce                            │
│                                                      │
│  1. Parse URL params                                │
│  2. Create cart with products                       │
│  3. Apply coupon                                    │
│  4. Render checkout page                            │
│  5. Process payment & fulfillment                   │
└─────────────────────────────────────────────────────┘
```

### Implementação Next.js

```typescript
// storefront/src/app/[countryCode]/(checkout)/checkout/meta-commerce/page.tsx
export default async function MetaCommerceCheckoutPage({
  searchParams,
}: {
  searchParams: { 
    products?: string;
    coupon?: string;
    cart_origin?: string;
    utm_source?: string;
    utm_medium?: string;
  };
}) {
  // 1. Parse products (format: "SKU1:qty1,SKU2:qty2")
  const products = parseProductsParam(searchParams.products);
  // Exemplo: "NEO-INV-DEYE-8K%3A2%2CNEO-PAINEL-DAH-550W%3A10"
  // → [{ sku: "NEO-INV-DEYE-8K", quantity: 2 }, { sku: "NEO-PAINEL-DAH-550W", quantity: 10 }]
  
  // 2. Create cart
  const cart = await createCart({
    region_id: await getRegionId(countryCode),
    items: products.map(p => ({
      variant_id: await getVariantIdFromSku(p.sku),
      quantity: p.quantity,
    })),
    context: {
      source: 'meta-commerce',
      origin: searchParams.cart_origin,
      utm: {
        source: searchParams.utm_source,
        medium: searchParams.utm_medium,
      },
    },
  });
  
  // 3. Apply coupon
  if (searchParams.coupon) {
    await applyDiscount(cart.id, searchParams.coupon);
  }
  
  // 4. Render checkout
  return <CheckoutTemplate cart={cart} />;
}

function parseProductsParam(param?: string): { sku: string; quantity: number }[] {
  if (!param) return [];
  
  // Decode: "SKU1%3A2%2CSKU2%3A1" → "SKU1:2,SKU2:1"
  const decoded = decodeURIComponent(param);
  
  return decoded.split(',').map(item => {
    const [sku, qty] = item.split(':');
    return { sku, quantity: parseInt(qty, 10) };
  });
}
```

### Best Practices

✅ **Obrigatório**:

- Clear cart on each call (prevent stale items)
- Guest checkout enabled (no login required)
- Handle out-of-stock gracefully
- Display applied discounts
- Mobile-optimized UI
- Express payment methods (PIX, Credit Card)
- UTM parameter tracking

❌ **Evitar**:

- Require email opt-in
- Multiple redirects
- Slow loading (< 2s target)
- Expired coupon errors without feedback

---

## 📊 Monitoramento & Relatórios

### Finance Reporting API

```typescript
// backend/src/meta-commerce/services/finance-reporting.service.ts
export class FinanceReportingService {
  async getDailyReport(date: string): Promise<FinanceReport> {
    const url = `${MetaCommerceConfig.api.baseUrl}/${MetaCommerceConfig.commerce.accountId}/payout_details`;
    
    const response = await axios.get(url, {
      params: {
        access_token: MetaCommerceConfig.systemUser.accessToken,
        start_date: date,
        end_date: date,
      }
    });
    
    return {
      totalRevenue: response.data.total_revenue,
      totalOrders: response.data.total_orders,
      platformFees: response.data.platform_fees,
      netPayout: response.data.net_payout,
    };
  }
}
```

### Metrics Dashboard

```typescript
// backend/src/meta-commerce/metrics/dashboard.ts
export class MetricsDashboard {
  async getIntegrationHealth(): Promise<HealthMetrics> {
    return {
      catalogSync: {
        lastSuccessfulSync: await this.getLastSyncTimestamp(),
        totalProducts: await this.getTotalProducts(),
        failedUploads: await this.getFailedUploads(),
      },
      inventorySync: {
        realtimeLatency: await this.getAverageBatchLatency(),
        outOfStockItems: await this.getOutOfStockCount(),
        oversellingIncidents: await this.getOversellingCount(),
      },
      orders: {
        totalOrders: await this.getTotalOrders(),
        averageAcknowledgmentTime: await this.getAvgAckTime(),
        cancellationRate: await this.getCancellationRate(),
      }
    };
  }
}
```

---

## 🚀 Roadmap de Implementação

### Fase 1: Setup & Autenticação (Semana 1-2)

- [ ] Criar Developer App no Meta for Developers
- [ ] Configurar System User no Business Manager
- [ ] Atribuir assets (App, Commerce Account, Page, Catalog)
- [ ] Gerar access token com permissões corretas
- [ ] Implementar `MetaCommerceConfig` no backend
- [ ] Criar testes de autenticação

### Fase 2: Mapeamento de Catálogo (Semana 3-4)

- [ ] Implementar mapeamento YSH → Meta product schema
- [ ] Criar tabela de categorias YSH → Google Product Categories
- [ ] Desenvolver transformadores de dados (price, availability, images)
- [ ] Implementar sistema de variantes (`item_group_id`)
- [ ] Gerar feed CSV de teste com 100 produtos

### Fase 3: Sincronização de Inventário (Semana 5-6)

- [ ] Implementar Feed API Service (scheduled sync)
- [ ] Implementar Batch API Service (realtime sync)
- [ ] Criar workflows de sincronização (hooks de inventário)
- [ ] Desenvolver estratégias anti-sobrevenda
- [ ] Configurar cron jobs para feeds programados

### Fase 4: Gestão de Pedidos (Semana 7-8)

- [ ] Implementar Order Acknowledgement API
- [ ] Implementar Order Fulfillment API
- [ ] Implementar Order Cancellation API
- [ ] Configurar webhooks de pedidos
- [ ] Integrar com módulo de aprovações B2B existente

### Fase 5: Checkout URL (Semana 9)

- [ ] Criar rota `/checkout/meta-commerce` no storefront
- [ ] Implementar parser de produtos URL
- [ ] Implementar aplicação automática de cupons
- [ ] Adicionar tracking UTM parameters
- [ ] Otimizar para mobile e performance

### Fase 6: Testes & Go-Live (Semana 10-12)

- [ ] Testes end-to-end em Test Commerce Account
- [ ] Testes de carga (1000 produtos, 100 pedidos/hora)
- [ ] Monitoramento de latência e erros
- [ ] Submeter App Review para produção
- [ ] Deploy gradual (10% → 50% → 100% traffic)

---

## 📈 KPIs & Métricas de Sucesso

### Performance

- **Latency de Batch API**: < 5 segundos (p95)
- **Feed Upload Time**: < 30 minutos para catálogo completo
- **Order Acknowledgement**: < 2 minutos após webhook

### Acurácia

- **Precisão de Inventário**: > 99% (inventário Meta vs real)
- **Taxa de Sobrevenda**: < 0.5% dos pedidos
- **Mapeamento de Produtos**: 100% dos 2.914 produtos mapeados

### Business

- **Taxa de Conversão**: > 2% (visitors → orders)
- **Ticket Médio**: > R$ 5.000 (B2B)
- **Taxa de Cancelamento**: < 3%
- **NPS Facebook/Instagram**: > 8.0

---

## 🔒 Segurança & Compliance

### Proteção de Dados

- Access tokens armazenados em secrets manager (AWS Secrets Manager / Azure Key Vault)
- Rotação automática de tokens a cada 60 dias
- Logs de API calls com PII mascarado
- Rate limiting: 200 req/min por endpoint

### Compliance

- LGPD: Consent para compartilhar dados com Meta
- PCI-DSS: Checkout não processa cartões diretamente
- Meta Commerce Policies: Verificação de produtos permitidos

---

## 📚 Referências

### Documentação Oficial Meta

- [Commerce Platform Overview](https://developers.facebook.com/docs/commerce-platform)
- [Catalog & Inventory Guide](https://developers.facebook.com/docs/commerce-platform/catalog)
- [Batch API Reference](https://developers.facebook.com/docs/commerce-platform/catalog/batch-api)
- [Order Management API](https://developers.facebook.com/docs/commerce-platform/order-management)
- [Catalog Fields Specification](https://developers.facebook.com/docs/commerce-platform/catalog/fields)

### Recursos YSH

- [Inventory Blueprint 360º](./INVENTORY_BLUEPRINT_360.md)
- [Manufacturers Complete List](../backend/data/products-inventory/MANUFACTURERS_360_COMPLETE.md)
- [Unified Product Schema](../backend/data/products-inventory/unified_product_blueprint.json)

---

## 📞 Suporte & Contatos

**Meta Developer Support**: https://developers.facebook.com/support  
**YSH Tech Lead**: fernando@yellosolarhub.com  
**Business Manager**: [YSH Business Manager ID]  
**App ID**: [To be created]  
**Commerce Account ID**: [To be configured]  

---

**Última Atualização**: 2025-01-13  
**Versão**: 1.0.0  
**Status**: ✅ Blueprint Completo - Pronto para Implementação
