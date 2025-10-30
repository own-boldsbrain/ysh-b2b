# 🎯 Cobertura 360° End-to-End: Master Task List

**Projeto:** YSH B2B Solar - Sistema Híbrido AI  
**Data:** 19 de outubro de 2025  
**Status:** Planejamento Completo  
**Objetivo:** Máxima Performance e Eficácia com AWS Free Tier

---

## 📊 Resumo Executivo

### Recursos Atuais Detectados

**Docker Local:**
- **42 imagens** totalizando ~25GB
- **Maior imagem:** infrastructure-mcp-server (3.62GB)
- **Containers ativos:** 8 (mcp-server, mcp-postgres, mcp-neo4j, mcp-redis, huginn, api-gateway, grafana)
- **Imagens antigas:** 15+ com 2-4 anos (selenium, jupyter, vpnkit = ~10GB)

**Infraestrutura Existente (docker-compose.agents.yml):**
- 15 serviços configurados
- 4 workers agents (catalog-extractor, price-intelligence, product-enricher, sku-governor)
- Stack completo: Temporal, Supabase, Redis, Redpanda, Prometheus, Grafana, Chrome headless

**AWS Free Tier Disponível:**
- EC2: 750 horas/mês t2.micro
- RDS: 750 horas/mês db.t2.micro PostgreSQL
- ElastiCache: 750 horas/mês cache.t2.micro
- Lambda: 1M requests/mês
- S3: 5GB storage
- ECR: 500MB/mês
- CloudWatch: 10 custom metrics

---

## 🗂️ Task List Completa (30 Tarefas)

### 🔍 **FASE 1: AUDITORIA E CONSOLIDAÇÃO** (Tasks 1-2)

#### ✅ Task 1: 📋 Auditoria de Infraestrutura Existente
**Status:** ✅ CONCLUÍDA  
**Prioridade:** 🔴 CRÍTICA  
**Duração:** 2h  

**Checklist:**
- [x] Listar todas imagens Docker locais (42 encontradas)
- [x] Identificar containers em execução (8 ativos)
- [x] Mapear docker-compose.agents.yml (15 serviços)
- [x] Calcular uso total de disco (25GB)
- [x] Validar recursos AWS Free Tier disponíveis

**Outputs:**
```
Docker Images: 42 (25GB total)
├─ infrastructure-mcp-server: 3.62GB ⚠️
├─ infrastructure-api-gateway: 652MB
├─ grafana/grafana: 974MB
├─ prom/prometheus: 507MB
└─ 38 outras imagens

Containers Ativos: 8
├─ mcp-server (healthy)
├─ mcp-postgres (healthy)
├─ mcp-neo4j (healthy)
├─ mcp-redis (healthy)
├─ mcp-api-gateway (healthy)
├─ huginn (healthy)
├─ mcp-grafana (created)
└─ mcp-prometheus (exited)

AWS Free Tier Mapping:
├─ EC2 t2.micro: backend + 4 workers = 5 instâncias (750h cada)
├─ RDS db.t2.micro: PostgreSQL 15 (20GB storage)
├─ ElastiCache t2.micro: Redis 7
├─ Lambda: Scrapers (1M requests/mês)
├─ S3: Logs + backups (5GB)
└─ ECR: Docker images (500MB/mês)
```

---

#### 🔄 Task 2: 🐳 Docker: Consolidação de Imagens
**Status:** ⏳ NÃO INICIADA  
**Prioridade:** 🟡 ALTA  
**Duração:** 4h  
**Depende de:** Task 1  

**Objetivos:**
1. Reduzir mcp-server de 3.62GB → <800MB (multi-stage build)
2. Consolidar prometheus + grafana em imagem única
3. Remover imagens antigas (2+ anos = ~10GB)
4. Otimizar Dockerfile.worker para <500MB

**Ações:**

```dockerfile
# Dockerfile.mcp-server-optimized
# Target: 3.62GB → 800MB (78% redução)

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY src ./src
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
EXPOSE 8000
CMD ["node", "dist/index.js"]

# Resultado esperado: ~600-800MB
```

