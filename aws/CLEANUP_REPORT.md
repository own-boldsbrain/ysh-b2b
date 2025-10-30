# ✅ Ambiente AWS Limpo - Reset Completo

**Data:** 19 de outubro de 2025  
**Account ID:** 773235999227  
**Region:** us-east-1

---

## 🧹 Limpeza Executada

### ✅ Recursos Removidos

**ECS Services:**

- ❌ `ysh-b2b-backend` (DELETADO)
- ❌ `ysh-b2b-storefront` (DELETADO)

**Task Definitions:**

- ❌ 15 versões de `ysh-b2b-backend` (DEREGISTRADAS)
- ❌ 9 versões de `ysh-b2b-storefront` (DEREGISTRADAS)
- **Total:** 24 task definitions removidas

**Configuração Local:**

- ❌ Perfil SSO `ysh-production` (REMOVIDO)
- ✅ Perfil `default` (MANTIDO)
- ❌ Arquivos temporários (REMOVIDOS)

---

## 🏗️ Infraestrutura Mantida

### CloudFormation Stack: `production-ysh-stack`

**Status:** ✅ ATIVO (recursos provisionados mas inativos)

| Recurso | ID/Endpoint | Status |
|---------|-------------|--------|
| **VPC** | `vpc-096abb11405bb44af` | ✅ Ativo |
| **Private Subnet 1** | `subnet-0a7620fdf057a8824` | ✅ Ativo |
| **Private Subnet 2** | `subnet-09c23e75aed3a5d76` | ✅ Ativo |
| **ECS Security Group** | `sg-06563301eba0427b2` | ✅ Ativo |
| **ALB Security Group** | `sg-04504f1416350279a` | ✅ Ativo |
| **DB Security Group** | `sg-0ed77cd5394f86cad` | ✅ Ativo |
| **RDS PostgreSQL** | `production-ysh-b2b-postgres.cmxiy0wqok6l...` | ✅ Ativo |
| **ElastiCache Redis** | `production-ysh-b2b-redis.97x7fb...` | ✅ Ativo |
| **ALB** | `production-ysh-b2b-alb-1849611639...` | ✅ Ativo |
| **ECS Cluster** | `production-ysh-b2b-cluster` | ✅ Ativo (vazio) |
| **Secrets Manager** | 8 secrets ativos | ✅ Ativo |

---

## 💰 Impacto de Custos

### Custos Antes da Limpeza (~$48/mês)

```tsx
ECS Backend (1 vCPU, 2GB):       $29.64
ECS Storefront (0.5 vCPU, 1GB):  $14.82
Secrets Manager (8 secrets):     $3.20
Route53 Hosted Zone:             $0.50
────────────────────────────────────────
TOTAL:                           $48.16/mês
```

### Custos Após Limpeza (~$4/mês)

```tsx
RDS PostgreSQL (idle):           FREE tier
ElastiCache Redis (idle):        FREE tier
ALB (sem targets):               FREE tier
ECS Cluster (vazio):             $0.00
Secrets Manager (8 secrets):     $3.20
Route53 Hosted Zone:             $0.50
────────────────────────────────────────
TOTAL:                           ~$3.70/mês
```

**💡 Economia:** $44.46/mês (92% redução)

---

## 🚀 Próximos Passos - Nova Estratégia

### Opção 1: Deploy com Docker Images Atualizadas

**1. Build e Push de Novas Images:**

```powershell
# Backend
cd backend
docker build -t ysh-backend:latest .

# Login ECR (criar profile primeiro)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 773235999227.dkr.ecr.us-east-1.amazonaws.com

# Tag e Push
docker tag ysh-backend:latest 773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:v2.0.0
docker push 773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:v2.0.0

# Repetir para storefront
cd ../storefront
docker build -t ysh-storefront:latest .
docker tag ysh-storefront:latest 773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-storefront:v2.0.0
docker push 773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-storefront:v2.0.0
```

**2. Criar Nova Task Definition:**

```powershell
# Atualizar task definitions com novas images
# backend-task-definition.json - mudar para v2.0.0
# storefront-task-definition.json - mudar para v2.0.0
```

**3. Deploy via Scripts:**

```powershell
cd aws
.\1-deploy-ecs-tasks.ps1 -BackendImage 773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:v2.0.0
```

---

### Opção 2: Deploy com Configuração Mínima (Teste)

**1. Usar Imagens Públicas Temporariamente:**

```powershell
# Testar com Node.js Alpine genérico
.\1-deploy-ecs-tasks.ps1 -BackendImage public.ecr.aws/docker/library/node:20-alpine
```

**2. Configurar Variáveis de Ambiente no Task:**

- DATABASE_URL via Secrets Manager
- REDIS_URL via Secrets Manager
- JWT_SECRET, COOKIE_SECRET
- PORT=9000 (backend), PORT=8000 (storefront)

