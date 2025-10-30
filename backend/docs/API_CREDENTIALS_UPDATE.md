# 🔐 Atualização de Credenciais de API

**Data:** 19 de outubro de 2025  
**Atualizado:** Credenciais de produção e homologação

---

## 🆕 NOVAS CREDENCIAIS ADICIONADAS

### 1. Hugging Face MCP Server

**Tipo:** Model Context Protocol Server  
**Ambiente:** Produção

#### Token de Acesso (Write)

```tsx
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
```

#### Configuração MCP

```json
{
  "servers": {
    "hf-mcp-server": {
      "url": "https://huggingface.co/mcp?login"
    }
  }
}
```

#### Uso Recomendado

- Upload de datasets ANEEL (210 CSVs)
- Acesso a modelos via MCP
- Integração com Hugging Face Hub API
- Pesquisa de papers e modelos

#### Comandos de Autenticação

```bash
# CLI Login
huggingface-cli login --token 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

# Verificar login
huggingface-cli whoami

# Variável de ambiente
export HF_TOKEN=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
```

#### Referências

- Token URL: https://huggingface.co/settings/tokens
- MCP Docs: https://huggingface.co/docs/mcp
- Datasets API: https://huggingface.co/docs/datasets

---

### 2. Cielo API Gateway (Nova Merchant)

**Tipo:** Gateway de Pagamentos  
**Ambiente:** Produção  
**Status:** Ativa

#### Merchant ID

```tsx
0a30c1b0-472a-472f-bf70-5250e1f1006b
```

#### Merchant Key

```tsx
nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS
```

#### Endpoints

```tsx
Produção: https://api.cielo.com.br
Sandbox: https://api2.cielo.com.br
```

#### Configuração de Autenticação

```bash
# Headers obrigatórios
MerchantId: 0a30c1b0-472a-472f-bf70-5250e1f1006b
MerchantKey: nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS
Content-Type: application/json
```

#### Exemplo de Requisição (Criar Transação)

```bash
curl -X POST https://api.cielo.com.br/1/sales \
  -H "Content-Type: application/json" \
  -H "MerchantId: 0a30c1b0-472a-472f-bf70-5250e1f1006b" \
  -H "MerchantKey: nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS" \
  -d '{
    "MerchantOrderId": "2025101901",
    "Customer": {
      "Name": "Cliente Teste"
    },
    "Payment": {
      "Type": "CreditCard",
      "Amount": 15700,
      "Installments": 1,
      "CreditCard": {
        "CardNumber": "4551870000000181",
        "Holder": "Teste Holder",
        "ExpirationDate": "12/2030",
        "SecurityCode": "123",
        "Brand": "Visa"
      }
    }
  }'
```

#### Comparação com Merchant Antiga

| Item | Merchant Antiga | Nova Merchant |
|------|----------------|---------------|
| **Merchant ID** | `a8cc1b3f-3407-4d0e-94b6-d18a7de36ac3` | `0a30c1b0-472a-472f-bf70-5250e1f1006b` |
| **Merchant Key** | N/A (usava Client ID/Secret) | `nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS` |
| **Autenticação** | OAuth2 (Client ID + Secret) | MerchantId + MerchantKey direto |
| **Modelo** | API 3.0 Link de Pagamento | API 1.0 E-commerce Cielo |
| **Uso Recomendado** | Link de pagamento | Transações diretas |

#### Referências

- Docs API: https://developercielo.github.io/manual/cielo-ecommerce
- Sandbox: https://sandbox.cieloecommerce.cielo.com.br
- Status API: https://status.cielo.com.br

---

### 3. Asaas API (Homologação)

**Tipo:** Gateway de Pagamentos/Cobrança  
**Ambiente:** Homologação (Sandbox)  
**Status:** Ativa

#### Token de Acesso (Sandbox)

```tsx
$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmMyYzc3ZGI0LWVlMTctNDA5MC1iMTU3LWVlYjgyYjI1MWY4MDo6JGFhY2hfNmNiZTBkNTctNTBhZS00NmM0LTgyMTgtY2I5NGUwYTNiYjJi
```

#### Endpoints

```tsx
Produção: https://api.asaas.com/v3
Sandbox: https://sandbox.asaas.com/api/v3
```

```tsx
Produção: https://api.asaas.com/v3
Sandbox: https://sandbox.asaas.com/api/v3
```

#### Configuração de Autenticação

```bash
# Header obrigatório
access_token: $aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmMyYzc3ZGI0LWVlMTctNDA5MC1iMTU3LWVlYjgyYjI1MWY4MDo6JGFhY2hfNmNiZTBkNTctNTBhZS00NmM0LTgyMTgtY2I5NGUwYTNiYjJi
```