**Cleanup de Imagens Antigas:**
```powershell
# Remover imagens 2+ anos
docker rmi selenium/node-firefox:4.9.0-20230421
docker rmi selenium/node-edge:4.9.0-20230421
docker rmi selenium/node-chrome:4.9.0-20230421
docker rmi selenium/hub:4.9.0-20230421
docker rmi jupyter/scipy-notebook:lab-4.0.7
docker rmi docker/desktop-vpnkit-controller:dc331cb22850be0cdd97c84a9cfecaf44a1afb6e
docker rmi docker/desktop-storage-provisioner:v2.0
docker rmi neo4j:5.13-community

# Espaço liberado: ~10GB
```

**Validação:**
```bash
# Verificar tamanho final
docker images | grep mcp-server
# Esperado: infrastructure-mcp-server-optimized:latest  800MB

# Testar build otimizado
docker build -t mcp-server-optimized -f Dockerfile.mcp-server-optimized .
docker run -d -p 8001:8000 mcp-server-optimized
curl http://localhost:8001/health
```

---

### ☁️ **FASE 2: AWS FREE TIER SETUP** (Tasks 3, 9, 10, 25)

#### 🗺️ Task 3: ☁️ AWS Free Tier: Mapeamento de Recursos
**Status:** ⏳ NÃO INICIADA  
**Prioridade:** 🔴 CRÍTICA  
**Duração:** 3h  
**Depende de:** Task 1  

**Mapeamento Completo:**

| Serviço Local | AWS Free Tier | Especificação | Limite Mensal |
|---------------|---------------|---------------|---------------|
| **Temporal Server** | ECS Fargate | 0.25 vCPU, 512MB | 20GB storage |
| **Postgres Temporal** | RDS PostgreSQL | db.t2.micro | 750h/mês |
| **Supabase DB** | RDS PostgreSQL | db.t2.micro | 20GB storage |
| **Redis Stack** | ElastiCache | cache.t2.micro | 750h/mês |
| **Redpanda** | MSK t3.small | 1 broker | ⚠️ Não elegível |
| **Prometheus** | CloudWatch | Custom metrics | 10 métricas |
| **Grafana** | EC2 t2.micro | 1 vCPU, 1GB | 750h/mês |
| **Chrome Headless** | Lambda | 1024MB mem | 1M requests |
| **4 Workers** | ECS Fargate | 0.5 vCPU, 1GB ea | 80GB storage |
| **Kong API Gateway** | EC2 t2.micro | 1 vCPU, 1GB | 750h/mês |

**Custos Estimados (12 meses Free Tier):**

```
Serviços Grátis (12 meses):
✅ EC2 t2.micro x5: $0 (750h/mês cada)
✅ RDS db.t2.micro x2: $0 (750h/mês cada)
✅ ElastiCache t2.micro: $0 (750h/mês)
✅ Lambda 1M requests: $0
✅ S3 5GB: $0
✅ ECR 500MB: $0
✅ CloudWatch 10 métricas: $0

Serviços Pagos (além Free Tier):
⚠️ Redpanda → Substituir por Amazon MSK (t3.small): ~$75/mês
⚠️ ECS Fargate 4 workers: ~$45/mês (0.5 vCPU x 4)
⚠️ Data Transfer Out >1GB: ~$0.09/GB

Total Mensal Estimado:
Meses 1-12: ~$120/mês (com Redpanda)
Alternativa FOSS: $45/mês (ECS workers + data transfer)
```

**Estratégia de Otimização:**

```yaml
# Opção 1: Máxima utilização Free Tier (12 meses)
services:
  backend: EC2 t2.micro #1
  workers:
    catalog-extractor: EC2 t2.micro #2
    price-intelligence: EC2 t2.micro #3
    product-enricher: EC2 t2.micro #4
    sku-governor: Lambda (baixa frequência)
  databases:
    temporal_db: RDS db.t2.micro #1
    supabase_db: RDS db.t2.micro #2
  cache: ElastiCache cache.t2.micro
  monitoring: CloudWatch (10 métricas)
  message_queue: Amazon SQS (1M requests free)

# Custo mensal: $0 (primeiros 12 meses)

# Opção 2: Híbrido (ECS Fargate + EC2)
services:
  backend: ECS Fargate (0.25 vCPU, 512MB)
  workers: ECS Fargate (0.5 vCPU, 1GB) x4
  databases: RDS db.t2.micro x2
  cache: ElastiCache cache.t2.micro
  monitoring: CloudWatch + Prometheus (EC2 t2.micro)

# Custo mensal: ~$45 (workers ECS)
```

