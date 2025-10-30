#!/bin/bash

set -e

echo "🚀 YSH Agents - Deploy Completo"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Verificando pré-requisitos..."

command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker não instalado${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose não instalado${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ Node.js não instalado${NC}"; exit 1; }

echo -e "${GREEN}✅ Pré-requisitos OK${NC}"
echo ""

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  ATENÇÃO: Configure suas credenciais em .env antes de continuar${NC}"
    echo ""
    read -p "Pressione Enter após configurar o .env..."
fi

echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
echo ""

# Install dependencies
echo "📦 Instalando dependências..."
npm install --silent
echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo ""

# Build TypeScript
echo "🔨 Compilando TypeScript..."
npm run build
echo -e "${GREEN}✅ Build concluído${NC}"
echo ""

# Stop existing containers
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.agents.yml down 2>/dev/null || true
echo -e "${GREEN}✅ Containers parados${NC}"
echo ""

# Pull images
echo "📥 Baixando imagens Docker..."
docker-compose -f docker-compose.agents.yml pull
echo -e "${GREEN}✅ Imagens atualizadas${NC}"
echo ""

# Start infrastructure
echo "🏗️  Iniciando infraestrutura base..."
docker-compose -f docker-compose.agents.yml up -d \
  postgres-temporal \
  temporal-server \
  supabase-db \
  kong \
  meta \
  supabase-studio \
  redis \
  redpanda

echo "⏳ Aguardando serviços iniciarem (90s)..."
sleep 90

# Check health
echo ""
echo "🏥 Verificando saúde dos serviços..."

check_service() {
  local service=$1
  local url=$2
  echo -n "  - ${service}: "
  if curl -sf "${url}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
  else
    echo -e "${RED}❌${NC}"
    return 1
  fi
}

check_service "Temporal" "http://localhost:8080"
check_service "Supabase" "http://localhost:54321"
check_service "Redis" "http://localhost:8001"
check_service "Redpanda" "http://localhost:19644/metrics"

echo ""

# Run migrations
echo "🗄️  Executando migrations..."
export SUPABASE_URL=http://localhost:8000
export SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

docker exec ysh-supabase-db psql -U supabase_admin -d postgres -f /docker-entrypoint-initdb.d/init.sql 2>/dev/null || echo -e "${YELLOW}⚠️  Migrations já executadas${NC}"
echo -e "${GREEN}✅ Database configurado${NC}"
echo ""

# Start observability
echo "📊 Iniciando observabilidade..."
docker-compose -f docker-compose.agents.yml up -d \
  prometheus \
  grafana \
  loki \
  promtail \
  redpanda-console

echo "⏳ Aguardando Grafana (30s)..."
sleep 30
echo -e "${GREEN}✅ Observabilidade ativa${NC}"
echo ""

# Start browser automation
echo "🌐 Iniciando browser automation..."
docker-compose -f docker-compose.agents.yml up -d chrome
echo "⏳ Aguardando Chrome (15s)..."
sleep 15
echo -e "${GREEN}✅ Chrome pronto${NC}"
echo ""

# Start workers
echo "🤖 Iniciando agent workers..."
docker-compose -f docker-compose.agents.yml up -d \
  catalog-extractor-worker \
  price-intelligence-worker \
  product-enricher-worker \
  sku-governor-worker

echo "⏳ Aguardando workers (30s)..."
sleep 30
echo -e "${GREEN}✅ Workers ativos${NC}"
echo ""

# Final status
echo "═══════════════════════════════════════"
echo "🎉 Deploy Concluído com Sucesso!"
echo "═══════════════════════════════════════"
echo ""
echo "📊 Interfaces Web:"
echo "  - Temporal UI:       http://localhost:8080"
echo "  - Supabase Studio:   http://localhost:54321"
echo "  - Grafana:           http://localhost:3000 (admin/admin)"
echo "  - Prometheus:        http://localhost:9090"
echo "  - Redis Commander:   http://localhost:8001"
echo "  - Redpanda Console:  http://localhost:8082"
echo ""
echo "🔧 Comandos úteis:"
echo "  - Ver logs:          docker-compose -f docker-compose.agents.yml logs -f"
echo "  - Status serviços:   docker-compose -f docker-compose.agents.yml ps"
echo "  - Parar tudo:        docker-compose -f docker-compose.agents.yml down"
echo "  - Restart:           docker-compose -f docker-compose.agents.yml restart <service>"
echo ""
echo "🚀 Próximos passos:"
echo "  1. Acesse Temporal UI para ver workflows"
echo "  2. Acesse Supabase Studio para ver produtos"
echo "  3. Execute: npm run workflow:extract -- --distributor neosolar"
echo ""
echo "📚 Documentação: AGENTES_SWARM_ESTRATEGIA_DEFINITIVA.md"
echo ""
