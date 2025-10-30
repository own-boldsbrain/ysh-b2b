# Inventário de Recursos AWS - YSH B2B Platform
**Data**: 19 de outubro de 2025  
**Perfil**: ysh-production  
**Região**: us-east-1  
**Account ID**: 773235999227

---

## 📊 Status da Infraestrutura

### ✅ Recursos Provisionados (via CloudFormation)

#### 🌐 Networking

| Recurso | ID/Endpoint | Status |
|---------|-------------|--------|
| **VPC** | `vpc-096abb11405bb44af` | ✅ Ativo |
| **Private Subnet 1** | `subnet-0a7620fdf057a8824` | ✅ Ativo |
| **Private Subnet 2** | `subnet-09c23e75aed3a5d76` | ✅ Ativo |
| **ECS Security Group** | `sg-06563301eba0427b2` | ✅ Ativo |
| **ALB Security Group** | `sg-04504f1416350279a` | ✅ Ativo |
| **DB Security Group** | `sg-0ed77cd5394f86cad` | ✅ Ativo |

#### 🐳 ECS Fargate

| Recurso | Nome/ARN | Detalhes |
|---------|----------|----------|
| **ECS Cluster** | `production-ysh-b2b-cluster` | Fargate + Fargate Spot |
| **Backend Service** | Medusa.js 2.10.3 | Task Definition disponível |
| **Storefront Service** | Next.js 15 | Task Definition disponível |
| **Migrations Task** | One-time runner | Task Definition disponível |

**Task Definitions Configuradas**:
- ✅ `backend-task-definition.json` (6.57 KB)
- ✅ `backend-migrations-task-definition.json` (4.20 KB)
- ✅ `backend-migrations-seed-task-definition.json` (4.31 KB)
- ✅ `storefront-task-definition.json` (4.54 KB)

#### 🗄️ Database (RDS PostgreSQL)

| Parâmetro | Valor |
|-----------|-------|
| **Endpoint** | `production-ysh-b2b-postgres.cmxiy0wqok6l.us-east-1.rds.amazonaws.com` |
| **Engine** | PostgreSQL (provavelmente 15.x) |
| **Port** | 5432 (padrão) |
| **Database** | `medusa_db` |
| **Username** | `medusa_user` |
| **Instance Class** | db.t4g.micro (Free Tier) |
| **Storage** | 20 GB SSD |
| **Multi-AZ** | Não (Free Tier) |

#### 🔴 Redis (ElastiCache)

| Parâmetro | Valor |
|-----------|-------|
| **Endpoint** | `production-ysh-b2b-redis.97x7fb.0001.use1.cache.amazonaws.com` |
| **Port** | 6379 (padrão) |
| **Engine** | Redis (provavelmente 7.x) |
| **Node Type** | cache.t4g.micro (Free Tier) |
| **Cluster Mode** | Disabled |

#### ⚖️ Application Load Balancer

| Parâmetro | Valor |
|-----------|-------|
| **DNS Name** | `production-ysh-b2b-alb-1849611639.us-east-1.elb.amazonaws.com` |
| **ARN** | `arn:aws:elasticloadbalancing:us-east-1:773235999227:loadbalancer/app/production-ysh-b2b-alb/7343171857909489` |
| **Scheme** | Internet-facing |
| **Listeners** | HTTP (80) → HTTPS (443) |

**Target Groups** (configurados em `target-groups-config.json`):
- Backend API (porta 9000)
- Storefront (porta 8000)

#### 📦 S3 Bucket (Media Storage)

**Configuração esperada** (via CloudFormation):

```yaml
Bucket Name: production-ysh-media-773235999227
Region: us-east-1
Access: Private (Block all public access)
CORS: Configurado para domínios YSH
Size: ~ 0-5 GB (Free Tier)
Objects: Imagens de produtos, uploads de usuários
```

**⚠️ Status**: Bucket pode não estar criado ainda (CloudFormation com domínio não deployado)

