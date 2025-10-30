# Multi-Platform Commerce Integration (Meta Ecosystem)

## 🌐 Plataformas Suportadas

### Facebook Shops
- **Catálogo principal** - Todos os produtos sincronizados
- **Facebook Marketplace** - Venda direta
- **Ads Catalog** - Anúncios dinâmicos
- **Collection Ads** - Anúncios imersivos

### Instagram Shopping
- **Product Tags** - Tags em posts e stories
- **Instagram Shop** - Loja nativa no perfil
- **Checkout** - Compra sem sair do Instagram
- **Shopping from Creators** - Parcerias com influencers

### WhatsApp Business Catalog
- **Catálogo compartilhável** - Enviado em conversas
- **Product Messages** - Mensagens com produtos individuais
- **Catalog Messages** - Lista com múltiplos produtos (max 30)
- **WhatsApp Business API** - Integração programática

## 🔄 Como Funciona

### Catálogo Unificado

**1 catálogo → 3 plataformas**

```
YSH Catalog (PostgreSQL)
         ↓
Facebook Commerce Catalog API
         ↓
    ┌────┴────┬────────────┐
    ↓         ↓            ↓
Facebook  Instagram   WhatsApp
 Shops    Shopping    Catalog
```

**Mesmo sync atualiza todas as plataformas simultaneamente!**

## 🚀 Setup Multi-Plataforma

### Passo 1: Criar Facebook App

1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Criar novo app → Tipo: **Business**
3. Adicionar produtos:
   - **Catalog** (obrigatório)
   - **Instagram** (opcional)
   - **WhatsApp** (opcional)

### Passo 2: Criar Catálogo

