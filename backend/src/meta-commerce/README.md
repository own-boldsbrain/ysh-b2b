# Meta Commerce Platform Integration Module

Este módulo implementa a integração de alta performance entre o inventário YSH e a Meta Commerce Platform (Facebook Shops & Instagram Shopping).

## 📁 Estrutura do Módulo

```tsx
backend/src/meta-commerce/
├── config/
│   ├── meta-commerce.config.ts      # Configurações gerais
│   └── rate-limits.config.ts        # Rate limiting
├── services/
│   ├── feed-sync.service.ts         # Feed API (scheduled)
│   ├── batch-sync.service.ts        # Batch API (realtime)
│   ├── order-acknowledgement.service.ts
│   ├── order-fulfillment.service.ts
│   ├── order-cancellation.service.ts
│   └── finance-reporting.service.ts
├── mappings/
│   ├── categories.ts                # YSH → Google Categories
│   ├── product-transformer.ts       # YSH Product → Meta Schema
│   └── order-transformer.ts         # Meta Order → YSH Order
├── strategies/
│   ├── pre-allocated-inventory.ts   # Alocação por canal
│   ├── dynamic-limits.ts            # Buffers dinâmicos
│   └── sales-velocity.ts            # Cálculo de velocidade
├── webhooks/
│   ├── orders.webhook.ts            # Webhooks de pedidos
│   └── catalog.webhook.ts           # Webhooks de catálogo
├── workflows/
│   ├── sync-catalog.workflow.ts     # Workflow de sincronização
│   └── process-order.workflow.ts    # Workflow de pedidos
├── validators/
│   ├── product.validator.ts         # Validação de produtos
│   └── order.validator.ts           # Validação de pedidos
└── index.ts                          # Exportações do módulo
```

## 🚀 Quick Start

### 1. Configuração de Variáveis de Ambiente

```bash
# .env
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_SYSTEM_USER_ID=system_user_id
META_SYSTEM_USER_TOKEN=long_lived_token
META_COMMERCE_ACCOUNT_ID=commerce_account_id
META_CATALOG_ID=catalog_id
META_PAGE_ID=page_id
META_API_VERSION=v18.0
```

### 2. Registrar Módulo no Medusa

```typescript
// backend/medusa-config.ts
export const META_COMMERCE_MODULE = "meta-commerce";

export default defineConfig({
  modules: {
    [META_COMMERCE_MODULE]: {
      resolve: "./modules/meta-commerce",
      options: {
        enableFeedSync: true,
        enableBatchSync: true,
        feedSchedule: "0 3 * * *", // 3h AM diariamente
        batchThrottleMs: 1000,
      },
    },
  },
});
```

### 3. Executar Primeira Sincronização

```bash
# Sincronizar catálogo completo via Feed API
yarn medusa exec backend/src/meta-commerce/scripts/initial-sync.ts

# Verificar status
yarn medusa exec backend/src/meta-commerce/scripts/check-sync-status.ts
```

## 📦 Uso dos Serviços

### Feed Sync Service (Sincronização Programada)

```typescript
import { FeedSyncService } from "@/meta-commerce/services/feed-sync.service";

// Executar sincronização completa
const feedSync = new FeedSyncService();
await feedSync.scheduledFullSync();

// Sincronizar apenas produtos atualizados
await feedSync.incrementalSync({ since: "2025-01-12" });

// Gerar feed CSV para debug
const csvContent = await feedSync.generateFeedCSV({ limit: 100 });
```

### Batch Sync Service (Atualizações em Tempo Real)

```typescript
import { BatchSyncService } from "@/meta-commerce/services/batch-sync.service";

// Atualizar inventário em tempo real
const batchSync = new BatchSyncService();
await batchSync.updateInventoryRealtime([
  { sku: "NEO-INV-DEYE-8K", quantity: 45 },
  { sku: "NEO-PAINEL-DAH-550W", quantity: 320 },
]);

// Criar novos produtos
await batchSync.createProducts([
  {
    retailer_id: "NEW-PRODUCT-SKU",
    title: "Novo Inversor",
    price: "8500.00 BRL",
    // ... outros campos
  },
]);

// Deletar produtos
await batchSync.deleteProducts(["OLD-SKU-1", "OLD-SKU-2"]);
```

