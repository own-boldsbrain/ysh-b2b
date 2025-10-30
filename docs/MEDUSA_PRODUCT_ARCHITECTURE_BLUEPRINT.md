# Blueprint Arquitetural: Gestão Avançada de Catálogo Medusa.js

> **Sistema de Gerenciamento de Produtos Solares B2B**  
> **Versão**: 1.0.0 | **Status**: 🔧 Planejamento Técnico | **Data**: 17 de Outubro de 2025

---

## 📋 Índice

1. [Fundamentos Arquiteturais](#1-fundamentos-arquiteturais)
2. [Padrão para Produtos Componentes](#2-padrão-para-produtos-componentes)
3. [Estratégias de Implementação de Bundles](#3-estratégias-de-implementação-de-bundles)
4. [Arquitetura Customizada de Bundle Module](#4-arquitetura-customizada-de-bundle-module)
5. [Fichas Técnicas e Gestão de Imagens](#5-fichas-técnicas-e-gestão-de-imagens)
6. [Roadmap de Implementação](#6-roadmap-de-implementação)

---

## 1. Fundamentos Arquiteturais

### 1.1 Arquitetura Composable do Medusa.js

Medusa.js é uma plataforma headless commerce com arquitetura desacoplada:

```tsx
┌─────────────────────────────────────────────────────┐
│                  CLIENTE (HTTP)                      │
│            (Storefront / Admin / API)                │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              API ROUTES (Express.js)                 │
│         /admin/products  |  /store/bundles           │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│                  WORKFLOWS                           │
│   createBundleWorkflow | addToCartWorkflow           │
│   (Orquestração + Rollback + Consistência)          │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│                   MODULES                            │
│   Product Module | Bundle Module | Inventory Module  │
│   (Serviços + Data Models + Lógica de Domínio)      │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│               DATA STORE (PostgreSQL)                │
│         product | bundle | inventory_level           │
└─────────────────────────────────────────────────────┘
```

**Camadas Arquiteturais**:

- **API Routes**: Ponto de entrada HTTP (Express.js)
- **Workflows**: Orquestração de lógica de negócio com rollback
- **Modules**: Domínios isolados (Product, Order, Bundle)
- **Data Store**: PostgreSQL com ORM Medusa DML

### 1.2 Mecanismos de Extensibilidade

#### Modules vs Plugins

| Conceito | Definição | Uso |
|----------|-----------|-----|
| **Module** | Pacote isolado de domínio único (ex: Bundle Module) | Criar novas entidades de negócio |
| **Plugin** | Pacote reutilizável com modules + API routes + Admin UI | Distribuir features completas |

#### Data Model Links

Padrão oficial para relacionar entidades entre módulos:

```typescript
// src/links/bundle-product.ts
import { defineLink } from "@medusajs/framework/utils"
import BundleModule from "../modules/bundle"
import ProductModule from "@medusajs/medusa/product"

export default defineLink(
  BundleModule.linkable.bundle_item,
  ProductModule.linkable.product
)
```

**Benefícios**:

- ✅ Preserva integridade do core
- ✅ Permite extensibilidade infinita
- ✅ Mantém isolamento de módulos

---

## 2. Padrão para Produtos Componentes

### 2.1 Mapeamento de Entidades Core

**Tríade Fundamental**: `Product` → `ProductVariant` → `ProductOption`

```tsx
Product (Template do Componente)
├── id: "prod_painel_m5"
├── title: "Painel Solar 550W PERC Monocristalino"
├── handle: "painel-550w-perc-mono"
├── description: "Painel de alta eficiência..."
├── tags: ["tier-2", "perc", "monocristalino"]
├── categories: ["paineis-solares"]
└── options:
    ├── Option 1: "Fabricante" → [JinkoSolar, Trina, Canadian]
    └── Option 2: "Certificação" → [INMETRO A, INMETRO B]
    
ProductVariant (SKU Real - Unidade Vendável)
├── id: "variant_jinko_550_a"
├── title: "JinkoSolar Tiger Pro 550W INMETRO A"
├── sku: "JKS-550-PERC-MONO-A"
├── inventory_quantity: 1200
├── manage_inventory: true
├── prices:
│   ├── currency: "BRL" → amount: 65000 (R$ 650,00)
│   └── currency: "USD" → amount: 13000 ($130.00)
└── options:
    ├── Fabricante: "JinkoSolar"
    └── Certificação: "INMETRO A"
```

### 2.2 Schema de Criação via API

**Endpoint**: `POST /admin/products`

```json
{
  "title": "Painel Solar 550W PERC Monocristalino",
  "subtitle": "Alta eficiência Tier 2",
  "handle": "painel-550w-perc-mono",
  "is_giftcard": false,
  "discountable": true,
  "options": [
    { "title": "Fabricante" },
    { "title": "Certificação" }
  ],
  "variants": [
    {
      "title": "JinkoSolar 550W INMETRO A",
      "sku": "JKS-550-PERC-MONO-A",
      "ean": "7891234567890",
      "inventory_quantity": 1200,
      "manage_inventory": true,
      "options": [
        { "value": "JinkoSolar" },
        { "value": "INMETRO A" }
      ],
      "prices": [
        { "currency_code": "brl", "amount": 65000 },
        { "currency_code": "usd", "amount": 13000 }
      ]
    },
    {
      "title": "Trina Solar 550W INMETRO B",
      "sku": "TRI-550-PERC-MONO-B",
      "ean": "7891234567891",
      "inventory_quantity": 800,
      "manage_inventory": true,
      "options": [
        { "value": "Trina" },
        { "value": "INMETRO B" }
      ],
      "prices": [
        { "currency_code": "brl", "amount": 62000 }
      ]
    }
  ],
  "tags": [
    { "value": "tier-2" },
    { "value": "perc" },
    { "value": "monocristalino" }
  ],
  "categories": [
    { "id": "pcat_paineis_solares" }
  ]
}
```

**Regras Críticas**:

- ⚠️ Ordem dos `options` deve ser idêntica entre Product e Variant
- ✅ `sku` deve ser único globalmente (SKU Agnóstico)
- ✅ `inventory_quantity` gerenciado por `InventoryLevel` (multi-location)

### 2.3 Consumo no Frontend

**Store API**: `GET /store/products?handle=painel-550w-perc-mono`

```typescript
// React Hook (medusa-react)
import { useProducts } from "medusa-react"

const { products } = useProducts({
  handle: "painel-550w-perc-mono",
  expand: "variants,variants.prices,tags,categories"
})

// Acesso aos dados
const product = products[0]
const variants = product.variants // Array de SKUs
const firstVariant = variants[0]
const price = firstVariant.prices.find(p => p.currency_code === "brl")
```

---

## 3. Estratégias de Implementação de Bundles

### 3.1 Comparativo de Abordagens

#### Opção 1: Native Inventory Kits

**Características**:

- ✅ Feature nativa do Medusa v2.0
- ✅ Setup rápido (flag `has_inventory_kit`)
- ❌ Sem precificação dinâmica
- ❌ Sem fulfillment separado de itens
- ❌ Dead-end para evolução

**Quando usar**: Kits simples pré-definidos sem lógica complexa

```typescript
// Criar variant "kit"
POST /admin/products/:id/variants
{
  "title": "Kit Solar Residencial 5kW",
  "sku": "KIT-RES-5KW",
  "has_inventory_kit": true,
  "inventory_items": [
    { "inventory_item_id": "iitem_painel_01", "quantity": 10 },
    { "inventory_item_id": "iitem_inversor_02", "quantity": 1 }
  ]
}
```

#### Opção 2: Custom Bundle Module

**Características**:

- ✅ Controle total sobre lógica de negócio
- ✅ Precificação dinâmica (workflows customizados)
- ✅ Fulfillment granular
- ✅ Escalável e extensível
- ❌ Alto esforço de desenvolvimento

**Quando usar**: B2B complexo, regras de negócio únicas

#### Opção 3: @agilo/medusa-plugin-bundles

**Características**:

- ✅ Solução pronta com Admin UI
- ✅ API dedicada (`/store/bundles`)
- ❌ Dependência de terceiro
- ❌ Risco de manutenção

**Quando usar**: MVP rápido com features do plugin alinhadas

### 3.2 Matriz de Decisão

| Critério | Native Inventory Kits | Custom Bundle Module | Plugin @agilo |
|----------|----------------------|----------------------|---------------|
| **Precificação Dinâmica** | ❌ Manual | ✅ Workflow customizado | ⚠️ Depende do plugin |
| **Fulfillment Separado** | ❌ | ✅ Lógica própria | ⚠️ Depende do plugin |
| **Admin UI** | ✅ Nativo | ❌ Precisa desenvolver | ✅ Fornecido |
| **Esforço Dev** | 🟢 Baixo | 🔴 Alto | 🟡 Médio |
| **Time-to-Market** | 🟢 Rápido | 🔴 Lento | 🟢 Rápido |
| **Flexibilidade** | 🔴 Muito Baixa | 🟢 Muito Alta | 🟡 Média |
| **Recomendado para** | Kits fixos simples | B2B complexo | MVP validação |

**Recomendação YSH B2B**: **Custom Bundle Module**  
_Justificativa_: Necessidade de precificação dinâmica baseada em distribuidores, fulfillment multi-location e regras de negócio específicas do setor solar.

---

## 4. Arquitetura Customizada de Bundle Module

### 4.1 Data Model Definitions (DML)

#### Bundle Entity

```typescript
// src/modules/bundle/models/bundle.ts
import { model } from "@medusajs/framework/utils"
import { BundleItem } from "./bundle-item"

export const Bundle = model.define("bundle", {
  id: model.id({ prefix: "bundle" }).primaryKey(),
  title: model.text(),
  description: model.text().nullable(),
  status: model.enum(["draft", "active", "archived"]).default("draft"),
  
  // Metadados B2B
  target_persona: model.text().nullable(), // "residencial", "comercial", "industrial"
  system_capacity_kw: model.number().nullable(),
  
  // Precificação
  pricing_strategy: model.enum(["sum", "discount", "fixed"]).default("sum"),
  discount_percentage: model.number().nullable(),
  fixed_price_brl: model.number().nullable(),
  
  // Relações
  items: model.hasMany(() => BundleItem, {
    mappedBy: "bundle",
  }),
  
  // Timestamps
  created_at: model.dateTime().default("now"),
  updated_at: model.dateTime().default("now"),
})
```

#### BundleItem Entity

```typescript
// src/modules/bundle/models/bundle-item.ts
import { model } from "@medusajs/framework/utils"
import { Bundle } from "./bundle"

export const BundleItem = model.define("bundle_item", {
  id: model.id({ prefix: "bitem" }).primaryKey(),
  
  quantity: model.number().default(1),
  
  // Ordem de exibição
  sort_order: model.number().default(0),
  
  // Customizações por item
  is_optional: model.boolean().default(false),
  
  // Relação com Bundle
  bundle: model.belongsTo(() => Bundle, {
    mappedBy: "items",
  }),
})
```

#### Data Model Links

```typescript
// src/links/bundle-product.ts
import { defineLink } from "@medusajs/framework/utils"
import BundleModule from "../modules/bundle"
import ProductModule from "@medusajs/medusa/product"

// Link BundleItem → Product (componentes do kit)
export default defineLink(
  BundleModule.linkable.bundle_item,
  ProductModule.linkable.product
)
```

```typescript
// src/links/bundle-shell-product.ts
import { defineLink } from "@medusajs/framework/utils"
import BundleModule from "../modules/bundle"
import ProductModule from "@medusajs/medusa/product"

// Link Bundle → Product (shell do kit no catálogo)
export default defineLink(
  BundleModule.linkable.bundle,
  ProductModule.linkable.product
)
```

### 4.2 Service Layer

```typescript
// src/modules/bundle/service.ts
import { MedusaService } from "@medusajs/framework/utils"
import { Bundle } from "./models/bundle"
import { BundleItem } from "./models/bundle-item"

export default class BundleModuleService extends MedusaService({
  Bundle,
  BundleItem,
}) {
  // Métodos CRUD herdados automaticamente:
  // - createBundles(data)
  // - retrieveBundle(id)
  // - updateBundles(id, data)
  // - deleteBundles(id)
  // - listBundles(filters)
  
  // Métodos customizados
  async calculateBundlePrice(bundleId: string, region: string): Promise<number> {
    // Lógica de precificação dinâmica
    // 1. Recuperar bundle com items
    // 2. Para cada item, buscar variant price no region
    // 3. Aplicar pricing_strategy (sum, discount, fixed)
    // 4. Retornar preço final
  }
  
  async checkBundleInventory(bundleId: string, locationId: string): Promise<boolean> {
    // Verificar disponibilidade de todos os componentes
  }
}
```

### 4.3 Workflows

#### createBundleWorkflow

```typescript
// src/workflows/bundle/create-bundle.ts
import { 
  createWorkflow, 
  createStep, 
  WorkflowResponse 
} from "@medusajs/workflows-sdk"
import { createProductsWorkflow } from "@medusajs/medusa/core-flows"

interface CreateBundleInput {
  title: string
  description?: string
  target_persona?: string
  system_capacity_kw?: number
  pricing_strategy: "sum" | "discount" | "fixed"
  discount_percentage?: number
  items: Array<{
    product_id: string
    quantity: number
    sort_order?: number
  }>
}

// Step 1: Criar Product Shell
const createBundleProductStep = createStep(
  "create-bundle-product",
  async (input: CreateBundleInput, { container }) => {
    const productData = {
      title: input.title,
      description: input.description,
      handle: input.title.toLowerCase().replace(/\s+/g, "-"),
      status: "draft",
      metadata: {
        is_bundle: true,
        bundle_type: input.target_persona,
      },
    }
    
    const { result } = await createProductsWorkflow(container).run({
      input: { products: [productData] },
    })
    
    return new StepResponse(result[0], { productId: result[0].id })
  },
  async (compensationData, { container }) => {
    // Rollback: deletar produto se algo falhar depois
    const productService = container.resolve("productService")
    await productService.delete(compensationData.productId)
  }
)

// Step 2: Criar Bundle Record
const createBundleRecordStep = createStep(
  "create-bundle-record",
  async (input: CreateBundleInput, { container }) => {
    const bundleService = container.resolve("bundleModuleService")
    
    const bundle = await bundleService.createBundles({
      title: input.title,
      description: input.description,
      target_persona: input.target_persona,
      system_capacity_kw: input.system_capacity_kw,
      pricing_strategy: input.pricing_strategy,
      discount_percentage: input.discount_percentage,
      status: "draft",
    })
    
    return new StepResponse(bundle, { bundleId: bundle.id })
  },
  async (compensationData, { container }) => {
    const bundleService = container.resolve("bundleModuleService")
    await bundleService.deleteBundles(compensationData.bundleId)
  }
)

// Step 3: Criar BundleItems
const createBundleItemsStep = createStep(
  "create-bundle-items",
  async (
    { bundleId, items }: { bundleId: string; items: CreateBundleInput["items"] },
    { container }
  ) => {
    const bundleService = container.resolve("bundleModuleService")
    
    const bundleItems = await Promise.all(
      items.map(item =>
        bundleService.createBundleItems({
          bundle_id: bundleId,
          quantity: item.quantity,
          sort_order: item.sort_order || 0,
        })
      )
    )
    
    return new StepResponse(bundleItems, { itemIds: bundleItems.map(i => i.id) })
  },
  async (compensationData, { container }) => {
    const bundleService = container.resolve("bundleModuleService")
    await Promise.all(
      compensationData.itemIds.map(id => bundleService.deleteBundleItems(id))
    )
  }
)

// Step 4: Criar Links
const linkBundleRecordsStep = createStep(
  "link-bundle-records",
  async (
    { 
      bundleId, 
      productId, 
      bundleItems, 
      itemProducts 
    }: {
      bundleId: string
      productId: string
      bundleItems: any[]
      itemProducts: CreateBundleInput["items"]
    },
    { container }
  ) => {
    const remoteLinkService = container.resolve("remoteLink")
    
    // Link Bundle → Product Shell
    await remoteLinkService.create({
      bundle: { bundle_id: bundleId },
      product: { product_id: productId },
    })
    
    // Link cada BundleItem → Product componente
    await Promise.all(
      bundleItems.map((item, index) =>
        remoteLinkService.create({
          bundle_item: { bundle_item_id: item.id },
          product: { product_id: itemProducts[index].product_id },
        })
      )
    )
    
    return new StepResponse({ success: true })
  }
)

// Workflow Composition
export const createBundleWorkflow = createWorkflow(
  "create-bundle",
  function (input: CreateBundleInput) {
    const product = createBundleProductStep(input)
    const bundle = createBundleRecordStep(input)
    const bundleItems = createBundleItemsStep({
      bundleId: bundle.id,
      items: input.items,
    })
    
    linkBundleRecordsStep({
      bundleId: bundle.id,
      productId: product.id,
      bundleItems: bundleItems,
      itemProducts: input.items,
    })
    
    return new WorkflowResponse({
      bundle: bundle,
      product: product,
      items: bundleItems,
    })
  }
)
```

#### addBundleToCartWorkflow

```typescript
// src/workflows/cart/add-bundle-to-cart.ts
import { createWorkflow, createStep } from "@medusajs/workflows-sdk"
import { addToCartWorkflow } from "@medusajs/medusa/core-flows"

const validateBundleInventoryStep = createStep(
  "validate-bundle-inventory",
  async ({ bundleId, quantity, locationId }, { container }) => {
    const bundleService = container.resolve("bundleModuleService")
    const query = container.resolve("query")
    
    // Buscar bundle com items e products linkados
    const { data: bundles } = await query.graph({
      entity: "bundle",
      fields: ["id", "items.*", "items.product.*", "items.product.variants.*"],
      filters: { id: bundleId },
    })
    
    const bundle = bundles[0]
    
    // Verificar estoque de cada componente
    for (const item of bundle.items) {
      const requiredQty = item.quantity * quantity
      const variant = item.product.variants[0] // Assumindo 1 variant por component
      
      if (variant.inventory_quantity < requiredQty) {
        throw new Error(
          `Estoque insuficiente para ${item.product.title}: ` +
          `necessário ${requiredQty}, disponível ${variant.inventory_quantity}`
        )
      }
    }
    
    return new StepResponse({ validated: true, bundle })
  }
)

export const addBundleToCartWorkflow = createWorkflow(
  "add-bundle-to-cart",
  function ({ cartId, bundleId, quantity }) {
    const { bundle } = validateBundleInventoryStep({ bundleId, quantity })
    
    // Adicionar cada componente ao carrinho
    for (const item of bundle.items) {
      const variant = item.product.variants[0]
      
      addToCartWorkflow.run({
        input: {
          cart_id: cartId,
          items: [{
            variant_id: variant.id,
            quantity: item.quantity * quantity,
            metadata: {
              bundle_id: bundleId,
              bundle_item_id: item.id,
            },
          }],
        },
      })
    }
    
    return new WorkflowResponse({ success: true })
  }
)
```

### 4.4 API Routes

#### Admin API

```typescript
// src/api/admin/bundles/route.ts
import type { 
  AuthenticatedMedusaRequest, 
  MedusaResponse 
} from "@medusajs/framework"
import { createBundleWorkflow } from "../../../workflows/bundle/create-bundle"

// POST /admin/bundles
export const POST = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const { result } = await createBundleWorkflow(req.scope).run({
    input: req.validatedBody,
  })
  
  res.json({ bundle: result.bundle, product: result.product })
}

// GET /admin/bundles
export const GET = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const query = req.scope.resolve("query")
  
  const { data: bundles } = await query.graph({
    entity: "bundle",
    fields: [
      "id",
      "title",
      "status",
      "pricing_strategy",
      "items.*",
      "items.product.title",
      "items.product.thumbnail",
    ],
  })
  
  res.json({ bundles })
}
```

```typescript
// src/api/admin/bundles/[id]/route.ts
export const GET = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const query = req.scope.resolve("query")
  const { id } = req.params
  
  const { data: bundles } = await query.graph({
    entity: "bundle",
    fields: [
      "*",
      "items.*",
      "items.product.*",
      "items.product.variants.*",
      "items.product.variants.prices.*",
    ],
    filters: { id },
  })
  
  if (!bundles.length) {
    return res.status(404).json({ message: "Bundle not found" })
  }
  
  res.json({ bundle: bundles[0] })
}
```

#### Store API

```typescript
// src/api/store/bundles/[id]/route.ts
import type { MedusaRequest, MedusaResponse } from "@medusajs/framework"

export const GET = async (
  req: MedusaRequest,
  res: MedusaResponse
) => {
  const query = req.scope.resolve("query")
  const bundleService = req.scope.resolve("bundleModuleService")
  const { id } = req.params
  
  // Buscar bundle completo
  const { data: bundles } = await query.graph({
    entity: "bundle",
    fields: [
      "*",
      "items.*",
      "items.product.*",
      "items.product.variants.*",
      "items.product.variants.prices.*",
      "items.product.images.*",
    ],
    filters: { id, status: "active" },
  })
  
  if (!bundles.length) {
    return res.status(404).json({ message: "Bundle not found" })
  }
  
  const bundle = bundles[0]
  
  // Calcular preço dinâmico
  const regionId = req.query.region_id || "reg_default"
  const calculatedPrice = await bundleService.calculateBundlePrice(id, regionId)
  
  res.json({
    bundle: {
      ...bundle,
      calculated_price: calculatedPrice,
    },
  })
}
```

---

## 5. Fichas Técnicas e Gestão de Imagens

### 5.1 Fichas Técnicas: Comparação de Abordagens

#### Opção 1: Campo `metadata` (Simples)

```typescript
// Adicionar URL ao metadata do Product
POST /admin/products/:id
{
  "metadata": {
    "technical_sheet_url": "https://s3.amazonaws.com/ysh-docs/paineis/jinko-550w.pdf",
    "technical_sheet_version": "v2.3",
    "certification_inmetro": "A",
    "warranty_years": 25
  }
}
```

**Prós**:

- ✅ Sem modificação de schema
- ✅ Implementação imediata

**Contras**:

- ❌ Sem validação
- ❌ Sem estrutura
- ❌ "Junk drawer" em escala

#### Opção 2: TechnicalSheet Custom Module (Robusto)

```typescript
// src/modules/technical-sheet/models/technical-sheet.ts
import { model } from "@medusajs/framework/utils"

export const TechnicalSheet = model.define("technical_sheet", {
  id: model.id({ prefix: "tsheet" }).primaryKey(),
  
  url: model.text(),
  file_type: model.enum(["pdf", "docx", "xlsx"]),
  file_size_kb: model.number(),
  version: model.text().default("1.0"),
  language: model.text().default("pt-BR"),
  
  // Metadata estruturada
  certification_level: model.text().nullable(), // "INMETRO A", "INMETRO B"
  warranty_years: model.number().nullable(),
  test_standards: model.json().nullable(), // ["IEC 61215", "IEC 61730"]
  
  created_at: model.dateTime().default("now"),
  updated_at: model.dateTime().default("now"),
})
```

```typescript
// src/links/technical-sheet-product.ts
import { defineLink } from "@medusajs/framework/utils"
import TechnicalSheetModule from "../modules/technical-sheet"
import ProductModule from "@medusajs/medusa/product"

export default defineLink(
  TechnicalSheetModule.linkable.technical_sheet,
  ProductModule.linkable.product
)
```

**Uso**:

```typescript
// Criar ficha técnica e linkar a produto
POST /admin/technical-sheets
{
  "url": "https://s3.amazonaws.com/ysh-docs/paineis/jinko-550w.pdf",
  "file_type": "pdf",
  "version": "2.3",
  "certification_level": "INMETRO A",
  "warranty_years": 25,
  "product_id": "prod_01HJKZ123"
}

// Query no frontend
const { data: products } = await query.graph({
  entity: "product",
  fields: [
    "id",
    "title",
    "technical_sheet.url",
    "technical_sheet.certification_level",
    "technical_sheet.warranty_years"
  ],
  filters: { id: productId }
})
```

**Recomendação**: **Opção 2 (Custom Module)**  
_Justificativa_: Estabelecer padrão estruturado, queryável e evolutivo (versionamento, multi-idioma).

### 5.2 Gestão de Imagens

#### Pré-requisito: File Service Plugin

**Instalação** (AWS S3):

```bash
npm install @medusajs/medusa-file-s3
```

**Configuração** (`medusa-config.ts`):

```typescript
import { defineConfig } from "@medusajs/framework/utils"

export default defineConfig({
  // ...
  plugins: [
    {
      resolve: "@medusajs/medusa-file-s3",
      options: {
        file_url: process.env.S3_FILE_URL, // https://s3.amazonaws.com/ysh-media
        access_key_id: process.env.S3_ACCESS_KEY_ID,
        secret_access_key: process.env.S3_SECRET_ACCESS_KEY,
        region: process.env.S3_REGION,
        bucket: process.env.S3_BUCKET, // "ysh-media"
        prefix: "products", // Pasta dentro do bucket
        download_file_duration: 3600, // Signed URL expiration (1h)
      },
    },
  ],
})
```

#### Workflow de Upload Programático

```typescript
// src/workflows/product/add-product-image.ts
import { createWorkflow, createStep } from "@medusajs/workflows-sdk"
import { createRemoteLinkStep } from "@medusajs/medusa/core-flows"

interface AddProductImageInput {
  product_id: string
  image_file: File | Buffer
  filename: string
  is_thumbnail?: boolean
}

const uploadImageStep = createStep(
  "upload-product-image",
  async ({ image_file, filename }: AddProductImageInput, { container }) => {
    const fileService = container.resolve("fileService")
    
    // Upload para S3 via File Service
    const uploadResult = await fileService.upload({
      file: image_file,
      filename: filename,
      acl: "public-read", // URL pública
    })
    
    return new StepResponse(
      { url: uploadResult.url, key: uploadResult.key },
      { key: uploadResult.key }
    )
  },
  async (compensationData, { container }) => {
    // Rollback: deletar arquivo do S3
    const fileService = container.resolve("fileService")
    await fileService.delete({ fileKey: compensationData.key })
  }
)

const createProductImageRecordStep = createStep(
  "create-product-image-record",
  async ({ url }: { url: string }, { container }) => {
    const productService = container.resolve("productService")
    
    const image = await productService.createImages({
      url: url,
    })
    
    return new StepResponse(image, { imageId: image.id })
  },
  async (compensationData, { container }) => {
    const productService = container.resolve("productService")
    await productService.deleteImages(compensationData.imageId)
  }
)

export const addProductImageWorkflow = createWorkflow(
  "add-product-image",
  function (input: AddProductImageInput) {
    const { url } = uploadImageStep(input)
    const image = createProductImageRecordStep({ url })
    
    createRemoteLinkStep({
      product: { product_id: input.product_id },
      product_image: { product_image_id: image.id },
    })
    
    // Se for thumbnail, atualizar campo Product.thumbnail
    if (input.is_thumbnail) {
      updateProductStep({
        id: input.product_id,
        thumbnail: url,
      })
    }
    
    return new WorkflowResponse({ image, url })
  }
)
```

#### API para Upload

```typescript
// src/api/admin/products/[id]/images/route.ts
import type { MedusaRequest, MedusaResponse } from "@medusajs/framework"
import { addProductImageWorkflow } from "../../../../../workflows/product/add-product-image"
import formidable from "formidable"

export const POST = async (
  req: MedusaRequest,
  res: MedusaResponse
) => {
  const { id } = req.params
  
  // Parse multipart form
  const form = formidable({ multiples: true })
  const [fields, files] = await form.parse(req)
  
  const imageFile = files.image[0]
  
  const { result } = await addProductImageWorkflow(req.scope).run({
    input: {
      product_id: id,
      image_file: imageFile,
      filename: imageFile.originalFilename,
      is_thumbnail: fields.is_thumbnail === "true",
    },
  })
  
  res.json({ image: result.image })
}
```

#### Admin UI: Upload Abstrato

No Medusa Admin, o upload é automático:
1. Admin seleciona imagem
2. UI chama `POST /admin/uploads` (retorna URL)
3. UI chama `POST /admin/products/:id` com `images: [{ url }]`
4. Medusa cria `ProductImage` e link

#### Gestão de Thumbnail

```typescript
// Definir thumbnail
POST /admin/products/:id
{
  "thumbnail": "https://s3.amazonaws.com/ysh-media/products/painel-550w-thumb.jpg"
}

// Query no Store API
GET /store/products?handle=painel-550w
Response:
{
  "products": [{
    "id": "prod_01",
    "title": "Painel 550W",
    "thumbnail": "https://s3.amazonaws.com/ysh-media/products/painel-550w-thumb.jpg",
    "images": [
      { "id": "img_01", "url": "https://..." },
      { "id": "img_02", "url": "https://..." }
    ]
  }]
}
```

---

## 6. Roadmap de Implementação

### Fase 1: Foundation Setup (Semana 1-2)

**Objetivo**: Infraestrutura base

- [ ] Deploy Medusa v2.x + PostgreSQL + Redis
- [ ] Instalar e configurar File Service Plugin (S3)
- [ ] Configurar ambientes (dev/staging/prod)
- [ ] Setup CI/CD para migrations

**Entregáveis**:

- ✅ Backend Medusa rodando
- ✅ S3 bucket configurado
- ✅ Admin Dashboard acessível

### Fase 2: Custom Data Extension (Semana 3-4)

**Objetivo**: Módulo TechnicalSheet

- [ ] Desenvolver `TechnicalSheet` module (models + service)
- [ ] Criar link `TechnicalSheet ↔ Product`
- [ ] Gerar e rodar migrations
- [ ] Desenvolver API routes (`/admin/technical-sheets`)
- [ ] Criar Admin Widget para gerenciar fichas técnicas

**Entregáveis**:

- ✅ Module funcional
- ✅ API testada
- ✅ Admin UI para upload de PDFs

### Fase 3: Component Products (Semana 5-6)

**Objetivo**: Popular catálogo base

- [ ] Criar script de importação de componentes (painéis, inversores)
- [ ] Implementar SKUs Agnósticos com multi-location inventory
- [ ] Associar imagens e fichas técnicas via workflows
- [ ] Validar dados com análise de cobertura

**Entregáveis**:

- ✅ ~4.500 componentes importados
- ✅ Imagens e fichas técnicas linkadas
- ✅ Inventory multi-distribuidor configurado

### Fase 4: Bundle Implementation (Semana 7-10)

**Objetivo**: Bundle Module completo

- [ ] Desenvolver `Bundle` e `BundleItem` models
- [ ] Criar links `Bundle ↔ Product` e `BundleItem ↔ Product`
- [ ] Implementar `createBundleWorkflow`
- [ ] Implementar `addBundleToCartWorkflow`
- [ ] Desenvolver Admin API (`/admin/bundles`)
- [ ] Desenvolver Store API (`/store/bundles/:id`)
- [ ] Criar Admin UI Route para gestão de bundles
- [ ] Implementar lógica de precificação dinâmica

**Entregáveis**:

- ✅ Bundle Module operacional
- ✅ Workflows testados
- ✅ Admin UI funcional
- ✅ APIs documentadas

### Fase 5: Storefront Integration (Semana 11-12)

**Objetivo**: Frontend consumindo Bundles

- [ ] Desenvolver componentes React para Bundle PDP
- [ ] Implementar "Add Bundle to Cart"
- [ ] Exibir links de fichas técnicas
- [ ] Integrar cálculo de preço dinâmico
- [ ] Implementar filtros de bundles (por persona, capacidade)
- [ ] Testes E2E do fluxo completo

**Entregáveis**:

- ✅ Storefront exibindo bundles
- ✅ Carrinho funcionando com componentes
- ✅ UX otimizada para B2B

### Fase 6: Optimization & Scale (Semana 13-14)

**Objetivo**: Performance e monitoramento

- [ ] Implementar caching (Redis) para queries de bundles
- [ ] Otimizar queries com índices PostgreSQL
- [ ] Setup monitoring (DataDog/Sentry)
- [ ] Documentação técnica final
- [ ] Treinamento da equipe

**Entregáveis**:

- ✅ Sistema otimizado
- ✅ Documentação completa
- ✅ Equipe treinada

---

## 📚 Referências

### Documentação Oficial

- [Medusa v2 Architecture](https://docs.medusajs.com/1.3/architecture)
- [Data Models](https://docs.medusajs.com/3.5/data-models)
- [Workflows SDK](https://docs.medusajs.com/workflows)
- [Bundled Products Recipe](https://docs.medusajs.com/recipes/bundled-products)
- [File Module](https://docs.medusajs.com/file-module)

### Plugins Relevantes

- [@medusajs/medusa-file-s3](https://docs.medusajs.com/plugins/file-s3)
- [@agilo/medusa-plugin-bundles](https://github.com/Agilo/medusa-plugin-bundles)

### Case Studies

- [Catalog: Building B2B Platform for SMBs](https://medusajs.com/blog/catalog-b2b-medusa)

---

## 🏁 Conclusão

Este blueprint fornece a fundação arquitetural completa para implementar um sistema avançado de gestão de catálogo no Medusa.js, especificamente otimizado para o cenário B2B de produtos solares da YSH.

**Princípios-Chave**:

1. **Separação de Concerns**: Componentes (Product/Variant) vs Bundles (Custom Module)
2. **Extensibilidade**: Data Model Links preservam integridade do core
3. **Consistência**: Workflows garantem transações seguras com rollback
4. **Escalabilidade**: Multi-location inventory + precificação dinâmica

**Próximos Passos**:

1. Revisar e aprovar este blueprint com stakeholders técnicos
2. Iniciar Fase 1 (Foundation Setup)
3. Executar implementação iterativa seguindo o roadmap

---

**Versão**: 1.0.0  
**Autor**: Equipe Técnica YSH B2B  
**Data**: 17 de Outubro de 2025  
**Status**: 📋 Aprovação Pendente