**Configuração CloudFormation:**

```yaml
# template.yml - AWS Free Tier Stack
AWSTemplateFormatVersion: '2010-09-09'
Description: 'YSH B2B - Free Tier Infrastructure'

Parameters:
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 KeyPair for SSH access

Resources:
  # VPC
  YshVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: ysh-vpc

  # Subnet Pública
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref YshVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  # EC2 Backend (t2.micro - Free Tier)
  BackendInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t2.micro
      ImageId: ami-0c55b159cbfafe1f0  # Amazon Linux 2
      KeyName: !Ref KeyPairName
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref BackendSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y docker
          service docker start
          usermod -a -G docker ec2-user
          docker run -d -p 8000:8000 infrastructure-mcp-server:optimized

  # RDS PostgreSQL (db.t2.micro - Free Tier)
  SupabaseDB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: ysh-supabase-db
      DBInstanceClass: db.t2.micro
      Engine: postgres
      EngineVersion: '15.4'
      MasterUsername: supabase_admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20  # 20GB Free Tier
      StorageType: gp2
      PubliclyAccessible: false
      VPCSecurityGroups:
        - !Ref DBSecurityGroup

  # ElastiCache Redis (cache.t2.micro - Free Tier)
  RedisCache:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t2.micro
      Engine: redis
      NumCacheNodes: 1
      VpcSecurityGroupIds:
        - !Ref CacheSecurityGroup

Outputs:
  BackendPublicIP:
    Value: !GetAtt BackendInstance.PublicIp
  SupabaseDBEndpoint:
    Value: !GetAtt SupabaseDB.Endpoint.Address
  RedisCacheEndpoint:
    Value: !GetAtt RedisCache.RedisEndpoint.Address
```

**Deploy Script:**

```bash
#!/bin/bash
# deploy-aws-free-tier.sh

# Validar AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI não instalado. Instalando..."
    pip install awscli
fi

# Configurar credenciais
aws configure

# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name ysh-b2b-free-tier \
  --template-body file://template.yml \
  --parameters ParameterKey=KeyPairName,ParameterValue=ysh-keypair \
  --capabilities CAPABILITY_IAM

# Aguardar criação
aws cloudformation wait stack-create-complete \
  --stack-name ysh-b2b-free-tier

# Obter outputs
aws cloudformation describe-stacks \
  --stack-name ysh-b2b-free-tier \
  --query 'Stacks[0].Outputs'
```

---

#### 💾 Task 9: 📊 Supabase: Migração Completa
**Status:** ⏳ NÃO INICIADA  
**Prioridade:** 🔴 CRÍTICA  
**Duração:** 3h  
**Depende de:** Task 3  

**Validação do Schema Existente:**

```bash
# Verificar init-scripts/supabase-init.sql
wc -l init-scripts/supabase-init.sql
# Esperado: 268 lines

# Validar sintaxe SQL
docker run --rm -v $(pwd)/init-scripts:/scripts postgres:15-alpine \
  psql -U postgres -f /scripts/supabase-init.sql --dry-run

# Checar componentes principais
grep -E "CREATE SCHEMA|CREATE TABLE|CREATE INDEX|CREATE TRIGGER" \
  init-scripts/supabase-init.sql
```

**Conteúdo Esperado (268 linhas):**