---

### Opção 3: Rebuild Completo da Infraestrutura

**1. Deletar Stack Atual:**

```powershell
aws cloudformation delete-stack --stack-name production-ysh-stack --profile default --region us-east-1
```

**2. Aguardar Deleção (15-30 min)**

**3. Criar Novo Stack com Configurações Otimizadas:**

```powershell
# Usar cloudformation-infrastructure.yml atualizado
# ou cloudformation-free-tier.yml
```

---

## 📋 Checklist para Nova Estratégia

### Pré-Requisitos

- [ ] Decidir qual opção seguir (1, 2 ou 3)
- [ ] Configurar credenciais AWS (SSO ou Access Keys)
- [ ] Validar imagens Docker existem (ou build novas)
- [ ] Revisar task definitions

### Deploy

- [ ] Criar/atualizar task definitions
- [ ] Registrar task definitions no ECS
- [ ] Criar ECS services (backend + storefront)
- [ ] Aguardar tasks entrarem em RUNNING
- [ ] Validar health checks

### Validação

- [ ] Backend health: `/health` retorna 200
- [ ] Storefront carrega sem erros
- [ ] ALB target groups healthy
- [ ] CloudWatch logs sem erros críticos

### Post-Deploy

- [ ] Executar migrations (se opção 1)
- [ ] Criar admin user
- [ ] Configurar publishable key
- [ ] Configurar monitoring
- [ ] Configurar billing alerts

---

## 🔧 Comandos Úteis (Reconfigurar AWS CLI)

### Opção A: Configurar SSO Novamente

```powershell
# Criar perfil SSO
$configContent = @"
[default]
region = us-east-1
output = json

[sso-session ysh-dev]
sso_start_url = https://d-9066293405.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access

[profile ysh-production]
sso_session = ysh-dev
sso_account_id = 773235999227
sso_role_name = AdministratorAccess
region = us-east-1
output = json
"@

Set-Content -Path ~/.aws/config -Value $configContent

# Login
aws sso login --profile ysh-production
```

### Opção B: Usar Access Keys com Default Profile

```powershell
aws configure
# AWS Access Key ID: [sua key]
# AWS Secret Access Key: [seu secret]
# Default region name: us-east-1
# Default output format: json
```

---

## 📊 Status Atual do Ambiente

| Componente | Status | Observação |
|------------|--------|------------|
| **ECS Services** | ❌ Nenhum | Todos deletados |
| **ECS Tasks** | ❌ Nenhum | Cluster vazio |
| **Task Definitions** | ❌ Deregistradas | 24 versões removidas |
| **Docker Images ECR** | ⚠️ Verificar | Podem existir mas não validado |
| **CloudFormation Stack** | ✅ Ativo | Infraestrutura base mantida |
| **RDS Database** | ✅ Ativo | Sem conexões ativas |
| **Redis Cache** | ✅ Ativo | Sem conexões ativas |
| **Load Balancer** | ✅ Ativo | Sem targets healthy |
| **Secrets Manager** | ✅ Ativo | 8 secrets disponíveis |
| **AWS CLI Config** | ✅ Default only | Profile SSO removido |

---

## 💡 Recomendações

### Imediato

1. **Decidir estratégia de deploy:** Opção 1 (rebuild images) recomendada
2. **Configurar AWS CLI:** SSO ou Access Keys
3. **Validar/build Docker images:** Garantir images funcionais

### Curto Prazo

1. **Implementar CI/CD:** GitHub Actions para automação
2. **Otimizar custos:** FARGATE_SPOT após validação
3. **Configurar monitoring:** CloudWatch alarms + dashboard

### Médio Prazo

1. **Auto-scaling:** Baseado em CPU/Memory
2. **Blue/green deploys:** Minimizar downtime
3. **Disaster recovery:** Backup strategy + runbook

---

## 🎯 Métricas de Sucesso (Próximo Deploy)

- [ ] Tasks RUNNING sem erros < 5 minutos após deploy
- [ ] Health checks passando 100%
- [ ] Backend response time < 500ms (P95)
- [ ] Storefront loading < 2s
- [ ] Zero errors em CloudWatch logs (primeira hora)
- [ ] Custo mensal < $50 (com otimizações < $30)

---

**Status:** 🟢 AMBIENTE LIMPO E PRONTO  
**Infraestrutura:** ✅ MANTIDA (CloudFormation stack ativo)  
**Custos:** 💰 $3.70/mês (92% redução)  
**Próximo Passo:** Definir estratégia de deploy

---

**Gerado em:** 19 de outubro de 2025  
**Executado por:** Automação de Limpeza AWS  
**Tempo Total:** ~2 minutos