---

## 🚀 Services ECS Configurados

### Backend (Medusa.js 2.10.3)

```json
{
  "serviceName": "backend-service",
  "taskDefinition": "backend-task",
  "desiredCount": 1,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "subnets": ["subnet-0a7620fdf057a8824", "subnet-09c23e75aed3a5d76"],
    "securityGroups": ["sg-06563301eba0427b2"]
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:...:targetgroup/backend-tg",
      "containerName": "backend",
      "containerPort": 9000
    }
  ]
}
```

**Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: Medusa JWT secret
- `COOKIE_SECRET`: Medusa cookie secret
- `MEDUSA_ADMIN_ONBOARDING_TYPE`: skip
- `S3_BUCKET`: production-ysh-media-773235999227
- `AWS_REGION`: us-east-1

### Storefront (Next.js 15)

```json
{
  "serviceName": "storefront-service",
  "taskDefinition": "storefront-task",
  "desiredCount": 1,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "subnets": ["subnet-0a7620fdf057a8824", "subnet-09c23e75aed3a5d76"],
    "securityGroups": ["sg-06563301eba0427b2"]
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:...:targetgroup/storefront-tg",
      "containerName": "storefront",
      "containerPort": 8000
    }
  ]
}
```

**Environment Variables**:
- `NEXT_PUBLIC_MEDUSA_BACKEND_URL`: http://backend-service:9000
- `NEXT_PUBLIC_BASE_URL`: https://yellosolarhub.store
- `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY`: pk_xxxxx

---

## 📝 Scripts de Deployment Disponíveis

### 1. `post-deployment.ps1` (Orquestrador Principal)

```powershell
.\aws\post-deployment.ps1 `
    -Environment production `
    -AdminEmail fernando@yellosolarhub.com `
    -AlertEmail suporte@yellosolarhub.com `
    -InteractiveMode
```

**Tarefas**:
- ✅ Deploy ECS tasks
- ✅ Setup database (migrations + seed)
- ✅ Configurar monitoring
- ✅ Configurar environment variables

### 2. `1-deploy-ecs-tasks.ps1`

```powershell
.\aws\1-deploy-ecs-tasks.ps1 -Environment production
```

### 3. `2-setup-database.ps1`

```powershell
.\aws\2-setup-database.ps1 -Environment production
```

### 4. `3-setup-monitoring.ps1`

```powershell
.\aws\3-setup-monitoring.ps1 -Environment production -AlertEmail suporte@yellosolarhub.com
```

---

## 🔑 Credenciais e Secrets

### AWS Secrets Manager

Secrets esperados (não criados ainda):

```
production/ysh-b2b/database-url
production/ysh-b2b/redis-url
production/ysh-b2b/jwt-secret
production/ysh-b2b/cookie-secret
production/ysh-b2b/publishable-key
```

### IAM Roles

```
ECSTaskExecutionRole: Para pull de imagens ECR
ECSTaskRole: Para acesso S3, Secrets Manager, CloudWatch
```

---

## 💰 Estimativa de Custos (Free Tier)

| Recurso | Uso Mensal | Custo |
|---------|------------|-------|
| **ECS Fargate** | 2 tasks × 0.25 vCPU × 730h | ~$7.50 |
| **RDS PostgreSQL** | db.t4g.micro 750h | **$0** (Free Tier) |
| **ElastiCache Redis** | cache.t4g.micro 750h | **$0** (Free Tier) |
| **ALB** | 1 ALB + requests | ~$16.20 |
| **S3** | < 5 GB storage + requests | **$0** (Free Tier) |
| **Data Transfer** | < 100 GB/mês | **$0** (Free Tier) |
| **CloudWatch Logs** | < 5 GB/mês | **$0** (Free Tier) |
| **TOTAL ESTIMADO** | | **~$23.70/mês** |

---

## 🔍 Verificação de Recursos

### Para listar recursos reais via AWS CLI:

