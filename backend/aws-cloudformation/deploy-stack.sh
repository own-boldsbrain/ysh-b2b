#!/bin/bash
# deploy-stack.sh - Deploy completo da stack AWS Free Tier

set -e

echo "🚀 YSH B2B - AWS Free Tier Deployment"
echo "════════════════════════════════════════════════════════════"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
STACK_NAME="ysh-b2b-production"
REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo -e "${CYAN}📋 Configurações:${NC}"
echo "  • Stack Name: $STACK_NAME"
echo "  • Region: $REGION"
echo "  • AWS Account: $AWS_ACCOUNT_ID"
echo ""

# Validar AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI não encontrado. Instalando...${NC}"
    pip3 install awscli
fi

# Configurar credenciais se necessário
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${YELLOW}⚙️  Configurando AWS CLI...${NC}"
    aws configure
fi

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}📦 Etapa 1/4: Build de Imagens Docker${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Build imagens otimizadas
echo -e "${YELLOW}🐳 Building backend image...${NC}"
docker build -t ysh/backend:latest -f Dockerfile.mcp-server-optimized .

echo ""
echo -e "${YELLOW}🐳 Building worker image...${NC}"
docker build -t ysh/worker:latest -f Dockerfile.worker .

echo -e "${GREEN}✅ Imagens construídas${NC}"

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}📤 Etapa 2/4: Push para ECR${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Criar repositórios ECR
echo -e "${YELLOW}📦 Criando repositórios ECR...${NC}"
aws ecr create-repository --repository-name ysh/backend --region $REGION 2>/dev/null || true
aws ecr create-repository --repository-name ysh/worker --region $REGION 2>/dev/null || true

# Login ECR
echo -e "${YELLOW}🔐 Login no ECR...${NC}"
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Tag imagens
echo -e "${YELLOW}🏷️  Tagging images...${NC}"
docker tag ysh/backend:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/ysh/backend:latest

docker tag ysh/worker:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/ysh/worker:latest

# Push imagens
echo -e "${YELLOW}📤 Pushing backend image...${NC}"
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/ysh/backend:latest

echo -e "${YELLOW}📤 Pushing worker image...${NC}"
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/ysh/worker:latest

echo -e "${GREEN}✅ Imagens no ECR${NC}"

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}☁️  Etapa 3/4: Deploy CloudFormation Stack${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Gerar senha segura para banco de dados
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "/@\"'")

echo -e "${YELLOW}🔑 Gerando senha do banco de dados...${NC}"
echo "DB_PASSWORD=$DB_PASSWORD" > .env.aws
echo -e "${GREEN}✅ Senha salva em .env.aws (mantenha seguro!)${NC}"

# Validar template
echo -e "${YELLOW}✅ Validando template CloudFormation...${NC}"
aws cloudformation validate-template \
  --template-body file://aws-cloudformation/main-stack.yml \
  --region $REGION

# Deploy stack
echo ""
echo -e "${YELLOW}🚀 Criando CloudFormation stack...${NC}"
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://aws-cloudformation/main-stack.yml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=ysh-keypair \
    ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD \
  --capabilities CAPABILITY_IAM \
  --region $REGION

# Aguardar criação
echo ""
echo -e "${YELLOW}⏳ Aguardando criação da stack (isso pode levar 15-20 minutos)...${NC}"
aws cloudformation wait stack-create-complete \
  --stack-name $STACK_NAME \
  --region $REGION

echo -e "${GREEN}✅ Stack criada com sucesso!${NC}"

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}💾 Etapa 4/4: Inicialização de Databases${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Obter outputs
echo -e "${YELLOW}📊 Obtendo endpoints...${NC}"
SUPABASE_DB=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`SupabaseDBEndpoint`].OutputValue' \
  --output text)

TEMPORAL_DB=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`TemporalDBEndpoint`].OutputValue' \
  --output text)

REDIS_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' \
  --output text)

BACKEND_URL=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
  --output text)

# Inicializar Supabase DB
echo -e "${YELLOW}💾 Inicializando Supabase DB...${NC}"
PGPASSWORD=$DB_PASSWORD psql \
  -h $SUPABASE_DB \
  -U supabase_admin \
  -d postgres \
  -f init-scripts/supabase-init.sql

echo -e "${GREEN}✅ Supabase DB inicializado${NC}"

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}📋 Informações da Stack:${NC}"
echo ""
echo -e "${YELLOW}Backend API:${NC}"
echo "  $BACKEND_URL"
echo ""
echo -e "${YELLOW}Databases:${NC}"
echo "  • Supabase DB: $SUPABASE_DB:5432"
echo "  • Temporal DB: $TEMPORAL_DB:5432"
echo ""
echo -e "${YELLOW}Cache:${NC}"
echo "  • Redis: $REDIS_ENDPOINT:6379"
echo ""
echo -e "${YELLOW}Credenciais:${NC}"
echo "  • DB Password: Salva em .env.aws"
echo ""

echo -e "${CYAN}💡 Próximos passos:${NC}"
echo "  1. Testar health: curl $BACKEND_URL/health"
echo "  2. Ver logs: aws logs tail /aws/ec2/ysh-backend --follow"
echo "  3. Monitorar custos: aws ce get-cost-and-usage"
echo ""

echo -e "${YELLOW}⚠️  Lembrete: Stack está no Free Tier por 12 meses${NC}"
echo ""