### Order Management

```typescript
import { OrderAcknowledgementService } from "@/meta-commerce/services/order-acknowledgement.service";
import { OrderFulfillmentService } from "@/meta-commerce/services/order-fulfillment.service";

// 1. Reconhecer pedido (CREATED → IN_PROGRESS)
const ackService = new OrderAcknowledgementService();
await ackService.acknowledgeOrder("meta-order-id");

// 2. Criar envio (IN_PROGRESS → FULFILLED)
const fulfillmentService = new OrderFulfillmentService();
await fulfillmentService.createShipment("meta-order-id", {
  items: [
    { sku: "NEO-INV-DEYE-8K", quantity: 2 },
  ],
  trackingNumber: "BR123456789",
  carrier: "correios",
  originZipCode: "01310-100",
});

// 3. Cancelar pedido (se necessário)
const cancellationService = new OrderCancellationService();
await cancellationService.cancelOrder("meta-order-id", {
  type: "sobrevenda",
  description: "Produto esgotado no estoque",
  shouldRestock: true,
});
```

## 🔄 Workflows

### Sincronização Automática de Inventário

```typescript
// backend/src/workflows/hooks/inventory-changed-meta.ts
import { createStep, createWorkflow, WorkflowResponse } from "@medusajs/workflows-sdk";
import { BatchSyncService } from "@/meta-commerce/services/batch-sync.service";

const syncInventoryToMetaStep = createStep(
  "sync-inventory-to-meta",
  async ({ product_id, new_quantity }, { container }) => {
    const batchSync = container.resolve(BatchSyncService);
    
    await batchSync.updateInventoryRealtime([
      { sku: product_id, quantity: new_quantity },
    ]);
    
    return new StepResponse({ synced: true });
  }
);

export const syncInventoryToMetaWorkflow = createWorkflow(
  "sync-inventory-to-meta",
  function (input: { product_id: string; new_quantity: number }) {
    const result = syncInventoryToMetaStep(input);
    return new WorkflowResponse(result);
  }
);

// Hook em updateProductWorkflow
import { updateProductWorkflow } from "@medusajs/core-flows";

updateProductWorkflow.hooks.productUpdated(async ({ product }, { container }) => {
  if (product.inventory?.quantity !== undefined) {
    await syncInventoryToMetaWorkflow.run({
      input: {
        product_id: product.id,
        new_quantity: product.inventory.quantity,
      },
      container,
    });
  }
});
```

### Processamento de Pedidos Meta

```typescript
// backend/src/workflows/meta-commerce/process-meta-order.workflow.ts
import { createWorkflow, createStep, WorkflowResponse } from "@medusajs/workflows-sdk";

const createYshOrderStep = createStep(
  "create-ysh-order-from-meta",
  async ({ metaOrder }, { container }) => {
    const orderTransformer = container.resolve(OrderTransformer);
    const yshOrder = orderTransformer.transform(metaOrder);
    
    // Criar ordem no Medusa
    const { result } = await createOrdersWorkflow.run({
      input: yshOrder,
      container,
    });
    
    return new StepResponse(result, { orderId: result.id });
  }
);

const checkApprovalStep = createStep(
  "check-b2b-approval",
  async ({ order }, { container }) => {
    const approvalService = container.resolve("approval");
    
    const needsApproval = await approvalService.checkIfApprovalNeeded({
      cart_id: order.cart_id,
      total: order.total,
      customer_id: order.customer_id,
    });
    
    return new StepResponse({ needsApproval });
  }
);

const acknowledgeMetaOrderStep = createStep(
  "acknowledge-meta-order",
  async ({ metaOrderId }, { container }) => {
    const ackService = container.resolve(OrderAcknowledgementService);
    await ackService.acknowledgeOrder(metaOrderId);
    
    return new StepResponse({ acknowledged: true });
  }
);

export const processMetaOrderWorkflow = createWorkflow(
  "process-meta-order",
  function (input: { metaOrder: MetaOrder }) {
    const yshOrder = createYshOrderStep(input);
    const approval = checkApprovalStep(yshOrder);
    
    const acknowledged = acknowledgeMetaOrderStep
      .when(() => approval.needsApproval === false)
      .then(() => ({
        metaOrderId: input.metaOrder.id,
      }));
    
    return new WorkflowResponse({
      order: yshOrder,
      needsApproval: approval.needsApproval,
      acknowledged: acknowledged?.acknowledged,
    });
  }
);
```