1. [Commerce Manager](https://business.facebook.com/commerce/)
2. **Catalog** → Create Catalog → **E-commerce**
3. Anotar **Catalog ID**

### Passo 3: Conectar Instagram (Opcional)

1. Ter Instagram Business Account
2. Commerce Manager → Catalog → Sales Channels
3. Add Sales Channel → **Instagram Shopping**
4. Conectar Instagram account
5. Aguardar aprovação (1-3 dias)
6. Anotar **Instagram Account ID**

### Passo 4: Conectar WhatsApp (Opcional)

1. Ter WhatsApp Business Account
2. Commerce Manager → Catalog → Sales Channels
3. Add Sales Channel → **WhatsApp**
4. Conectar WhatsApp Business Account
5. Anotar:
   - **WhatsApp Business Account ID**
   - **Phone Number ID**

### Passo 5: Gerar Access Token

1. Graph API Explorer
2. Permissões:
   - `catalog_management`
   - `instagram_basic` (se usar Instagram)
   - `instagram_shopping_tag_products`
   - `whatsapp_business_management` (se usar WhatsApp)
   - `whatsapp_business_messaging`
3. Gerar **Long-Lived Token** (60 dias)

### Passo 6: Configurar YSH Backend

```bash
# .env
FACEBOOK_APP_ID=123456789
FACEBOOK_APP_SECRET=abc123...
FACEBOOK_ACCESS_TOKEN=EAAx...
FACEBOOK_CATALOG_ID=987654321

# Instagram (opcional)
INSTAGRAM_ACCOUNT_ID=17841400...

# WhatsApp (opcional)
WHATSAPP_BUSINESS_ACCOUNT_ID=102938...
WHATSAPP_PHONE_NUMBER_ID=556199...
```

## 📡 Endpoints Multi-Plataforma

### Verificar Status das Plataformas

```bash
GET /admin/facebook-catalog/platforms/status

Response:
{
  "platforms": {
    "facebook": {
      "platform": "facebook",
      "enabled": true,
      "catalog_info": {
        "id": "987654321",
        "name": "YSH Solar Catalog",
        "product_count": 1250
      }
    },
    "instagram": {
      "platform": "instagram",
      "enabled": true,
      "connected": true,
      "account_id": "17841400..."
    },
    "whatsapp": {
      "platform": "whatsapp",
      "enabled": true,
      "connected": true,
      "business_account_id": "102938...",
      "phone_number_id": "556199..."
    }
  },
  "summary": {
    "total_platforms": 3,
    "enabled_platforms": 3,
    "catalog_id": "987654321"
  }
}
```

### Conectar Plataformas

```bash
# Conectar Instagram
POST /admin/facebook-catalog/platforms/connect
{
  "platform": "instagram"
}

# Conectar WhatsApp
POST /admin/facebook-catalog/platforms/connect
{
  "platform": "whatsapp"
}

# Conectar todas
POST /admin/facebook-catalog/platforms/connect
{
  "platform": "all"
}
```

### WhatsApp: Enviar Produto Individual

```bash
POST /admin/facebook-catalog/whatsapp/send-product
{
  "to": "5561999887766",  # Com código do país
  "sku_code": "PANEL-550W-CANADIAN",
  "message": "Confira nosso painel solar 550W!"
}
```

**Resultado**: Cliente recebe mensagem WhatsApp com card do produto (imagem, preço, descrição, botão "Visualizar no catálogo")

### WhatsApp: Enviar Catálogo (Lista de Produtos)

```bash
POST /admin/facebook-catalog/whatsapp/send-catalog
{
  "to": "5561999887766",
  "sku_codes": [
    "PANEL-550W-CANADIAN",
    "INVERTER-3KW-GROWATT",
    "BATTERY-100AH-MOURA"
  ],
  "header": "Kits Solares YSH",
  "message": "Escolha os componentes do seu sistema solar:"
}
```

**Resultado**: Cliente recebe mensagem com lista de produtos (max 30)

## 🎯 Casos de Uso

### 1. Facebook Shops

**Objetivo**: Loja completa no Facebook

```bash
# Sync automático
POST /admin/facebook-catalog/sync
{
  "catalog_id": "987654321",
  "operation": "UPDATE"
}

# Resultado:
# - Produtos aparecem em facebook.com/shop/ysh-solar
# - Disponíveis para Marketplace
# - Usados em Ads Catalog
```

### 2. Instagram Shopping

**Objetivo**: Tags em posts + Instagram Shop

**Setup**:
1. Sync produtos (automático após conectar)
2. Posts/Stories: Tag produtos manualmente
3. Shop tab: Produtos aparecem automaticamente

**Fluxo do cliente**:
```
Ver post → Clicar tag → Ver produto → Comprar
Ver perfil → Shop tab → Ver catálogo → Comprar
```

### 3. WhatsApp Business Catalog

**Objetivo**: Venda por conversação

**Cenário 1: Atendimento Ativo**
```typescript
// Cliente: "Quero um painel solar 550W"
// Atendente usa API:
POST /admin/facebook-catalog/whatsapp/send-product
{
  "to": "5561999887766",
  "sku_code": "PANEL-550W-CANADIAN",
  "message": "Esse modelo atende suas necessidades!"
}
// Cliente recebe card do produto
```

**Cenário 2: Envio de Orçamento**
```typescript
// Cliente: "Preciso de um kit completo"
POST /admin/facebook-catalog/whatsapp/send-catalog
{
  "to": "5561999887766",
  "sku_codes": ["PANEL-550W", "INVERTER-3KW", "BATTERY-100AH"],
  "header": "Orçamento Kit Solar 3kW",
  "message": "Componentes do seu sistema:"
}
// Cliente recebe lista interativa
```

## 📊 Rastreamento Multi-Plataforma

### Model: FacebookCatalogSync

```typescript
{
  id: "fbsync_123",
  catalog_id: "987654321",
  platforms: ["facebook", "instagram", "whatsapp"], // Onde foi sincronizado
  operation: "UPDATE",
  status: "completed",
  total_items: 1250,
  items_created: 50,
  items_updated: 1200
}
```

### Model: FacebookProductMapping

```typescript
{
  id: "fbprod_456",
  sku_id: "sku_abc123",
  sku_code: "PANEL-550W-CANADIAN",
  catalog_id: "987654321",
  synced_platforms: ["facebook", "instagram", "whatsapp"], // Disponível em
  status: "active",
  last_synced_at: "2025-10-20T10:30:00Z"
}
```

## ⚡ Performance Multi-Plataforma

**1 sync = 3 plataformas atualizadas**

- **Facebook Shops**: Atualização imediata (2-5 min)
- **Instagram Shopping**: Atualização em 15-30 min
- **WhatsApp Catalog**: Atualização imediata

**Batch size**: 5000 produtos/batch (todas as plataformas)

## 🔐 Permissões Necessárias

### Facebook Shops (Obrigatório)
- ✅ `catalog_management`

### Instagram Shopping (Opcional)
- ✅ `instagram_basic`
- ✅ `instagram_shopping_tag_products`
- ✅ `pages_read_engagement` (para Instagram Business)

### WhatsApp Business (Opcional)
- ✅ `whatsapp_business_management`
- ✅ `whatsapp_business_messaging`

## 📚 Recursos Meta

- [Commerce Platform Overview](https://developers.facebook.com/docs/commerce-platform)
- [Instagram Shopping Setup](https://business.facebook.com/business/help/instagram-shopping)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/business-management-api)
- [Catalog Best Practices](https://developers.facebook.com/docs/commerce-platform/catalog/best-practices)

## 🎯 Próximos Passos

- [ ] Instagram Stories API (auto-tag produtos)
- [ ] WhatsApp Webhooks (responder pedidos)
- [ ] Facebook Pixel (tracking conversões)
- [ ] Product Collections (kits solares)
- [ ] Multi-currency support (exportação internacional)