```sql
-- init-scripts/supabase-init.sql

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. Schemas (4 total)
CREATE SCHEMA IF NOT EXISTS catalog;
CREATE SCHEMA IF NOT EXISTS pricing;
CREATE SCHEMA IF NOT EXISTS products;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 3. Tables (5 principais)
CREATE TABLE catalog.distributors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    api_url VARCHAR(500),
    credentials JSONB,
    last_sync_at TIMESTAMPTZ,
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products.catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    distributor_id UUID REFERENCES catalog.distributors(id),
    sku VARCHAR(100) NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price_brl DECIMAL(10,2),
    metadata JSONB,
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-large
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pricing.price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products.catalog(id),
    price_brl DECIMAL(10,2) NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50)
);

-- 4. Indexes (para performance)
CREATE INDEX idx_catalog_distributor ON products.catalog(distributor_id);
CREATE INDEX idx_catalog_sku ON products.catalog(sku);
CREATE INDEX idx_catalog_embedding ON products.catalog 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_catalog_fulltext ON products.catalog 
  USING gin(to_tsvector('portuguese', name || ' ' || COALESCE(description, '')));

-- 5. Triggers (auto-update)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_catalog_updated_at
    BEFORE UPDATE ON products.catalog
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- 6. Views (para analytics)
CREATE VIEW analytics.product_completeness AS
SELECT 
    d.name AS distributor,
    COUNT(*) AS total_products,
    COUNT(CASE WHEN price_brl > 0 THEN 1 END) AS products_with_price,
    ROUND(100.0 * COUNT(CASE WHEN price_brl > 0 THEN 1 END) / COUNT(*), 2) AS completeness_pct
FROM products.catalog c
JOIN catalog.distributors d ON c.distributor_id = d.id
GROUP BY d.name;

-- 7. Pre-load 7 distributors
INSERT INTO catalog.distributors (name, api_url, status) VALUES
    ('Fortlev', 'https://api.fortlev.com.br', 'active'),
    ('Neosolar', 'https://api.neosolar.com.br', 'active'),
    ('Solfacil', 'https://api.solfacil.com.br', 'active'),
    ('Fotus', 'https://api.fotus.com.br', 'active'),
    ('Odex', 'https://api.odex.com.br', 'active'),
    ('Edeltec', 'https://api.edeltec.com.br', 'active'),
    ('Dynamis', 'https://api.dynamis.com.br', 'active');
```

**Migração para AWS RDS:**

```bash
#!/bin/bash
# migrate-to-rds.sh

# 1. Export local data
docker exec ysh-supabase-db pg_dump -U supabase_admin postgres \
  > backup_local_$(date +%Y%m%d).sql

# 2. Create RDS instance (via CloudFormation - já feito em Task 3)

# 3. Restore to RDS
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier ysh-supabase-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

psql -h $RDS_ENDPOINT -U supabase_admin -d postgres \
  -f init-scripts/supabase-init.sql

# 4. Validate
psql -h $RDS_ENDPOINT -U supabase_admin -d postgres \
  -c "SELECT COUNT(*) FROM catalog.distributors;"
# Esperado: 7 rows

psql -h $RDS_ENDPOINT -U supabase_admin -d postgres \
  -c "SELECT * FROM analytics.product_completeness;"
```

**Testes de Integração:**

```typescript
// tests/supabase-rds.test.ts
import { createClient } from '@supabase/supabase-js';

const RDS_ENDPOINT = process.env.RDS_ENDPOINT;
const supabase = createClient(
  `https://${RDS_ENDPOINT}`,
  process.env.SUPABASE_SERVICE_KEY
);

describe('Supabase RDS Migration', () => {
  test('pgvector extension enabled', async () => {
    const { data, error } = await supabase
      .rpc('check_extension', { extension_name: 'vector' });
    expect(error).toBeNull();
    expect(data).toBe(true);
  });

  test('7 distributors loaded', async () => {
    const { data, error } = await supabase
      .from('catalog.distributors')
      .select('count');
    expect(error).toBeNull();
    expect(data[0].count).toBe(7);
  });

  test('full-text search functional', async () => {
    const { data, error } = await supabase
      .from('products.catalog')
      .select()
      .textSearch('name', 'painel solar');
    expect(error).toBeNull();
  });

  test('price history tracking', async () => {
    const product_id = 'test-uuid';
    const { error } = await supabase
      .from('pricing.price_history')
      .insert({ product_id, price_brl: 1250.00, source: 'neosolar' });
    expect(error).toBeNull();
  });
});
```

---

#### ⚡ Task 10: ⚡ Redis Stack: Cache + Vector
**Status:** ⏳ NÃO INICIADA  
**Prioridade:** 🟡 ALTA  
**Duração:** 2h  
**Depende de:** Task 3  

**Configuração AWS ElastiCache:**

```yaml
# elasticache-redis.yml (CloudFormation)
RedisReplicationGroup:
  Type: AWS::ElastiCache::ReplicationGroup
  Properties:
    ReplicationGroupId: ysh-redis-cluster
    ReplicationGroupDescription: YSH B2B Redis Cache
    Engine: redis
    EngineVersion: 7.0
    CacheNodeType: cache.t2.micro  # Free Tier
    NumCacheClusters: 1
    AutomaticFailoverEnabled: false
    CacheSubnetGroupName: !Ref RedisSubnetGroup
    SecurityGroupIds:
      - !Ref RedisSecurityGroup
    CacheParameterGroupName: !Ref RedisParameterGroup