```bash
# 1. Fazer login SSO
aws sso login --profile ysh-production

# 2. Listar buckets S3
aws s3 ls --profile ysh-production

# 3. Listar instâncias EC2 (se houver)
aws ec2 describe-instances --profile ysh-production

# 4. Listar clusters ECS
aws ecs list-clusters --profile ysh-production

# 5. Listar services ECS
aws ecs list-services --cluster production-ysh-b2b-cluster --profile ysh-production

# 6. Descrever instâncias RDS
aws rds describe-db-instances --profile ysh-production

# 7. Descrever clusters ElastiCache
aws elasticache describe-cache-clusters --profile ysh-production
```

### Ou usar o script Python criado:

```bash
# Fazer login SSO primeiro
aws sso login --profile ysh-production

# Executar verificação completa
python scripts/check-aws-resources.py
```

---

## 📊 Dados Armazenados (Esperados)

### S3 Bucket: `production-ysh-media-773235999227`

**Estrutura esperada**:

```
production-ysh-media-773235999227/
├── products/
│   ├── NEO-INV-DEYE-SUN-8K/
│   │   ├── hero.webp
│   │   ├── meta.jpg
│   │   ├── thumb.webp
│   │   └── gallery/
│   │       ├── angle-1.webp
│   │       ├── angle-2.webp
│   │       └── detail-closeup.webp
│   └── ... (2.914 produtos)
├── uploads/
│   ├── customer-documents/
│   └── company-logos/
└── temp/
```

**Status atual**: Provavelmente vazio ou não criado (aguardando deployment com CloudFormation domain)

### RDS PostgreSQL: `production-ysh-b2b-postgres`

**Databases**:
- `medusa_db` (Medusa.js core)
- Schemas: public, company, quote, approval

**Tabelas principais**:
- `product` (2.914 registros esperados)
- `product_variant` (16.532 SKUs esperados)
- `company` (empresas B2B)
- `employee` (colaboradores)
- `quote` (cotações)
- `approval` (aprovações de carrinhos)
- `order` (pedidos)

**Status**: Aguardando migrations (`yarn medusa db:migrate` + `yarn run seed`)

---

## 🚨 Próximos Passos

### 1. Fazer Login SSO

```bash
aws sso login --profile ysh-production
```

### 2. Verificar Recursos Reais

```bash
python scripts/check-aws-resources.py
```

### 3. Verificar se S3 Bucket Existe

```bash
aws s3 ls s3://production-ysh-media-773235999227 --profile ysh-production
```

### 4. Se Bucket não existir, criar via CloudFormation

```bash
aws cloudformation deploy \
  --template-file aws/cloudformation-with-domain.yml \
  --stack-name ysh-b2b-infrastructure \
  --parameter-overrides \
    Environment=production \
    DomainName=yellosolarhub.store \
    HostedZoneId=ZXXXXXXXXXXXXX \
    CertificateArn=arn:aws:acm:us-east-1:773235999227:certificate/xxxxx \
  --capabilities CAPABILITY_IAM \
  --profile ysh-production
```

### 5. Deploy ECS Services

```powershell
.\aws\1-deploy-ecs-tasks.ps1 -Environment production
```

### 6. Setup Database

```powershell
.\aws\2-setup-database.ps1 -Environment production
```

---

## 📚 Documentação Relacionada

- [AWS Deployment Guide](./aws/DEPLOYMENT_GUIDE_DOMAIN.md)
- [Post Deployment README](./aws/POST_DEPLOYMENT_README.md)
- [Product Image Automation Strategy](./docs/PRODUCT_IMAGE_AUTOMATION_STRATEGY.md)
- [Meta Commerce Integration Blueprint](./docs/META_COMMERCE_INTEGRATION_BLUEPRINT.md)

---

**Última Atualização**: 2025-10-19  
**Status**: ⚠️ Infraestrutura provisionada, aguardando login SSO para verificação completa
