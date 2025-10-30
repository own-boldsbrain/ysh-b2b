# Facebook Commerce Platform Integration

Integração completa com **Facebook Commerce Platform** para sincronização automática de catálogo em múltiplas plataformas:
- ✅ **Facebook Shops** - Loja no Facebook
- ✅ **Instagram Shopping** - Tags de produtos e Loja no Instagram  
- ✅ **WhatsApp Business Catalog** - Catálogo de produtos no WhatsApp

## 📋 Visão Geral

Este módulo implementa sincronização unificada entre o catálogo YSH e o ecossistema Meta Commerce, permitindo:

- ✅ **Catálogo Unificado**: Um sync atualiza Facebook + Instagram + WhatsApp
- ✅ **Upload em Lote**: Até 5000 items por batch
- ✅ **Sincronização Automática**: Via eventos (create/update/delete)
- ✅ **Instagram Shopping**: Tags de produtos e checkout nativo
- ✅ **WhatsApp Catalog**: Envio de produtos por mensagem
- ✅ **Multi-plataforma**: Rastreamento individual por plataforma
- ✅ **Transformação de Dados**: SKU → Facebook Product Item
- ✅ **Google Product Taxonomy**: Mapeamento de 13 categorias solares

## 🏗️ Arquitetura

### Models

**FacebookCatalogSync**
- Rastreia batches de sincronização
- Status: `pending`, `in_progress`, `completed`, `failed`, `partial`
- Métricas: items created/updated/deleted/failed

**FacebookProductMapping**
- Mapeia SKUs YSH → Facebook Product IDs
- Sync hash para detecção de mudanças
- Status tracking por produto

### Workflows

**syncCatalogToFacebookWorkflow**
1. `fetchActiveSKUsStep` - Busca SKUs ativos do catálogo
2. `transformSKUsToFacebookProductsStep` - Transforma para formato Facebook
3. `uploadBatchToFacebookStep` - Envia batches via API
4. `waitForBatchCompletionStep` - Aguarda processamento (polling)
5. `updateProductMappingsStep` - Atualiza mapeamentos

### Transformers

**SKUToFacebookProductTransformer**
- Converte SKU → FacebookProductItem
- Mapeia categorias para Google Product Taxonomy
- Calcula pricing e availability baseado em offers
- Gera sync hash para change detection

### API Endpoints

**Admin Routes**
- `POST /admin/facebook-catalog/sync` - Trigger manual sync
- `GET /admin/facebook-catalog/syncs` - Listar histórico
- `GET /admin/facebook-catalog/mappings` - Listar mapeamentos

### Event Subscribers

- `catalog.product.updated` → Sync automático (UPDATE)
- `catalog.product.created` → Sync automático (UPDATE)
- `catalog.product.deleted` → Sync automático (DELETE)

## 🔧 Configuração

### 1. Credenciais Meta Commerce Platform