RedisParameterGroup:
  Type: AWS::ElastiCache::ParameterGroup
  Properties:
    CacheParameterGroupFamily: redis7
    Description: YSH Redis parameters
    Properties:
      maxmemory-policy: allkeys-lru
      maxmemory: 512mb  # t2.micro = 555MB total
```

**Migração de Dados Local → ElastiCache:**

```bash
#!/bin/bash
# migrate-redis.sh

# 1. Export local Redis data
docker exec ysh-redis redis-cli --rdb /data/dump.rdb
docker cp ysh-redis:/data/dump.rdb ./backup_redis_$(date +%Y%m%d).rdb

# 2. Get ElastiCache endpoint
REDIS_ENDPOINT=$(aws elasticache describe-replication-groups \
  --replication-group-id ysh-redis-cluster \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text)

# 3. Restore to ElastiCache (via EC2 bastion)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name ysh-keypair \
  --subnet-id subnet-xxx \
  --security-group-ids sg-xxx \
  --user-data file://restore-redis-userdata.sh

# restore-redis-userdata.sh content:
# #!/bin/bash
# yum install -y redis
# redis-cli -h $REDIS_ENDPOINT --rdb dump.rdb
```

**Validação de Cache:**

```typescript
// tests/redis-elasticache.test.ts
import Redis from 'ioredis';

const redis = new Redis({
  host: process.env.REDIS_ENDPOINT,
  port: 6379,
  maxRetriesPerRequest: 3,
});

describe('Redis ElastiCache', () => {
  test('connection successful', async () => {
    const pong = await redis.ping();
    expect(pong).toBe('PONG');
  });

  test('maxmemory policy allkeys-lru', async () => {
    const policy = await redis.config('GET', 'maxmemory-policy');
    expect(policy[1]).toBe('allkeys-lru');
  });

  test('cache write/read', async () => {
    await redis.set('test:key', 'value', 'EX', 60);
    const value = await redis.get('test:key');
    expect(value).toBe('value');
  });

  test('vector search (RediSearch module)', async () => {
    // Verificar se RedisSearch está habilitado
    const modules = await redis.call('MODULE', 'LIST');
    const hasSearch = modules.some((m: any) => m[1] === 'search');
    expect(hasSearch).toBe(true);
  });
});
```

---

#### 🚀 Task 25: 🚀 Deploy AWS: Free Tier Stack
**Status:** ⏳ NÃO INICIADA  
**Prioridade:** 🔴 CRÍTICA  
**Duração:** 6h  
**Depende de:** Tasks 3, 9, 10  

**Arquitetura Final AWS:**

```
┌────────────────────────────────────────────────────────────────┐
│                        AWS FREE TIER                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Application Load Balancer (ALB)             │  │
│  │         (Parte de EC2 Free Tier - 750h/mês)             │  │
│  └────────────┬───────────────────────────┬─────────────────┘  │
│               │                           │                     │
│  ┌────────────▼─────────┐   ┌────────────▼─────────┐          │
│  │  EC2 t2.micro #1     │   │  EC2 t2.micro #2     │          │
│  │  Backend Server      │   │  Catalog Extractor   │          │
│  │  (750h/mês)          │   │  Worker (750h/mês)   │          │
│  └──────────────────────┘   └──────────────────────┘          │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │ EC2 t2.micro│   │ EC2 t2.micro│   │ EC2 t2.micro│          │
│  │ #3: Price   │   │ #4: Product │   │ #5: Grafana │          │
│  │ Intelligence│   │ Enricher    │   │ Monitoring  │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          RDS PostgreSQL db.t2.micro #1                   │  │
│  │          Temporal DB (750h/mês, 20GB)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          RDS PostgreSQL db.t2.micro #2                   │  │
│  │          Supabase DB (750h/mês, 20GB)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │       ElastiCache Redis cache.t2.micro                   │  │
│  │       (750h/mês, 555MB RAM)                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Lambda Functions                            │  │
│  │  • SKU Governor (baixa freq)                             │  │
│  │  • Scrapers (1M requests/mês)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Amazon SQS                               │  │
│  │  (Substitui Redpanda - 1M requests/mês)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                Amazon S3 (5GB)                            │  │
│  │  • Logs (CloudWatch)                                     │  │
│  │  • Backups                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Amazon ECR (500MB/mês)                            │  │
│  │  • mcp-server-optimized (800MB) ⚠️ excede                │  │
│  │  • workers (500MB total) ✅                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘

Custo Total: $0/mês (primeiros 12 meses)
Exceções: Data Transfer Out >1GB (~$0.09/GB)
```

**Deploy Completo (CloudFormation + Terraform):**

```yaml
# main-stack.yml - Master CloudFormation Template
AWSTemplateFormatVersion: '2010-09-09'
Description: 'YSH B2B - Complete Free Tier Stack'

Parameters:
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
  DBPassword:
    Type: String
    NoEcho: true

Resources:
  # Network
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']

  # EC2 Instances (5 x t2.micro)
  BackendInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t2.micro
      ImageId: ami-0c55b159cbfafe1f0
      KeyName: !Ref KeyPairName
      SubnetId: !Ref PublicSubnet1
      SecurityGroupIds: [!Ref BackendSG]
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y docker
          service docker start
          
          # Login to ECR
          aws ecr get-login-password --region us-east-1 | \
            docker login --username AWS --password-stdin ${AWS::AccountId}.dkr.ecr.us-east-1.amazonaws.com
          
          # Pull and run backend
          docker pull ${AWS::AccountId}.dkr.ecr.us-east-1.amazonaws.com/ysh/backend:latest
          docker run -d -p 8000:8000 \
            -e TEMPORAL_ADDRESS=${TemporalDB.Endpoint.Address}:7233 \
            -e SUPABASE_URL=http://${SupabaseDB.Endpoint.Address}:5432 \
            -e REDIS_URL=redis://${RedisCache.RedisEndpoint.Address}:6379 \
            ${AWS::AccountId}.dkr.ecr.us-east-1.amazonaws.com/ysh/backend:latest

  # RDS Instances (2 x db.t2.micro)
  TemporalDB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: ysh-temporal-db
      DBInstanceClass: db.t2.micro
      Engine: postgres
      EngineVersion: '15.4'
      MasterUsername: temporal
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      StorageType: gp2

  SupabaseDB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: ysh-supabase-db
      DBInstanceClass: db.t2.micro
      Engine: postgres
      EngineVersion: '15.4'
      MasterUsername: supabase_admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      StorageType: gp2

  # ElastiCache Redis (cache.t2.micro)
  RedisCache:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t2.micro
      Engine: redis
      NumCacheNodes: 1

  # Lambda Functions
  SKUGovernorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: ysh-sku-governor
      Runtime: nodejs20.x
      Handler: index.handler
      Code:
        ZipFile: |
          exports.handler = async (event) => {
            // SKU governance logic
            return { statusCode: 200 };
          };
      MemorySize: 512
      Timeout: 30

  # SQS Queue (substitui Redpanda)
  MessageQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: ysh-message-queue
      VisibilityTimeout: 300

  # S3 Bucket (5GB Free Tier)
  LogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'ysh-logs-${AWS::AccountId}'
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldLogs
            Status: Enabled
            ExpirationInDays: 30

