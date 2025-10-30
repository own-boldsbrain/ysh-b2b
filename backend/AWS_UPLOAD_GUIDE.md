# 📋 Guia de Upload AWS + Sincronização Facebook

## 🎯 Objetivo
Fazer upload de **937 imagens** para S3 e **3.337 SKUs** para DynamoDB, depois sincronizar com Facebook Catalog.

---

## ✅ Pré-requisitos

### 1. Credenciais AWS
```bash
# Configure as variáveis de ambiente:
export AWS_ACCESS_KEY_ID=seu_access_key
export AWS_SECRET_ACCESS_KEY=seu_secret_access_key
export AWS_REGION=us-east-1

# Ou adicione ao .env:
AWS_ACCESS_KEY_ID=seu_access_key
AWS_SECRET_ACCESS_KEY=seu_secret_access_key
AWS_REGION=us-east-1
```

### 2. Credenciais Facebook
```bash
# No .env, configure:
FACEBOOK_TOKEN=seu_system_user_token
FACEBOOK_CATALOG_ID=716960371408497

# Ou como variáveis:
export FACEBOOK_TOKEN=seu_token
export FACEBOOK_CATALOG_ID=716960371408497
```

### 3. Dependências Node.js
```bash
npm install aws-sdk axios
```

---

## 🚀 Execução

### Opção 1: Upload Maestro (Recomendado)
Executa todos os uploads em sequência:

```bash
node scripts/upload-to-aws.js
```

**Saída esperada:**
```
🚀 UPLOAD COMPLETO PARA AWS - INICIALIZANDO

🔐 ETAPA 0: Verificando Credenciais AWS
✓ AWS_REGION: us-east-1
✓ S3_BUCKET: ysh-b2b-products
✓ DYNAMODB_TABLE: ysh-products-catalog

📸 ETAPA 1: UPLOAD DE IMAGENS PARA S3
✅ Upload de imagens concluído

📦 ETAPA 2: UPLOAD DE SKUs PARA DYNAMODB
✅ Upload de SKUs concluído

🎉 UPLOAD PARA AWS CONCLUÍDO COM SUCESSO!
```

---

### Opção 2: Uploads Individuais

#### 2.1 Upload de Imagens para S3
```bash
node scripts/upload-images-s3.js
```

**Arquivos gerados:**
- `S3_UPLOAD_REPORT.json` - Relatório com mapeamento de URLs

**Exemplo de saída:**
```json
{
  "s3_bucket": "ysh-b2b-products",
  "uploaded_count": 937,
  "error_count": 0,
  "total_size_bytes": 45678901,
  "image_urls": {
    "inversores/Fronius_Primo_5.0-1_jpg": "https://ysh-b2b-products.s3.us-east-1.amazonaws.com/images/products/inversores/Fronius_Primo_5.0-1.jpg",
    ...
  }
}
```

#### 2.2 Upload de SKUs para DynamoDB
```bash
node scripts/upload-skus-dynamodb.js
```

**Arquivos gerados:**
- `DYNAMODB_UPLOAD_REPORT.json` - Relatório com schema e amostra

**Exemplo de saída:**
```json
{
  "dynamodb_table": "ysh-products-catalog",
  "uploaded_count": 3337,
  "error_count": 0,
  "schema": {
    "partition_key": "SKU#",
    "sort_key": "PRODUCT#",
    "indexes": ["sku_code", "category", "manufacturer_id", "synced_at"]
  }
}
```

---

## 🔄 Sincronização com Facebook

Após confirmar uploads, sincronizar com Facebook Catalog:

```bash
node scripts/sync-facebook-from-aws.js
```

**Saída esperada:**
```
🚀 SINCRONIZAÇÃO AWS → FACEBOOK INICIANDO

📥 Carregando URLs de imagens do S3...
✓ 937 URLs carregadas

📦 Carregando SKUs do DynamoDB...
✓ 3337 SKUs carregados do DynamoDB

📊 Total de SKUs para sincronizar: 3337

📤 Lote 1/34 (100 SKUs)...
....................................................
✓ Lote 1 concluído
  Sucesso: 100, Falhas: 0

...

📋 RELATÓRIO FINAL DE SINCRONIZAÇÃO
Total de SKUs: 3337
✅ Sincronizados: 3337
❌ Falhados: 0
Taxa de sucesso: 100.0%

✅ Sincronização concluída!
```