Criar app no [Facebook Developers](https://developers.facebook.com/) e obter credenciais:

```bash
# Facebook/Instagram (obrigatório)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_CATALOG_ID=your_catalog_id
FACEBOOK_BASE_PRODUCT_URL=https://ysh.com.br/produtos

# Instagram Shopping (opcional)
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id

# WhatsApp Business (opcional)
WHATSAPP_BUSINESS_ACCOUNT_ID=your_whatsapp_business_account_id
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
```

**Permissões necessárias**:
- `catalog_management` - Gerenciar catálogo
- `instagram_basic` - Instagram Shopping (se usar)
- `instagram_shopping_tag_products` - Tags de produtos Instagram
- `whatsapp_business_management` - WhatsApp Catalog (se usar)
- `whatsapp_business_messaging` - Enviar mensagens WhatsApp

### 2. Instalação de Dependências

```bash
npm install axios
```

### 3. Feature Flag (opcional)

```typescript
// medusa-config.ts
featureFlags: {
  facebook_catalog_sync: true
}
```

## 📖 Uso

### Sync Manual (Admin API)

```bash
# Sync completo do catálogo
curl -X POST http://localhost:9000/admin/facebook-catalog/sync \
  -H "Content-Type: application/json" \
  -d '{
    "catalog_id": "123456789",
    "operation": "UPDATE",
    "batch_size": 5000
  }'

# Sync de SKUs específicos
curl -X POST http://localhost:9000/admin/facebook-catalog/sync \
  -H "Content-Type: application/json" \
  -d '{
    "catalog_id": "123456789",
    "sku_ids": ["sku_abc123", "sku_def456"],
    "operation": "UPDATE"
  }'

# Deletar produtos
curl -X POST http://localhost:9000/admin/facebook-catalog/sync \
  -H "Content-Type: application/json" \
  -d '{
    "catalog_id": "123456789",
    "sku_ids": ["sku_old123"],
    "operation": "DELETE"
  }'
```

### Sync Automático

Sincronização automática acontece via event subscribers:

```typescript
// Atualizar produto → trigger sync automático
await unifiedCatalogService.updateSKU("sku_123", {
  name: "Painel Solar 550W Updated",
  price: 1500
});
// → Evento "catalog.product.updated" → Facebook sync

// Criar produto → trigger sync automático
await unifiedCatalogService.createSKU({
  sku_code: "PANEL-550W-NEW",
  name: "Painel Solar 550W",
  category: "panels"
});
// → Evento "catalog.product.created" → Facebook sync

// Deletar produto → trigger sync automático
await unifiedCatalogService.deleteSKU("sku_123");
// → Evento "catalog.product.deleted" → Facebook delete
```

### Listar Histórico de Syncs

```bash
# Todos os syncs
curl http://localhost:9000/admin/facebook-catalog/syncs

# Filtrar por status
curl "http://localhost:9000/admin/facebook-catalog/syncs?status=completed&limit=20"
```

### Listar Mapeamentos

```bash
# Todos os mapeamentos
curl http://localhost:9000/admin/facebook-catalog/mappings

# Filtrar por SKU
curl "http://localhost:9000/admin/facebook-catalog/mappings?sku_id=sku_abc123"
```

## 📊 Mapeamento de Campos

| Campo YSH | Campo Facebook | Transformação |
|-----------|----------------|---------------|
| `sku_code` | `id` (retailer_id) | Direto |
| `name` + `model_number` | `title` | "Brand Model - Power - Category" |
| `description` | `description` | Direto ou gerado |
| `lowest_price` + offers | `price` | "1000.00 BRL" |
| Stock > 0 | `availability` | "in stock" / "out of stock" |
| `manufacturer.name` | `brand` | Direto |
| `image_urls[0]` | `image_link` | URL principal |
| `image_urls[1..10]` | `additional_image_link` | URLs adicionais |
| `model_number` | `mpn` | Manufacturer Part Number |
| `category` | `google_product_category` | Mapeado para Google Taxonomy |
| `category` | `product_type` | "Energia Solar > Painéis" |
| `warranty_years` | `custom_label_3` | "5y warranty" |

## 🔍 Google Product Taxonomy

Mapeamento de categorias YSH → Google Product Taxonomy:

- `panels` → `1279` (Electronics > Solar Panels)
- `inverters` → `1801` (Electronics > Power Inverters)
- `batteries` → `505371` (Electronics > Batteries)
- `structures` → `632` (Hardware > Building Materials)
- `cables` → `238` (Electronics > Cables)
- Outros → `1801` (Electronics Accessories)

## ⚡ Performance

- **Batch Size**: Max 5000 items por batch (Facebook API limit)
- **Polling Interval**: 2 segundos entre checks de status
- **Max Polling Attempts**: 30 tentativas (60 segundos total)
- **Concurrent Batches**: Processados sequencialmente
- **Change Detection**: Sync hash evita uploads desnecessários

## 🐛 Troubleshooting

### Sync falhou com "Invalid Access Token"

Verificar:
- Token não expirado
- Token tem permissões `catalog_management`
- App está em modo Production (não Development)

```bash
# Testar token
curl "https://graph.facebook.com/v21.0/me?access_token=YOUR_TOKEN"
```

### Produtos não aparecem no Facebook

Verificar:
- Campos obrigatórios preenchidos (id, title, description, price, availability, brand, link, image_link)
- URLs de imagem acessíveis publicamente
- Formato de preço correto ("1000.00 BRL")
- Status do batch: `GET /admin/facebook-catalog/syncs`

### Batch fica em "in_progress" indefinidamente

- Facebook pode levar até 30 segundos para processar
- Verificar erros no batch: `facebook_response.errors`
- Tentar batch menor (500-1000 items)

## 🔐 Segurança

- ⚠️ **Nunca commitar** credenciais no código
- ✅ Usar variáveis de ambiente
- ✅ Restringir access_token a IPs específicos
- ✅ Renovar tokens regularmente
- ✅ Feature flag para desabilitar sync em dev

## 📚 Referências

- [Facebook Catalog API](https://developers.facebook.com/docs/marketing-api/catalog)
- [Catalog Batch API](https://developers.facebook.com/docs/marketing-api/catalog/guides/manage-catalog-items/catalog-batch-api)
- [Product Specification](https://developers.facebook.com/docs/marketing-api/catalog/reference)
- [Google Product Taxonomy](https://support.google.com/merchants/answer/6324436)

## 🚀 Próximos Passos

- [ ] Implementar webhooks do Facebook para sync reverso
- [ ] Dashboard de métricas (Grafana)
- [ ] Retry automático com exponential backoff
- [ ] Suporte a variações de produto (item_group_id)
- [ ] Sync incremental (apenas produtos alterados)
- [ ] Validação de imagens antes do upload
- [ ] Suporte a múltiplos catálogos
