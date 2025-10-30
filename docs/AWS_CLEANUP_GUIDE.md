# Guia Rápido: Limpeza de Infraestrutura AWS

## 🔐 Passo 1: Login AWS SSO

1. **Acesse o portal**: https://d-9066293405.awsapps.com/start
2. **Faça login** com suas credenciais
3. **Selecione o account** YSH Production (773235999227)
4. **Clique em "Command line or programmatic access"**
5. **Copie as credenciais** (Option 1 ou Option 2)

### Option 1: Variáveis de Ambiente (PowerShell)

```powershell
$env:AWS_ACCESS_KEY_ID="ASIA..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_SESSION_TOKEN="..."
$env:AWS_DEFAULT_REGION="us-east-1"
```

### Option 2: Credentials File

Copie e cole no arquivo `~/.aws/credentials`:

```ini
[ysh-production]
aws_access_key_id=ASIA...
aws_secret_access_key=...
aws_session_token=...
region=us-east-1
```

---

## 🔍 Passo 2: Verificar Recursos (DRY-RUN)

```powershell
# Ativar venv (se ainda não estiver ativo)
.\venv\Scripts\Activate.ps1

# Executar DRY-RUN (não deleta nada)
python scripts\cleanup-aws-infrastructure.py
```

Isso vai listar TODOS os recursos AWS que seriam deletados.

---

## 🗑️ Passo 3: Executar Limpeza Real

**⚠️ ATENÇÃO: Esta ação é IRREVERSÍVEL!**

```powershell
# Executar limpeza real
python scripts\cleanup-aws-infrastructure.py --confirm
```

Você precisará digitar `CONFIRMAR` quando solicitado.

---

## 📊 Recursos que Serão Deletados

Baseado no inventário AWS:

### ECS (Fargate)
- ✅ Cluster: `production-ysh-b2b-cluster`
- ✅ Services: backend, storefront
- ✅ Tasks em execução

### Load Balancer
- ✅ ALB: `production-ysh-b2b-alb`
- ✅ Target Groups (backend, storefront)

### Databases
- ✅ RDS PostgreSQL: `production-ysh-b2b-postgres.cmxiy0wqok6l.us-east-1.rds.amazonaws.com`
- ✅ ElastiCache Redis: `production-ysh-b2b-redis.97x7fb.0001.use1.cache.amazonaws.com`

### Storage
- ✅ S3 Bucket: `production-ysh-media-773235999227` (se existir)
- ✅ Todos os objetos dentro do bucket

### Networking
- ✅ VPC: `vpc-096abb11405bb44af`
- ✅ Subnets (2 privadas, 2 públicas)
- ✅ Security Groups (3)
- ✅ Internet Gateway

### Logs
- ✅ CloudWatch Log Groups (ECS logs)

### CloudFormation
- ✅ Stacks relacionados ao YSH B2B

---

## 💰 Economia Após Limpeza

**Custo atual**: ~$23.70/mês  
**Após limpeza**: $0/mês  

Nova arquitetura (Facebook Commerce + Serverless):
- Railway/Fly.io: ~$5/mês
- Neon PostgreSQL: $0 (Free Tier)
- Cloudflare R2: ~$1/mês
- **Total**: ~$6/mês (75% de economia)

---

## 🚀 Próximos Passos (Após Limpeza)

1. ✅ **Setup Nova Infra**
   - Cloudflare R2 para storage de imagens
   - Railway/Fly.io para Medusa.js backend
   - Vercel/Netlify para Next.js storefront

2. ✅ **Integração Facebook Commerce**
   - Criar Facebook Developer App
   - Setup System User com permissões
   - Configurar Product Catalog
   - Implementar webhooks de pedidos

3. ✅ **Automação de Imagens**
   - Implementar pipeline com modelos Docker locais (Gemma3, SmolLM2)
   - Processar 2.914 produtos
   - Upload para Cloudflare R2
   - Sync com Meta Catalog API

---

## 📞 Suporte

Se encontrar problemas durante a limpeza:

1. **Erro de credenciais**: Refaça login SSO
2. **Recurso não deleta**: Pode ter dependências, aguarde e tente novamente
3. **Timeout**: Alguns recursos (RDS, Redis) levam tempo para deletar (5-10 min)

---

## ⏱️ Tempo Estimado

- **Login SSO**: 2 minutos
- **DRY-RUN**: 1 minuto
- **Limpeza Real**: 10-15 minutos
- **TOTAL**: ~20 minutos

---

**Data**: 2025-10-19  
**Versão**: 1.0.0  
**Status**: Pronto para execução