#### Exemplo de Requisição (Listar Clientes)

```bash
curl -X GET https://sandbox.asaas.com/api/v3/customers \
  -H "access_token: \$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmMyYzc3ZGI0LWVlMTctNDA5MC1iMTU3LWVlYjgyYjI1MWY4MDo6JGFhY2hfNmNiZTBkNTctNTBhZS00NmM0LTgyMTgtY2I5NGUwYTNiYjJi"
```

#### Comparação Produção vs Homologação

| Item | Produção (yello-v1) | Homologação (Nova) |
|------|--------------------|--------------------|
| **Token** | `$aact_prod_000...ZGRl` | `$aact_hmlg_000...YjJi` |
| **Ambiente** | Produção | Sandbox |
| **API Base** | `https://api.asaas.com/v3` | `https://sandbox.asaas.com/api/v3` |
| **Criado em** | 22/05/2025 | 19/10/2025 |
| **Uso Recomendado** | Cobranças reais | Testes e desenvolvimento |

#### Referências

- Docs API: https://docs.asaas.com
- Dashboard Sandbox: https://sandbox.asaas.com
- Dashboard Produção: https://app.asaas.com

---

## 📊 RESUMO CONSOLIDADO DE CREDENCIAIS

### APIs Ativas por Categoria

#### 🤖 Inteligência Artificial (8)

1. ✅ **Google Gemini** - 48 modelos (produção)
2. ✅ **Groq** - 19 modelos ultra-rápidos (produção)
3. ✅ **Groq Vercel** - 19 modelos (backup)
4. ✅ **Together AI** - 100+ modelos (produção)
5. ✅ **Replicate** - ML/AI (produção)
6. ✅ **Hugging Face** - MCP + Hub (produção) 🆕
7. ❌ **OpenAI** - Chave inválida
8. ⚠️ **XAI/Grok** - Créditos esgotados

#### 💳 Pagamentos (3)

1. ✅ **Asaas Produção** - yello-v1 (ativa)
2. ✅ **Asaas Homologação** - Sandbox (ativa) 🆕
3. ✅ **Cielo Nova Merchant** - E-commerce API 1.0 (ativa) 🆕
4. 🟡 **Cielo Antiga** - Link API 3.0 (não testada)
5. 🟡 **Stripe** - Não testada

#### 🗄️ Banco de Dados (2)

1. 🟡 **Neon Postgres (Principal)** - us-east-2
2. 🟡 **Neon Postgres (Vercel)** - sa-east-1

#### 🔄 Cache/Storage (3)

1. ❌ **Upstash Redis (Principal)** - Falha conexão
2. ❌ **Upstash Redis (Vercel)** - Falha conexão
3. 🟡 **Vercel Blob Storage** - Não testada

#### 🗺️ Mapas/Geolocalização (2)

1. 🟡 **MapTiler** - Não testada
2. 🟡 **Sentinel Hub** - Earth observation

#### 🔧 DevOps/Infraestrutura (4)

1. 🟡 **GitHub PAT** - Não testada
2. 🟡 **Google OAuth** - Não testada
3. 🟡 **Hypertune** - Feature flags
4. ✅ **AWS CloudFormation** - Stack criada

**Total:** 22 APIs/Services

---

## 🔒 BOAS PRÁTICAS DE SEGURANÇA

### ✅ Checklist Implementado

- [x] Tokens separados por ambiente (prod/sandbox)
- [x] Documentação centralizada
- [x] Múltiplos provedores de IA (fallback)
- [x] Credenciais de pagamento homologação disponível

### ⚠️ Ações Pendentes

- [ ] Regenerar OpenAI API Key
- [ ] Recarregar créditos XAI (2 teams)
- [ ] Corrigir conexão Upstash Redis (2 instâncias)
- [ ] Testar integração Neon Postgres
- [ ] Implementar rotação automática de secrets (AWS Secrets Manager)
- [ ] Configurar alertas de expiração de tokens
- [ ] Documentar fluxo de deploy com secrets

### 🔐 Armazenamento Seguro

#### Desenvolvimento Local

```bash
# .env (nunca commitar!)
HF_TOKEN=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
CIELO_MERCHANT_ID=0a30c1b0-472a-472f-bf70-5250e1f1006b
CIELO_MERCHANT_KEY=nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS
ASAAS_SANDBOX_TOKEN=$aact_hmlg_000...YjJi
```