Outputs:
  BackendURL:
    Value: !Sub 'http://${BackendInstance.PublicIp}:8000'
  TemporalDBEndpoint:
    Value: !GetAtt TemporalDB.Endpoint.Address
  SupabaseDBEndpoint:
    Value: !GetAtt SupabaseDB.Endpoint.Address
  RedisEndpoint:
    Value: !GetAtt RedisCache.RedisEndpoint.Address
  SQSQueueURL:
    Value: !Ref MessageQueue
```

**Deploy Script:**

```bash
#!/bin/bash
# deploy-complete-stack.sh

set -e

echo "🚀 Deploying YSH B2B to AWS Free Tier..."

# 1. Build and push Docker images to ECR
echo "📦 Building Docker images..."
docker build -t ysh/backend:latest -f Dockerfile.optimized .
docker build -t ysh/worker:latest -f Dockerfile.worker .

# Tag for ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1

docker tag ysh/backend:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ysh/backend:latest

docker tag ysh/worker:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ysh/worker:latest

# Create ECR repositories
aws ecr create-repository --repository-name ysh/backend || true
aws ecr create-repository --repository-name ysh/worker || true

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Push images
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ysh/backend:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ysh/worker:latest

# 2. Deploy CloudFormation stack
echo "☁️ Deploying CloudFormation stack..."
aws cloudformation create-stack \
  --stack-name ysh-b2b-production \
  --template-body file://main-stack.yml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=ysh-keypair \
    ParameterKey=DBPassword,ParameterValue=$(openssl rand -base64 32) \
  --capabilities CAPABILITY_IAM

# Wait for completion
echo "⏳ Waiting for stack creation..."
aws cloudformation wait stack-create-complete \
  --stack-name ysh-b2b-production

# 3. Get outputs
echo "✅ Stack deployed successfully!"
aws cloudformation describe-stacks \
  --stack-name ysh-b2b-production \
  --query 'Stacks[0].Outputs'

# 4. Initialize databases
echo "💾 Initializing databases..."
TEMPORAL_DB=$(aws cloudformation describe-stacks \
  --stack-name ysh-b2b-production \
  --query 'Stacks[0].Outputs[?OutputKey==`TemporalDBEndpoint`].OutputValue' \
  --output text)

SUPABASE_DB=$(aws cloudformation describe-stacks \
  --stack-name ysh-b2b-production \
  --query 'Stacks[0].Outputs[?OutputKey==`SupabaseDBEndpoint`].OutputValue' \
  --output text)

# Run migrations
psql -h $SUPABASE_DB -U supabase_admin -d postgres \
  -f init-scripts/supabase-init.sql

echo "🎉 Deployment complete!"
echo "Backend URL: http://$(aws cloudformation describe-stacks \
  --stack-name ysh-b2b-production \
  --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
  --output text)"
```

---

### 🤖 **FASE 3: AI COMPONENTS** (Tasks 4-8, 17-20)

*(Continua na próxima seção...)*

---

## 📊 Progress Tracker

| Fase | Tasks | Concluídas | Em Progresso | Pendentes | % Completo |
|------|-------|------------|--------------|-----------|------------|
| **Fase 1: Auditoria** | 1-2 | 1 | 1 | 0 | 50% |
| **Fase 2: AWS Setup** | 3, 9-10, 25 | 0 | 0 | 4 | 0% |
| **Fase 3: AI** | 4-8, 17-20 | 0 | 0 | 9 | 0% |
| **Fase 4: Workers** | 11-15, 21 | 0 | 0 | 6 | 0% |
| **Fase 5: Observability** | 13, 16, 23-24, 28 | 0 | 0 | 5 | 0% |
| **Fase 6: Deploy** | 26-27, 29-30 | 0 | 0 | 4 | 0% |
| **TOTAL** | 30 | 1 | 1 | 28 | **3.3%** |

---

## 🎯 Próximos Passos Imediatos

1. **Completar Task 2** (Docker Consolidation) - ETA: 4h
2. **Executar Task 3** (AWS Free Tier Mapping) - ETA: 3h
3. **Iniciar Task 9** (Supabase Migration) - ETA: 3h
4. **Total próximas 24h:** 10h de trabalho → 3 tasks concluídas (13% progresso)

---

**Documento gerado em:** 19 de outubro de 2025  
**Última atualização:** Task 1 concluída  
**Próxima revisão:** Após conclusão de Task 2