## 🔧 Product Transformer

```typescript
// backend/src/meta-commerce/mappings/product-transformer.ts
import { Product } from "@medusajs/medusa";
import { MetaProduct, YSH_TO_GOOGLE_CATEGORIES } from "./categories";

export class ProductTransformer {
  transform(yshProduct: Product): MetaProduct {
    return {
      // Campos obrigatórios
      id: yshProduct.external_id || yshProduct.id,
      title: yshProduct.title,
      description: this.buildDescription(yshProduct),
      availability: this.mapAvailability(yshProduct.status),
      condition: "new",
      price: `${yshProduct.variants[0].prices[0].amount / 100} BRL`,
      link: `${process.env.STOREFRONT_URL}/products/${yshProduct.handle}`,
      image_link: yshProduct.images[0]?.url,
      brand: yshProduct.metadata?.manufacturer as string,
      google_product_category: this.mapCategory(yshProduct.categories[0]?.name),
      
      // Inventário
      quantity_to_sell_on_fb: this.calculateMetaInventory(yshProduct),
      
      // Campos opcionais
      additional_image_link: yshProduct.images.slice(1, 4).map(img => img.url),
      item_group_id: yshProduct.metadata?.base_product_id as string,
      custom_label_0: yshProduct.categories[0]?.name, // Categoria YSH
      custom_label_1: yshProduct.metadata?.manufacturer as string,
      custom_label_2: yshProduct.metadata?.distributor as string,
      custom_label_3: yshProduct.metadata?.technology as string,
      
      // Variantes
      ...(yshProduct.variants.length > 1 && {
        size: yshProduct.variants[0].metadata?.power_rating as string,
      }),
    };
  }
  
  private buildDescription(product: Product): string {
    let desc = product.description || "";
    
    // Adicionar especificações técnicas
    if (product.metadata?.specs) {
      const specs = product.metadata.specs as Record<string, string>;
      desc += "\n\nEspecificações:\n";
      Object.entries(specs).forEach(([key, value]) => {
        desc += `• ${key}: ${value}\n`;
      });
    }
    
    return desc.substring(0, 5000); // Limite Meta: 5000 chars
  }
  
  private mapAvailability(status: string): "in stock" | "out of stock" {
    return status === "published" ? "in stock" : "out of stock";
  }
  
  private mapCategory(yshCategory: string): string {
    return YSH_TO_GOOGLE_CATEGORIES[yshCategory] || "Electronics";
  }
  
  private calculateMetaInventory(product: Product): number {
    const totalInventory = product.variants.reduce(
      (sum, v) => sum + (v.inventory_quantity || 0),
      0
    );
    
    // Aplicar estratégia de pré-alocação (30% para Meta)
    const metaAllocation = Math.floor(totalInventory * 0.30);
    
    // Aplicar buffer de segurança (10%)
    const withBuffer = Math.floor(metaAllocation * 0.90);
    
    return Math.max(withBuffer, 0);
  }
}
```

## 📊 Monitoramento

### Health Check Endpoint

```typescript
// backend/src/api/admin/meta-commerce/health/route.ts
import { MedusaRequest, MedusaResponse } from "@medusajs/medusa";
import { BatchSyncService } from "@/meta-commerce/services/batch-sync.service";

export const GET = async (
  req: MedusaRequest,
  res: MedusaResponse
) => {
  const batchSync = req.scope.resolve(BatchSyncService);
  const feedSync = req.scope.resolve(FeedSyncService);
  
  const health = {
    catalog: {
      totalProducts: await batchSync.getTotalProductsInCatalog(),
      lastSync: await feedSync.getLastSyncTimestamp(),
      failedUploads: await batchSync.getFailedUploadsCount(),
    },
    inventory: {
      realtimeLatency: await batchSync.getAverageBatchLatency(),
      outOfStock: await batchSync.getOutOfStockCount(),
      lastBatchUpdate: await batchSync.getLastBatchTimestamp(),
    },
    orders: {
      pendingAcknowledgement: await this.getPendingAckCount(),
      averageAckTime: await this.getAverageAckTime(),
      totalOrders: await this.getTotalMetaOrders(),
    },
    status: "healthy",
  };
  
  res.json(health);
};
```