**Arquivo gerado:**
- `FACEBOOK_SYNC_FROM_AWS.json` - Mapeamento de SKU → Facebook Product ID

---

## 📊 Relatórios Gerados

| Arquivo | Conteúdo | Uso |
|---------|----------|-----|
| `AWS_UPLOAD_COMPLETE.json` | Status de ambos uploads | Verificação de progresso |
| `S3_UPLOAD_REPORT.json` | URLs de 937 imagens | Referência para DynamoDB |
| `DYNAMODB_UPLOAD_REPORT.json` | Schema e amostra | Verificação de estrutura |
| `FACEBOOK_SYNC_FROM_AWS.json` | Mapeamento SKU→Facebook ID | Rastreamento de sincronização |

---

## 🔍 Verificação

### Verificar S3
```bash
aws s3 ls s3://ysh-b2b-products/images/products/ --recursive --region us-east-1
```

**Saída esperada:**
```
2024-01-15 10:30:45    12345 images/products/inversores/Fronius_Primo_5.0-1.jpg
2024-01-15 10:30:46     8901 images/products/inversores/Fronius_Primo_8.2-1.jpg
...
```

### Verificar DynamoDB
```bash
aws dynamodb describe-table \
  --table-name ysh-products-catalog \
  --region us-east-1 \
  --query 'Table.ItemCount'
```

**Saída esperada:**
```
3337
```

### Verificar Facebook Catalog
```bash
curl -s "https://graph.facebook.com/v21.0/716960371408497?fields=item_count&access_token=$FACEBOOK_TOKEN"
```

**Saída esperada:**
```json
{
  "item_count": 3337,
  "id": "716960371408497"
}
```

---

## 🐛 Troubleshooting

### Erro: "AWS credenciais não configuradas"
```bash
# Solução:
export AWS_ACCESS_KEY_ID=sua_chave
export AWS_SECRET_ACCESS_KEY=seu_segredo
export AWS_REGION=us-east-1
```

### Erro: "S3 bucket não encontrado"
```bash
# Solução: Criar bucket manualmente
aws s3 mb s3://ysh-b2b-products --region us-east-1
```

### Erro: "DynamoDB table não encontrada"
```bash
# Solução: Criar tabela manualmente ou usar CloudFormation
aws cloudformation create-stack \
  --template-body file://aws-cloudformation/main-stack-simple.yml \
  --stack-name ysh-b2b
```

### Erro: "Taxa de requisição Facebook excedida"
```
# Script automaticamente respeita rate limit com delays
# Se ainda assim errar, aguarde 60 segundos e reexecute:
node scripts/sync-facebook-from-aws.js
```

### Erro: "FACEBOOK_TOKEN inválido"
```bash
# Verifique permissões:
node scripts/check-facebook-permissions.js

# Se expirou, obtenha novo token em Facebook Business Manager
# Copie em .env: FACEBOOK_TOKEN=novo_token
```

---

## 📱 Validar em Plataformas Meta

Após sincronização completa:

### 1. Facebook Commerce Manager
- Acesse: https://business.facebook.com
- Navegue para Catálogos → ysh-products-catalog
- Verifique: "3.337 produtos"

### 2. Instagram Shopping
- Acesse seu perfil Instagram
- Vá para: Loja → Produtos
- Verifique: Todos os 3.337 produtos aparecem

### 3. WhatsApp Business
- Acesse: https://business.facebook.com/wa
- Catálogos → ysh-products-catalog
- Teste envio de produtos via ChatBot

---

## 🎯 Próximas Etapas

1. ✅ Upload S3 (937 imagens)
2. ✅ Upload DynamoDB (3.337 SKUs)
3. ✅ Sincronização Facebook
4. ⏳ Validar em plataformas Meta
5. ⏳ Monitorar performance
6. ⏳ Otimizar imagens se necessário

---

## 📞 Suporte

Para erros, consulte:
- `S3_UPLOAD_REPORT.json` → status S3
- `DYNAMODB_UPLOAD_REPORT.json` → status DynamoDB
- `FACEBOOK_SYNC_FROM_AWS.json` → erros de sincronização
- Logs no console (ctrl+c para interromper)

---

**Tempo estimado total:** 15-30 minutos