#### AWS Secrets Manager (Produção)

```bash
# Criar secrets
aws secretsmanager create-secret \
  --name ysh-backend/huggingface-token \
  --secret-string "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" \
  --region us-east-1

aws secretsmanager create-secret \
  --name ysh-backend/cielo-merchant-id \
  --secret-string "0a30c1b0-472a-472f-bf70-5250e1f1006b" \
  --region us-east-1

aws secretsmanager create-secret \
  --name ysh-backend/cielo-merchant-key \
  --secret-string "nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS" \
  --region us-east-1

# Recuperar secrets
aws secretsmanager get-secret-value \
  --secret-id ysh-backend/huggingface-token \
  --query SecretString \
  --output text
```

#### Vercel Environment Variables

```bash
# Via CLI
vercel env add HF_TOKEN production
vercel env add CIELO_MERCHANT_ID production
vercel env add CIELO_MERCHANT_KEY production
vercel env add ASAAS_SANDBOX_TOKEN development
```

---

## 🧪 COMANDOS DE TESTE

### Hugging Face

```bash
# Verificar autenticação
huggingface-cli whoami

# Listar datasets do usuário
huggingface-cli repo ls fernando-bold --include "*.csv"

# Upload teste
echo "test,data" > test.csv
huggingface-cli upload fernando-bold/test-dataset test.csv
```

### Cielo (Nova Merchant)

```bash
# Consultar transação
curl https://api.cielo.com.br/1/sales/{PaymentId} \
  -H "MerchantId: 0a30c1b0-472a-472f-bf70-5250e1f1006b" \
  -H "MerchantKey: nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS"

# Capturar transação
curl -X PUT https://api.cielo.com.br/1/sales/{PaymentId}/capture \
  -H "MerchantId: 0a30c1b0-472a-472f-bf70-5250e1f1006b" \
  -H "MerchantKey: nvnQqx3clFFY86dtD9PimFHDfgROh7zkEpXe6BGS"
```

### Asaas (Homologação)

```bash
# Criar cliente teste
curl -X POST https://sandbox.asaas.com/api/v3/customers \
  -H "access_token: \$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmMyYzc3ZGI0LWVlMTctNDA5MC1iMTU3LWVlYjgyYjI1MWY4MDo6JGFhY2hfNmNiZTBkNTctNTBhZS00NmM0LTgyMTgtY2I5NGUwYTNiYjJi" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cliente Teste Helios",
    "email": "teste@yelloenergia.com.br",
    "cpfCnpj": "12345678901"
  }'

# Criar cobrança teste
curl -X POST https://sandbox.asaas.com/api/v3/payments \
  -H "access_token: \$aact_hmlg_000..." \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "{customerId}",
    "billingType": "CREDIT_CARD",
    "value": 100.00,
    "dueDate": "2025-10-30"
  }'
```

---

## 📈 PRÓXIMOS PASSOS

### Prioridade Alta

1. ✅ Autenticar Hugging Face CLI com novo token
2. ✅ Testar upload de 1 CSV ANEEL para validação
3. ✅ Configurar Nova Merchant Cielo no backend
4. ✅ Testar fluxo de pagamento em sandbox Asaas
5. ⏳ Migrar secrets para AWS Secrets Manager

### Prioridade Média

6. ⏳ Implementar fallback entre Cielo merchants
7. ⏳ Criar ambiente de testes isolado (Asaas sandbox)
8. ⏳ Documentar fluxo de integração Hugging Face MCP
9. ⏳ Configurar alertas de quota/limite de APIs

### Prioridade Baixa

10. ⏳ Implementar rate limiting por API
11. ⏳ Dashboard de monitoramento de custos
12. ⏳ Auditoria completa de todas as 22 APIs

---

## 📚 REFERÊNCIAS

### Documentação Oficial

- Hugging Face Hub: https://huggingface.co/docs/hub
- Hugging Face MCP: https://huggingface.co/docs/mcp
- Cielo E-commerce: https://developercielo.github.io/manual/cielo-ecommerce
- Asaas API: https://docs.asaas.com
- AWS Secrets Manager: https://docs.aws.amazon.com/secretsmanager

### Arquivos Relacionados

- `docs/API_STATUS_REPORT.md` - Status completo de todas as APIs
- `secrets/README.md` - Guia de gerenciamento de secrets
- `data/project-helios/upload_to_huggingface.py` - Script de upload ANEEL

---

**Documento Gerado por:** GitHub Copilot  
**Para:** Projeto YSH B2B - Helios HaaS Platform  
**Última Atualização:** 19/10/2025