### Logging & Alertas

```typescript
// backend/src/meta-commerce/utils/logger.ts
import { Logger } from "@medusajs/medusa";

export class MetaCommerceLogger {
  private logger: Logger;
  
  constructor(logger: Logger) {
    this.logger = logger;
  }
  
  logBatchRequest(request: BatchRequest) {
    this.logger.info("Meta Batch API Request", {
      type: "batch_request",
      itemCount: request.requests.length,
      timestamp: new Date().toISOString(),
    });
  }
  
  logBatchError(error: Error, handle: string) {
    this.logger.error("Meta Batch API Error", {
      type: "batch_error",
      handle,
      error: error.message,
      stack: error.stack,
    });
    
    // Enviar alerta se taxa de erro > 5%
    this.checkErrorRate();
  }
  
  logOrderWebhook(order: MetaOrder) {
    this.logger.info("Meta Order Webhook Received", {
      type: "order_webhook",
      orderId: order.id,
      total: order.total,
      itemCount: order.items.length,
    });
  }
}
```

## 🧪 Testes

### Testes Unitários

```typescript
// backend/src/meta-commerce/__tests__/product-transformer.spec.ts
import { ProductTransformer } from "../mappings/product-transformer";

describe("ProductTransformer", () => {
  it("should transform YSH product to Meta schema", () => {
    const yshProduct = {
      id: "prod_123",
      external_id: "NEO-INV-DEYE-8K",
      title: "Inversor Deye SUN-8K",
      description: "Inversor híbrido",
      status: "published",
      variants: [
        {
          prices: [{ amount: 785000, currency_code: "BRL" }],
          inventory_quantity: 45,
        },
      ],
      images: [{ url: "https://cdn.ysh.com.br/inv-deye-8k.jpg" }],
      categories: [{ name: "inversores" }],
      metadata: {
        manufacturer: "Deye",
        distributor: "Neosolar",
        technology: "Híbrido",
      },
    };
    
    const transformer = new ProductTransformer();
    const metaProduct = transformer.transform(yshProduct);
    
    expect(metaProduct.id).toBe("NEO-INV-DEYE-8K");
    expect(metaProduct.price).toBe("7850.00 BRL");
    expect(metaProduct.availability).toBe("in stock");
    expect(metaProduct.quantity_to_sell_on_fb).toBe(12); // 45 * 0.30 * 0.90
  });
});
```

### Testes de Integração

```typescript
// backend/integration-tests/meta-commerce/batch-sync.spec.ts
import { BatchSyncService } from "@/meta-commerce/services/batch-sync.service";

describe("Batch Sync Integration", () => {
  it("should update inventory via Batch API", async () => {
    const batchSync = new BatchSyncService();
    
    await batchSync.updateInventoryRealtime([
      { sku: "TEST-SKU-1", quantity: 100 },
    ]);
    
    // Verificar que produto foi atualizado no catálogo Meta
    const product = await batchSync.getProductFromCatalog("TEST-SKU-1");
    expect(product.quantity_to_sell_on_fb).toBe(100);
  });
});
```

## 📖 Guias Adicionais

- [Setup Inicial](./docs/SETUP.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [Best Practices](./docs/BEST_PRACTICES.md)
- [API Reference](./docs/API_REFERENCE.md)

## 🔗 Links Úteis

- [Meta Commerce Platform Docs](https://developers.facebook.com/docs/commerce-platform)
- [Blueprint de Integração](../../docs/META_COMMERCE_INTEGRATION_BLUEPRINT.md)
- [YSH Inventory Blueprint](../data/products-inventory/INVENTORY_BLUEPRINT_360.md)

---

**Versão**: 1.0.0  
**Status**: Em Desenvolvimento  
**Última Atualização**: 2025-01-13
