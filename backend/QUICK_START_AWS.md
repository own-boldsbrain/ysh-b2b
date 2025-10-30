# 🚀 MIGRAÇÃO YSH PARA AWS - GUIA RÁPIDO

## ✅ O QUE FOI CRIADO

### 🎯 Scripts Principais
1. **`upload-to-aws.js`** - Maestro que orquestra todo o upload
2. **`sync-facebook-from-aws.js`** - Sincroniza dados AWS com Facebook Catalog
3. **`test-connectivity.js`** - Valida conectividade AWS/Facebook
4. **`verify-aws-setup.js`** - Verifica pré-requisitos
5. **`upload-dashboard.js`** - Dashboard em tempo real
6. **`aws-summary.js`** - Resumo executivo

### 📊 Volumes de Dados
- **937 imagens** → S3 bucket `ysh-b2b-products`
- **3.337 SKUs** → DynamoDB table `ysh-products-catalog`
- **3 plataformas Meta** → Facebook, Instagram, WhatsApp

---

## 🎬 COMO COMEÇAR

### 1️⃣ Ver Resumo Executivo
```bash
node scripts/aws-summary.js
```
Mostra guia passo-a-passo completo com dicas

### 2️⃣ Testar Conectividade
```bash
node scripts/test-connectivity.js
```
Valida AWS, S3, DynamoDB, Facebook

### 3️⃣ Verificar Setup
```bash
node scripts/verify-aws-setup.js
```
Valida credenciais, buckets, tabelas e imagens

### 4️⃣ Abrir Dashboard (em outro terminal)
```bash
node scripts/upload-dashboard.js
```
Monitora progresso em tempo real

### 5️⃣ Executar Upload Principal
```bash
node scripts/upload-to-aws.js
```
Faz upload de 937 imagens + 3.337 SKUs

### 6️⃣ Sincronizar com Facebook
```bash
node scripts/sync-facebook-from-aws.js
```
Sincroniza todos os produtos com 3 plataformas Meta

---

## 🔧 PRÉ-REQUISITOS

### Variáveis de Ambiente `.env`
```bash
# AWS
AWS_ACCESS_KEY_ID=seu_access_key
AWS_SECRET_ACCESS_KEY=seu_secret_access_key
AWS_REGION=us-east-1

# Facebook
FACEBOOK_TOKEN=seu_system_user_token
FACEBOOK_CATALOG_ID=716960371408497

# Opcional
S3_BUCKET=ysh-b2b-products
DYNAMODB_TABLE=ysh-products-catalog
```

### Dependências Node.js
```bash
npm install aws-sdk axios dotenv
```

### AWS Services (devem existir)
- S3 bucket: `ysh-b2b-products`
- DynamoDB table: `ysh-products-catalog`

---

## 📋 ARQUIVOS GERADOS

Após execução bem-sucedida:

| Arquivo | Contém |
|---------|--------|
| `S3_UPLOAD_REPORT.json` | URLs de 937 imagens |
| `DYNAMODB_UPLOAD_REPORT.json` | Schema + amostra SKUs |
| `AWS_UPLOAD_COMPLETE.json` | Status consolidado |
| `FACEBOOK_SYNC_FROM_AWS.json` | Mapping SKU → Facebook ID |

---

## ⏱️ TEMPO ESTIMADO

- Preparação: ~5 min
- Upload S3: ~8 min
- Upload DynamoDB: ~5 min
- Sincronização Facebook: ~30 min
- **Total: 45-60 minutos**

---

## 📞 TROUBLESHOOTING

### Erro "AWS credenciais não configuradas"
```bash
export AWS_ACCESS_KEY_ID=sua_chave
export AWS_SECRET_ACCESS_KEY=seu_segredo
export AWS_REGION=us-east-1
```

### Erro "S3 bucket não encontrado"
Crie manualmente ou use CloudFormation:
```bash
aws cloudformation create-stack \
  --template-body file://aws-cloudformation/main-stack-simple.yml \
  --stack-name ysh-b2b
```

### Erro "DynamoDB table não encontrada"
Execute a mesma stack CloudFormation acima

### Produtos não aparecem no Facebook
Aguarde 1-2 horas e verifique:
1. Permissões do catalog
2. Token Facebook válido
3. Sem erros em `FACEBOOK_SYNC_FROM_AWS.json`

---

## 🎉 RESULTADO ESPERADO

Ao final você terá:

✅ **937 imagens** em S3 com URLs públicas
✅ **3.337 SKUs** em DynamoDB com índices
✅ **3.337 produtos** em Facebook Shops
✅ **3.337 produtos** em Instagram Shopping  
✅ **Catálogo completo** em WhatsApp Business

---

## 📚 DOCUMENTAÇÃO COMPLETA

Consulte `AWS_UPLOAD_GUIDE.md` para detalhes técnicos completos

---

**Status**: ✅ Pronto para começar!
**Próximo passo**: `node scripts/aws-summary.js`
